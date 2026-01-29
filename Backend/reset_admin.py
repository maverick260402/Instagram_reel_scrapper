"""
Reset admin user to default credentials
"""

from database import SessionLocal
from models import AdminUser
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def reset_admin():
    db = SessionLocal()

    try:
        # Get first admin user
        admin = db.query(AdminUser).first()

        if not admin:
            print("[ERROR] No admin users found!")
            return

        print(f"Updating admin user ID: {admin.id}")
        print(f"Old email: {admin.email}")
        print(f"Old username: {admin.username}")

        # Update to default credentials
        admin.email = "admin@example.com"
        admin.username = "admin"
        admin.password_hash = pwd_context.hash("admin123")
        admin.is_active = True

        db.commit()

        print("\n" + "="*70)
        print("ADMIN CREDENTIALS RESET")
        print("="*70)
        print("Email: admin@example.com")
        print("Password: admin123")
        print("="*70)
        print("\nYou can now login at: http://localhost:8888/static/admin/login.html")

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin()
