"""
Helper script to add Instagram accounts to the pool
"""

from database import SessionLocal
from crud import create_instagram_account, get_all_instagram_accounts

def add_account(username: str, email: str, password: str):
    """Add an Instagram account to the pool"""
    db = SessionLocal()

    try:
        # Check if account already exists
        from crud import get_instagram_account_by_username
        existing = get_instagram_account_by_username(db, username)

        if existing:
            print(f"[EXISTS] Account '{username}' already exists in the pool!")
            return False

        # Create account
        account = create_instagram_account(db, username, email, password)
        print(f"[OK] Successfully added Instagram account: {account.username}")
        print(f"  - Email: {account.email}")
        print(f"  - Active: {account.is_active}")
        print(f"  - ID: {account.id}")

        return True

    except Exception as e:
        print(f"[ERROR] Error adding account: {str(e)}")
        return False
    finally:
        db.close()


def list_accounts():
    """List all Instagram accounts in the pool"""
    db = SessionLocal()

    try:
        accounts = get_all_instagram_accounts(db)

        if not accounts:
            print("\n[WARNING] No Instagram accounts in the pool yet!")
            return

        print(f"\n[INFO] Instagram Accounts in Pool: {len(accounts)}")
        print("=" * 70)

        for acc in accounts:
            status = "[ACTIVE]" if acc.is_active and not acc.is_paused else "[INACTIVE]"
            print(f"\nID: {acc.id}")
            print(f"  Username: {acc.username}")
            print(f"  Email: {acc.email}")
            print(f"  Status: {status}")
            print(f"  Daily Scrapes: {acc.daily_scrape_count}")
            print(f"  Total Scrapes: {acc.total_scrapes}")

    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("Instagram Account Pool Manager")
    print("=" * 70)

    # Add the first account
    print("\nAdding first Instagram account...")

    success = add_account(
    )

    if success:
        print("\n[SUCCESS] Account added successfully!")

    # List all accounts
    list_accounts()

    print("\n" + "=" * 70)
    print("To add more accounts later, modify this script or use Python shell:")
    print("  from crud import create_instagram_account")
    print("  from database import SessionLocal")
    print("  db = SessionLocal()")
    print('  create_instagram_account(db, "username", "email", "password")')
    print("  db.close()")
    print("=" * 70 + "\n")
