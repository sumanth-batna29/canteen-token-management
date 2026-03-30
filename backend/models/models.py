from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from ..database.database import Base
import datetime

class User(Base):
    __tablename__ = "User"
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone_no = Column(String(15))
    gender = Column(Enum('Male', 'Female', 'Other'))
    role = Column(Enum('Admin', 'Customer'), default='Customer')
    password = Column(String(255), nullable=False)
    address = Column(Text)

class Item(Base):
    __tablename__ = "Item"
    item_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50))
    dietary = Column(Enum('Veg', 'Non-Veg'), nullable=False)
    price = Column(Float, nullable=False)
    status = Column(Enum('Available', 'Out of Stock'), default='Available')

class Order(Base):
    __tablename__ = "Orders"
    order_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("User.user_id", ondelete="CASCADE"))
    order_date = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String(20), default='Pending')
    total_amount = Column(Float, nullable=False)
    
    user = relationship("User")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "Order_Items"
    order_item_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("Orders.order_id", ondelete="CASCADE"))
    item_id = Column(Integer, ForeignKey("Item.item_id", ondelete="CASCADE"))
    quantity = Column(Integer, nullable=False)
    subtotal = Column(Float, nullable=False)
    
    order = relationship("Order", back_populates="items")
    item = relationship("Item")

class Payment(Base):
    __tablename__ = "Payment"
    payment_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("Orders.order_id", ondelete="CASCADE"), unique=True)
    transaction_id = Column(String(100), unique=True)
    method = Column(Enum('UPI', 'Card', 'Cash'))
    status = Column(Enum('Pending', 'Success', 'Failed'), default='Pending')
    paid_amount = Column(Float, nullable=False)

class Token(Base):
    __tablename__ = "Token"
    token_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("Orders.order_id", ondelete="CASCADE"), unique=True)
    token_no = Column(Integer, nullable=False)
    token_time = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(Enum('Preparing', 'Ready', 'Delivered'), default='Preparing')
