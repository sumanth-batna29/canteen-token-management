from passlib.context import CryptContext
from sqlalchemy.orm import Session
from backend.database.database import SessionLocal
from backend.models import models

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def setup_admin():
    db = SessionLocal()
    email = "admin@canteen.com"
    db_user = db.query(models.User).filter(models.User.email == email).first()
    
    hashed_password = pwd_context.hash("admin")
    
    if db_user:
        db_user.password = hashed_password
        db_user.role = "Admin"
    else:
        new_user = models.User(
            name="Super Admin",
            email=email,
            phone_no="9876543210",
            gender="Male",
            role="Admin",
            password=hashed_password,
            address="Canteen HQ"
        )
        db.add(new_user)
    
    db.commit()
    print(f"Admin user {email} set up with password: admin")
    db.close()

if __name__ == "__main__":
    setup_admin()
