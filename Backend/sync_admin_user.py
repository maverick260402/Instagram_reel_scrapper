"""
Sync admin user - create corresponding User record
"""

from database import SessionLocal
from models import AdminUser, User
from passlib.context import CryptContext

def sync_admin_user():
    db = SessionLocal()

    try:
        # Get admin user
        admin = db.query(AdminUser).filter(AdminUser.email == "admin@example.com").first()

        if not admin:
            print("[ERROR] Admin user not found!")
            return

        print(f"Found admin: {admin.email}")

        # Check if corresponding User exists
        user = db.query(User).filter(User.email == admin.email).first()

        if user:
            print(f"[INFO] User already exists with ID: {user.id}")
        else:
            # Create User record for admin
            user = User(
                email=admin.email,
                username=admin.username,
                password_hash=admin.password_hash,
                daily_credit_limit=999999,  # Unlimited for admins
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"[OK] Created User record with ID: {user.id}")

        print("\n" + "="*70)
        print("ADMIN USER SYNCED")
        print("="*70)
        print(f"Admin ID: {admin.id}")
        print(f"User ID: {user.id}")
        print(f"Email: {admin.email}")
        print("="*70)
        print("\nYou can now login at: http://localhost:8080/static/admin/login.html")

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    sync_admin_user()
