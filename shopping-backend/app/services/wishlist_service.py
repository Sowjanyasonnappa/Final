from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.database.models import Product
from app.database.user_model import User
from app.database.wishlist_model import WishlistItem


def get_wishlist(db: Session, user: User):
    return db.query(WishlistItem).filter(WishlistItem.user_id == user.id).all()


def add_to_wishlist(db: Session, user: User, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    existing = db.query(WishlistItem).filter(WishlistItem.user_id == user.id, WishlistItem.product_id == product_id).first()
    if existing:
        return existing
    item = WishlistItem(user_id=user.id, product_id=product_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def remove_from_wishlist(db: Session, user: User, product_id: int):
    item = db.query(WishlistItem).filter(WishlistItem.user_id == user.id, WishlistItem.product_id == product_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Wishlist item not found")
    db.delete(item)
    db.commit()
    return True
