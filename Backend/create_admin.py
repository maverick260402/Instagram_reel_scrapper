"""
Quick script to create admin user
"""

from database import SessionLocal
from models import AdminUser
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin_user():
    db = SessionLocal()

    try:
        # Check if admin already exists
        existing = db.query(AdminUser).filter(AdminUser.email == "admin@example.com").first()

        if existing:
            print("[INFO] Admin user already exists")
            print(f"Email: {existing.email}")
            print(f"Username: {existing.username}")
            print(f"Active: {existing.is_active}")

            # Update password to admin123
            existing.password_hash = pwd_context.hash("admin123")
            existing.is_active = True
            db.commit()
            print("\n[OK] Password reset to: admin123")
            return

        # Create new admin user
        admin = AdminUser(
            username="admin",
            email="admin@example.com",
            password_hash=pwd_context.hash("admin123"),
            is_active=True
        )

        db.add(admin)
        db.commit()

        print("="*70)
        print("ADMIN USER CREATED SUCCESSFULLY")
        print("="*70)
        print(f"Email: admin@example.com")
        print(f"Password: admin123")
        print("="*70)
        print("\nYou can now login at: http://localhost:8888/static/admin/login.html")

    except Exception as e:
        print(f"[ERROR] Failed to create admin user: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
