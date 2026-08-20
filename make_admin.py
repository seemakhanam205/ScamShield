from app.db.database import SessionLocal
from app.db.models import User

# Open database session
db = SessionLocal()

try:
    # Find your user by email
    user = db.query(User).filter(User.email == "seema864k@gmail.com").first()
    
    if user:
        user.role = "ADMIN"
        db.commit()
        print(f"Success! {user.email} is now an ADMIN.")
    else:
        print("User not found. Check the email address.")
finally:
    db.close()