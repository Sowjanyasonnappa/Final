from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.database.cart_model import CartItem
from app.database.models import Product
from app.database.user_model import User


def get_cart(db: Session, user: User):
    items = (
        db.query(CartItem)
        .filter(CartItem.user_id == user.id)
        .all()
    )

    response = []
    total_price = 0.0
    total_items = 0

    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product is None:
            continue
        item_total = product.price * item.quantity
        total_price += item_total
        total_items += item.quantity
        response.append({
            "id": item.id,
            "product_id": item.product_id,
            "quantity": item.quantity,
            "product_name": product.name,
            "price": product.price,
            "stock": product.stock,
        })

    return {"items": response, "total_items": total_items, "total_price": total_price}


def add_to_cart(db: Session, user: User, product_id: int, quantity: int):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.stock < quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    existing_item = (
        db.query(CartItem)
        .filter(CartItem.user_id == user.id, CartItem.product_id == product_id)
        .first()
    )

    if existing_item:
        existing_item.quantity += quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item

    cart_item = CartItem(user_id=user.id, product_id=product_id, quantity=quantity)
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart_item


def update_cart_item(db: Session, user: User, item_id: int, quantity: int):
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.user_id == user.id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Cart item not found")

    product = db.query(Product).filter(Product.id == item.product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    if quantity < 1:
        raise HTTPException(status_code=400, detail="Quantity must be at least 1")
    if product.stock < quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    item.quantity = quantity
    db.commit()
    db.refresh(item)
    return item


def remove_cart_item(db: Session, user: User, item_id: int):
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.user_id == user.id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Cart item not found")
    db.delete(item)
    db.commit()
    return True


def clear_cart(db: Session, user: User):
    db.query(CartItem).filter(CartItem.user_id == user.id).delete()
    db.commit()
    return True
