import getpass
import sys
from pathlib import Path

# Lets the script import from the "app" package
sys.path.append(str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select  # noqa: E402

from app import models  # noqa: E402,F401
from app.core.database import Base, SessionLocal, engine  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models.user import User, UserRole  # noqa: E402


def main():
    Base.metadata.create_all(bind=engine)

    email = input("Admin email: ").strip().lower()
    full_name = input("Full name: ").strip()
    password = getpass.getpass("Password (min 8 chars): ")

    if len(password) < 8:
        print("Password must be at least 8 characters.")
        return

    db = SessionLocal()
    try:
        user = db.scalar(select(User).where(User.email == email))
        if user:
            user.role = UserRole.HR_ADMIN.value
            print(f"Existing user {email} promoted to HR Admin.")
        else:
            db.add(
                User(
                    email=email,
                    full_name=full_name,
                    hashed_password=hash_password(password),
                    role=UserRole.HR_ADMIN.value,
                )
            )
            print(f"HR Admin {email} created.")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()