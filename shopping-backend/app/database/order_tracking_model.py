from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class OrderTracking(Base):
    __tablename__ = "order_tracking"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
    )

    status = Column(
        String(50),
        nullable=False,
    )

    remarks = Column(
        String(255),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    order = relationship(
        "Order",
        back_populates="tracking_history",
    )