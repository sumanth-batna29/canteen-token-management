from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone_no: Optional[str] = None
    gender: Optional[str] = None
    role: str = "Customer"
    address: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    user_id: int
    class Config:
        from_attributes = True

class TokenData(BaseModel):
    email: Optional[str] = None

class TokenRecord(BaseModel):
    access_token: str
    token_type: str
    user: Optional[dict] = None

class ItemBase(BaseModel):
    name: str
    category: Optional[str] = None
    dietary: str
    price: float
    status: str = "Available"

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    item_id: int
    class Config:
        from_attributes = True

class OrderItemBase(BaseModel):
    item_id: int
    quantity: int

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    order_item_id: int
    subtotal: float
    item: Item
    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    user_id: int
    total_amount: float
    status: str = "Pending"

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]

class Order(OrderBase):
    order_id: int
    order_date: datetime
    items: List[OrderItem]
    class Config:
        from_attributes = True

class PaymentBase(BaseModel):
    order_id: int
    transaction_id: str
    method: str
    paid_amount: float
    status: str = "Pending"

class TokenBase(BaseModel):
    order_id: int
    token_no: int
    token_time: datetime
    status: str = "Preparing"
