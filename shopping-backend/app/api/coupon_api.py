from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.auth.oauth2 import (
    admin_required,
    user_required,
)

from app.database.user_model import User

from app.schemas.coupon import CouponCreate

from app.services.coupon_service import (
    create_coupon,
    get_all_coupons,
    validate_coupon,
)

router = APIRouter(
    prefix="/coupons",
    tags=["Coupons"],
)


@router.get("/")
def list_coupons(
    db: Session = Depends(get_db),
    current_user: User = Depends(user_required),
):

    return get_all_coupons(db)


@router.post("/")
def create_coupon_endpoint(
    payload: CouponCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):

    coupon = create_coupon(
        db,
        payload.code,
        payload.discount_percentage,
        payload.expiry_date,
        payload.active,
    )

    if coupon is None:

        raise HTTPException(
            status_code=400,
            detail="Coupon already exists",
        )

    return coupon


@router.get("/validate/{code}")
def validate_coupon_endpoint(
    code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_required),
):

    coupon = validate_coupon(
        db,
        code,
    )

    if coupon is None:

        raise HTTPException(
            status_code=404,
            detail="Invalid or Expired Coupon",
        )

    return coupon