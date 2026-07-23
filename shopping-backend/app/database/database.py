import importlib
import os
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./shopping.db")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def initialize_database():
    database_dir = os.path.dirname(__file__)
    for filename in sorted(os.listdir(database_dir)):
        if filename.endswith(".py") and filename not in {"__init__.py", "database.py"}:
            module_name = f"app.database.{filename[:-3]}"
            importlib.import_module(module_name)

    Base.metadata.create_all(bind=engine)

    from app.database import alert_model, category_model, models, kubernetes_model

    db = SessionLocal()
    try:
        if db.query(category_model.Category).count() == 0:
            categories = [
                category_model.Category(name="Electronics", description="Smart devices and gadgets"),
                category_model.Category(name="Home", description="Home essentials and decor"),
                category_model.Category(name="Fashion", description="Modern apparel and accessories"),
            ]
            db.add_all(categories)
            db.commit()

        if db.query(models.Product).count() == 0:
            electronics = db.query(category_model.Category).filter_by(name="Electronics").first()
            home = db.query(category_model.Category).filter_by(name="Home").first()
            fashion = db.query(category_model.Category).filter_by(name="Fashion").first()

            products = [
                models.Product(name="AI Monitor", category="Electronics", price=499.99, stock=24, category_id=electronics.id if electronics else None, image_url="https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80"),
                models.Product(name="Smart Lamp", category="Home", price=79.99, stock=40, category_id=home.id if home else None, image_url="https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=800&q=80"),
                models.Product(name="Travel Backpack", category="Fashion", price=89.99, stock=18, category_id=fashion.id if fashion else None, image_url="https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=800&q=80"),
            ]
            db.add_all(products)
            db.commit()

        if db.query(alert_model.AlertRule).count() == 0:
            rules = [
                alert_model.AlertRule(
                    name="High CPU Usage",
                    description="Alert when CPU usage exceeds 90% for 5 minutes",
                    rule_type="cpu_usage",
                    metric_name="cpu",
                    operator=">",
                    threshold=90.0,
                    duration=300,
                    severity="HIGH",
                    auto_create_incident=True,
                ),
                alert_model.AlertRule(
                    name="High Memory Usage",
                    description="Alert when memory pressure rises above 90%",
                    rule_type="memory_usage",
                    metric_name="memory",
                    operator=">",
                    threshold=90.0,
                    duration=300,
                    severity="MEDIUM",
                    auto_create_incident=True,
                ),
                alert_model.AlertRule(
                    name="CrashLoopBackOff",
                    description="Alert when a pod enters CrashLoopBackOff",
                    rule_type="crash_loop_backoff",
                    metric_name="restart_count",
                    operator=">",
                    threshold=3.0,
                    duration=180,
                    severity="CRITICAL",
                    auto_create_incident=True,
                ),
            ]
            db.add_all(rules)
            db.commit()

        if db.query(alert_model.KnowledgeBaseArticle).count() == 0:
            articles = [
                alert_model.KnowledgeBaseArticle(
                    title="Kubernetes CrashLoopBackOff Recovery",
                    slug="kubernetes-crashloopbackoff-recovery",
                    content="Check the previous container exit reason, inspect the pod logs, confirm the image and environment variables, and restart the deployment only after the root cause has been addressed.",
                    category="pod_crashes",
                    keywords=["crashloopbackoff", "pod", "restart"],
                    related_alert_types=["crash_loop_backoff"],
                    author="System",
                    is_published=True,
                ),
                alert_model.KnowledgeBaseArticle(
                    title="CPU Spike Investigation Checklist",
                    slug="cpu-spike-investigation-checklist",
                    content="Review recent deployments, scale limits, HPA behavior, node pressure, and application memory settings before increasing replicas.",
                    category="resource_pressure",
                    keywords=["cpu", "hpa", "scaling"],
                    related_alert_types=["cpu_usage"],
                    author="System",
                    is_published=True,
                ),
                alert_model.KnowledgeBaseArticle(
                    title="Memory Pressure Triage Guide",
                    slug="memory-pressure-triage-guide",
                    content="Inspect recent memory spikes, high-cardinality traffic patterns, and container limits before increasing allocations or scaling aggressively.",
                    category="memory_pressure",
                    keywords=["memory", "oom", "limits"],
                    related_alert_types=["memory_usage"],
                    author="System",
                    is_published=True,
                ),
            ]
            db.add_all(articles)
            db.commit()

        if db.query(kubernetes_model.KubernetesCluster).count() == 0:
            clusters = [
                kubernetes_model.KubernetesCluster(
                    name="prod-eastus",
                    context="prod-eastus",
                    api_server="https://api.prod-eastus.example.com",
                    status="connected",
                ),
                kubernetes_model.KubernetesCluster(
                    name="staging-europe",
                    context="staging-europe",
                    api_server="https://api.staging-europe.example.com",
                    status="warning",
                ),
            ]
            db.add_all(clusters)
            db.commit()

        if db.query(alert_model.Alert).count() == 0:
            rules = db.query(alert_model.AlertRule).all()
            if rules:
                cpu_rule = next((rule for rule in rules if rule.rule_type == "cpu_usage"), rules[0])
                crash_rule = next((rule for rule in rules if rule.rule_type == "crash_loop_backoff"), rules[0])

                alerts = [
                    alert_model.Alert(
                        rule_id=cpu_rule.id,
                        pod_name="checkout-7cf59b",
                        pod_namespace="payments",
                        deployment_name="checkout",
                        title="High CPU detected on checkout service",
                        description="Checkout pods are sustaining CPU usage above 92% for the last 10 minutes.",
                        value=92.4,
                        severity="HIGH",
                        status="FIRING",
                    ),
                    alert_model.Alert(
                        rule_id=crash_rule.id,
                        pod_name="search-6b6d5c",
                        pod_namespace="search",
                        deployment_name="search",
                        title="CrashLoopBackOff detected in search namespace",
                        description="The search deployment restarted multiple times after the container failed to start.",
                        value=4.0,
                        severity="CRITICAL",
                        status="FIRING",
                    ),
                ]
                db.add_all(alerts)
                db.commit()

                alert_records = db.query(alert_model.Alert).order_by(alert_model.Alert.created_at.desc()).limit(2).all()
                incidents = [
                    alert_model.Incident(
                        alert_id=alert_records[0].id,
                        title="Checkout latency spike",
                        description="The checkout pathway is experiencing elevated latency and intermittent 502 responses.",
                        status="IN_PROGRESS",
                        priority="HIGH",
                        severity="HIGH",
                        root_cause_analysis="Recent deployment increased CPU saturation and queue depth on the checkout pods.",
                        suggested_fix="Scale the checkout service and verify the latest deployment rollout.",
                        recommended_action="Shift traffic to the warm standby and confirm the rollout is complete.",
                        impact="Customers may see slower checkout and temporary request failures.",
                        namespace="payments",
                        pod_name="checkout-7cf59b",
                        deployment_name="checkout",
                        assigned_to="SRE Team",
                        tags=["latency", "checkout", "deployment"],
                    ),
                    alert_model.Incident(
                        alert_id=alert_records[1].id,
                        title="Search service restart loop",
                        description="The search service is repeatedly restarting after a startup failure.",
                        status="OPEN",
                        priority="CRITICAL",
                        severity="CRITICAL",
                        root_cause_analysis="The container image is missing a required environment variable and exits immediately.",
                        suggested_fix="Update the deployment config and redeploy the image with the required variables.",
                        recommended_action="Restore the last known-good manifest and verify the pod starts cleanly.",
                        impact="Search results may be unavailable until the pod recovers.",
                        namespace="search",
                        pod_name="search-6b6d5c",
                        deployment_name="search",
                        assigned_to="Platform Team",
                        tags=["restart", "search", "startup"],
                    ),
                ]
                db.add_all(incidents)
                db.commit()
    finally:
        db.close()