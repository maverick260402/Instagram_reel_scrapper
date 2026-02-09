from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, status, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse, Response
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import sys
from pathlib import Path
from datetime import datetime, timedelta
import asyncio
import io
import csv
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import math
# Add Scripts directory to path
scripts_dir = Path(__file__).parent / "Scripts"
sys.path.insert(0, str(scripts_dir))

# Import new cookie-based pipeline
from pipeline_with_cookie_extraction import (
    get_target_id_with_cookie,
    fetch_reels_paginated_with_cookie,
    extract_metadata_to_csv,
    CookieManager,
    extract_cookie_value
)

# Import new modules
from database import get_db, init_db
from config import settings
import models
import schemas
import crud
from auth import get_current_user, authenticate_user, create_access_token, hash_password
from account_rotation import get_least_used_account, increment_account_usage, NoAccountsAvailableError
from credit_system import validate_scrape_request, deduct_credits, InsufficientCreditsError
from scheduler import start_scheduler, stop_scheduler
import admin_routes

# Initialize FastAPI app
app = FastAPI(
    title="Instagram Reel Scraper API",
    description="Multi-user Instagram reel scraping with analytics",
    version="2.0.0"
)

# In-memory job storage (temporary, will migrate to database polling)
jobs_db: Dict[str, dict] = {}

# ==================== Instagram Cookie Configuration ====================
# Instagram credentials loaded from environment variables
INSTAGRAM_EMAIL = settings.INSTAGRAM_EMAIL
INSTAGRAM_PASSWORD = settings.INSTAGRAM_PASSWORD

# Initialize global cookie manager (only if credentials are configured)
cookie_manager = None
if INSTAGRAM_EMAIL and INSTAGRAM_PASSWORD:
    cookie_manager = CookieManager(INSTAGRAM_EMAIL, INSTAGRAM_PASSWORD)
else:
    print("[WARN] Instagram credentials not configured in .env - cookie extraction fallback disabled")

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


# Rate limit exceeded handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return Response(
        content='{"detail": "Rate limit exceeded. Please try again later."}',
        status_code=429,
        media_type="application/json"
    )


# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


# CORS middleware (restricted configuration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
)

# Mount static files
frontend_path = Path(__file__).parent.parent / "Frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

# Include routers
app.include_router(admin_routes.router)


# ==================== Startup/Shutdown Events ====================

@app.on_event("startup")
async def startup_event():
    """Initialize database and scheduler on startup"""
    print("Starting Instagram Reel Scraper API...")
    try:
        init_db()
        print("[OK] Database initialized successfully")
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")
        print("API will start but database features will not work")

    try:
        start_scheduler()
        print("[OK] Daily reset scheduler started")
    except Exception as e:
        print(f"[ERROR] Scheduler initialization failed: {e}")
        print("Daily resets will not work automatically")


@app.on_event("shutdown")
async def shutdown_event():
    """Gracefully shut down scheduler"""
    try:
        stop_scheduler()
        print("[OK] Scheduler stopped")
    except Exception as e:
        print(f"[ERROR] Scheduler shutdown failed: {e}")


# ==================== Root & Health Check ====================

@app.get("/")
async def read_root():
    """Serve the landing page"""
    landing_path = frontend_path / "landing.html"
    if landing_path.exists():
        return FileResponse(landing_path)
    return {"message": "Instagram Reel Scraper API - Multi-User Version"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "2.0.0"}


# ==================== Authentication Endpoints ====================

