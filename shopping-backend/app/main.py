from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import Base
from app.database.database import engine
from app.database.database import initialize_database

from app.database import models
from app.database import user_model
from app.database import order_tracking_model
from app.database import kubernetes_model
from app.database import alert_model
from app.database import ecommerce_extension_model
from app.database import cart_model, order_model, order_item_model, wishlist_model, category_model, coupon_model, payment_model, audit_log_model, notification_model

from app.api.product_api import router as product_router
from app.api.auth_api import router as auth_router
from app.api.user_api import router as user_router
from app.api.cart_api import router as cart_router
from app.api.order_api import router as order_router
from app.api.wishlist_api import router as wishlist_router
from app.api.category_api import router as category_router
from app.api.coupon_api import router as coupon_router
from app.api.admin_api import router as admin_router
from app.api.search_api import router as search_router
from app.api.invoice_api import router as invoice_router
from app.api.payment_api import router as payment_router
from app.api.review_api import router as review_router
from app.api.inventory_api import router as inventory_router
from app.api.kubernetes_api import router as kubernetes_router
from app.api.alert_api import router as alert_router
from app.api.ai_chat_api import router as ai_chat_router
from app.api.ecommerce_extension_api import router as ecommerce_extension_router

initialize_database()

app = FastAPI(
    title="Shopping Backend API",
    version="1.0.0",
    description="E-Commerce Backend for StreamSentinel",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Shopping Backend is Running"}


@app.get("/health")
def health():
    return {
        "status": "UP",
        "service": "shopping-backend",
        "version": "1.0.0",
    }


app.include_router(auth_router)
app.include_router(product_router)
app.include_router(user_router)
app.include_router(cart_router)
app.include_router(order_router)
app.include_router(wishlist_router)
app.include_router(category_router)
app.include_router(coupon_router)
app.include_router(admin_router)
app.include_router(search_router)
app.include_router(payment_router)
app.include_router(invoice_router)
app.include_router(review_router)
app.include_router(inventory_router)
app.include_router(kubernetes_router)
app.include_router(alert_router)
app.include_router(ai_chat_router)
app.include_router(ecommerce_extension_router)