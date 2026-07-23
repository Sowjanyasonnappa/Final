"""
E-commerce Extension Models - Returns, Shipping, Addresses, Analytics
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.database import Base


class Address(Base):
    """Store user addresses"""
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Address details
    title = Column(String(100), nullable=False)  # Home, Work, etc.
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(255), nullable=False)
    street_address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=False)
    country = Column(String(100), nullable=False)
    
    # Preferences
    is_default = Column(Boolean, default=False)
    address_type = Column(String(50), default="billing")  # billing, shipping, both
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="addresses")
    orders = relationship("Order", back_populates="shipping_address_obj")


class OrderReturn(Base):
    """Store order returns"""
    __tablename__ = "order_returns"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    order_item_id = Column(Integer, ForeignKey("order_items.id", ondelete="CASCADE"), nullable=True)
    
    # Return details
    reason = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), default="INITIATED")  # INITIATED, APPROVED, REJECTED, COMPLETED
    quantity = Column(Integer, default=1)
    refund_amount = Column(Float, nullable=True)
    
    # Dates
    requested_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    
    # Additional info
    tracking_number = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="returns")


class Refund(Base):
    """Store refund information"""
    __tablename__ = "refunds"

    id = Column(Integer, primary_key=True, index=True)
    order_return_id = Column(Integer, ForeignKey("order_returns.id", ondelete="CASCADE"), nullable=False, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="CASCADE"), nullable=True)
    
    # Refund details
    amount = Column(Float, nullable=False)
    status = Column(String(50), default="PENDING")  # PENDING, PROCESSING, COMPLETED, FAILED
    method = Column(String(50), default="ORIGINAL")  # ORIGINAL, STORE_CREDIT
    
    # External reference
    gateway_refund_id = Column(String(255), nullable=True)
    gateway_response = Column(JSON, nullable=True)
    
    # Dates
    initiated_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ShippingMethod(Base):
    """Store available shipping methods"""
    __tablename__ = "shipping_methods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    base_cost = Column(Float, nullable=False)
    cost_per_item = Column(Float, default=0)
    estimated_days = Column(Integer, nullable=False)  # Estimated delivery days
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    shipments = relationship("Shipment", back_populates="shipping_method")


class Shipment(Base):
    """Store shipment information"""
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    shipping_method_id = Column(Integer, ForeignKey("shipping_methods.id"), nullable=False)
    
    # Shipping details
    tracking_number = Column(String(255), nullable=True, unique=True, index=True)
    carrier = Column(String(100), nullable=False)
    status = Column(String(50), default="PENDING")  # PENDING, SHIPPED, IN_TRANSIT, DELIVERED, FAILED
    
    # Address
    from_address = Column(JSON, nullable=True)  # Store address details as JSON
    to_address = Column(JSON, nullable=False)
    
    # Dates
    ship_date = Column(DateTime, nullable=True)
    estimated_delivery = Column(DateTime, nullable=True)
    actual_delivery = Column(DateTime, nullable=True)
    
    # Cost
    shipping_cost = Column(Float, nullable=False)
    insurance_cost = Column(Float, default=0)
    
    # Events
    events = Column(JSON, default=[])  # Array of delivery events
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    order = relationship("Order", back_populates="shipments")
    shipping_method = relationship("ShippingMethod", back_populates="shipments")


class SalesMetric(Base):
    """Store daily sales metrics"""
    __tablename__ = "sales_metrics"

    id = Column(Integer, primary_key=True, index=True)
    
    # Date metrics
    date = Column(DateTime, nullable=False, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    day = Column(Integer, nullable=False)
    
    # Sales metrics
    total_orders = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    average_order_value = Column(Float, default=0.0)
    total_items_sold = Column(Integer, default=0)
    unique_customers = Column(Integer, default=0)
    
    # Product metrics
    top_product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    top_category = Column(String(100), nullable=True)
    
    # Customer metrics
    new_customers = Column(Integer, default=0)
    returning_customers = Column(Integer, default=0)
    
    # Returns and refunds
    total_returns = Column(Integer, default=0)
    total_refunds = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class ProductViewHistory(Base):
    """Track recently viewed products"""
    __tablename__ = "product_view_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    
    view_count = Column(Integer, default=1)
    last_viewed = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    product = relationship("Product")


class ProductRecommendation(Base):
    """Store AI product recommendations"""
    __tablename__ = "product_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Recommendation metadata
    reason = Column(String(255), nullable=True)  # why_recommended, related_to_purchase, etc.
    score = Column(Float, nullable=True)  # 0.0 to 1.0
    recommendation_type = Column(String(50), default="SIMILAR")  # SIMILAR, FREQUENTLY_BOUGHT_WITH, TRENDING, etc.
    
    # AI metadata
    ai_generated = Column(Boolean, default=False)
    ai_model = Column(String(100), nullable=True)
    
    # Engagement
    clicked = Column(Boolean, default=False)
    clicked_at = Column(DateTime, nullable=True)
    purchased = Column(Boolean, default=False)
    purchased_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    product = relationship("Product")


class CustomerSegment(Base):
    """Store customer segmentation data"""
    __tablename__ = "customer_segments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Segment metrics
    total_purchases = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)
    average_order_value = Column(Float, default=0.0)
    last_purchase_date = Column(DateTime, nullable=True)
    days_since_purchase = Column(Integer, nullable=True)
    
    # Segment classification
    segment = Column(String(50), default="NEW")  # NEW, ACTIVE, INACTIVE, VIP, CHURNED
    lifetime_value = Column(Float, default=0.0)
    churn_risk = Column(Float, default=0.0)  # 0.0 to 1.0
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")
