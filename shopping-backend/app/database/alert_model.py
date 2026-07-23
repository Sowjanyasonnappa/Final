from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.database import Base


class AlertRule(Base):
    """Store alert rules for monitoring"""
    __tablename__ = "alert_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    rule_type = Column(String(100), nullable=False)  # cpu_usage, memory_usage, pod_restart, deployment_down, etc.
    
    # Rule condition
    metric_name = Column(String(255), nullable=False)  # cpu, memory, restart_count, etc.
    operator = Column(String(20), nullable=False)  # >, <, >=, <=, ==, !=
    threshold = Column(Float, nullable=False)
    duration = Column(Integer, default=300)  # Duration in seconds before alerting
    
    # Alert severity
    severity = Column(String(50), default="WARNING")  # CRITICAL, HIGH, MEDIUM, LOW
    enabled = Column(Boolean, default=True)
    
    # Scope
    namespace = Column(String(255), nullable=True)  # null = all namespaces
    pod_name_pattern = Column(String(255), nullable=True)  # regex pattern for pod names
    deployment_name = Column(String(255), nullable=True)
    
    # Actions
    auto_create_incident = Column(Boolean, default=True)
    notify_channels = Column(JSON, default={})  # {"email": ["admin@example.com"], "slack": ["#alerts"]}
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    alerts = relationship("Alert", back_populates="rule", cascade="all, delete-orphan")


class Alert(Base):
    """Store generated alerts"""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("alert_rules.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Alert context
    pod_name = Column(String(255), nullable=True)
    pod_namespace = Column(String(255), nullable=True)
    deployment_name = Column(String(255), nullable=True)
    node_name = Column(String(255), nullable=True)
    
    # Alert details
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    value = Column(Float, nullable=False)
    severity = Column(String(50), default="WARNING")  # CRITICAL, HIGH, MEDIUM, LOW
    status = Column(String(50), default="FIRING")  # FIRING, RESOLVED, ACKNOWLEDGED
    
    # Timestamps
    triggered_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime, nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    rule = relationship("AlertRule", back_populates="alerts")
    incidents = relationship("Incident", back_populates="alert")


class Incident(Base):
    """Store incidents created from alerts"""
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id", ondelete="CASCADE"), nullable=True, index=True)
    
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text, nullable=False)
    status = Column(String(50), default="OPEN")  # OPEN, IN_PROGRESS, RESOLVED, CLOSED
    priority = Column(String(50), default="MEDIUM")  # CRITICAL, HIGH, MEDIUM, LOW
    severity = Column(String(50), default="MEDIUM")  # CRITICAL, HIGH, MEDIUM, LOW
    
    # AI Generated fields
    root_cause_analysis = Column(Text, nullable=True)
    suggested_fix = Column(Text, nullable=True)
    recommended_action = Column(Text, nullable=True)
    preventive_action = Column(Text, nullable=True)
    impact = Column(Text, nullable=True)
    
    # Affected resources
    namespace = Column(String(255), nullable=True)
    pod_name = Column(String(255), nullable=True)
    deployment_name = Column(String(255), nullable=True)
    node_name = Column(String(255), nullable=True)
    
    # Assignment & notes
    assigned_to = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    tags = Column(JSON, default={})
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    alert = relationship("Alert", back_populates="incidents")
    rcas = relationship("RCA", back_populates="incident", cascade="all, delete-orphan")


class RCA(Base):
    """Root Cause Analysis for incidents"""
    __tablename__ = "rcas"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String(500), nullable=False)
    summary = Column(Text, nullable=False)
    root_cause = Column(Text, nullable=False)
    contributing_factors = Column(JSON, default={})  # List of factors
    timeline = Column(JSON, default={})  # Sequence of events
    impact_analysis = Column(Text, nullable=True)
    corrective_actions = Column(JSON, default={})  # List of actions taken
    preventive_measures = Column(JSON, default={})  # Future preventions
    
    # AI Generated
    ai_generated = Column(Boolean, default=False)
    ai_model = Column(String(100), nullable=True)  # gpt-4, gpt-3.5-turbo, etc.
    ai_confidence = Column(Float, nullable=True)  # 0.0 to 1.0
    
    # Metrics
    mttr = Column(Integer, nullable=True)  # Mean Time To Recovery in seconds
    mtbf = Column(Integer, nullable=True)  # Mean Time Between Failures in seconds
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    incident = relationship("Incident", back_populates="rcas")


class KnowledgeBaseArticle(Base):
    """Store knowledge base articles for incident resolution"""
    __tablename__ = "knowledge_base_articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, unique=True, index=True)
    slug = Column(String(500), nullable=False, unique=True, index=True)
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)  # pod_crashes, memory_leaks, etc.
    
    # Keywords for search
    keywords = Column(JSON, default=[])
    
    # Related incidents/alerts
    related_alert_types = Column(JSON, default=[])
    
    # Visibility
    is_published = Column(Boolean, default=True)
    author = Column(String(255), nullable=True)
    
    # Metrics
    views_count = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AIChat(Base):
    """Store AI chat conversations for Ops support"""
    __tablename__ = "ai_chats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=True)
    context = Column(JSON, default={})  # Context about K8s cluster, incident, etc.
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship("AIChatMessage", back_populates="chat", cascade="all, delete-orphan")


class AIChatMessage(Base):
    """Store individual messages in AI chat"""
    __tablename__ = "ai_chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("ai_chats.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(50), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    chat = relationship("AIChat", back_populates="messages")
