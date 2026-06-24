"""History routes. Users see and clear only their own records — enforced by
filtering on the authenticated user's id, never on a client-supplied id."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import get_current_user

router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=list[schemas.HistoryItem])
def list_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return (
        db.query(models.History)
        .filter(models.History.user_id == current_user.id)
        .order_by(models.History.created_at.desc())
        .limit(min(limit, 200))
        .all()
    )


@router.delete("/{item_id}", status_code=204)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    item = (
        db.query(models.History)
        .filter(
            models.History.id == item_id,
            models.History.user_id == current_user.id,
        )
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="History item not found")
    db.delete(item)
    db.commit()
