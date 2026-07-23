from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.auth.oauth2 import admin_required

from app.schemas.inventory import StockUpdate

from app.services.inventory_service import (
    update_stock,
    increase_stock,
    decrease_stock,
    inventory_history,
    inventory_dashboard,
    low_stock_products,
    out_of_stock_products,
    search_inventory,
)

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"],
)


@router.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(admin_required),
):

    return inventory_dashboard(db)


@router.get("/low-stock")
def low_stock(
    db: Session = Depends(get_db),
    current_user=Depends(admin_required),
):

    return low_stock_products(db)


@router.get("/out-of-stock")
def out_stock(
    db: Session = Depends(get_db),
    current_user=Depends(admin_required),
):

    return out_of_stock_products(db)


@router.get("/history/{product_id}")
def history(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required),
):

    return inventory_history(
        db,
        product_id,
    )


@router.get("/search")
def search(
    keyword: str,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required),
):

    return search_inventory(
        db,
        keyword,
    )


@router.put("/{product_id}")
def edit_stock(
    product_id: int,
    payload: StockUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required),
):

    return update_stock(
        db,
        product_id,
        payload.stock,
        payload.remarks,
    )


@router.post("/{product_id}/increase")
def add_stock(
    product_id: int,
    quantity: int,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required),
):

    return increase_stock(
        db,
        product_id,
        quantity,
    )


@router.post("/{product_id}/decrease")
def reduce_stock(
    product_id: int,
    quantity: int,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required),
):

    return decrease_stock(
        db,
        product_id,
        quantity,
    )