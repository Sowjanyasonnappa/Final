from sqlalchemy.orm import Session

from app.database.user_model import User

from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
)


def register_user(
    db: Session,
    email: str,
    password: str,
):

    existing_user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing_user:
        return None

    user_count = db.query(User).count()

    role = "ADMIN" if user_count == 0 else "USER"

    new_user = User(
        email=email,
        password=hash_password(password),
        role=role,
    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return new_user


def login_user(
    db: Session,
    email: str,
    password: str,
):

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if user is None:
        return None

    if not verify_password(
        password,
        user.password,
    ):
        return None

    token = create_access_token(
        {
            "sub": user.email,
            "role": user.role,
        }
    )

    return token