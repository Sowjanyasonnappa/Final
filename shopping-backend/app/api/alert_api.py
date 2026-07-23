"""
Alert Management API Routes
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database import alert_model
from app.schemas import kubernetes_schema
from app.services.alert_engine import AlertEngine
from app.services.ai_service import AIService
from app.auth.oauth2 import get_current_user
from app.utils.role_checker import admin_only

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/alerts", tags=["Alerts & Incidents"])


# Alert Rules
@router.get("/rules", response_model=List[kubernetes_schema.AlertRuleResponse])
async def get_alert_rules(
    enabled: Optional[bool] = Query(None),
    severity: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all alert rules"""
    admin_only(current_user)
    
    query = db.query(alert_model.AlertRule)
    
    if enabled is not None:
        query = query.filter_by(enabled=enabled)
    
    if severity:
        query = query.filter_by(severity=severity)
    
    rules = query.all()
    return rules


@router.post("/rules", response_model=kubernetes_schema.AlertRuleResponse)
async def create_alert_rule(
    rule: kubernetes_schema.AlertRuleCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new alert rule"""
    admin_only(current_user)
    
    # Check if rule already exists
    existing = db.query(alert_model.AlertRule).filter_by(name=rule.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Alert rule with this name already exists")
    
    db_rule = alert_model.AlertRule(**rule.dict())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule


@router.get("/rules/{rule_id}", response_model=kubernetes_schema.AlertRuleResponse)
async def get_alert_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get alert rule details"""
    admin_only(current_user)
    
    rule = db.query(alert_model.AlertRule).filter_by(id=rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    return rule


@router.put("/rules/{rule_id}", response_model=kubernetes_schema.AlertRuleResponse)
async def update_alert_rule(
    rule_id: int,
    rule_update: kubernetes_schema.AlertRuleCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update alert rule"""
    admin_only(current_user)
    
    rule = db.query(alert_model.AlertRule).filter_by(id=rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    
    for key, value in rule_update.dict().items():
        setattr(rule, key, value)
    
    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/rules/{rule_id}")
async def delete_alert_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete alert rule"""
    admin_only(current_user)
    
    rule = db.query(alert_model.AlertRule).filter_by(id=rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    
    db.delete(rule)
    db.commit()
    return {"message": "Alert rule deleted"}


@router.post("/rules/bulk-update", response_model=dict)
async def bulk_update_alert_rules(
    update: kubernetes_schema.BulkAlertRuleUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Bulk update alert rules"""
    admin_only(current_user)
    
    rules = db.query(alert_model.AlertRule).filter(
        alert_model.AlertRule.id.in_(update.rule_ids)
    ).all()
    
    for rule in rules:
        if update.enabled is not None:
            rule.enabled = update.enabled
        if update.severity is not None:
            rule.severity = update.severity
    
    db.commit()
    return {"message": f"Updated {len(rules)} alert rules"}


# Alerts
@router.get("", response_model=List[kubernetes_schema.AlertResponse])
async def get_alerts(
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    limit: int = Query(100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all alerts"""
    admin_only(current_user)
    
    query = db.query(alert_model.Alert)
    
    if status:
        query = query.filter_by(status=status)
    
    if severity:
        query = query.filter_by(severity=severity)
    
    alerts = query.order_by(alert_model.Alert.triggered_at.desc()).limit(limit).all()
    return alerts


# Incidents
@router.get("/incidents", response_model=List[kubernetes_schema.IncidentResponse])
async def get_incidents(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    limit: int = Query(100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all incidents"""
    admin_only(current_user)
    
    query = db.query(alert_model.Incident)
    
    if status:
        query = query.filter_by(status=status)
    
    if priority:
        query = query.filter_by(priority=priority)
    
    incidents = query.order_by(alert_model.Incident.created_at.desc()).limit(limit).all()
    return incidents


@router.get("/{alert_id:int}", response_model=kubernetes_schema.AlertResponse)
async def get_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get alert details"""
    admin_only(current_user)
    
    alert = db.query(alert_model.Alert).filter_by(id=alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.put("/{alert_id:int}", response_model=kubernetes_schema.AlertResponse)
async def update_alert(
    alert_id: int,
    alert_update: kubernetes_schema.AlertUpdateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update alert"""
    admin_only(current_user)
    
    alert = db.query(alert_model.Alert).filter_by(id=alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    for key, value in alert_update.dict(exclude_unset=True).items():
        setattr(alert, key, value)
    
    db.commit()
    db.refresh(alert)
    return alert


@router.post("/{alert_id:int}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Acknowledge an alert"""
    admin_only(current_user)
    
    engine = AlertEngine(db)
    success = engine.acknowledge_alert(alert_id, current_user.email)
    
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"message": "Alert acknowledged"}


@router.post("/{alert_id:int}/resolve")
async def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Resolve an alert"""
    admin_only(current_user)
    
    engine = AlertEngine(db)
    success = engine.resolve_alert(alert_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"message": "Alert resolved"}


@router.post("/{alert_id:int}/create-incident")
async def create_incident_from_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create an incident from an alert"""
    admin_only(current_user)
    
    alert = db.query(alert_model.Alert).filter_by(id=alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    engine = AlertEngine(db)
    engine._create_incident_from_alert(alert, 1)  # Assuming cluster_id = 1
    
    return {"message": "Incident created from alert"}


@router.post("/incidents", response_model=kubernetes_schema.IncidentResponse)
async def create_incident(
    incident: kubernetes_schema.IncidentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new incident"""
    admin_only(current_user)
    
    db_incident = alert_model.Incident(**incident.dict())
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)
    return db_incident


@router.get("/incidents/{incident_id}", response_model=kubernetes_schema.IncidentResponse)
async def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get incident details"""
    admin_only(current_user)
    
    incident = db.query(alert_model.Incident).filter_by(id=incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.put("/incidents/{incident_id}", response_model=kubernetes_schema.IncidentResponse)
async def update_incident(
    incident_id: int,
    incident_update: kubernetes_schema.IncidentUpdateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update incident"""
    admin_only(current_user)
    
    incident = db.query(alert_model.Incident).filter_by(id=incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    for key, value in incident_update.dict(exclude_unset=True).items():
        setattr(incident, key, value)
    
    db.commit()
    db.refresh(incident)
    return incident


# RCA
@router.get("/incidents/{incident_id}/rcas", response_model=List[kubernetes_schema.RCAResponse])
async def get_rcas(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get RCAs for an incident"""
    admin_only(current_user)
    
    rcas = db.query(alert_model.RCA).filter_by(incident_id=incident_id).all()
    return rcas


@router.post("/incidents/{incident_id}/rcas", response_model=kubernetes_schema.RCAResponse)
async def create_rca(
    incident_id: int,
    rca: kubernetes_schema.RCACreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create RCA for an incident"""
    admin_only(current_user)
    
    db_rca = alert_model.RCA(incident_id=incident_id, **rca.dict())
    db.add(db_rca)
    db.commit()
    db.refresh(db_rca)
    return db_rca


@router.post("/incidents/{incident_id}/rcas/ai-generate")
async def generate_ai_rca(
    incident_id: int,
    request: kubernetes_schema.AIRCARequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Generate AI RCA for an incident"""
    admin_only(current_user)
    
    incident = db.query(alert_model.Incident).filter_by(id=incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    ai_service = AIService()
    incident_data = {
        "title": incident.title,
        "description": incident.description,
        "pod_name": incident.pod_name,
        "namespace": incident.namespace,
        "logs": request.logs or "",
        "metrics": request.metrics or {}
    }
    
    result = ai_service.generate_root_cause_analysis(incident_data)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    # Save to database
    db_rca = alert_model.RCA(
        incident_id=incident_id,
        title=incident.title + " - AI Analysis",
        summary=result["root_cause_analysis"].get("summary", ""),
        root_cause=result["root_cause_analysis"].get("root_cause", ""),
        ai_generated=True,
        ai_model=result.get("model"),
        ai_confidence=result.get("confidence")
    )
    db.add(db_rca)
    
    # Update incident with AI analysis
    incident.root_cause_analysis = result["root_cause_analysis"].get("root_cause", "")
    incident.suggested_fix = result["root_cause_analysis"].get("suggested_fix", "")
    incident.recommended_action = result["root_cause_analysis"].get("recommended_action", "")
    incident.preventive_action = result["root_cause_analysis"].get("preventive_action", "")
    
    db.commit()
    db.refresh(db_rca)
    
    return db_rca
