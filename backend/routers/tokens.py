from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from ..database.database import get_db
from ..models import models
from ..schemas import schemas

router = APIRouter(prefix="/tokens", tags=["tokens"])

@router.get("/", response_model=List[schemas.TokenBase])
def get_tokens(db: Session = Depends(get_db)):
    # Fetch all tokens that are not delivered yet, or just all for listing
    return db.query(models.Token).order_by(models.Token.token_time.desc()).limit(20).all()

@router.patch("/{token_id}/status")
def update_token_status(token_id: int, status: str, db: Session = Depends(get_db)):
    db_token = db.query(models.Token).filter(models.Token.token_id == token_id).first()
    if db_token:
        db_token.status = status
        db.commit()
    return {"message": "Token status updated"}
