"""
Instagram Account Rotation System
Intelligently selects least-used Instagram accounts for scraping requests
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, date
from typing import Optional
from models import InstagramAccount
from crud import create_activity_log


class NoAccountsAvailableError(Exception):
    """Raised when no Instagram accounts are available for scraping"""
    pass


class AccountRotationError(Exception):
    """General error for account rotation issues"""
    pass


def get_least_used_account(db: Session) -> InstagramAccount:
    """
    Get the least-used active Instagram account for scraping.

    Selection criteria (in order):
    1. Account must be active (is_active=True)
    2. Account must not be paused (is_paused=False)
    3. Sort by daily_scrape_count (ascending) - least used first
    4. Sort by last_used_at (ascending, nulls first) - oldest usage first

    Args:
        db: Database session

    Returns:
        InstagramAccount: The selected Instagram account

    Raises:
        NoAccountsAvailableError: If no accounts are available
    """
    try:
        # Query available accounts
        accounts = db.query(InstagramAccount).filter(
            and_(
                InstagramAccount.is_active == True,
                InstagramAccount.is_paused == False
            )
        ).order_by(
            InstagramAccount.daily_scrape_count.asc(),
            InstagramAccount.last_used_at.asc().nullsfirst()
        ).all()

        if not accounts:
            raise NoAccountsAvailableError(
                "All Instagram accounts are exhausted or unavailable. Please try again later."
            )

        selected_account = accounts[0]

        # Log account rotation event
        create_activity_log(
            db=db,
            event_type="account_rotated",
            instagram_account_id=selected_account.id,
            details={
                "account_username": selected_account.username,
                "daily_scrape_count": selected_account.daily_scrape_count,
                "last_used_at": selected_account.last_used_at.isoformat() if selected_account.last_used_at else None
            }
        )

        return selected_account

    except NoAccountsAvailableError:
        raise
    except Exception as e:
        raise AccountRotationError(f"Error selecting Instagram account: {str(e)}")


def increment_account_usage(
    db: Session,
    account_id: int,
    reels_scraped: int,
    success: bool = True
) -> None:
    """
    Update Instagram account usage statistics.

    Args:
        db: Database session
        account_id: Instagram account ID
        reels_scraped: Number of reels scraped
        success: Whether the scrape was successful

    Raises:
        AccountRotationError: If account not found
    """
    try:
        account = db.query(InstagramAccount).filter(
            InstagramAccount.id == account_id
        ).first()

        if not account:
            raise AccountRotationError(f"Instagram account {account_id} not found")

        # Update counters
        account.daily_scrape_count += reels_scraped
        account.total_scrapes += reels_scraped
        account.last_used_at = datetime.now()

        if success:
            account.success_count += reels_scraped
        else:
            account.failure_count += reels_scraped

        db.commit()

        # Log usage update
        create_activity_log(
            db=db,
            event_type="account_usage_updated",
            instagram_account_id=account_id,
            details={
                "reels_scraped": reels_scraped,
                "success": success,
                "daily_scrape_count": account.daily_scrape_count,
                "total_scrapes": account.total_scrapes
            }
        )

    except AccountRotationError:
        raise
    except Exception as e:
        db.rollback()
        raise AccountRotationError(f"Error updating account usage: {str(e)}")


def mark_account_failed(
    db: Session,
    account_id: int,
    error: str,
    pause: bool = False
) -> None:
    """
    Mark an Instagram account as failed and optionally pause it.

    Args:
        db: Database session
        account_id: Instagram account ID
        error: Error message
        pause: Whether to pause the account

    Raises:
        AccountRotationError: If account not found
    """
    try:
        account = db.query(InstagramAccount).filter(
            InstagramAccount.id == account_id
        ).first()

        if not account:
            raise AccountRotationError(f"Instagram account {account_id} not found")

        # Increment failure count
        account.failure_count += 1

        # Optionally pause account
        if pause:
            account.is_paused = True

        db.commit()

        # Log failure
        create_activity_log(
            db=db,
            event_type="account_failed",
            instagram_account_id=account_id,
            details={
                "error": error,
                "paused": pause,
                "failure_count": account.failure_count
            }
        )

    except AccountRotationError:
        raise
    except Exception as e:
        db.rollback()
        raise AccountRotationError(f"Error marking account as failed: {str(e)}")


def reset_daily_counts(db: Session) -> int:
    """
    Reset daily scrape counts for all Instagram accounts.
    Should be called at midnight via scheduler.

    Args:
        db: Database session

    Returns:
        int: Number of accounts reset

    Raises:
        AccountRotationError: If reset fails
    """
    try:
        today = date.today()

        # Get all accounts that need reset
        accounts = db.query(InstagramAccount).filter(
            InstagramAccount.last_reset_date < today
        ).all()

        count = 0
        for account in accounts:
            account.daily_scrape_count = 0
            account.last_reset_date = today
            count += 1

        db.commit()

        # Log reset event
        if count > 0:
            create_activity_log(
                db=db,
                event_type="daily_reset",
                details={
                    "accounts_reset": count,
                    "reset_date": today.isoformat()
                }
            )

        return count

    except Exception as e:
        db.rollback()
        raise AccountRotationError(f"Error resetting daily counts: {str(e)}")


def get_account_stats(db: Session, account_id: int) -> dict:
    """
    Get statistics for a specific Instagram account.

    Args:
        db: Database session
        account_id: Instagram account ID

    Returns:
        dict: Account statistics

    Raises:
        AccountRotationError: If account not found
    """
    try:
        account = db.query(InstagramAccount).filter(
            InstagramAccount.id == account_id
        ).first()

        if not account:
            raise AccountRotationError(f"Instagram account {account_id} not found")

        # Calculate success rate
        total_attempts = account.success_count + account.failure_count
        success_rate = (
            (account.success_count / total_attempts * 100)
            if total_attempts > 0 else 0
        )

        # Check cookie health
        cookie_health = "Unknown"
        if account.cookies_updated_at:
            days_since_update = (datetime.now() - account.cookies_updated_at).days
            if days_since_update > 7:
                cookie_health = "Stale"
            elif days_since_update > 5:
                cookie_health = "Expiring Soon"
            else:
                cookie_health = "Fresh"

        return {
            "id": account.id,
            "username": account.username,
            "is_active": account.is_active,
            "is_paused": account.is_paused,
            "daily_scrape_count": account.daily_scrape_count,
            "total_scrapes": account.total_scrapes,
            "success_count": account.success_count,
            "failure_count": account.failure_count,
            "success_rate": round(success_rate, 2),
            "cookie_health": cookie_health,
            "last_used_at": account.last_used_at.isoformat() if account.last_used_at else None,
            "cookies_updated_at": account.cookies_updated_at.isoformat() if account.cookies_updated_at else None,
            "created_at": account.created_at.isoformat()
        }

    except AccountRotationError:
        raise
    except Exception as e:
        raise AccountRotationError(f"Error getting account stats: {str(e)}")


def get_all_account_stats(db: Session) -> list:
    """
    Get statistics for all Instagram accounts.

    Args:
        db: Database session

    Returns:
        list: List of account statistics dictionaries
    """
    try:
        accounts = db.query(InstagramAccount).all()
        return [get_account_stats(db, account.id) for account in accounts]
    except Exception as e:
        raise AccountRotationError(f"Error getting all account stats: {str(e)}")


def pause_account(db: Session, account_id: int) -> None:
    """
    Pause an Instagram account (prevents it from being used).

    Args:
        db: Database session
        account_id: Instagram account ID

    Raises:
        AccountRotationError: If account not found
    """
    try:
        account = db.query(InstagramAccount).filter(
            InstagramAccount.id == account_id
        ).first()

        if not account:
            raise AccountRotationError(f"Instagram account {account_id} not found")

        account.is_paused = True
        db.commit()

        # Log pause event
        create_activity_log(
            db=db,
            event_type="account_paused",
            instagram_account_id=account_id,
            details={"username": account.username}
        )

    except AccountRotationError:
        raise
    except Exception as e:
        db.rollback()
        raise AccountRotationError(f"Error pausing account: {str(e)}")


def resume_account(db: Session, account_id: int) -> None:
    """
    Resume a paused Instagram account.

    Args:
        db: Database session
        account_id: Instagram account ID

    Raises:
        AccountRotationError: If account not found
    """
    try:
        account = db.query(InstagramAccount).filter(
            InstagramAccount.id == account_id
        ).first()

        if not account:
            raise AccountRotationError(f"Instagram account {account_id} not found")

        account.is_paused = False
        db.commit()

        # Log resume event
        create_activity_log(
            db=db,
            event_type="account_resumed",
            instagram_account_id=account_id,
            details={"username": account.username}
        )

    except AccountRotationError:
        raise
    except Exception as e:
        db.rollback()
        raise AccountRotationError(f"Error resuming account: {str(e)}")
