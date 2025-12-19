"""
Admin Routes for Phase 3 - Admin Panel
Provides endpoints for user management, statistics, and monitoring
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc, text
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel

import models
import crud
from database import SessionLocal
from auth import get_current_user, create_access_token
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create router
router = APIRouter(prefix="/api/admin", tags=["admin"])


# ==================== DEPENDENCY ====================

def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_admin(current_user: models.User = Depends(get_current_user)):
    """Verify that current user is an admin"""
    # For now, we'll check if user exists in admin_users table
    # In the future, you can add an is_admin field to users table
    db = SessionLocal()
    try:
        admin = db.query(models.AdminUser).filter(
            models.AdminUser.email == current_user.email
        ).first()

        if not admin or not admin.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )

        return current_user
    finally:
        db.close()


# ==================== PYDANTIC MODELS ====================

class AdminLogin(BaseModel):
    email: str
    password: str


class UserUpdate(BaseModel):
    daily_credit_limit: Optional[int] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    daily_credit_limit: int
    credits_used_today: int
    is_active: bool
    created_at: datetime
    last_credit_reset_date: Optional[datetime]


class UserStatsResponse(BaseModel):
    user_id: int
    username: str
    email: str
    total_jobs: int
    total_reels_scraped: int
    credits_used_today: int
    credits_remaining: int
    daily_credit_limit: int
    last_job_date: Optional[datetime]


# ==================== AUTHENTICATION ====================

@router.post("/auth/login")
async def admin_login(credentials: AdminLogin, db: Session = Depends(get_db)):
    """Admin login endpoint"""
    try:
        # Find admin user
        admin = db.query(models.AdminUser).filter(
            models.AdminUser.email == credentials.email
        ).first()

        if not admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Verify password
        if not pwd_context.verify(credentials.password, admin.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Check if active
        if not admin.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin account is deactivated"
            )

        # Update last login
        admin.last_login = datetime.now()
        db.commit()

        # Create JWT token (reusing existing auth system)
        # We need to find or create corresponding user record
        user = db.query(models.User).filter(
            models.User.email == credentials.email
        ).first()

        if not user:
            # Create a user record for the admin
            user = models.User(
                email=credentials.email,
                username=admin.username,
                password_hash=admin.password_hash,
                daily_credit_limit=999999,  # Admins get unlimited credits
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # Generate token with user_id (required by get_current_user)
        access_token = create_access_token(data={"user_id": user.id})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": admin.id,
                "email": admin.email,
                "username": admin.username
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.get("/auth/me")
async def get_admin_profile(
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get current admin user profile"""
    admin = db.query(models.AdminUser).filter(
        models.AdminUser.email == current_user.email
    ).first()

    return {
        "id": admin.id,
        "email": admin.email,
        "username": admin.username,
        "is_active": admin.is_active,
        "last_login": admin.last_login
    }


# ==================== USER MANAGEMENT ====================

@router.get("/users")
async def list_users(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """List all users with optional filtering"""
    try:
        query = db.query(models.User)

        # Apply filters
        if is_active is not None:
            query = query.filter(models.User.is_active == is_active)

        # Get total count
        total = query.count()

        # Get users with pagination
        users = query.order_by(desc(models.User.created_at)).offset(skip).limit(limit).all()

        # Format response
        user_list = []
        for user in users:
            credits_remaining = user.daily_credit_limit - user.credits_used_today
            user_list.append({
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "daily_credit_limit": user.daily_credit_limit,
                "credits_used_today": user.credits_used_today,
                "credits_remaining": credits_remaining,
                "usage_percent": round((user.credits_used_today / user.daily_credit_limit) * 100, 1) if user.daily_credit_limit > 0 else 0,
                "is_active": user.is_active,
                "created_at": user.created_at,
                "last_credit_reset_date": user.last_credit_reset_date
            })

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "users": user_list
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch users: {str(e)}"
        )


