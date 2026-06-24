"""Shared FastAPI dependencies. get_current_user turns a bearer token into a
User row, raising 401 if anything is off."""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from . import auth, models
from .database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    email = auth.decode_token(token)
    if email is None:
        raise credentials_error
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_error
    return user
