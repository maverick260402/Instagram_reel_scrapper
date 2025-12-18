"""
Credit System for User Scraping Limits
Manages daily credit quotas and consumption tracking
"""

from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import Optional, Tuple
from models import User
from crud import create_activity_log


class InsufficientCreditsError(Exception):
    """Raised when user doesn't have enough credits"""
    pass


class CreditSystemError(Exception):
    """General error for credit system issues"""
    pass


def check_user_credits(db: Session, user_id: int, required_credits: int) -> bool:
    """
    Check if user has enough credits for the requested operation.

    Args:
        db: Database session
        user_id: User ID
        required_credits: Number of credits required

    Returns:
        bool: True if user has enough credits, False otherwise

    Raises:
        CreditSystemError: If user not found or other error
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise CreditSystemError(f"User {user_id} not found")

        # Check if credits need reset (new day)
        if user.last_credit_reset_date < date.today():
            reset_user_credits(db, user_id)
            # Refresh user object after reset
            db.refresh(user)

        remaining_credits = user.daily_credit_limit - user.credits_used_today
        return remaining_credits >= required_credits

    except CreditSystemError:
        raise
    except Exception as e:
        raise CreditSystemError(f"Error checking user credits: {str(e)}")


def get_user_credits_remaining(db: Session, user_id: int) -> int:
    """
    Get the number of credits remaining for a user today.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        int: Number of credits remaining

    Raises:
        CreditSystemError: If user not found
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise CreditSystemError(f"User {user_id} not found")

        # Check if credits need reset (new day)
        if user.last_credit_reset_date < date.today():
            reset_user_credits(db, user_id)
            db.refresh(user)

        return user.daily_credit_limit - user.credits_used_today

    except CreditSystemError:
        raise
    except Exception as e:
        raise CreditSystemError(f"Error getting remaining credits: {str(e)}")


def deduct_credits(db: Session, user_id: int, credits: int) -> int:
    """
    Deduct credits from a user's daily quota.

    Args:
        db: Database session
        user_id: User ID
        credits: Number of credits to deduct

    Returns:
        int: Remaining credits after deduction

    Raises:
        InsufficientCreditsError: If user doesn't have enough credits
        CreditSystemError: If user not found or other error
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise CreditSystemError(f"User {user_id} not found")

        # Check if credits need reset (new day)
        if user.last_credit_reset_date < date.today():
            reset_user_credits(db, user_id)
            db.refresh(user)

        remaining = user.daily_credit_limit - user.credits_used_today

        if remaining < credits:
            # Log credit limit reached event
            create_activity_log(
                db=db,
                event_type="credit_limit_reached",
                user_id=user_id,
                details={
                    "credits_requested": credits,
                    "credits_remaining": remaining,
                    "daily_limit": user.daily_credit_limit
                }
            )

            raise InsufficientCreditsError(
                f"Not enough credits. Remaining: {remaining}, Required: {credits}"
            )

        # Deduct credits
        user.credits_used_today += credits
        db.commit()

        new_remaining = user.daily_credit_limit - user.credits_used_today

        # Log credit deduction
        create_activity_log(
            db=db,
            event_type="credits_deducted",
            user_id=user_id,
            details={
                "credits_deducted": credits,
                "credits_remaining": new_remaining,
                "credits_used_today": user.credits_used_today
            }
        )

        return new_remaining

    except (InsufficientCreditsError, CreditSystemError):
        raise
    except Exception as e:
        db.rollback()
        raise CreditSystemError(f"Error deducting credits: {str(e)}")


def reset_user_credits(db: Session, user_id: int) -> None:
    """
    Reset a user's daily credit usage.

    Args:
        db: Database session
        user_id: User ID

    Raises:
        CreditSystemError: If user not found or reset fails
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise CreditSystemError(f"User {user_id} not found")

        old_usage = user.credits_used_today
        user.credits_used_today = 0
        user.last_credit_reset_date = date.today()
        db.commit()

        # Log reset event
        create_activity_log(
            db=db,
            event_type="credits_reset",
            user_id=user_id,
            details={
                "previous_usage": old_usage,
                "daily_limit": user.daily_credit_limit,
                "reset_date": date.today().isoformat()
            }
        )

    except CreditSystemError:
        raise
    except Exception as e:
        db.rollback()
        raise CreditSystemError(f"Error resetting user credits: {str(e)}")


def reset_all_daily_credits(db: Session) -> int:
    """
    Reset daily credits for all users.
    Should be called at midnight via scheduler.

    Args:
        db: Database session

    Returns:
        int: Number of users reset

    Raises:
        CreditSystemError: If reset fails
    """
    try:
        today = date.today()

        # Get all users that need reset
        users = db.query(User).filter(
            User.last_credit_reset_date < today
        ).all()

        count = 0
        for user in users:
            user.credits_used_today = 0
            user.last_credit_reset_date = today
            count += 1

        db.commit()

        # Log reset event
        if count > 0:
            create_activity_log(
                db=db,
                event_type="daily_credits_reset",
                details={
                    "users_reset": count,
                    "reset_date": today.isoformat()
                }
            )

        return count

    except Exception as e:
        db.rollback()
        raise CreditSystemError(f"Error resetting all daily credits: {str(e)}")


