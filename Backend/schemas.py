from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional
from datetime import datetime


# ==================== User Schemas ====================

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)

    @validator('password')
    def password_strength(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isalpha() for char in v):
            raise ValueError('Password must contain at least one letter')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    daily_credit_limit: int
    credits_used_today: int

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


# ==================== Instagram Account Schemas ====================

class InstagramAccountCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=255)

    @validator('username')
    def validate_username(cls, v):
        # Remove whitespace
        v = v.strip()
        if not v:
            raise ValueError('Username cannot be empty')
        return v


# ==================== User Group Schemas ====================

class UserGroupBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    usernames: List[str] = Field(..., min_items=1, max_items=100)

    @validator('usernames')
    def validate_usernames(cls, v):
        # Remove empty strings and duplicates
        cleaned = [u.strip() for u in v if u.strip()]
        if len(cleaned) == 0:
            raise ValueError('At least one username is required')
        if len(cleaned) != len(set(cleaned)):
            raise ValueError('Duplicate usernames are not allowed')
        return cleaned


class UserGroupCreate(UserGroupBase):
    pass


class UserGroupUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    usernames: Optional[List[str]] = Field(None, min_items=1, max_items=100)


class UserGroupResponse(UserGroupBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    last_used: Optional[datetime]
    times_used: int

    class Config:
        from_attributes = True


# ==================== Scraping Job Schemas ====================

class ScrapeRequest(BaseModel):
    usernames: List[str] = Field(..., min_items=1, max_items=500)
    reel_count: int = Field(default=20, ge=1, le=100)
    group_id: Optional[int] = None  # If scraping from a saved group

    @validator('usernames')
    def validate_usernames(cls, v):
        cleaned = [u.strip() for u in v if u.strip()]
        if len(cleaned) == 0:
            raise ValueError('At least one username is required')
        return cleaned


class ScrapingJobResponse(BaseModel):
    id: int
    job_id: str
    user_id: int
    usernames: List[str]
    reel_count: int
    status: str
    progress: float
    start_time: datetime
    end_time: Optional[datetime]
    duration: Optional[float]
    error_message: Optional[str]

    class Config:
        from_attributes = True


class JobStartResponse(BaseModel):
    job_id: str
    status: str
    message: str


# ==================== Scraped Reel Schemas ====================

class ScrapedReelResponse(BaseModel):
    id: int
    instagram_username: str
    reel_pk: str
    reel_code: Optional[str]
    play_count: int
    comment_count: int
    like_count: int
    engagement_ratio: float
    is_reel_pinned: Optional[str] = None
    reel_url: Optional[str]
    scraped_at: datetime

    class Config:
        from_attributes = True


class AnalyticsFilters(BaseModel):
    username: Optional[str] = None
    min_play_count: Optional[int] = Field(None, ge=0)
    min_like_count: Optional[int] = Field(None, ge=0)
    min_comment_count: Optional[int] = Field(None, ge=0)
    min_engagement_ratio: Optional[float] = Field(None, ge=0.0)
    sort_by: str = Field(default="scraped_at", pattern="^(play_count|like_count|comment_count|scraped_at|engagement_ratio)$")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=50, ge=1, le=200)


class AnalyticsResponse(BaseModel):
    items: List[ScrapedReelResponse]
    total: int
    page: int
    pages: int
    per_page: int


# ==================== Generic Responses ====================

class MessageResponse(BaseModel):
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    detail: str
    success: bool = False
