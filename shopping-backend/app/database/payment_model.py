from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    ForeignKey,
    DateTime,
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    order_id = Column(
        Integer,
        ForeignKey(
            "orders.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    amount = Column(
        Float,
        nullable=False,
    )

    payment_method = Column(
        String(50),
        nullable=False,
    )

    transaction_id = Column(
        String(100),
        unique=True,
        nullable=True,
    )

    status = Column(
        String(30),
        nullable=False,
        default="Pending",
    )

    payment_date = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    order = relationship(
        "Order",
        back_populates="payments",
    )