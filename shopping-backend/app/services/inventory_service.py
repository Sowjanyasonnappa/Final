from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.database.models import Product
from app.database.inventory_history_model import InventoryHistory


LOW_STOCK_LIMIT = 10


def update_stock(
    db: Session,
    product_id: int,
    new_stock: int,
    remarks: str | None = None,
):

    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    previous_stock = product.stock

    product.stock = new_stock

    history = InventoryHistory(
        product_id=product.id,
        previous_stock=previous_stock,
        new_stock=new_stock,
        action="Stock Updated",
        remarks=remarks,
    )

    db.add(history)

    db.commit()

    db.refresh(product)

    return product


def increase_stock(
    db: Session,
    product_id: int,
    quantity: int,
):

    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    previous_stock = product.stock

    product.stock += quantity

    history = InventoryHistory(
        product_id=product.id,
        previous_stock=previous_stock,
        new_stock=product.stock,
        action="Stock Increased",
        remarks=f"+{quantity}",
    )

    db.add(history)

    db.commit()

    db.refresh(product)

    return product


def decrease_stock(
    db: Session,
    product_id: int,
    quantity: int,
):

    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    if quantity > product.stock:
        raise HTTPException(
            status_code=400,
            detail="Insufficient stock",
        )

    previous_stock = product.stock

    product.stock -= quantity

    history = InventoryHistory(
        product_id=product.id,
        previous_stock=previous_stock,
        new_stock=product.stock,
        action="Stock Decreased",
        remarks=f"-{quantity}",
    )

    db.add(history)

    db.commit()

    db.refresh(product)

    return product


def low_stock_products(
    db: Session,
):

    return (
        db.query(Product)
        .filter(Product.stock <= LOW_STOCK_LIMIT)
        .all()
    )


def out_of_stock_products(
    db: Session,
):

    return (
        db.query(Product)
        .filter(Product.stock == 0)
        .all()
    )


def inventory_history(
    db: Session,
    product_id: int,
):

    return (
        db.query(InventoryHistory)
        .filter(
            InventoryHistory.product_id == product_id,
        )
        .order_by(
            InventoryHistory.created_at.desc(),
        )
        .all()
    )


def inventory_dashboard(
    db: Session,
):

    total_products = db.query(Product).count()

    in_stock = (
        db.query(Product)
        .filter(Product.stock > LOW_STOCK_LIMIT)
        .count()
    )

    low_stock = (
        db.query(Product)
        .filter(
            Product.stock <= LOW_STOCK_LIMIT,
            Product.stock > 0,
        )
        .count()
    )

    out_stock = (
        db.query(Product)
        .filter(Product.stock == 0)
        .count()
    )

    return {
        "total_products": total_products,
        "in_stock": in_stock,
        "low_stock": low_stock,
        "out_of_stock": out_stock,
    }


def search_inventory(
    db: Session,
    keyword: str,
):

    return (
        db.query(Product)
        .filter(
            Product.name.ilike(f"%{keyword}%")
        )
        .all()
    )