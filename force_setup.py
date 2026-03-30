import sys
import os
# Add current directory to path so we can import backend
sys.path.append(os.getcwd())

from backend.database.database import SessionLocal
from backend.models import models
from backend.routers.auth import get_password_hash

def create_user(name, email, password, role):
    db = SessionLocal()
    try:
        # Check if exists
        existing = db.query(models.User).filter(models.User.email == email).first()
        if existing:
            print(f"User {email} already exists, updating...")
            existing.password = get_password_hash(password)
            existing.role = role
        else:
            new_user = models.User(
                name=name,
                email=email,
                password=get_password_hash(password),
                role=role,
                phone_no="1234567890",
                gender="Male",
                address="HQ"
            )
            db.add(new_user)
        db.commit()
        print(f"Successfully created/updated {email}")
    except Exception as e:
        print(f"Error for {email}: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_user("Admin", "admin@canteen.com", "admin", "Admin")
    create_user("Customer", "user@test.com", "password", "Customer")
