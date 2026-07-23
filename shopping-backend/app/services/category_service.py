from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.database.category_model import Category


def get_all_categories(db: Session):
    return db.query(Category).order_by(Category.id).all()


def create_category(db: Session, name: str, description: str | None = None):
    category = Category(name=name, description=description)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, category_id: int, name: str, description: str | None = None):
    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    category.name = name
    category.description = description
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: int):
    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
    return True
