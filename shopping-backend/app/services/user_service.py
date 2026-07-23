from sqlalchemy.orm import Session

from app.database.user_model import User


def get_all_users(db: Session):

    return (
        db.query(User)
        .order_by(User.id)
        .all()
    )


def get_user(db: Session, user_id: int):

    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )


def update_role(
    db: Session,
    user_id: int,
    role: str,
):

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        return None

    user.role = role.upper()

    db.commit()

    db.refresh(user)

    return user


def delete_user(
    db: Session,
    user_id: int,
):

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        return False

    db.delete(user)

    db.commit()

    return True