"""
Check admin users in database
"""

from database import SessionLocal
from models import AdminUser
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def check_admin_users():
    db = SessionLocal()

    try:
        admins = db.query(AdminUser).all()

        print("="*70)
        print(f"ADMIN USERS IN DATABASE: {len(admins)}")
        print("="*70)

        for admin in admins:
            print(f"\nID: {admin.id}")
            print(f"Username: {admin.username}")
            print(f"Email: {admin.email}")
            print(f"Active: {admin.is_active}")
            print(f"Created: {admin.created_at}")
            print(f"Password Hash: {admin.password_hash[:50]}...")

            # Test password
            try:
                is_valid = pwd_context.verify("admin123", admin.password_hash)
                print(f"Password 'admin123' works: {is_valid}")
            except:
                print(f"Password verification failed")

        print("="*70)

    except Exception as e:
        print(f"[ERROR] {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    check_admin_users()
