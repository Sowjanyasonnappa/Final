from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    coupon_id = Column(Integer, ForeignKey("coupons.id", ondelete="SET NULL"), nullable=True, index=True)
    shipping_address_id = Column(Integer, ForeignKey("addresses.id", ondelete="SET NULL"), nullable=True)
    total_amount = Column(Float, nullable=False, default=0.0)
    status = Column(String(20), nullable=False, default="Pending")
    payment_status = Column(String(20), nullable=False, default="Pending")
    coupon_code = Column(String(50), nullable=True)
    discount_amount = Column(Float, nullable=False, default=0.0)
    shipping_address = Column(String(255), nullable=True)
    shipping_cost = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="orders")
    coupon = relationship("Coupon", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="order", cascade="all, delete-orphan")
    tracking_history = relationship(
        "OrderTracking",
        back_populates="order",
        cascade="all, delete",
    )
    returns = relationship("OrderReturn", back_populates="order", cascade="all, delete-orphan")
    shipments = relationship("Shipment", back_populates="order", cascade="all, delete-orphan")
    shipping_address_obj = relationship("Address", back_populates="orders")