@app.post("/api/auth/signup", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
async def signup(request: Request, user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if email already exists
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if username already exists
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create user
    db_user = crud.create_user(db, user)
    print(f"New user registered: {db_user.email}")

    return db_user


@app.post("/api/auth/login", response_model=schemas.Token)
@limiter.limit("5/minute")
async def login(request: Request, user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """Login and get access token"""
    user = authenticate_user(db, user_credentials.email, user_credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(
        data={"user_id": user.id, "email": user.email}
    )

    print(f"User logged in: {user.email}")

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@app.get("/api/auth/me", response_model=schemas.UserResponse)
async def get_current_user_info(current_user: models.User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


# ==================== User Groups Endpoints ====================

@app.get("/api/groups", response_model=List[schemas.UserGroupResponse])
async def get_groups(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all groups for current user"""
    groups = crud.get_user_groups(db, current_user.id)
    return groups


@app.post("/api/groups", response_model=schemas.UserGroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    group: schemas.UserGroupCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new user group"""
    try:
        db_group = crud.create_group(db, current_user.id, group)
        print(f"Group created: '{db_group.name}' by user {current_user.email}")
        return db_group
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.put("/api/groups/{group_id}", response_model=schemas.UserGroupResponse)
async def update_group(
    group_id: int,
    group_update: schemas.UserGroupUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a user group"""
    try:
        db_group = crud.update_group(db, group_id, current_user.id, group_update)
        if not db_group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
        print(f"Group updated: '{db_group.name}' by user {current_user.email}")
        return db_group
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.delete("/api/groups/{group_id}", response_model=schemas.MessageResponse)
async def delete_group(
    group_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a user group"""
    success = crud.delete_group(db, group_id, current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    print(f"Group deleted: ID {group_id} by user {current_user.email}")
    return {"message": "Group deleted successfully", "success": True}


# ==================== Scraping Endpoints (Enhanced) ====================

def run_scraping_job_with_db(
    job_id: str,
    user_id: int,
    usernames: List[str],
    reel_count: int,
    instagram_account_id: int,
    group_id: Optional[int] = None
):
    """Background task to run the scraping job with database integration"""
    import time as time_module
    from database import SessionLocal

    start_time = time_module.time()
    db = SessionLocal()

    # Disable autoflush for better performance during bulk operations
    db.autoflush = False

    try:
        print(f"\n{'='*60}")
        print(f"STARTING BACKGROUND JOB: {job_id}")
        print(f"   User ID: {user_id}")
        print(f"   Usernames: {usernames}")
        print(f"   Reel count: {reel_count}")
        print(f"   Instagram Account ID: {instagram_account_id}")
        print(f"   Time: {time_module.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")

        # Get Instagram account from database
        instagram_account = crud.get_instagram_account_by_id(db, instagram_account_id)
        if not instagram_account:
            raise Exception(f"Instagram account {instagram_account_id} not found")

        print(f"[INFO] Using Instagram account: {instagram_account.username}")

        # Get cookies from Instagram account (or use cookie manager as fallback)
        if instagram_account.cookie_string:
            cookie_string = instagram_account.cookie_string
            print("[INFO] Using stored cookies from Instagram account")
        elif cookie_manager:
            print("[WARN] No cookies stored for account, using cookie manager...")
            cookie_string = cookie_manager.get_cookie()
        else:
            raise Exception("No cookies available and cookie manager not configured. Please update cookies for this account.")

        # Create job in database with Instagram account linkage
        db_job = crud.create_job(db, user_id, job_id, usernames, reel_count, instagram_account_id)

        # Update group usage if from group
        if group_id:
            crud.update_group_usage(db, group_id, user_id)

        results = []

        for idx, username in enumerate(usernames, 1):
            # Update job progress in memory only (faster, no DB write)
            progress = (idx - 1) / len(usernames) * 100
            jobs_db[job_id]['progress'] = progress
            jobs_db[job_id]['current_username'] = username

            # Only update database every 5 usernames or on first/last to reduce DB writes
            if idx == 1 or idx == len(usernames) or idx % 5 == 0:
                crud.update_job_status(db, job_id, 'running', progress=progress)

            print(f"\n[{idx}/{len(usernames)}] Processing username: {username}")
            try:
                # Get target ID with cookie
                target_id = get_target_id_with_cookie(username, cookie_string)
                if not target_id:
                    result = {
                        'username': username,
                        'status': 'failed',
                        'error': 'Could not find target ID'
                    }
                    results.append(result)
                    continue

                # Fetch reels with pagination using cookie
                meta_output_path = fetch_reels_paginated_with_cookie(
                    target_id,
                    username,
                    cookie_string,
                    desired_count=reel_count,
                    sleep_seconds=3.0,
                    max_per_page=50
                )

                if meta_output_path:
                    # Extract metadata to DataFrame and save CSV
                    df_result = extract_metadata_to_csv(str(meta_output_path))

                    # Save reels to database - use vectorized operations (much faster than iterrows)
                    reels_data = df_result.to_dict('records')
                    # Add username to each record
                    for reel in reels_data:
                        reel['username'] = username
                        # Ensure numeric fields are integers
                        reel['pk'] = str(reel.get('pk') or '')
                        # Safe int conversion (handles None, NaN, and invalid values)
                        def safe_int(val):
                            if val is None:
                                return 0
                            try:
                                if math.isnan(float(val)):
                                    return 0
                            except (TypeError, ValueError):
                                pass
                            try:
                                return int(float(val))
                            except (TypeError, ValueError):
                                return 0
                        reel['play_count'] = safe_int(reel.get('play_count'))
                        reel['comment_count'] = safe_int(reel.get('comment_count'))
                        reel['like_count'] = safe_int(reel.get('like_count'))
#                        reel['play_count'] = int(reel.get('play_count') or 0)
#                        reel['comment_count'] = int(reel.get('comment_count') or 0)
#                        reel['like_count'] = int(reel.get('like_count') or 0)
#
#            reel['pk'] = str(reel.get('pk', ''))
#                        reel['play_count'] = int(reel.get('play_count', 0))
#                        reel['comment_count'] = int(reel.get('comment_count', 0))
#                        reel['like_count'] = int(reel.get('like_count', 0))

                    # Bulk insert reels with Instagram account tracking
                    crud.bulk_create_reels(db, user_id, job_id, reels_data, instagram_account_id)

                    # Deduct credits for successfully scraped reels
                    reels_scraped = len(df_result)
                    deduct_credits(db, user_id, reels_scraped)
                    print(f"[CREDITS] Deducted {reels_scraped} credits from user {user_id}")

                    result = {
                        'username': username,
                        'status': 'success',
                        'reels_scraped': reels_scraped,
                        'csv_path': str(Path(meta_output_path).parent / "scrapped_data.csv"),
                        'json_path': str(meta_output_path)
                    }
                    results.append(result)
                else:
                    result = {
                        'username': username,
                        'status': 'failed',
                        'error': 'Failed to retrieve meta data'
                    }
                    results.append(result)
         
            except Exception as e:
                print(f"[ERROR] Failed to process {username}: {str(e)}")
                import traceback
                traceback.print_exc()
                result = {
                    'username': username,
                    'status': 'failed',
                    'error': str(e)
                }

                results.append(result)

        elapsed_time = time_module.time() - start_time

        # Calculate total reels successfully scraped
        total_reels_scraped = sum(r.get('reels_scraped', 0) for r in results if r['status'] == 'success')

        # Update Instagram account usage counters
        if total_reels_scraped > 0:
            increment_account_usage(db, instagram_account_id, total_reels_scraped)
            print(f"[ACCOUNT] Updated usage for Instagram account {instagram_account_id}: +{total_reels_scraped} reels")

        # Log activity

        crud.create_activity_log(
            db=db,
            event_type="scrape_job_completed",
            user_id=user_id,
            instagram_account_id=instagram_account_id,
            job_id=job_id,
            details={
                "usernames": usernames,
                "total_reels_scraped": total_reels_scraped,
                "successful_accounts": sum(1 for r in results if r['status'] == 'success'),
                "failed_accounts": sum(1 for r in results if r['status'] == 'failed'),
                "duration_seconds": elapsed_time
            }
        )

        # Update job status to completed in both memory and database
        jobs_db[job_id]['status'] = 'completed'
        jobs_db[job_id]['progress'] = 100
        jobs_db[job_id]['results'] = results
        jobs_db[job_id]['end_time'] = datetime.now().isoformat()
        jobs_db[job_id]['duration'] = elapsed_time

        crud.update_job_status(db, job_id, 'completed', progress=100, duration=elapsed_time)

        print(f"\n{'='*60}")
        print(f"BACKGROUND JOB COMPLETED: {job_id}")
        print(f"   Total time: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
        print(f"   Successful: {sum(1 for r in results if r['status'] == 'success')}/{len(results)}")
        print(f"   Failed: {sum(1 for r in results if r['status'] == 'failed')}/{len(results)}")
        print(f"   Total reels scraped: {total_reels_scraped}")
        print(f"   Reels saved to database")
        print(f"{'='*60}\n")

    except Exception as e:
        # Update job as failed
        error_msg = str(e)
        jobs_db[job_id]['status'] = 'failed'
        jobs_db[job_id]['error_message'] = error_msg
        crud.update_job_status(db, job_id, 'failed', error_message=error_msg)

        # Log failure
        crud.create_activity_log(
            db=db,
            event_type="scrape_job_failed",
            user_id=user_id,
            instagram_account_id=instagram_account_id,
            job_id=job_id,
            details={
                "error": error_msg,
                "usernames": usernames
            }
        )

        print(f"\nJOB FAILED: {job_id} - {error_msg}\n")

    finally:
        db.close()


@app.post("/api/scrape", response_model=schemas.JobStartResponse)
@limiter.limit("10/minute")
async def scrape_reels(
    request: Request,
    scrape_request: schemas.ScrapeRequest,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a scraping job (requires authentication, validates credits, uses account rotation)"""
    try:
        usernames = scrape_request.usernames
        reel_count = scrape_request.reel_count
        group_id = scrape_request.group_id

        if not usernames:
            raise HTTPException(status_code=400, detail="No usernames provided")

        # Calculate total reels requested
        total_reels_requested = len(usernames) * reel_count

        # Validate user has enough credits
        is_valid, validation_msg, remaining_credits = validate_scrape_request(
            db, current_user.id, total_reels_requested
        )

        if not is_valid:
            # Log credit limit reached
            crud.create_activity_log(
                db=db,
                event_type="credit_limit_reached",
                user_id=current_user.id,
                instagram_account_id=None,
                job_id=None,
                details={
                    "requested_reels": total_reels_requested,
                    "remaining_credits": remaining_credits
                }
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=validation_msg
            )

        # Get least used Instagram account
        try:
            instagram_account = get_least_used_account(db)
        except NoAccountsAvailableError as e:
            # Log no accounts available
            crud.create_activity_log(
                db=db,
                event_type="no_accounts_available",
                user_id=current_user.id,
                instagram_account_id=None,
                job_id=None,
                details={
                    "requested_reels": total_reels_requested,
                    "usernames": usernames
                }
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(e)
            )

        # Generate unique job ID
        job_id = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        # Create job record in memory
        jobs_db[job_id] = {
            'job_id': job_id,
            'user_id': current_user.id,
            'status': 'running',
            'progress': 0,
            'usernames': usernames,
            'reel_count': reel_count,
            'start_time': datetime.now().isoformat(),
            'current_username': None,
            'results': [],
            'end_time': None,
            'duration': None
        }

        print(f"\nSCRAPE REQUEST RECEIVED - Job ID: {job_id}")
        print(f"   User: {current_user.email}")
        print(f"   Usernames: {usernames}")
        print(f"   Reel count: {reel_count}")
        print(f"   Instagram Account: {instagram_account.username} (ID: {instagram_account.id})")
        print(f"   Credits remaining: {remaining_credits}\n")

        # Start background task with Instagram account rotation
        background_tasks.add_task(
            run_scraping_job_with_db,
            job_id,
            current_user.id,
            usernames,
            reel_count,
            instagram_account.id,  # Pass Instagram account ID
            group_id
        )

        # Return immediately with job ID
        return {
            'job_id': job_id,
            'status': 'started',
            'message': f'Scraping job started using Instagram account {instagram_account.username}. Use /api/job/{{job_id}} to check status'
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"\nERROR: {str(e)}\n")
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/api/job/{job_id}")
async def get_job_status(
    job_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the status of a scraping job (user must own the job)"""
    print(f"\nSTATUS REQUEST for job: {job_id} by user: {current_user.email}")

    # First check in-memory for running jobs
    if job_id in jobs_db:
        job = jobs_db[job_id]
        # Verify user owns this job
        if job.get('user_id') != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to view this job")
        print(f"Job found in memory - Status: {job['status']}, Progress: {job['progress']}%")
        return job
    
    # Fallback: Check database for completed/failed jobs
    db_job = db.query(models.ScrapingJob).filter(
        models.ScrapingJob.job_id == job_id,
        models.ScrapingJob.user_id == current_user.id
    ).first()
    
    if not db_job:
        print(f"Job {job_id} NOT FOUND in memory or database")
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    print(f"Job found in database - Status: {db_job.status}")

    # Build results array from scraped reels
    results = []
    for username in (db_job.usernames or []):
        reel_count = db.query(models.ScrapedReel).filter(
            models.ScrapedReel.job_id == job_id,
            models.ScrapedReel.instagram_username == username
        ).count()
        results.append({
            "username": username,
            "status": "success" if reel_count > 0 else "failed",
            "reels_scraped": reel_count,
            "message": f"Scraped {reel_count} reels" if reel_count > 0 else "No reels found"
        })
    
    # Return job data from database
    return {
        "job_id": db_job.job_id,
        "status": db_job.status,
        "progress": db_job.progress,
        "usernames": db_job.usernames,
        "reel_count": db_job.reel_count,
        "start_time": db_job.start_time.isoformat() if db_job.start_time else None,
        "end_time": db_job.end_time.isoformat() if db_job.end_time else None,
        "duration": db_job.duration,
        "error_message": db_job.error_message,
        "credits_consumed": db_job.credits_consumed,
        "user_id": db_job.user_id,
        "results": results
    }


#@app.get("/api/job/{job_id}")
#async def get_job_status(
#    job_id: str,
#    current_user: models.User = Depends(get_current_user)
#):
#    """Get the status of a scraping job (user must own the job)"""
#    print(f"\nSTATUS REQUEST for job: {job_id} by user: {current_user.email}")
#
#    if job_id not in jobs_db:
#        print(f"Job {job_id} NOT FOUND in memory")
#        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
#
#    job = jobs_db[job_id]
#
#    # Verify user owns this job
#    if job.get('user_id') != current_user.id:
#        raise HTTPException(status_code=403, detail="Not authorized to view this job")
#
#    print(f"Job found - Status: {job['status']}, Progress: {job['progress']}%")
#
#    return job
#*/

# ==================== Analytics Endpoints ====================

@app.get("/api/analytics", response_model=schemas.AnalyticsResponse)
async def get_analytics(
    username: Optional[str] = None,
    group_id: Optional[int] = None,
    min_play_count: Optional[int] = None,
    min_like_count: Optional[int] = None,
    min_comment_count: Optional[int] = None,
    min_engagement_ratio: Optional[float] = None,
    sort_by: str = "scraped_at",
    sort_order: str = "desc",
    page: int = 1,
    per_page: int = 50,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics data with filtering and pagination - supports multiple usernames and group filtering"""
    reels, total = crud.get_analytics_reels(
        db=db,
        user_id=current_user.id,
        username=username,
        group_id=group_id,
        min_play_count=min_play_count,
        min_like_count=min_like_count,
        min_comment_count=min_comment_count,
        min_engagement_ratio=min_engagement_ratio,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        per_page=per_page
    )

    pages = (total + per_page - 1) // per_page  # Ceiling division

    return {
        "items": reels,
        "total": total,
        "page": page,
        "pages": pages,
        "per_page": per_page
    }


@app.get("/api/analytics/usernames")
async def get_unique_usernames(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of unique usernames that the user has scraped"""
    usernames = crud.get_unique_usernames(db, current_user.id)
    return {"usernames": usernames}


@app.get("/api/analytics/export")
async def export_analytics_csv(
    username: Optional[str] = None,
    group_id: Optional[int] = None,
    min_play_count: Optional[int] = None,
    min_like_count: Optional[int] = None,
    min_comment_count: Optional[int] = None,
    min_engagement_ratio: Optional[float] = None,
    sort_by: str = "scraped_at",
    sort_order: str = "desc",
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export analytics data as CSV"""
    # Get all reels (no pagination for export)
    reels, _ = crud.get_analytics_reels(
        db=db,
        user_id=current_user.id,
        username=username,
        group_id=group_id,
        min_play_count=min_play_count,
        min_like_count=min_like_count,
        min_comment_count=min_comment_count,
        min_engagement_ratio=min_engagement_ratio,
        sort_by=sort_by,
        sort_order=sort_order,
        page=1,
        per_page=10000  # Get all
    )

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(['Username', 'Play Count', 'Like Count', 'Comment Count', 'Engagement Ratio', 'URL', 'Scraped At'])

    # Write data
    for reel in reels:
        writer.writerow([
            reel.instagram_username,
            reel.play_count,
            reel.like_count,
            reel.comment_count,
            reel.engagement_ratio,
            reel.reel_url,
            reel.scraped_at.isoformat()
        ])

    # Return as streaming response
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        }
    )


# ==================== Admin API Endpoints (Cookie Management) ====================

def verify_api_key(x_api_key: str = Header(...)):
    """Verify API key for admin endpoints"""
    from database import SessionLocal
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    db = SessionLocal()

    try:
        # Get all active API keys
        api_keys = crud.get_all_api_keys(db)

        # Check if provided key matches any active API key
        for api_key_record in api_keys:
            if api_key_record.is_active and pwd_context.verify(x_api_key, api_key_record.api_key):
                # Update last used timestamp
                api_key_record.last_used_at = datetime.now()
                db.commit()

                # Return a dict instead of the model object to avoid session binding issues
                return {
                    "id": api_key_record.id,
                    "key_name": api_key_record.key_name,
                    "is_active": api_key_record.is_active
                }

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key"
        )

    finally:
        db.close()


@app.post("/api/admin/instagram-accounts/{account_id}/cookies")
async def update_instagram_cookies(
    account_id: int,
    cookies: dict,
    api_key: dict = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Update cookies for a specific Instagram account (requires API key authentication)"""
    try:
        # Validate cookies not empty
        if not cookies or len(cookies) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cookies cannot be empty"
            )

        # Get Instagram account
        account = crud.get_instagram_account_by_id(db, account_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Instagram account with ID {account_id} not found"
            )

        # Format cookies for HTTP headers
        cookie_string = "; ".join([f"{name}={value}" for name, value in cookies.items()])

        # Extract CSRF token if present
        x_csrf_token = cookies.get('csrftoken', '')

        # Update account cookies
        crud.update_instagram_account_cookies(
            db=db,
            account_id=account_id,
            cookies=cookies,
            cookie_string=cookie_string,
            x_csrf_token=x_csrf_token
        )

        # Log the update
        crud.create_activity_log(
            db=db,
            event_type="cookies_updated",
            user_id=None,
            instagram_account_id=account_id,
            job_id=None,
            details={
                "account_username": account.username,
                "updated_by_api_key": api_key["key_name"],
                "cookies_count": len(cookies)
            }
        )

        print(f"[OK] Cookies updated for Instagram account: {account.username} (ID: {account_id})")

        return {
            "status": "success",
            "message": f"Cookies updated for account {account.username}",
            "account_id": account_id,
            "account_username": account.username,
            "updated_at": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to update cookies for account {account_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update cookies: {str(e)}"
        )


@app.post("/api/admin/instagram-accounts/bulk-update-cookies")
async def bulk_update_instagram_cookies(
    updates: List[dict],
    api_key: dict = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    Bulk update cookies for multiple Instagram accounts
    Expected format: [{"account_id": 1, "cookies": {...}}, {"account_id": 2, "cookies": {...}}]
    """
    try:
        if not updates or len(updates) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No updates provided"
            )

        results = []
        errors = []

        for update in updates:
            account_id = update.get('account_id')
            cookies = update.get('cookies')

            if not account_id or not cookies:
                errors.append({
                    "account_id": account_id,
                    "error": "Missing account_id or cookies"
                })
                continue

            try:
                # Get Instagram account
                account = crud.get_instagram_account_by_id(db, account_id)
                if not account:
                    errors.append({
                        "account_id": account_id,
                        "error": "Account not found"
                    })
                    continue

                # Format cookies
                cookie_string = "; ".join([f"{name}={value}" for name, value in cookies.items()])
                x_csrf_token = cookies.get('csrftoken', '')

                # Update cookies
                crud.update_instagram_account_cookies(
                    db=db,
                    account_id=account_id,
                    cookies=cookies,
                    cookie_string=cookie_string,
                    x_csrf_token=x_csrf_token
                )

                results.append({
                    "account_id": account_id,
                    "account_username": account.username,
                    "status": "success"
                })

                print(f"[OK] Bulk update: Cookies updated for {account.username}")

            except Exception as e:
                errors.append({
                    "account_id": account_id,
                    "error": str(e)
                })

        # Log bulk update
        crud.create_activity_log(
            db=db,
            event_type="bulk_cookies_updated",
            user_id=None,
            instagram_account_id=None,
            job_id=None,
            details={
                "updated_by_api_key": api_key["key_name"],
                "successful_updates": len(results),
                "failed_updates": len(errors),
                "total_requested": len(updates)
            }
        )

        return {
            "status": "completed",
            "successful_updates": len(results),
            "failed_updates": len(errors),
            "results": results,
            "errors": errors
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Bulk cookie update failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk update failed: {str(e)}"
        )


@app.post("/api/admin/instagram-accounts", status_code=201)
async def create_instagram_account_endpoint(
    account_data: schemas.InstagramAccountCreate,
    db: Session = Depends(get_db),
    admin: models.AdminUser = Depends(admin_routes.get_current_admin)
):
    """
    Create a new Instagram account in the pool.
    Only accessible by admin users.
    """
    try:
        # Check for duplicate username
        existing = crud.get_instagram_account_by_username(db, account_data.username)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Instagram account with username '{account_data.username}' already exists"
            )

        # Check for duplicate email
        existing_email = db.query(models.InstagramAccount).filter(
            models.InstagramAccount.email == account_data.email
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Instagram account with email '{account_data.email}' already exists"
            )

        # Create account
        new_account = crud.create_instagram_account(
            db=db,
            username=account_data.username,
            email=account_data.email,
            password=account_data.password
        )

        # Log activity
        crud.create_activity_log(
            db=db,
            event_type="account_created",
            user_id=None,
            instagram_account_id=new_account.id,
            job_id=None,
            details={
                "username": new_account.username,
                "email": new_account.email,
                "created_by_admin_id": admin.id,
                "created_by_admin_username": admin.username
            }
        )

        return {
            "status": "success",
            "message": f"Instagram account '{new_account.username}' created successfully",
            "account": {
                "id": new_account.id,
                "username": new_account.username,
                "email": new_account.email,
                "is_active": new_account.is_active,
                "is_paused": new_account.is_paused,
                "daily_scrape_count": new_account.daily_scrape_count,
                "total_scrapes": new_account.total_scrapes,
                "success_count": new_account.success_count,
                "failure_count": new_account.failure_count,
                "cookies_updated_at": new_account.cookies_updated_at,
                "created_at": new_account.created_at.isoformat()
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create Instagram account: {str(e)}"
        )


@app.get("/api/admin/instagram-accounts")
async def list_instagram_accounts(
    api_key: dict = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """List all Instagram accounts in the pool (requires API key authentication)"""
    try:
        accounts = crud.get_all_instagram_accounts(db)

        account_list = []
        for account in accounts:
            account_list.append({
                "id": account.id,
                "username": account.username,
                "email": account.email,
                "is_active": account.is_active,
                "is_paused": account.is_paused,
                "daily_scrape_count": account.daily_scrape_count,
                "total_scrapes": account.total_scrapes,
                "success_count": account.success_count,
                "failure_count": account.failure_count,
                "cookies_updated_at": account.cookies_updated_at.isoformat() if account.cookies_updated_at else None,
                "last_used_at": account.last_used_at.isoformat() if account.last_used_at else None
            })

        return {
            "status": "success",
            "count": len(account_list),
            "accounts": account_list
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list accounts: {str(e)}"
        )


# ==================== Server Startup ====================

if __name__ == '__main__':
    import uvicorn
    # Configure uvicorn with longer timeout for long-running scraping requests
    uvicorn.run(
        app,
        host="127.0.0.1",  # Changed from 0.0.0.0 to avoid Windows firewall issues
        port=8888,  # Changed to 8888 to avoid port conflicts
        timeout_keep_alive=600,  # 10 minutes keepalive timeout
        timeout_graceful_shutdown=30
    )
