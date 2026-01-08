from sqlalchemy import Boolean, Column, Integer, String, Float, TIMESTAMP, Text, ARRAY, ForeignKey, BigInteger, Index, CheckConstraint, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from database import Base


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    # Credit system fields
    daily_credit_limit = Column(Integer, default=2000, nullable=False)
    credits_used_today = Column(Integer, default=0, nullable=False)
    last_credit_reset_date = Column(Date, server_default=func.current_date(), nullable=False)

    # Relationships
    groups = relationship("UserGroup", back_populates="user", cascade="all, delete-orphan")
    jobs = relationship("ScrapingJob", back_populates="user", cascade="all, delete-orphan")
    reels = relationship("ScrapedReel", back_populates="user", cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")


class UserGroup(Base):
    """User groups for organizing Instagram usernames"""
    __tablename__ = "user_groups"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    usernames = Column(ARRAY(String), nullable=False)  # Array of Instagram usernames
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_used = Column(TIMESTAMP(timezone=True), nullable=True)
    times_used = Column(Integer, default=0, nullable=False)

    # Relationships
    user = relationship("User", back_populates="groups")

    # Indexes
    __table_args__ = (
        Index('idx_user_groups_user_id', 'user_id'),
        # Unique constraint: user can't have duplicate group names
        CheckConstraint('array_length(usernames, 1) >= 1', name='check_usernames_not_empty'),
    )


class ScrapingJob(Base):
    """Scraping job tracking"""
    __tablename__ = "scraping_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(100), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    instagram_account_id = Column(Integer, ForeignKey("instagram_accounts.id", ondelete="SET NULL"), nullable=True)
    usernames = Column(ARRAY(String), nullable=False)  # Instagram usernames being scraped
    reel_count = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False)  # running, completed, failed
    progress = Column(Float, default=0, nullable=False)
    credits_consumed = Column(Integer, default=0, nullable=False)
    start_time = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    end_time = Column(TIMESTAMP(timezone=True), nullable=True)
    duration = Column(Float, nullable=True)  # Duration in seconds
    error_message = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="jobs")
    instagram_account = relationship("InstagramAccount", back_populates="jobs")
    reels = relationship("ScrapedReel", back_populates="job", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_jobs_user_id', 'user_id'),
        Index('idx_jobs_instagram_account_id', 'instagram_account_id'),
        Index('idx_jobs_status', 'status'),
        Index('idx_jobs_start_time', 'start_time'),
    )


class ScrapedReel(Base):
    """Scraped Instagram reel data"""
    __tablename__ = "scraped_reels"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(100), ForeignKey("scraping_jobs.job_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    instagram_account_id = Column(Integer, ForeignKey("instagram_accounts.id", ondelete="SET NULL"), nullable=True)
    instagram_username = Column(String(100), nullable=False)
    reel_pk = Column(String(100), nullable=False)  # Instagram reel primary key
    reel_code = Column(String(50), nullable=True)  # Short code
    play_count = Column(BigInteger, default=0, nullable=False)
    comment_count = Column(Integer, default=0, nullable=False)
    like_count = Column(BigInteger, default=0, nullable=False)
    is_reel_pinned = Column(String(3), nullable=True)  # "Yes" or "No"
    reel_url = Column(Text, nullable=True)
    scraped_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    raw_data = Column(JSONB, nullable=True)  # Store full Instagram API response

    # Relationships
    user = relationship("User", back_populates="reels")
    job = relationship("ScrapingJob", back_populates="reels")
    instagram_account = relationship("InstagramAccount", back_populates="reels")

    # Indexes for analytics queries
    __table_args__ = (
        Index('idx_reels_user_id', 'user_id'),
        Index('idx_reels_instagram_account_id', 'instagram_account_id'),
        Index('idx_reels_instagram_username', 'instagram_username'),
        Index('idx_reels_play_count', 'play_count'),
        Index('idx_reels_like_count', 'like_count'),
        Index('idx_reels_comment_count', 'comment_count'),
        Index('idx_reels_scraped_at', 'scraped_at'),
        # Unique constraint: same reel can't be added twice by same user
        CheckConstraint('user_id IS NOT NULL AND reel_pk IS NOT NULL', name='check_user_reel_not_null'),
    )


class InstagramAccount(Base):
    """Instagram account pool for rotation"""
    __tablename__ = "instagram_accounts"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)

    # Authentication data
    cookies = Column(JSONB, nullable=True)  # Full cookie object from Playwright
    cookie_string = Column(Text, nullable=True)  # Formatted cookie string for headers
    x_csrf_token = Column(String(255), nullable=True)  # Extracted CSRF token

    # Status flags
    is_active = Column(Boolean, default=True, nullable=False)
    is_paused = Column(Boolean, default=False, nullable=False)

    # Usage tracking
    daily_scrape_count = Column(Integer, default=0, nullable=False)
    last_reset_date = Column(Date, server_default=func.current_date(), nullable=False)
    total_scrapes = Column(Integer, default=0, nullable=False)
    success_count = Column(Integer, default=0, nullable=False)
    failure_count = Column(Integer, default=0, nullable=False)

    # Timestamps
    last_used_at = Column(TIMESTAMP(timezone=True), nullable=True)
    cookies_updated_at = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    jobs = relationship("ScrapingJob", back_populates="instagram_account")
    reels = relationship("ScrapedReel", back_populates="instagram_account")
    activity_logs = relationship("ActivityLog", back_populates="instagram_account")

    # Indexes
    __table_args__ = (
        Index('idx_instagram_accounts_active', 'is_active', 'is_paused'),
        Index('idx_instagram_accounts_daily_count', 'daily_scrape_count'),
        Index('idx_instagram_accounts_last_used', 'last_used_at'),
    )


class ApiKey(Base):
    """API keys for cookie update authentication"""
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key_name = Column(String(100), nullable=False)
    api_key = Column(String(255), unique=True, nullable=False)  # Hashed with bcrypt
    is_active = Column(Boolean, default=True, nullable=False)
    permissions = Column(JSONB, default=lambda: ["update_cookies"], nullable=False)
    last_used_at = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    # Indexes
    __table_args__ = (
        Index('idx_api_keys_active', 'is_active'),
    )


class AdminUser(Base):
    """Admin panel user accounts"""
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    last_login = Column(TIMESTAMP(timezone=True), nullable=True)


class ActivityLog(Base):
    """Activity and event logging"""
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False)
    # Event types: 'scrape_success', 'scrape_failed', 'credit_limit_reached',
    #              'account_rotated', 'cookies_updated', 'admin_action', etc.

    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    instagram_account_id = Column(Integer, ForeignKey("instagram_accounts.id", ondelete="SET NULL"), nullable=True)
    job_id = Column(String(100), nullable=True)

    details = Column(JSONB, nullable=True)  # Flexible JSON for event-specific data
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="activity_logs")
    instagram_account = relationship("InstagramAccount", back_populates="activity_logs")

    # Indexes
    __table_args__ = (
        Index('idx_activity_logs_user', 'user_id', 'created_at'),
        Index('idx_activity_logs_event', 'event_type', 'created_at'),
        Index('idx_activity_logs_instagram_account', 'instagram_account_id', 'created_at'),
    )
