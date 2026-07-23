from datetime import datetime, timedelta

from jose import JWTError, jwt

from fastapi import Depends, HTTPException, status

from fastapi.security import HTTPBearer
from fastapi.security import HTTPAuthorizationCredentials

SECRET_KEY = "streamsentinel_secret_key"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


security = HTTPBearer()


def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update(
        {
            "exp": expire
        }
    )

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def verify_token(token: str):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        return payload

    except JWTError:

        return None


def get_current_user(

    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),

):

    token = credentials.credentials

    payload = verify_token(token)

    if payload is None:

        raise HTTPException(

            status_code=status.HTTP_401_UNAUTHORIZED,

            detail="Invalid or Expired Token",

        )

    return payload