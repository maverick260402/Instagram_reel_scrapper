"""
API Key Generation Utility
Generate secure API keys for cookie update endpoints
"""

import secrets
from database import SessionLocal
from crud import create_api_key
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_secure_api_key(length: int = 32) -> str:
    """Generate a cryptographically secure random API key"""
    return secrets.token_urlsafe(length)


def create_new_api_key(key_name: str):
    """Create a new API key and store it in the database"""
    db = SessionLocal()

    try:
        # Generate random API key
        api_key_raw = generate_secure_api_key()

        # Hash the API key for storage
        api_key_hash = pwd_context.hash(api_key_raw)

        # Store in database
        api_key_record = create_api_key(db, key_name, api_key_hash)

        print("=" * 70)
        print("API KEY GENERATED SUCCESSFULLY")
        print("=" * 70)
        print(f"Key Name: {api_key_record.key_name}")
        print(f"Key ID: {api_key_record.id}")
        print(f"Created At: {api_key_record.created_at}")
        print()
        print("IMPORTANT: Save this API key securely. It will not be shown again!")
        print("-" * 70)
        print(f"API Key: {api_key_raw}")
        print("-" * 70)
        print()
        print("Use this key in the 'X-API-Key' header when calling admin endpoints.")
        print("Example:")
        print(f'  curl -H "X-API-Key: {api_key_raw}" http://localhost:8080/api/admin/instagram-accounts')
        print()
        print("Or in Python requests:")
        print(f'  headers = {{"X-API-Key": "{api_key_raw}"}}')
        print(f'  requests.post(url, headers=headers, json=data)')
        print("=" * 70)

        return api_key_raw

    except Exception as e:
        print(f"[ERROR] Failed to create API key: {str(e)}")
        return None

    finally:
        db.close()


def list_api_keys():
    """List all API keys in the database"""
    db = SessionLocal()

    try:
        from crud import get_all_api_keys
        api_keys = get_all_api_keys(db)

        if not api_keys:
            print("\n[WARNING] No API keys found in database!")
            return

        print("\n" + "=" * 70)
        print(f"API KEYS IN DATABASE: {len(api_keys)}")
        print("=" * 70)

        for key in api_keys:
            status = "[ACTIVE]" if key.is_active else "[INACTIVE]"
            print(f"\nID: {key.id}")
            print(f"  Name: {key.key_name}")
            print(f"  Status: {status}")
            print(f"  Created: {key.created_at}")
            print(f"  Last Used: {key.last_used_at if key.last_used_at else 'Never'}")

        print("=" * 70 + "\n")

    finally:
        db.close()


def revoke_api_key(key_id: int):
    """Revoke (deactivate) an API key"""
    db = SessionLocal()

    try:
        from models import ApiKey

        api_key = db.query(ApiKey).filter(ApiKey.id == key_id).first()

        if not api_key:
            print(f"[ERROR] API key with ID {key_id} not found!")
            return False

        api_key.is_active = False
        db.commit()

        print(f"[OK] API key '{api_key.key_name}' (ID: {key_id}) has been revoked")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to revoke API key: {str(e)}")
        return False

    finally:
        db.close()


if __name__ == "__main__":
    import sys

    print("\n" + "=" * 70)
    print("API KEY MANAGEMENT UTILITY")
    print("=" * 70)

    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python generate_api_key.py create <key_name>    - Create a new API key")
        print("  python generate_api_key.py list                 - List all API keys")
        print("  python generate_api_key.py revoke <key_id>      - Revoke an API key")
        print("\nExamples:")
        print('  python generate_api_key.py create "Cookie Updater - Windows PC"')
        print("  python generate_api_key.py list")
        print("  python generate_api_key.py revoke 1")
        print("=" * 70 + "\n")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "create":
        if len(sys.argv) < 3:
            print("[ERROR] Please provide a key name")
            print('Example: python generate_api_key.py create "Cookie Updater - Windows PC"')
            sys.exit(1)

        key_name = sys.argv[2]
        create_new_api_key(key_name)

    elif command == "list":
        list_api_keys()

    elif command == "revoke":
        if len(sys.argv) < 3:
            print("[ERROR] Please provide the key ID to revoke")
            print("Example: python generate_api_key.py revoke 1")
            sys.exit(1)

        try:
            key_id = int(sys.argv[2])
            revoke_api_key(key_id)
        except ValueError:
            print("[ERROR] Key ID must be a number")
            sys.exit(1)

    else:
        print(f"[ERROR] Unknown command: {command}")
        print("Available commands: create, list, revoke")
        sys.exit(1)
