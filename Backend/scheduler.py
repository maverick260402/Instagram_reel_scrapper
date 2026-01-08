"""
Background Scheduler for Daily Reset Jobs
Automatically resets credits and usage counters at midnight
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from database import SessionLocal
from credit_system import reset_all_daily_credits
from account_rotation import reset_daily_counts
from crud import create_activity_log
import logging
import pytz  # For IST timezone configuration

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global scheduler instance configured for IST (Indian Standard Time)
scheduler = AsyncIOScheduler(timezone=pytz.timezone('Asia/Kolkata'))


async def daily_reset_job():
    """
    Daily reset job that runs at midnight
    Resets both user credits and Instagram account usage counters
    """
    logger.info("=" * 60)
    logger.info(f"Starting daily reset job at {datetime.now()}")
    logger.info("=" * 60)

    db = SessionLocal()

    try:
        # Reset user credits
        logger.info("Resetting user credits...")
        users_reset = reset_all_daily_credits(db)
        logger.info(f"[OK] Reset credits for {users_reset} user(s)")

        # Reset Instagram account daily counts
        logger.info("Resetting Instagram account daily counts...")
        accounts_reset = reset_daily_counts(db)
        logger.info(f"[OK] Reset daily counts for {accounts_reset} Instagram account(s)")

        # Log the reset event
        create_activity_log(
            db=db,
            event_type="daily_reset_completed",
            details={
                "users_reset": users_reset,
                "accounts_reset": accounts_reset,
                "reset_time": datetime.now().isoformat()
            }
        )

        logger.info("=" * 60)
        logger.info(f"Daily reset completed successfully at {datetime.now()}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"[ERROR] Daily reset failed: {str(e)}")

        # Log the failure
        try:
            create_activity_log(
                db=db,
                event_type="daily_reset_failed",
                details={
                    "error": str(e),
                    "reset_time": datetime.now().isoformat()
                }
            )
        except:
            pass

    finally:
        db.close()


def start_scheduler():
    """
    Initialize and start the scheduler
    """
    logger.info("Initializing daily reset scheduler...")

    # Add daily reset job - runs at midnight (00:00) every day
    scheduler.add_job(
        daily_reset_job,
        trigger=CronTrigger(hour=0, minute=0),  # Midnight
        id='daily_reset',
        name='Daily Credit and Usage Counter Reset',
        replace_existing=True
    )

    # Start the scheduler
    scheduler.start()
    logger.info("[OK] Scheduler started successfully")
    logger.info("Timezone: Asia/Kolkata (IST - Indian Standard Time)")
    logger.info("Daily reset job scheduled for 00:00 IST (midnight) every day")


def stop_scheduler():
    """
    Stop the scheduler gracefully
    """
    logger.info("Stopping scheduler...")
    scheduler.shutdown()
    logger.info("[OK] Scheduler stopped")


def run_manual_reset():
    """
    Manually trigger the reset job (for testing)
    """
    import asyncio
    logger.info("Running manual reset...")
    asyncio.run(daily_reset_job())


# For testing: Check scheduler status
def get_scheduler_status():
    """
    Get information about scheduled jobs
    """
    jobs = scheduler.get_jobs()

    if not jobs:
        return {"status": "no_jobs", "jobs": []}

    job_info = []
    for job in jobs:
        job_info.append({
            "id": job.id,
            "name": job.name,
            "next_run": str(job.next_run_time) if job.next_run_time else "Not scheduled"
        })

    return {
        "status": "running" if scheduler.running else "stopped",
        "jobs": job_info
    }


if __name__ == "__main__":
    """
    For testing the scheduler manually
    """
    print("\n" + "=" * 60)
    print("Daily Reset Scheduler - Manual Test")
    print("=" * 60)

    # Run manual reset
    run_manual_reset()

    print("\n" + "=" * 60)
    print("To start the scheduler in production, call start_scheduler()")
    print("from your FastAPI app startup event")
    print("=" * 60 + "\n")
