from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc
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

def create_job(db: Session, user_id: int, job_id: str, usernames: List[str], reel_count: int) -> models.ScrapingJob:
    """Create a new scraping job"""
    db_job = models.ScrapingJob(
        job_id=job_id,
        user_id=user_id,
        usernames=usernames,
        reel_count=reel_count,
        status='running',
        progress=0
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
        reel_url=reel_data.get('url'),
        raw_data=reel_data
    )
    db.add(db_reel)
    db.commit()
    db.refresh(db_reel)
    return db_reel


def bulk_create_reels(db: Session, user_id: int, job_id: str, reels_data: List[dict]):
    """Bulk create reel records - optimized for speed"""
    if not reels_data:
        return

    # Use bulk_insert_mappings for maximum performance (faster than bulk_save_objects)
    mappings = [
        {
            'job_id': job_id,
            'user_id': user_id,
            'instagram_username': reel.get('username', ''),
            'reel_pk': str(reel.get('pk', '')),
            'reel_code': reel.get('code'),
            'play_count': reel.get('play_count', 0),
            'comment_count': reel.get('comment_count', 0),
            'like_count': reel.get('like_count', 0),
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

    # Get total count before pagination
    total = query.count()

    # Apply sorting
    sort_column = getattr(models.ScrapedReel, sort_by, models.ScrapedReel.scraped_at)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    # Apply pagination
    offset = (page - 1) * per_page
    reels = query.offset(offset).limit(per_page).all()

    return reels, total


def get_unique_usernames(db: Session, user_id: int) -> List[str]:
    """Get list of unique Instagram usernames that the user has scraped"""
    result = db.query(models.ScrapedReel.instagram_username)\
        .filter(models.ScrapedReel.user_id == user_id)\
        .distinct()\
        .order_by(models.ScrapedReel.instagram_username)\
        .all()
    return [row[0] for row in result if row[0]]
