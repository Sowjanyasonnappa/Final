from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.product import Product

from app.services.product_service import (
    get_all_products,
    get_product,
    add_product,
    update_product,
    delete_product,
)

from app.auth.oauth2 import admin_required

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@router.get("/")
def list_products(
    db: Session = Depends(get_db),
):
    return get_all_products(db)


@router.get("/{product_id}")
def fetch_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = get_product(db, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return product


@router.post("/")
def create_product(
    product: Product,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required),
):
    return add_product(db, product)


@router.put("/{product_id}")
def edit_product(
    product_id: int,
    product: Product,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required),
):

    updated = update_product(
        db,
        product_id,
        product,
    )

    if updated is None:

        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return updated


@router.delete("/{product_id}")
def remove_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required),
):

    deleted = delete_product(
        db,
        product_id,
    )

    if not deleted:

        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return {
        "message": "Product deleted successfully"
    }