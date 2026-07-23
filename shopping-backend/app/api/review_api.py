from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.auth.oauth2 import user_required

from app.database.user_model import User

from app.schemas.review import (
    ReviewCreate,
    ReviewUpdate,
)

from app.services.review_service import (
    add_review,
    update_review,
    delete_review,
    get_product_reviews,
)

router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"],
)


@router.get("/{product_id}")
def list_reviews(
    product_id: int,
    db: Session = Depends(get_db),
):

    return get_product_reviews(
        db,
        product_id,
    )


@router.post("/{product_id}")
def create_review(
    product_id: int,
    payload: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_required),
):

    return add_review(
        db,
        current_user,
        product_id,
        payload.rating,
        payload.comment,
    )


@router.put("/{review_id}")
def edit_review(
    review_id: int,
    payload: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_required),
):

    return update_review(
        db,
        current_user,
        review_id,
        payload.rating,
        payload.comment,
    )


@router.delete("/{review_id}")
def remove_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_required),
):

    return delete_review(
        db,
        current_user,
        review_id,
    )