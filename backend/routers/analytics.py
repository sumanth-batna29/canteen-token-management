from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from ..database.database import get_db
from ..models import models
from .auth import get_current_user
import datetime

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db), user = Depends(get_current_user)):
    # Most Sold Item
    most_sold = db.query(
        models.Item.name,
        func.sum(models.OrderItem.quantity).label("total")
    ).join(models.OrderItem).group_by(models.Item.item_id).order_by(
        func.sum(models.OrderItem.quantity).desc()
    ).first()

    # Orders per day
    orders_per_day = db.query(
        func.date(models.Order.order_date),
        func.count(models.Order.order_id)
    ).group_by(func.date(models.Order.order_date)).all()

    return {
        "most_sold_item": most_sold[0] if most_sold else "N/A",
        "orders_today": db.query(models.Order).filter(
            func.date(models.Order.order_date) == datetime.date.today()
        ).count(),
        "orders_trend": [{"date": str(d), "count": c} for d, c in orders_per_day]
    }

@router.get("/queue-status")
def get_queue_status(db: Session = Depends(get_db)):
    preparing_count = db.query(models.Token).filter(models.Token.status == "Preparing").count()
    estimated_wait = max(preparing_count * 3, 5)

    # Show the smallest Ready token (actually being served right now)
    ready_token = db.query(models.Token.token_no).filter(models.Token.status == "Ready").order_by(models.Token.token_no.asc()).first()
    
    if ready_token:
        now_serving_val = str(ready_token[0])
    else:
        # If no Ready token, show the most recently completed token number
        last_done = db.query(models.Token.token_no).filter(models.Token.status == "Ready").order_by(models.Token.token_no.desc()).first()
        now_serving_val = str(last_done[0]) if last_done else "---"

    return {
        "estimated_wait_minutes": estimated_wait,
        "preparing_orders": preparing_count,
        "now_serving": now_serving_val
    }

@router.get("/recommendations")
def get_recommendations(user_id: int, db: Session = Depends(get_db)):
    # Logic: Recommend items from categories they frequently order but haven't bought recently
    past_items = db.query(models.Item.category).join(models.OrderItem).join(models.Order).filter(models.Order.user_id == user_id).all()
    if not past_items:
        # Default: Show top rated or popular
        return db.query(models.Item).limit(3).all()
    
    categories = [p[0] for p in past_items]
    fav_category = max(set(categories), key=categories.count)
    
    recommendations = db.query(models.Item).filter(models.Item.category == fav_category).limit(3).all()
    return recommendations
