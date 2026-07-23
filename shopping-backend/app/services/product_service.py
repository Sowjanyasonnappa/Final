from sqlalchemy.orm import Session

from app.database.models import Product


def product_to_dict(product):

    return {
        "id": product.id,
        "name": product.name,
        "category": product.category,
        "price": product.price,
        "stock": product.stock,
        "image_url": product.image_url,
        "thumbnail_url": product.thumbnail_url,
        "average_rating": product.average_rating,
        "total_reviews": product.total_reviews,
    }


def get_all_products(db: Session):

    products = db.query(Product).all()

    return [
        product_to_dict(product)
        for product in products
    ]


def get_product(
    db: Session,
    product_id: int,
):

    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if product is None:
        return None

    return product_to_dict(product)


def add_product(
    db: Session,
    product,
):

    db_product = Product(
        name=product.name,
        category=product.category,
        price=product.price,
        stock=product.stock,
    )

    db.add(db_product)

    db.commit()

    db.refresh(db_product)

    return product_to_dict(db_product)


def update_product(
    db: Session,
    product_id: int,
    product,
):

    db_product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if db_product is None:
        return None

    db_product.name = product.name
    db_product.category = product.category
    db_product.price = product.price
    db_product.stock = product.stock

    db.commit()

    db.refresh(db_product)

    return product_to_dict(db_product)


def delete_product(
    db: Session,
    product_id: int,
):

    db_product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if db_product is None:
        return False

    db.delete(db_product)

    db.commit()

    return True