from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc, cast, Numeric
from typing import List, Optional
from datetime import datetime
import models
import schemas
from auth import hash_password
from config import settings


# ==================== User CRUD ====================

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user"""
    hashed_password = hash_password(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get user by email"""
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Get user by username"""
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    """Get user by ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()


# ==================== User Group CRUD ====================

def create_group(db: Session, user_id: int, group: schemas.UserGroupCreate) -> models.UserGroup:
    """Create a new user group"""
    # Check if user already has 10 groups
    group_count = db.query(models.UserGroup).filter(models.UserGroup.user_id == user_id).count()
    if group_count >= settings.MAX_GROUPS_PER_USER:
        raise ValueError(f"User cannot have more than {settings.MAX_GROUPS_PER_USER} groups")

    # Check if group name already exists for this user
    existing = db.query(models.UserGroup).filter(
        models.UserGroup.user_id == user_id,
        models.UserGroup.name == group.name
    ).first()
    if existing:
        raise ValueError(f"Group with name '{group.name}' already exists")

    db_group = models.UserGroup(
        user_id=user_id,
        name=group.name,
        usernames=group.usernames
    )
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group


def get_user_groups(db: Session, user_id: int) -> List[models.UserGroup]:
    """Get all groups for a user"""
    return db.query(models.UserGroup).filter(
        models.UserGroup.user_id == user_id
    ).order_by(desc(models.UserGroup.last_used), desc(models.UserGroup.created_at)).all()


def get_group_by_id(db: Session, group_id: int, user_id: int) -> Optional[models.UserGroup]:
    """Get a specific group by ID (user must own it)"""
    return db.query(models.UserGroup).filter(
        models.UserGroup.id == group_id,
        models.UserGroup.user_id == user_id
    ).first()


def update_group(db: Session, group_id: int, user_id: int, group_update: schemas.UserGroupUpdate) -> Optional[models.UserGroup]:
    """Update a user group"""
    db_group = get_group_by_id(db, group_id, user_id)
    if not db_group:
        return None

    # Update fields if provided
    if group_update.name is not None:
        # Check if new name conflicts with existing group
        if group_update.name != db_group.name:
            existing = db.query(models.UserGroup).filter(
                models.UserGroup.user_id == user_id,
                models.UserGroup.name == group_update.name
            ).first()
            if existing:
                raise ValueError(f"Group with name '{group_update.name}' already exists")
        db_group.name = group_update.name

    if group_update.usernames is not None:
        db_group.usernames = group_update.usernames

    db_group.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_group)
    return db_group


def delete_group(db: Session, group_id: int, user_id: int) -> bool:
    """Delete a user group"""
    db_group = get_group_by_id(db, group_id, user_id)
    if not db_group:
        return False

    db.delete(db_group)
    db.commit()
    return True


def update_group_usage(db: Session, group_id: int, user_id: int):
    """Update group's last_used timestamp and times_used counter"""
    db_group = get_group_by_id(db, group_id, user_id)
    if db_group:
        db_group.last_used = datetime.utcnow()
        db_group.times_used += 1
        db.commit()


# ==================== Scraping Job CRUD ====================

