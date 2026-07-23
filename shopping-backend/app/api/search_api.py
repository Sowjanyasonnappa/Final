from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.database.models import Product
from app.database.category_model import Category

router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


@router.get("/")
def search_products(
    q: str | None = None,
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort: str = "asc",
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
):

    query = db.query(Product)

    if q:
        query = query.filter(
            Product.name.ilike(f"%{q}%")
        )

    if category:
        query = query.filter(
            Product.category.ilike(f"%{category}%")
        )

    if min_price is not None:
        query = query.filter(
            Product.price >= min_price
        )

    if max_price is not None:
        query = query.filter(
            Product.price <= max_price
        )

    if sort.lower() == "desc":

        query = query.order_by(
            Product.price.desc()
        )

    else:

        query = query.order_by(
            Product.price.asc()
        )

    total = query.count()

    products = (
        query.offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": products,
        "page": page,
        "page_size": page_size,
        "total": total,
    }


@router.get("/categories")
def search_categories(
    q: str | None = None,
    db: Session = Depends(get_db),
):

    query = db.query(Category)

    if q:

        query = query.filter(
            Category.name.ilike(f"%{q}%")
        )

    return query.all()