@router.get("/users/{user_id}")
async def get_user_details(
    user_id: int,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific user"""
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        # Get user statistics
        total_jobs = db.query(func.count(models.ScrapingJob.id)).filter(
            models.ScrapingJob.user_id == user_id
        ).scalar()

        total_reels = db.query(func.count(models.ScrapedReel.id)).filter(
            models.ScrapedReel.user_id == user_id
        ).scalar()

        successful_jobs = db.query(func.count(models.ScrapingJob.id)).filter(
            and_(
                models.ScrapingJob.user_id == user_id,
                models.ScrapingJob.status == "completed"
            )
        ).scalar()

        # Get recent jobs
        recent_jobs = db.query(models.ScrapingJob).filter(
            models.ScrapingJob.user_id == user_id
        ).order_by(desc(models.ScrapingJob.created_at)).limit(10).all()

        recent_jobs_list = []
        for job in recent_jobs:
            recent_jobs_list.append({
                "job_id": job.job_id,
                "status": job.status,
                "target_usernames": job.target_usernames,
                "reels_scraped": job.reels_scraped,
                "credits_consumed": job.credits_consumed,
                "created_at": job.created_at,
                "completed_at": job.completed_at
            })

        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "daily_credit_limit": user.daily_credit_limit,
                "credits_used_today": user.credits_used_today,
                "credits_remaining": user.daily_credit_limit - user.credits_used_today,
                "is_active": user.is_active,
                "created_at": user.created_at,
                "last_credit_reset_date": user.last_credit_reset_date
            },
            "statistics": {
                "total_jobs": total_jobs,
                "successful_jobs": successful_jobs,
                "failed_jobs": total_jobs - successful_jobs,
                "success_rate": round((successful_jobs / total_jobs) * 100, 1) if total_jobs > 0 else 0,
                "total_reels_scraped": total_reels
            },
            "recent_jobs": recent_jobs_list
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user details: {str(e)}"
        )


@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    updates: UserUpdate,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update user settings (credit limit, active status)"""
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        # Apply updates
        if updates.daily_credit_limit is not None:
            user.daily_credit_limit = updates.daily_credit_limit

        if updates.is_active is not None:
            user.is_active = updates.is_active

        db.commit()
        db.refresh(user)

        # Log the update
        crud.create_activity_log(
            db=db,
            event_type="user_updated",
            user_id=user_id,
            instagram_account_id=None,
            job_id=None,
            details={
                "updated_by_admin": current_user.email,
                "updates": updates.dict(exclude_none=True)
            }
        )

        return {
            "status": "success",
            "message": f"User {user.username} updated successfully",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "daily_credit_limit": user.daily_credit_limit,
                "is_active": user.is_active
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Soft delete a user (deactivate)"""
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        # Soft delete (deactivate)
        user.is_active = False
        db.commit()

        # Log the deletion
        crud.create_activity_log(
            db=db,
            event_type="user_deleted",
            user_id=user_id,
            instagram_account_id=None,
            job_id=None,
            details={
                "deleted_by_admin": current_user.email,
                "user_email": user.email
            }
        )

        return {
            "status": "success",
            "message": f"User {user.username} deactivated successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )


@router.get("/users/{user_id}/stats")
async def get_user_stats(
    user_id: int,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get detailed statistics for a user"""
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        # Get daily usage for last 7 days
        seven_days_ago = datetime.now() - timedelta(days=7)

        daily_usage = db.query(
            func.date(models.ScrapedReel.scraped_at).label('date'),
            func.count(models.ScrapedReel.id).label('reels_count')
        ).filter(
            and_(
                models.ScrapedReel.user_id == user_id,
                models.ScrapedReel.scraped_at >= seven_days_ago
            )
        ).group_by(
            func.date(models.ScrapedReel.scraped_at)
        ).all()

        # Format daily usage
        usage_by_day = []
        for day in daily_usage:
            usage_by_day.append({
                "date": day.date.strftime("%Y-%m-%d"),
                "reels_count": day.reels_count
            })

        return {
            "user_id": user.id,
            "username": user.username,
            "credits_used_today": user.credits_used_today,
            "credits_remaining": user.daily_credit_limit - user.credits_used_today,
            "daily_credit_limit": user.daily_credit_limit,
            "usage_by_day": usage_by_day
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user stats: {str(e)}"
        )


# ==================== INSTAGRAM ACCOUNTS ====================

@router.get("/instagram-accounts")
async def get_instagram_accounts(
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all Instagram accounts in the pool (JWT auth version for admin panel)"""
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
            detail=f"Failed to fetch Instagram accounts: {str(e)}"
        )


# ==================== REQUEST MODELS ====================

class InstagramAccountStatusUpdate(BaseModel):
    """Request model for updating Instagram account status"""
    is_active: Optional[bool] = None
    is_paused: Optional[bool] = None


# ==================== HELPER FUNCTIONS ====================

def format_cookies_for_header(cookies: dict) -> str:
    """Format cookies dict into header string"""
    return "; ".join([f"{k}={v}" for k, v in cookies.items()])


def extract_csrf_token(cookies: dict) -> str:
    """Extract CSRF token from cookies"""
    return cookies.get("csrftoken", "")


# ==================== INSTAGRAM ACCOUNT COOKIES UPDATE ====================

@router.put("/instagram-accounts/{account_id}/cookies")
async def update_instagram_account_cookies_admin(
    account_id: int,
    cookies: dict,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Update cookies for Instagram account (JWT-authenticated for admin panel)

    This endpoint allows admins to manually update Instagram account cookies through the admin panel.
    It's separate from the API key-authenticated endpoint used by the remote cookie updater.

    Args:
        account_id: Instagram account ID
        cookies: Dict with cookie fields (sessionid, csrftoken, ds_user_id, ig_did, etc.)
        current_user: Current authenticated admin user
        db: Database session

    Returns:
        Success response with account details and update timestamp
    """
    try:
        # Validate cookies not empty
        if not cookies or len(cookies) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cookies cannot be empty"
            )

        # Get Instagram account
        account = db.query(models.InstagramAccount).filter(
            models.InstagramAccount.id == account_id
        ).first()

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Instagram account with ID {account_id} not found"
            )

        # Update cookies
        account.cookies = cookies
        account.cookie_string = format_cookies_for_header(cookies)
        account.x_csrf_token = extract_csrf_token(cookies)
        account.cookies_updated_at = datetime.now()

        db.commit()
        db.refresh(account)

        # Log the update activity
        crud.create_activity_log(
            db=db,
            event_type="cookies_updated_manual",
            user_id=None,
            instagram_account_id=account_id,
            job_id=None,
            details={
                "updated_by_admin": current_user.email,
                "account_username": account.username,
                "cookies_count": len(cookies),
                "cookie_fields": list(cookies.keys())
            }
        )

        return {
            "status": "success",
            "message": f"Cookies updated for account {account.username}",
            "account_id": account.id,
            "account_username": account.username,
            "updated_at": account.cookies_updated_at.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update cookies: {str(e)}"
        )


@router.patch("/instagram-accounts/{account_id}/status")
async def update_instagram_account_status(
    account_id: int,
    status_update: InstagramAccountStatusUpdate,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Update status flags for Instagram account (JWT-authenticated for admin panel)

    Args:
        account_id: Instagram account ID
        status_update: Status update model (is_active and/or is_paused)
        current_user: Current authenticated admin user
        db: Database session

    Returns:
        Success response with updated account details
    """
    try:
        # Get Instagram account
        account = db.query(models.InstagramAccount).filter(
            models.InstagramAccount.id == account_id
        ).first()

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Instagram account with ID {account_id} not found"
            )

        # Track changes for logging
        changes = {}

        # Update is_active if provided
        if status_update.is_active is not None:
            old_value = account.is_active
            account.is_active = status_update.is_active
            changes['is_active'] = {'old': old_value, 'new': status_update.is_active}

        # Update is_paused if provided
        if status_update.is_paused is not None:
            old_value = account.is_paused
            account.is_paused = status_update.is_paused
            changes['is_paused'] = {'old': old_value, 'new': status_update.is_paused}

        # Check if any changes were made
        if not changes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No status changes provided"
            )

        db.commit()
        db.refresh(account)

        # Log the status change
        crud.create_activity_log(
            db=db,
            event_type="account_status_updated",
            user_id=None,
            instagram_account_id=account_id,
            job_id=None,
            details={
                "updated_by_admin": current_user.email,
                "account_username": account.username,
                "changes": changes
            }
        )

        return {
            "status": "success",
            "message": f"Status updated for account {account.username}",
            "account_id": account.id,
            "account_username": account.username,
            "is_active": account.is_active,
            "is_paused": account.is_paused
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update account status: {str(e)}"
        )


# ==================== ACTIVITY LOGS ====================

@router.get("/logs")
async def get_activity_logs(
    skip: int = 0,
    limit: int = 100,
    event_type: Optional[str] = None,
    user_id: Optional[int] = None,
    instagram_account_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get activity logs with filtering"""
    try:
        query = db.query(models.ActivityLog)

        # Apply filters
        if event_type:
            query = query.filter(models.ActivityLog.event_type == event_type)

        if user_id:
            query = query.filter(models.ActivityLog.user_id == user_id)

        if instagram_account_id:
            query = query.filter(models.ActivityLog.instagram_account_id == instagram_account_id)

        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(models.ActivityLog.created_at >= start_dt)

        if end_date:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(models.ActivityLog.created_at <= end_dt)

        # Get total count
        total = query.count()

        # Get logs with pagination
        logs = query.order_by(desc(models.ActivityLog.created_at)).offset(skip).limit(limit).all()

        # Format response
        logs_list = []
        for log in logs:
            logs_list.append({
                "id": log.id,
                "event_type": log.event_type,
                "user_id": log.user_id,
                "instagram_account_id": log.instagram_account_id,
                "job_id": log.job_id,
                "details": log.details,
                "created_at": log.created_at
            })

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "logs": logs_list
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch logs: {str(e)}"
        )


@router.get("/logs/stats")
async def get_log_statistics(
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get statistics about activity logs"""
    try:
        # Count by event type
        event_counts = db.query(
            models.ActivityLog.event_type,
            func.count(models.ActivityLog.id).label('count')
        ).group_by(models.ActivityLog.event_type).all()

        event_stats = []
        for event_type, count in event_counts:
            event_stats.append({
                "event_type": event_type,
                "count": count
            })

        # Total logs
        total_logs = db.query(func.count(models.ActivityLog.id)).scalar()

        # Logs in last 24 hours
        yesterday = datetime.now() - timedelta(days=1)
        recent_logs = db.query(func.count(models.ActivityLog.id)).filter(
            models.ActivityLog.created_at >= yesterday
        ).scalar()

        return {
            "total_logs": total_logs,
            "logs_last_24h": recent_logs,
            "event_type_breakdown": event_stats
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch log statistics: {str(e)}"
        )


# ==================== SYSTEM STATISTICS ====================

@router.get("/stats/overview")
async def get_system_overview(
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get system overview statistics"""
    try:
        # User statistics
        total_users = db.query(func.count(models.User.id)).scalar()
        active_users = db.query(func.count(models.User.id)).filter(
            models.User.is_active == True
        ).scalar()

        # Instagram account statistics
        total_accounts = db.query(func.count(models.InstagramAccount.id)).scalar()
        active_accounts = db.query(func.count(models.InstagramAccount.id)).filter(
            and_(
                models.InstagramAccount.is_active == True,
                models.InstagramAccount.is_paused == False
            )
        ).scalar()

        # Today's statistics
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        today_jobs = db.query(func.count(models.ScrapingJob.id)).filter(
            models.ScrapingJob.created_at >= today_start
        ).scalar()

        today_reels = db.query(func.count(models.ScrapedReel.id)).filter(
            models.ScrapedReel.scraped_at >= today_start
        ).scalar()

        today_credits_used = db.query(func.sum(models.User.credits_used_today)).scalar() or 0

        # Success rate
        total_jobs = db.query(func.count(models.ScrapingJob.id)).scalar()
        successful_jobs = db.query(func.count(models.ScrapingJob.id)).filter(
            models.ScrapingJob.status == "completed"
        ).scalar()

        success_rate = round((successful_jobs / total_jobs) * 100, 1) if total_jobs > 0 else 0

        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "inactive": total_users - active_users
            },
            "instagram_accounts": {
                "total": total_accounts,
                "active": active_accounts,
                "paused": total_accounts - active_accounts
            },
            "today": {
                "jobs_completed": today_jobs,
                "reels_scraped": today_reels,
                "credits_consumed": int(today_credits_used)
            },
            "overall": {
                "total_jobs": total_jobs,
                "successful_jobs": successful_jobs,
                "failed_jobs": total_jobs - successful_jobs,
                "success_rate": success_rate
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch system overview: {str(e)}"
        )


@router.get("/stats/usage")
async def get_usage_statistics(
    days: int = 7,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get usage statistics over time"""
    try:
        start_date = datetime.now() - timedelta(days=days)

        # Daily scraping trends
        daily_reels = db.query(
            func.date(models.ScrapedReel.scraped_at).label('date'),
            func.count(models.ScrapedReel.id).label('reels_count'),
            func.count(func.distinct(models.ScrapedReel.user_id)).label('active_users')
        ).filter(
            models.ScrapedReel.scraped_at >= start_date
        ).group_by(
            func.date(models.ScrapedReel.scraped_at)
        ).all()

        # Format daily trends
        daily_trends = []
        for day in daily_reels:
            daily_trends.append({
                "date": day.date.strftime("%Y-%m-%d"),
                "reels_scraped": day.reels_count,
                "active_users": day.active_users
            })

        # Credit usage by user (top 10)
        top_users = db.query(
            models.User.username,
            models.User.credits_used_today
        ).filter(
            models.User.credits_used_today > 0
        ).order_by(
            desc(models.User.credits_used_today)
        ).limit(10).all()

        credit_usage_by_user = []
        for username, credits in top_users:
            credit_usage_by_user.append({
                "username": username,
                "credits_used": credits
            })

        return {
            "period_days": days,
            "daily_trends": daily_trends,
            "top_credit_consumers": credit_usage_by_user
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch usage statistics: {str(e)}"
        )


@router.get("/stats/performance")
async def get_performance_metrics(
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get performance metrics"""
    try:
        # Account usage distribution
        account_usage = db.query(
            models.InstagramAccount.username,
            models.InstagramAccount.daily_scrape_count,
            models.InstagramAccount.total_scrapes,
            models.InstagramAccount.success_count,
            models.InstagramAccount.failure_count
        ).filter(
            models.InstagramAccount.is_active == True
        ).all()

        account_stats = []
        for username, daily_count, total, success, failure in account_usage:
            success_rate = round((success / (success + failure)) * 100, 1) if (success + failure) > 0 else 0
            account_stats.append({
                "username": username,
                "daily_usage": daily_count,
                "total_usage": total,
                "success_rate": success_rate
            })

        # Average reels per job
        avg_reels = db.query(func.avg(models.ScrapingJob.reels_scraped)).filter(
            models.ScrapingJob.status == "completed"
        ).scalar()

        return {
            "account_distribution": account_stats,
            "average_reels_per_job": round(avg_reels, 1) if avg_reels else 0
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch performance metrics: {str(e)}"
        )