def create_job(db: Session, user_id: int, job_id: str, usernames: List[str], reel_count: int, instagram_account_id: Optional[int] = None) -> models.ScrapingJob:
    """Create a new scraping job"""
    db_job = models.ScrapingJob(
        job_id=job_id,
        user_id=user_id,
        instagram_account_id=instagram_account_id,
        usernames=usernames,
        reel_count=reel_count,
        status='running',
        progress=0,
        credits_consumed=0
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


def get_job_by_job_id(db: Session, job_id: str, user_id: int) -> Optional[models.ScrapingJob]:
    """Get a job by job_id (user must own it)"""
    return db.query(models.ScrapingJob).filter(
        models.ScrapingJob.job_id == job_id,
        models.ScrapingJob.user_id == user_id
    ).first()


def update_job_status(db: Session, job_id: str, status: str, progress: float = None,
                     error_message: str = None, duration: float = None):
    """Update job status and progress"""
    db_job = db.query(models.ScrapingJob).filter(models.ScrapingJob.job_id == job_id).first()
    if db_job:
        db_job.status = status
        if progress is not None:
            db_job.progress = progress
        if error_message is not None:
            db_job.error_message = error_message
        if duration is not None:
            db_job.duration = duration
        if status == 'completed' or status == 'failed':
            db_job.end_time = datetime.utcnow()
        db.commit()
        db.refresh(db_job)
        return db_job
    return None


def get_user_jobs(db: Session, user_id: int, limit: int = 50) -> List[models.ScrapingJob]:
    """Get all jobs for a user"""
    return db.query(models.ScrapingJob).filter(
        models.ScrapingJob.user_id == user_id
    ).order_by(desc(models.ScrapingJob.start_time)).limit(limit).all()


# ==================== Scraped Reel CRUD ====================

def create_reel(db: Session, user_id: int, job_id: str, reel_data: dict) -> models.ScrapedReel:
    """Create a scraped reel record"""
    db_reel = models.ScrapedReel(
        job_id=job_id,
        user_id=user_id,
        instagram_username=reel_data.get('username', ''),
        reel_pk=str(reel_data.get('pk', '')),
        reel_code=reel_data.get('code'),
        play_count=reel_data.get('play_count', 0),
        comment_count=reel_data.get('comment_count', 0),
        like_count=reel_data.get('like_count', 0),
        is_reel_pinned=reel_data.get('is_reel_pinned', 'No'),
        reel_url=reel_data.get('url'),
        raw_data=reel_data
    )
    db.add(db_reel)
    db.commit()
    db.refresh(db_reel)
    return db_reel


def bulk_create_reels(db: Session, user_id: int, job_id: str, reels_data: List[dict], instagram_account_id: Optional[int] = None):
    """Bulk create reel records - optimized for speed"""
    if not reels_data:
        return

    # Use bulk_insert_mappings for maximum performance (faster than bulk_save_objects)
    mappings = [
        {
            'job_id': job_id,
            'user_id': user_id,
            'instagram_account_id': instagram_account_id,
            'instagram_username': reel.get('username', ''),
            'reel_pk': str(reel.get('pk', '')),
            'reel_code': reel.get('code'),
            'play_count': reel.get('play_count', 0),
            'comment_count': reel.get('comment_count', 0),
            'like_count': reel.get('like_count', 0),
            'is_reel_pinned': reel.get('is_reel_pinned', 'No'),
            'reel_url': reel.get('url'),
            'raw_data': reel,
            'scraped_at': datetime.utcnow()
        }
        for reel in reels_data
    ]
    db.bulk_insert_mappings(models.ScrapedReel, mappings)
    db.commit()


def get_analytics_reels(
    db: Session,
    user_id: int,
    username: Optional[str] = None,
    group_id: Optional[int] = None,
    min_play_count: Optional[int] = None,
    min_like_count: Optional[int] = None,
    min_comment_count: Optional[int] = None,
    min_engagement_ratio: Optional[float] = None,
    sort_by: str = "scraped_at",
    sort_order: str = "desc",
    page: int = 1,
    per_page: int = 50
) -> tuple[List[models.ScrapedReel], int]:
    """
    Get reels for analytics with filtering and pagination
    Supports filtering by multiple usernames (comma-separated) and user groups
    Returns (reels, total_count)
    """
    query = db.query(models.ScrapedReel).filter(models.ScrapedReel.user_id == user_id)

    # Apply filters
    if username:
        # Support multiple usernames separated by commas
        usernames_list = [u.strip() for u in username.split(',') if u.strip()]
        if len(usernames_list) == 1:
            # Single username - use ILIKE for partial match
            query = query.filter(models.ScrapedReel.instagram_username.ilike(f"%{usernames_list[0]}%"))
        elif len(usernames_list) > 1:
            # Multiple usernames - exact match for each
            query = query.filter(models.ScrapedReel.instagram_username.in_(usernames_list))

    # Filter by group - get usernames from the group
    if group_id:
        group = db.query(models.UserGroup).filter(
            models.UserGroup.id == group_id,
            models.UserGroup.user_id == user_id
        ).first()
        if group and group.usernames:
            query = query.filter(models.ScrapedReel.instagram_username.in_(group.usernames))

    if min_play_count is not None:
        query = query.filter(models.ScrapedReel.play_count >= min_play_count)
    if min_like_count is not None:
        query = query.filter(models.ScrapedReel.like_count >= min_like_count)
    if min_comment_count is not None:
        query = query.filter(models.ScrapedReel.comment_count >= min_comment_count)

    # Filter by engagement ratio (calculated as (likes + comments) / plays)
    if min_engagement_ratio is not None:
        # Only include reels with play_count > 0 to avoid division by zero
        engagement_expr = cast(models.ScrapedReel.like_count + models.ScrapedReel.comment_count, Numeric) / func.nullif(models.ScrapedReel.play_count, 0)
        query = query.filter(engagement_expr >= min_engagement_ratio)

    # Get total count before pagination
    total = query.count()

    # Apply sorting
    if sort_by == "engagement_ratio":
        # Sort by computed engagement ratio
        engagement_expr = cast(models.ScrapedReel.like_count + models.ScrapedReel.comment_count, Numeric) / func.nullif(models.ScrapedReel.play_count, 0)
        if sort_order == "desc":
            query = query.order_by(desc(engagement_expr))
        else:
            query = query.order_by(asc(engagement_expr))
    else:
        sort_column = getattr(models.ScrapedReel, sort_by, models.ScrapedReel.scraped_at)
        if sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

    # Apply pagination
    offset = (page - 1) * per_page
    reels = query.offset(offset).limit(per_page).all()

    # Add engagement_ratio as a computed attribute to each reel
    for reel in reels:
        if reel.play_count > 0:
            reel.engagement_ratio = round((reel.like_count + reel.comment_count) / reel.play_count, 4)
        else:
            reel.engagement_ratio = 0.0

    return reels, total


def get_unique_usernames(db: Session, user_id: int) -> List[str]:
    """Get list of unique Instagram usernames that the user has scraped"""
    result = db.query(models.ScrapedReel.instagram_username)\
        .filter(models.ScrapedReel.user_id == user_id)\
        .distinct()\
        .order_by(models.ScrapedReel.instagram_username)\
        .all()
    return [row[0] for row in result if row[0]]


# ==================== Instagram Account CRUD ====================

def create_instagram_account(db: Session, username: str, email: str, password: str) -> models.InstagramAccount:
    """Create a new Instagram account in the pool"""
    db_account = models.InstagramAccount(
        username=username,
        email=email,
        password=password
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


def get_instagram_account_by_id(db: Session, account_id: int) -> Optional[models.InstagramAccount]:
    """Get Instagram account by ID"""
    return db.query(models.InstagramAccount).filter(models.InstagramAccount.id == account_id).first()


def get_instagram_account_by_username(db: Session, username: str) -> Optional[models.InstagramAccount]:
    """Get Instagram account by username"""
    return db.query(models.InstagramAccount).filter(models.InstagramAccount.username == username).first()


def get_all_instagram_accounts(db: Session) -> List[models.InstagramAccount]:
    """Get all Instagram accounts"""
    return db.query(models.InstagramAccount).order_by(asc(models.InstagramAccount.daily_scrape_count)).all()


def update_instagram_account_cookies(
    db: Session,
    account_id: int,
    cookies: dict,
    cookie_string: str,
    x_csrf_token: str
) -> Optional[models.InstagramAccount]:
    """Update Instagram account cookies"""
    account = get_instagram_account_by_id(db, account_id)
    if not account:
        return None

    account.cookies = cookies
    account.cookie_string = cookie_string
    account.x_csrf_token = x_csrf_token
    account.cookies_updated_at = datetime.utcnow()
    db.commit()
    db.refresh(account)
    return account


def delete_instagram_account(db: Session, account_id: int) -> bool:
    """Delete an Instagram account"""
    account = get_instagram_account_by_id(db, account_id)
    if not account:
        return False

    db.delete(account)
    db.commit()
    return True


# ==================== API Key CRUD ====================

def create_api_key(db: Session, key_name: str, api_key_hash: str) -> models.ApiKey:
    """Create a new API key"""
    db_key = models.ApiKey(
        key_name=key_name,
        api_key=api_key_hash
    )
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    return db_key


def get_api_key_by_key(db: Session, api_key_hash: str) -> Optional[models.ApiKey]:
    """Get API key by hashed key"""
    return db.query(models.ApiKey).filter(
        models.ApiKey.api_key == api_key_hash,
        models.ApiKey.is_active == True
    ).first()


def get_all_api_keys(db: Session) -> List[models.ApiKey]:
    """Get all API keys"""
    return db.query(models.ApiKey).order_by(desc(models.ApiKey.created_at)).all()


def deactivate_api_key(db: Session, key_id: int) -> bool:
    """Deactivate an API key"""
    key = db.query(models.ApiKey).filter(models.ApiKey.id == key_id).first()
    if not key:
        return False

    key.is_active = False
    db.commit()
    return True


def update_api_key_last_used(db: Session, key_id: int):
    """Update API key last used timestamp"""
    key = db.query(models.ApiKey).filter(models.ApiKey.id == key_id).first()
    if key:
        key.last_used_at = datetime.utcnow()
        db.commit()


# ==================== Admin User CRUD ====================

def create_admin_user(db: Session, username: str, email: str, password_hash: str) -> models.AdminUser:
    """Create a new admin user"""
    db_admin = models.AdminUser(
        username=username,
        email=email,
        password_hash=password_hash
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin


def get_admin_by_username(db: Session, username: str) -> Optional[models.AdminUser]:
    """Get admin user by username"""
    return db.query(models.AdminUser).filter(
        models.AdminUser.username == username,
        models.AdminUser.is_active == True
    ).first()


def get_admin_by_id(db: Session, admin_id: int) -> Optional[models.AdminUser]:
    """Get admin user by ID"""
    return db.query(models.AdminUser).filter(models.AdminUser.id == admin_id).first()


def update_admin_last_login(db: Session, admin_id: int):
    """Update admin last login timestamp"""
    admin = get_admin_by_id(db, admin_id)
    if admin:
        admin.last_login = datetime.utcnow()
        db.commit()


# ==================== Activity Log CRUD ====================

def create_activity_log(
    db: Session,
    event_type: str,
    user_id: Optional[int] = None,
    instagram_account_id: Optional[int] = None,
    job_id: Optional[str] = None,
    details: Optional[dict] = None
) -> models.ActivityLog:
    """Create an activity log entry"""
    log = models.ActivityLog(
        event_type=event_type,
        user_id=user_id,
        instagram_account_id=instagram_account_id,
        job_id=job_id,
        details=details
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_activity_logs(
    db: Session,
    event_type: Optional[str] = None,
    user_id: Optional[int] = None,
    instagram_account_id: Optional[int] = None,
    limit: int = 100
) -> List[models.ActivityLog]:
    """Get activity logs with optional filtering"""
    query = db.query(models.ActivityLog)

    if event_type:
        query = query.filter(models.ActivityLog.event_type == event_type)
    if user_id:
        query = query.filter(models.ActivityLog.user_id == user_id)
    if instagram_account_id:
        query = query.filter(models.ActivityLog.instagram_account_id == instagram_account_id)

    return query.order_by(desc(models.ActivityLog.created_at)).limit(limit).all()


def get_recent_activity(db: Session, limit: int = 50) -> List[models.ActivityLog]:
    """Get recent activity logs"""
    return db.query(models.ActivityLog).order_by(desc(models.ActivityLog.created_at)).limit(limit).all()