def update_user_credit_limit(
    db: Session,
    user_id: int,
    new_limit: int,
    admin_user_id: Optional[int] = None
) -> None:
    """
    Update a user's daily credit limit (admin function).

    Args:
        db: Database session
        user_id: User ID
        new_limit: New daily credit limit
        admin_user_id: ID of admin making the change (optional)

    Raises:
        CreditSystemError: If user not found or update fails
    """
    try:
        if new_limit < 0:
            raise CreditSystemError("Credit limit must be non-negative")

        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise CreditSystemError(f"User {user_id} not found")

        old_limit = user.daily_credit_limit
        user.daily_credit_limit = new_limit
        db.commit()

        # Log limit change
        create_activity_log(
            db=db,
            event_type="credit_limit_updated",
            user_id=user_id,
            details={
                "old_limit": old_limit,
                "new_limit": new_limit,
                "updated_by_admin_id": admin_user_id
            }
        )

    except CreditSystemError:
        raise
    except Exception as e:
        db.rollback()
        raise CreditSystemError(f"Error updating credit limit: {str(e)}")


def get_user_credit_summary(db: Session, user_id: int) -> dict:
    """
    Get comprehensive credit information for a user.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        dict: Credit summary with all relevant information

    Raises:
        CreditSystemError: If user not found
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise CreditSystemError(f"User {user_id} not found")

        # Check if credits need reset (new day)
        needs_reset = user.last_credit_reset_date < date.today()
        if needs_reset:
            reset_user_credits(db, user_id)
            db.refresh(user)

        remaining = user.daily_credit_limit - user.credits_used_today
        usage_percent = (
            (user.credits_used_today / user.daily_credit_limit * 100)
            if user.daily_credit_limit > 0 else 0
        )

        return {
            "user_id": user.id,
            "username": user.username,
            "daily_limit": user.daily_credit_limit,
            "used_today": user.credits_used_today,
            "remaining": remaining,
            "usage_percent": round(usage_percent, 2),
            "last_reset_date": user.last_credit_reset_date.isoformat(),
            "is_active": user.is_active
        }

    except CreditSystemError:
        raise
    except Exception as e:
        raise CreditSystemError(f"Error getting credit summary: {str(e)}")


def validate_scrape_request(
    db: Session,
    user_id: int,
    reel_count: int
) -> Tuple[bool, str, int]:
    """
    Validate if a user can perform a scrape request.

    Args:
        db: Database session
        user_id: User ID
        reel_count: Number of reels requested

    Returns:
        Tuple[bool, str, int]: (can_scrape, message, remaining_credits)

    Raises:
        CreditSystemError: If validation fails
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise CreditSystemError(f"User {user_id} not found")

        if not user.is_active:
            return False, "User account is inactive", 0

        # Check if credits need reset
        if user.last_credit_reset_date < date.today():
            reset_user_credits(db, user_id)
            db.refresh(user)

        remaining = user.daily_credit_limit - user.credits_used_today

        if remaining < reel_count:
            message = f"Insufficient credits. Remaining: {remaining}, Required: {reel_count}"
            return False, message, remaining

        return True, "Request validated successfully", remaining

    except CreditSystemError:
        raise
    except Exception as e:
        raise CreditSystemError(f"Error validating scrape request: {str(e)}")


def add_bonus_credits(
    db: Session,
    user_id: int,
    bonus_credits: int,
    reason: str = "Admin bonus",
    admin_user_id: Optional[int] = None
) -> int:
    """
    Add bonus credits to a user (increases their limit for today).

    Args:
        db: Database session
        user_id: User ID
        bonus_credits: Number of bonus credits to add
        reason: Reason for bonus credits
        admin_user_id: ID of admin granting bonus

    Returns:
        int: New daily credit limit

    Raises:
        CreditSystemError: If user not found or update fails
    """
    try:
        if bonus_credits <= 0:
            raise CreditSystemError("Bonus credits must be positive")

        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise CreditSystemError(f"User {user_id} not found")

        old_limit = user.daily_credit_limit
        user.daily_credit_limit += bonus_credits
        db.commit()

        # Log bonus credits
        create_activity_log(
            db=db,
            event_type="bonus_credits_added",
            user_id=user_id,
            details={
                "bonus_credits": bonus_credits,
                "old_limit": old_limit,
                "new_limit": user.daily_credit_limit,
                "reason": reason,
                "granted_by_admin_id": admin_user_id
            }
        )

        return user.daily_credit_limit

    except CreditSystemError:
        raise
    except Exception as e:
        db.rollback()
        raise CreditSystemError(f"Error adding bonus credits: {str(e)}")
