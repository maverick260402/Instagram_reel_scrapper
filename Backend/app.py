from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import sys
from pathlib import Path
from datetime import datetime, timedelta
import asyncio
import io
import csv

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

# Initialize FastAPI app
app = FastAPI(
    title="Instagram Reel Scraper API",
    description="Multi-user Instagram reel scraping with analytics",
    version="2.0.0"
)

# In-memory job storage (temporary, will migrate to database polling)
jobs_db: Dict[str, dict] = {}

# ==================== Instagram Cookie Configuration ====================
# Instagram credentials for cookie extraction
# TODO: Move these to environment variables for production
INSTAGRAM_EMAIL = "jigglyphilcam@gmail.com"  # Set your Instagram email
INSTAGRAM_PASSWORD = "Maverick15#"  # Set your Instagram password

# Initialize global cookie manager
cookie_manager = CookieManager(INSTAGRAM_EMAIL, INSTAGRAM_PASSWORD)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
frontend_path = Path(__file__).parent.parent / "Frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")


# ==================== Startup/Shutdown Events ====================

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("Starting Instagram Reel Scraper API...")
    try:
        init_db()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization failed: {e}")
        print("API will start but database features will not work")


# ==================== Root & Health Check ====================

@app.get("/")
async def read_root():
    """Serve the login page"""
    login_path = frontend_path / "login.html"
    if login_path.exists():
        return FileResponse(login_path)
    return {"message": "Instagram Reel Scraper API - Multi-User Version"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "2.0.0"}


# ==================== Authentication Endpoints ====================

@app.post("/api/auth/signup", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
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
async def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
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
        print(f"   Time: {time_module.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")

        # Get Instagram cookies (uses cached or extracts fresh)
        print("🔑 Getting Instagram cookies...")
        cookie_string = cookie_manager.get_cookie()
        print("✔ Cookies ready\n")

        # Create job in database
        db_job = crud.create_job(db, user_id, job_id, usernames, reel_count)

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
                        reel['pk'] = str(reel.get('pk', ''))
                        reel['play_count'] = int(reel.get('play_count', 0))
                        reel['comment_count'] = int(reel.get('comment_count', 0))
                        reel['like_count'] = int(reel.get('like_count', 0))

                    # Bulk insert reels
                    crud.bulk_create_reels(db, user_id, job_id, reels_data)

                    result = {
                        'username': username,
                        'status': 'success',
                        'reels_scraped': len(df_result),
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
                result = {
                    'username': username,
                    'status': 'failed',
                    'error': str(e)
                }
                results.append(result)

        elapsed_time = time_module.time() - start_time

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
        print(f"   Reels saved to database")
        print(f"{'='*60}\n")

    except Exception as e:
        # Update job as failed
        error_msg = str(e)
        jobs_db[job_id]['status'] = 'failed'
        jobs_db[job_id]['error_message'] = error_msg
        crud.update_job_status(db, job_id, 'failed', error_message=error_msg)
        print(f"\nJOB FAILED: {job_id} - {error_msg}\n")

    finally:
        db.close()


@app.post("/api/scrape", response_model=schemas.JobStartResponse)
async def scrape_reels(
    request: schemas.ScrapeRequest,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a scraping job (requires authentication)"""
    try:
        usernames = request.usernames
        reel_count = request.reel_count
        group_id = request.group_id

        if not usernames:
            raise HTTPException(status_code=400, detail="No usernames provided")

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
        print(f"   Reel count: {reel_count}\n")

        # Start background task
        background_tasks.add_task(
            run_scraping_job_with_db,
            job_id,
            current_user.id,
            usernames,
            reel_count,
            group_id
        )

        # Return immediately with job ID
        return {
            'job_id': job_id,
            'status': 'started',
            'message': 'Scraping job started. Use /api/job/{job_id} to check status'
        }

    except Exception as e:
        print(f"\nERROR: {str(e)}\n")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/job/{job_id}")
async def get_job_status(
    job_id: str,
    current_user: models.User = Depends(get_current_user)
):
    """Get the status of a scraping job (user must own the job)"""
    print(f"\nSTATUS REQUEST for job: {job_id} by user: {current_user.email}")

    if job_id not in jobs_db:
        print(f"Job {job_id} NOT FOUND in memory")
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    job = jobs_db[job_id]

    # Verify user owns this job
    if job.get('user_id') != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this job")

    print(f"Job found - Status: {job['status']}, Progress: {job['progress']}%")

    return job


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


# ==================== Server Startup ====================

if __name__ == '__main__':
    import uvicorn
    # Configure uvicorn with longer timeout for long-running scraping requests
    uvicorn.run(
        app,
        host="127.0.0.1",  # Changed from 0.0.0.0 to avoid Windows firewall issues
        port=8080,  # Changed to 8080 to avoid Windows reserved port range (1-5000)
        timeout_keep_alive=600,  # 10 minutes keepalive timeout
        timeout_graceful_shutdown=30
    )
