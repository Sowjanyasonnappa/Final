from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime
from sqlalchemy.sql import func

from sqlalchemy.orm import relationship

from app.database.database import Base


class InventoryHistory(Base):

    __tablename__ = "inventory_history"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    product_id = Column(
        Integer,
        ForeignKey(
            "products.id",
            ondelete="CASCADE",
        ),
    )

    previous_stock = Column(
        Integer,
        nullable=False,
    )

    new_stock = Column(
        Integer,
        nullable=False,
    )

    action = Column(
        String(100),
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

    product = relationship("Product")