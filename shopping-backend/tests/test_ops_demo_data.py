import importlib
import sys


def test_initialize_database_creates_demo_ops_data(tmp_path, monkeypatch):
    db_path = tmp_path / "shopping.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    for module_name in [
        "app.database.database",
        "app.database.alert_model",
        "app.database.kubernetes_model",
        "app.database.models",
        "app.database.cart_model",
        "app.database.order_model",
        "app.database.order_item_model",
        "app.database.wishlist_model",
        "app.database.category_model",
        "app.database.coupon_model",
        "app.database.payment_model",
        "app.database.audit_log_model",
        "app.database.notification_model",
    ]:
        sys.modules.pop(module_name, None)

    database = importlib.import_module("app.database.database")
    database = importlib.reload(database)

    database.initialize_database()

    db = database.SessionLocal()
    try:
        from app.database import alert_model, kubernetes_model

        assert db.query(kubernetes_model.KubernetesCluster).count() >= 2
        assert db.query(alert_model.Alert).count() >= 2
        assert db.query(alert_model.Incident).count() >= 2
        assert db.query(alert_model.KnowledgeBaseArticle).count() >= 2
    finally:
        db.close()
