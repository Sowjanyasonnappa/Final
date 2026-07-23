from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from app.database.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)

    category_id = Column(
        Integer,
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    image_url = Column(String(255), nullable=True)
    thumbnail_url = Column(String(255), nullable=True)

    category_ref = relationship(
        "Category",
        back_populates="products",
    )

    cart_items = relationship(
        "CartItem",
        back_populates="product",
        cascade="all, delete-orphan",
    )

    order_items = relationship(
        "OrderItem",
        back_populates="product",
    )

    wishlist_items = relationship(
        "WishlistItem",
        back_populates="product",
        cascade="all, delete-orphan",
    )

    reviews = relationship(
        "Review",
        back_populates="product",
        cascade="all, delete",
    )
    inventory_logs = relationship(
    "InventoryHistory",
    cascade="all, delete",
)

    @hybrid_property
    def average_rating(self):

        if not self.reviews:
            return 0

        return round(
            sum(review.rating for review in self.reviews)
            / len(self.reviews),
            2,
        )

    @hybrid_property
    def total_reviews(self):

        return len(self.reviews)