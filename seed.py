from sqlalchemy import select

from app.database import session_local
from app.models.user import User
from app.security import hash_password


# Required initial users from the LeaveDesk assignment.
SEED_USERS = [
    {
        "name": "Priya Manager",
        "email": "priya.manager@leavedesk.test",
        "role": "manager",
        "password": "Manager@123",
        "manager_email": None,
    },
    {
        "name": "Arjun Employee",
        "email": "arjun@leavedesk.test",
        "role": "employee",
        "password": "Employee@123",
        "manager_email": "priya.manager@leavedesk.test",
    },
    {
        "name": "Meera Employee",
        "email": "meera@leavedesk.test",
        "role": "employee",
        "password": "Employee@123",
        "manager_email": "priya.manager@leavedesk.test",
    },
]


def seed_users():
    db = session_local()

    try:
        users_by_email = {}

        # Step 1: Create or find all users.
        for data in SEED_USERS:
            email = data["email"].lower().strip()

            user = db.scalar(
                select(User).where(User.email == email)
            )

            if user is None:
                user = User(
                    name=data["name"],
                    email=email,
                    password_hash=hash_password(data["password"]),
                    role=data["role"],
                    is_active=True,
                )

                db.add(user)
                print(f"Created user: {email}")

            else:
                print(f"User already exists: {email}")

            users_by_email[email] = user

        # Step 2: Assign manager relationships.
        db.flush()

        for data in SEED_USERS:
            email = data["email"].lower().strip()
            manager_email = data["manager_email"]

            user = users_by_email[email]

            if manager_email is None:
                user.manager_id = None
                continue

            manager_email = manager_email.lower().strip()
            manager = users_by_email.get(manager_email)

            if manager is None or manager.role != "manager":
                raise ValueError(
                    f"Valid manager not found for {email}"
                )

            user.manager_id = manager.id

        # Step 3: Save everything.
        db.commit()

        print("\nLeaveDesk seed completed successfully!")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_users()
