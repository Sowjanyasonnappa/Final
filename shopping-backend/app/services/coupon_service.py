from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.database.coupon_model import Coupon


def get_all_coupons(db: Session):
    return db.query(Coupon).order_by(Coupon.id).all()


def create_coupon(db: Session, code: str, discount_percentage: float, expiry_date: datetime, active: bool = True):
    coupon = Coupon(
        code=code.upper(),
        discount_percentage=discount_percentage,
        expiry_date=expiry_date,
        active=1 if active else 0,
    )
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    return coupon


def validate_coupon(db: Session, code: str):
    coupon = db.query(Coupon).filter(Coupon.code == code.upper()).first()
    if coupon is None:
        raise HTTPException(status_code=404, detail="Coupon not found")
    if coupon.active != 1:
        raise HTTPException(status_code=400, detail="Coupon is inactive")
    expiry_date = coupon.expiry_date
    if expiry_date.tzinfo is None:
        expiry_date = expiry_date.replace(tzinfo=timezone.utc)
    if expiry_date < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Coupon expired")
    return coupon
