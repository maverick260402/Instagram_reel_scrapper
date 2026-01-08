"""
Verify Instagram accounts in the pool
"""

from database import SessionLocal
from crud import get_all_instagram_accounts

db = SessionLocal()

try:
    accounts = get_all_instagram_accounts(db)

    print("\n" + "=" * 70)
    print(f"Instagram Accounts in Pool: {len(accounts)}")
    print("=" * 70)

    if not accounts:
        print("\n[WARNING] No Instagram accounts found!")
    else:
        for acc in accounts:
            status = "[ACTIVE]" if acc.is_active and not acc.is_paused else "[INACTIVE]"
            print(f"\nID: {acc.id}")
            print(f"  Username: {acc.username}")
            print(f"  Email: {acc.email}")
            print(f"  Status: {status}")
            print(f"  Daily Scrapes: {acc.daily_scrape_count}")
            print(f"  Total Scrapes: {acc.total_scrapes}")
            print(f"  Has Cookies: {'Yes' if acc.cookies else 'No'}")

    print("\n" + "=" * 70)

finally:
    db.close()
