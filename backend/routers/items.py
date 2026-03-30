from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database.database import get_db
from ..models import models
from ..schemas import schemas
from .auth import get_current_admin

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/", response_model=List[schemas.Item])
def get_items(db: Session = Depends(get_db)):
    return db.query(models.Item).all()

@router.post("/", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    new_item = models.Item(**item.dict())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.put("/{item_id}", response_model=schemas.Item)
def update_item(item_id: int, item_update: schemas.ItemCreate, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    db_item = db.query(models.Item).filter(models.Item.item_id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    for key, value in item_update.dict().items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    db_item = db.query(models.Item).filter(models.Item.item_id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted success"}
