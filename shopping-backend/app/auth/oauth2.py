from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.user_model import User

from app.utils.security import SECRET_KEY, ALGORITHM


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        email = payload.get("sub")

        if email is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if user is None:
        raise credentials_exception

    return user


def admin_required(
    current_user: User = Depends(get_current_user),
):

    if current_user.role.upper() != "ADMIN":

        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )

    return current_user


def user_required(
    current_user: User = Depends(get_current_user),
):

    if current_user.role.upper() not in [
        "USER",
        "ADMIN",
    ]:

        raise HTTPException(
            status_code=403,
            detail="User access required",
        )

    return current_user


def seller_required(
    current_user: User = Depends(get_current_user),
):

    if current_user.role.upper() not in [
        "SELLER",
        "ADMIN",
    ]:

        raise HTTPException(
            status_code=403,
            detail="Seller access required",
        )

    return current_user