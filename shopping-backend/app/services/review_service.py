from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException

from app.database.review_model import Review
from app.database.models import Product
from app.database.order_model import Order
from app.database.order_item_model import OrderItem
from app.database.user_model import User


def add_review(
    db: Session,
    current_user: User,
    product_id: int,
    rating: int,
    comment: str,
):

    if rating < 1 or rating > 5:
        raise HTTPException(
            status_code=400,
            detail="Rating must be between 1 and 5",
        )

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

    purchased = (
        db.query(OrderItem)
        .join(
            Order,
            Order.id == OrderItem.order_id,
        )
        .filter(
            Order.user_id == current_user.id,
            OrderItem.product_id == product_id,
            Order.status == "Delivered",
        )
        .first()
    )

    if purchased is None:
        raise HTTPException(
            status_code=400,
            detail="Only verified buyers can review this product",
        )

    already_reviewed = (
        db.query(Review)
        .filter(
            Review.user_id == current_user.id,
            Review.product_id == product_id,
        )
        .first()
    )

    if already_reviewed:
        raise HTTPException(
            status_code=400,
            detail="You already reviewed this product",
        )

    review = Review(
        rating=rating,
        comment=comment,
        user_id=current_user.id,
        product_id=product_id,
    )

    db.add(review)

    db.commit()

    db.refresh(review)

    return review


def update_review(
    db: Session,
    current_user: User,
    review_id: int,
    rating: int,
    comment: str,
):

    review = (
        db.query(Review)
        .filter(
            Review.id == review_id,
            Review.user_id == current_user.id,
        )
        .first()
    )

    if review is None:
        raise HTTPException(
            status_code=404,
            detail="Review not found",
        )

    review.rating = rating
    review.comment = comment

    db.commit()

    db.refresh(review)

    return review


def delete_review(
    db: Session,
    current_user: User,
    review_id: int,
):

    review = (
        db.query(Review)
        .filter(
            Review.id == review_id,
            Review.user_id == current_user.id,
        )
        .first()
    )

    if review is None:
        raise HTTPException(
            status_code=404,
            detail="Review not found",
        )

    db.delete(review)

    db.commit()

    return {
        "message": "Review deleted successfully",
    }


def get_product_reviews(
    db: Session,
    product_id: int,
):

    reviews = (
        db.query(Review)
        .filter(
            Review.product_id == product_id,
        )
        .all()
    )

    avg_rating = (
        db.query(
            func.avg(Review.rating)
        )
        .filter(
            Review.product_id == product_id,
        )
        .scalar()
    )

    total_reviews = (
        db.query(
            func.count(Review.id)
        )
        .filter(
            Review.product_id == product_id,
        )
        .scalar()
    )

    return {
        "average_rating": round(avg_rating or 0, 2),
        "total_reviews": total_reviews,
        "reviews": reviews,
    }