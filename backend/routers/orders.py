from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from jose import jwt
from typing import List, Optional
import datetime, uuid
from ..database.database import get_db
from ..models import models
from ..schemas import schemas
from .auth import get_current_user, get_current_admin, SECRET_KEY, ALGORITHM

oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

class StatusUpdate(BaseModel):
    new_status: str

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", response_model=schemas.Order)
async def place_order(order_data: schemas.OrderCreate, db: Session = Depends(get_db), token: Optional[str] = Depends(oauth2_scheme_optional)):
    user_id = None

    # Try to get user from token if provided
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email = payload.get("sub")
            if email:
                u = db.query(models.User).filter(models.User.email == email).first()
                if u:
                    user_id = u.user_id
        except Exception:
            pass

    # Fallback: use the first user in the database (Guest mode)
    if not user_id:
        guest = db.query(models.User).first()
        if not guest:
            raise HTTPException(status_code=500, detail="No users found. Run setup first.")
        user_id = guest.user_id

    total_amount = 0
    order_items = []
    
    for item_in in order_data.items:
        db_item = db.query(models.Item).filter(models.Item.item_id == item_in.item_id).first()
        if not db_item:
            raise HTTPException(status_code=400, detail=f"Item {item_in.item_id} not found")
        
        subtotal = db_item.price * item_in.quantity
        total_amount += subtotal
        order_items.append(models.OrderItem(item_id=item_in.item_id, quantity=item_in.quantity, subtotal=subtotal))
    
    # Create Order
    new_order = models.Order(user_id=user_id, total_amount=total_amount, status="Pending")
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    # Add Items
    for oi in order_items:
        oi.order_id = new_order.order_id
        db.add(oi)
    
    # Automatic Token Generation (Simplified)
    last_token = db.query(models.Token).filter(models.Token.token_time >= datetime.datetime.combine(datetime.date.today(), datetime.time.min)).order_by(models.Token.token_no.desc()).first()
    token_no = (last_token.token_no + 1) if last_token else 1
    
    new_token = models.Token(order_id=new_order.order_id, token_no=token_no, status="Preparing")
    db.add(new_token)
    
    db.commit()
    db.refresh(new_order)
    return new_order

@router.get("/history", response_model=List[schemas.Order])
def get_order_history(db: Session = Depends(get_db), user = Depends(get_current_user)):
    return db.query(models.Order).filter(models.Order.user_id == user.user_id).all()

@router.get("/all", response_model=List[schemas.Order])
def get_all_orders(db: Session = Depends(get_db), user = Depends(get_current_user)):
    return db.query(models.Order).all()

class StatusUpdate(BaseModel):
    new_status: str

@router.patch("/{order_id}/status")
def update_order_status(order_id: int, body: StatusUpdate, db: Session = Depends(get_db), user = Depends(get_current_user)):
    new_status = body.new_status
    db_order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    db_order.status = new_status
    
    # Update token status
    token_map = {"Pending": "Preparing", "Completed": "Ready"}
    db_token = db.query(models.Token).filter(models.Token.order_id == order_id).first()
    if db_token:
        db_token.status = token_map.get(new_status, "Preparing")
    
    # Auto-create Payment record when Completed (so revenue counts it)
    if new_status == "Completed":
        existing = db.query(models.Payment).filter(models.Payment.order_id == order_id).first()
        if not existing:
            payment = models.Payment(
                order_id=order_id,
                transaction_id=f"TXN-{uuid.uuid4().hex[:8].upper()}",
                method="Cash",
                status="Success",
                paid_amount=db_order.total_amount
            )
            db.add(payment)
    
    db.commit()
    return {"message": f"Order #{order_id} updated to {new_status}"}

# Payment Simulation
@router.post("/{order_id}/pay")
def pay_order(order_id: int, method: str, db: Session = Depends(get_db), user = Depends(get_current_user)):
    db_order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if already paid
    existing_payment = db.query(models.Payment).filter(models.Payment.order_id == order_id).first()
    if existing_payment and existing_payment.status == "Success":
        raise HTTPException(status_code=400, detail="Order already paid")

    # Simulation Logic
    transaction_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
    new_payment = models.Payment(
        order_id=order_id,
        transaction_id=transaction_id,
        method=method,
        status="Success",
        paid_amount=db_order.total_amount
    )
    db.add(new_payment)
    
    # Token generation (normally done by trigger in DB, but we'll add logic here too for fallback/clarity)
    # Check if token exists
    existing_token = db.query(models.Token).filter(models.Token.order_id == order_id).first()
    if not existing_token:
        last_token = db.query(models.Token).filter(models.Token.token_time >= datetime.datetime.combine(datetime.date.today(), datetime.time.min)).order_by(models.Token.token_no.desc()).first()
        token_no = (last_token.token_no + 1) if last_token else 1
        
        token = models.Token(order_id=order_id, token_no=token_no, status="Preparing")
        db.add(token)

    db.commit()
    return {"message": "Payment successful", "transaction_id": transaction_id, "token_no": token_no if not existing_token else existing_token.token_no}
