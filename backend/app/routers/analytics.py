"""Analytics dashboard endpoint. Returns this user's usage summary."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import analytics, models
from ..database import get_db
from ..deps import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("")
def my_analytics(db: Session = Depends(get_db),
                 user: models.User = Depends(get_current_user)):
    return analytics.summary(db, user_id=user.id)
