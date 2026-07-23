from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime
from sqlalchemy import Text

from sqlalchemy.orm import relationship

from sqlalchemy.sql import func

from app.database.database import Base


class Review(Base):

    __tablename__ = "reviews"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    rating = Column(
        Integer,
        nullable=False,
    )

    comment = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
    )

    product_id = Column(
        Integer,
        ForeignKey(
            "products.id",
            ondelete="CASCADE",
        ),
    )

    user = relationship(
        "User",
        back_populates="reviews",
    )

    product = relationship(
        "Product",
        back_populates="reviews",
    )