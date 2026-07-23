"""
Alert Engine - Process alerts and create incidents
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.database import alert_model, kubernetes_model
from app.database.database import SessionLocal
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)


class AlertEngine:
    """Process alerts against metrics and create incidents"""
    
    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
        self.ai_service = AIService()
    
    def evaluate_rules(self, cluster_id: int):
        """Evaluate all alert rules against current metrics"""
        try:
            rules = self.db.query(alert_model.AlertRule).filter_by(enabled=True).all()
            
            for rule in rules:
                self._evaluate_rule(rule, cluster_id)
            
            self.db.commit()
            logger.info(f"Evaluated {len(rules)} alert rules")
        except Exception as e:
            logger.error(f"Error evaluating rules: {e}")
            self.db.rollback()
    
    def _evaluate_rule(self, rule: alert_model.AlertRule, cluster_id: int):
        """Evaluate a single alert rule"""
        try:
            if rule.rule_type == "cpu_usage":
                self._evaluate_cpu_rule(rule, cluster_id)
            elif rule.rule_type == "memory_usage":
                self._evaluate_memory_rule(rule, cluster_id)
            elif rule.rule_type == "pod_restart_count":
                self._evaluate_pod_restart_rule(rule, cluster_id)
            elif rule.rule_type == "pod_down":
                self._evaluate_pod_down_rule(rule, cluster_id)
            elif rule.rule_type == "deployment_down":
                self._evaluate_deployment_down_rule(rule, cluster_id)
            elif rule.rule_type == "disk_full":
                self._evaluate_disk_full_rule(rule, cluster_id)
            elif rule.rule_type == "oom_killed":
                self._evaluate_oom_killed_rule(rule, cluster_id)
            elif rule.rule_type == "image_pull_backoff":
                self._evaluate_image_pull_backoff_rule(rule, cluster_id)
            elif rule.rule_type == "crash_loop_backoff":
                self._evaluate_crash_loop_backoff_rule(rule, cluster_id)
        except Exception as e:
            logger.error(f"Error evaluating rule {rule.name}: {e}")
    
    def _evaluate_cpu_rule(self, rule: alert_model.AlertRule, cluster_id: int):
        """Evaluate CPU usage rule"""
        try:
            # Get recent CPU metrics
            cutoff_time = datetime.utcnow() - timedelta(seconds=rule.duration)
            metrics = self.db.query(kubernetes_model.KubernetesMetric).filter(
                kubernetes_model.KubernetesMetric.cluster_id == cluster_id,
                kubernetes_model.KubernetesMetric.metric_type.in_(["node_cpu", "pod_cpu"]),
                kubernetes_model.KubernetesMetric.timestamp >= cutoff_time
            ).all()
            
            for metric in metrics:
                # Convert to percentage (CPU is in cores, threshold might be in percentage)
                value = float(metric.value) * 100 if metric.unit == "cores" else float(metric.value)
                
                if self._check_threshold(value, rule.operator, rule.threshold):
                    self._create_alert(rule, metric, value, cluster_id)
        except Exception as e:
            logger.error(f"Error evaluating CPU rule: {e}")
    
    def _evaluate_memory_rule(self, rule: alert_model.AlertRule, cluster_id: int):
        """Evaluate memory usage rule"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(seconds=rule.duration)
            metrics = self.db.query(kubernetes_model.KubernetesMetric).filter(
                kubernetes_model.KubernetesMetric.cluster_id == cluster_id,
                kubernetes_model.KubernetesMetric.metric_type.in_(["node_memory", "pod_memory"]),
                kubernetes_model.KubernetesMetric.timestamp >= cutoff_time
            ).all()
            
            for metric in metrics:
                # Memory value is in bytes
                value = float(metric.value)
                
                if self._check_threshold(value, rule.operator, rule.threshold):
                    self._create_alert(rule, metric, value, cluster_id)
        except Exception as e:
            logger.error(f"Error evaluating memory rule: {e}")
    
    def _evaluate_pod_restart_rule(self, rule: alert_model.AlertRule, cluster_id: int):
        """Evaluate pod restart count rule"""
        try:
            namespace = rule.namespace or None
            
            if namespace:
                pods = self.db.query(kubernetes_model.KubernetesPod).join(
                    kubernetes_model.KubernetesNamespace
                ).filter(
                    kubernetes_model.KubernetesPod.cluster_id == cluster_id,
                    kubernetes_model.KubernetesNamespace.name == namespace
                ).all()
            else:
                pods = self.db.query(kubernetes_model.KubernetesPod).filter_by(cluster_id=cluster_id).all()
            
            for pod in pods:
                if self._check_threshold(pod.restart_count, rule.operator, rule.threshold):
                    self._create_alert_from_pod(rule, pod, cluster_id)
        except Exception as e:
            logger.error(f"Error evaluating pod restart rule: {e}")
    
    def _evaluate_pod_down_rule(self, rule: alert_model.AlertRule, cluster_id: int):
        """Evaluate pod down rule"""
        try:
            namespace = rule.namespace or None
            
            if namespace:
                pods = self.db.query(kubernetes_model.KubernetesPod).join(
                    kubernetes_model.KubernetesNamespace
                ).filter(
                    kubernetes_model.KubernetesPod.cluster_id == cluster_id,
                    kubernetes_model.KubernetesNamespace.name == namespace,
                    kubernetes_model.KubernetesPod.status.notin_(["Running"])
                ).all()
            else:
                pods = self.db.query(kubernetes_model.KubernetesPod).filter(
                    kubernetes_model.KubernetesPod.cluster_id == cluster_id,
                    kubernetes_model.KubernetesPod.status.notin_(["Running"])
                ).all()
            
            for pod in pods:
                self._create_alert_from_pod(rule, pod, cluster_id)
        except Exception as e:
            logger.error(f"Error evaluating pod down rule: {e}")
    
    def _evaluate_deployment_down_rule(self, rule: alert_model.AlertRule, cluster_id: int):
        """Evaluate deployment down rule"""
        try:
            namespace = rule.namespace or None
            
            if namespace:
                deployments = self.db.query(kubernetes_model.KubernetesDeployment).join(
                    kubernetes_model.KubernetesNamespace
                ).filter(
                    kubernetes_model.KubernetesDeployment.cluster_id == cluster_id,
                    kubernetes_model.KubernetesNamespace.name == namespace
                ).all()
            else:
                deployments = self.db.query(kubernetes_model.KubernetesDeployment).filter_by(
                    cluster_id=cluster_id
                ).all()
            
            for deployment in deployments:
                if deployment.ready_replicas == 0 or (deployment.ready_replicas or 0) < (deployment.replicas or 1):
                    self._create_alert_from_deployment(rule, deployment, cluster_id)
        except Exception as e:
            logger.error(f"Error evaluating deployment down rule: {e}")
    
    def _evaluate_disk_full_rule(self, rule: alert_model.AlertRule, cluster_id: int):
        """Evaluate disk full rule"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(seconds=rule.duration)
            metrics = self.db.query(kubernetes_model.KubernetesMetric).filter(
                kubernetes_model.KubernetesMetric.cluster_id == cluster_id,
                kubernetes_model.KubernetesMetric.metric_type == "node_disk",
                kubernetes_model.KubernetesMetric.timestamp >= cutoff_time
            ).all()
            
            for metric in metrics:
                value = float(metric.value)
                
                if self._check_threshold(value, rule.operator, rule.threshold):
                    self._create_alert(rule, metric, value, cluster_id)
        except Exception as e:
            logger.error(f"Error evaluating disk full rule: {e}")
    
    def _evaluate_oom_killed_rule(self, rule: alert_model.AlertRule, cluster_id: int):
        """Evaluate OOM killed rule"""
        try:
            namespace = rule.namespace or None
            
            if namespace:
                pods = self.db.query(kubernetes_model.KubernetesPod).join(
                    kubernetes_model.KubernetesNamespace
                ).filter(
                    kubernetes_model.KubernetesPod.cluster_id == cluster_id,
                    kubernetes_model.KubernetesNamespace.name == namespace,
                    kubernetes_model.KubernetesPod.oom_killed == True
                ).all()
            else:
                pods = self.db.query(kubernetes_model.KubernetesPod).filter(
                    kubernetes_model.KubernetesPod.cluster_id == cluster_id,
                    kubernetes_model.KubernetesPod.oom_killed == True
                ).all()
            
            for pod in pods:
                self._create_alert_from_pod(rule, pod, cluster_id)
        except Exception as e:
            logger.error(f"Error evaluating OOM killed rule: {e}")
    
    def _evaluate_image_pull_backoff_rule(self, rule: alert_model.AlertRule, cluster_id: int):
        """Evaluate ImagePullBackOff rule"""
        try:
            namespace = rule.namespace or None
            
            if namespace:
                pods = self.db.query(kubernetes_model.KubernetesPod).join(
                    kubernetes_model.KubernetesNamespace
                ).filter(
                    kubernetes_model.KubernetesPod.cluster_id == cluster_id,
                    kubernetes_model.KubernetesNamespace.name == namespace,
                    kubernetes_model.KubernetesPod.image_pull_errors == True
                ).all()
            else:
                pods = self.db.query(kubernetes_model.KubernetesPod).filter(
                    kubernetes_model.KubernetesPod.cluster_id == cluster_id,
                    kubernetes_model.KubernetesPod.image_pull_errors == True
                ).all()
            
            for pod in pods:
                self._create_alert_from_pod(rule, pod, cluster_id)
        except Exception as e:
            logger.error(f"Error evaluating ImagePullBackOff rule: {e}")
    
    def _evaluate_crash_loop_backoff_rule(self, rule: alert_model.AlertRule, cluster_id: int):
        """Evaluate CrashLoopBackOff rule"""
        try:
            namespace = rule.namespace or None
            
            if namespace:
                pods = self.db.query(kubernetes_model.KubernetesPod).join(
                    kubernetes_model.KubernetesNamespace
                ).filter(
                    kubernetes_model.KubernetesPod.cluster_id == cluster_id,
                    kubernetes_model.KubernetesNamespace.name == namespace,
                    kubernetes_model.KubernetesPod.crash_loop_backoff == True
                ).all()
            else:
                pods = self.db.query(kubernetes_model.KubernetesPod).filter(
                    kubernetes_model.KubernetesPod.cluster_id == cluster_id,
                    kubernetes_model.KubernetesPod.crash_loop_backoff == True
                ).all()
            
            for pod in pods:
                self._create_alert_from_pod(rule, pod, cluster_id)
        except Exception as e:
            logger.error(f"Error evaluating CrashLoopBackOff rule: {e}")
    
    def _check_threshold(self, value: float, operator: str, threshold: float) -> bool:
        """Check if value violates threshold"""
        if operator == ">":
            return value > threshold
        elif operator == "<":
            return value < threshold
        elif operator == ">=":
            return value >= threshold
        elif operator == "<=":
            return value <= threshold
        elif operator == "==":
            return value == threshold
        elif operator == "!=":
            return value != threshold
        return False
    
    def _create_alert(self, rule: alert_model.AlertRule, metric: kubernetes_model.KubernetesMetric, value: float, cluster_id: int):
        """Create alert for metric"""
        try:
            # Check if alert already exists (within last 5 minutes)
            cutoff_time = datetime.utcnow() - timedelta(minutes=5)
            existing_alert = self.db.query(alert_model.Alert).filter(
                alert_model.Alert.rule_id == rule.id,
                alert_model.Alert.status == "FIRING",
                alert_model.Alert.triggered_at >= cutoff_time
            ).first()
            
            if existing_alert:
                return  # Don't create duplicate alert
            
            alert = alert_model.Alert(
                rule_id=rule.id,
                title=f"Alert: {rule.name}",
                description=f"{rule.description or rule.name} - Value: {value:.2f}",
                value=value,
                severity=rule.severity,
                status="FIRING",
                pod_name=None,
                pod_namespace=metric.pod.namespace.name if metric.pod else None,
                node_name=metric.node.name if metric.node else None,
                triggered_at=datetime.utcnow()
            )
            self.db.add(alert)
            self.db.flush()
            
            # Create incident if enabled
            if rule.auto_create_incident:
                self._create_incident_from_alert(alert, cluster_id)
            
            self.db.commit()
            logger.info(f"Created alert for rule {rule.name}")
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
    
    def _create_alert_from_pod(self, rule: alert_model.AlertRule, pod: kubernetes_model.KubernetesPod, cluster_id: int):
        """Create alert for pod"""
        try:
            # Check if alert already exists
            cutoff_time = datetime.utcnow() - timedelta(minutes=5)
            existing_alert = self.db.query(alert_model.Alert).filter(
                alert_model.Alert.rule_id == rule.id,
                alert_model.Alert.pod_name == pod.name,
                alert_model.Alert.status == "FIRING",
                alert_model.Alert.triggered_at >= cutoff_time
            ).first()
            
            if existing_alert:
                return
            
            alert = alert_model.Alert(
                rule_id=rule.id,
                title=f"Alert: {rule.name}",
                description=f"{rule.description or rule.name} - Pod: {pod.name}",
                value=pod.restart_count if rule.rule_type == "pod_restart_count" else 0,
                severity=rule.severity,
                status="FIRING",
                pod_name=pod.name,
                pod_namespace=pod.namespace.name,
                triggered_at=datetime.utcnow()
            )
            self.db.add(alert)
            self.db.flush()
            
            if rule.auto_create_incident:
                self._create_incident_from_alert(alert, cluster_id)
            
            self.db.commit()
            logger.info(f"Created alert for pod {pod.name}")
        except Exception as e:
            logger.error(f"Error creating pod alert: {e}")
    
    def _create_alert_from_deployment(self, rule: alert_model.AlertRule, deployment: kubernetes_model.KubernetesDeployment, cluster_id: int):
        """Create alert for deployment"""
        try:
            # Check if alert already exists
            cutoff_time = datetime.utcnow() - timedelta(minutes=5)
            existing_alert = self.db.query(alert_model.Alert).filter(
                alert_model.Alert.rule_id == rule.id,
                alert_model.Alert.pod_name == deployment.name,
                alert_model.Alert.status == "FIRING",
                alert_model.Alert.triggered_at >= cutoff_time
            ).first()
            
            if existing_alert:
                return
            
            alert = alert_model.Alert(
                rule_id=rule.id,
                title=f"Alert: {rule.name}",
                description=f"{rule.description or rule.name} - Deployment: {deployment.name}",
                value=deployment.ready_replicas or 0,
                severity=rule.severity,
                status="FIRING",
                pod_name=deployment.name,
                pod_namespace=deployment.namespace.name,
                triggered_at=datetime.utcnow()
            )
            self.db.add(alert)
            self.db.flush()
            
            if rule.auto_create_incident:
                self._create_incident_from_alert(alert, cluster_id)
            
            self.db.commit()
            logger.info(f"Created alert for deployment {deployment.name}")
        except Exception as e:
            logger.error(f"Error creating deployment alert: {e}")
    
    def _create_incident_from_alert(self, alert: alert_model.Alert, cluster_id: int):
        """Create incident from alert"""
        try:
            incident = alert_model.Incident(
                alert_id=alert.id,
                title=alert.title,
                description=alert.description,
                status="OPEN",
                priority=self._get_priority_from_severity(alert.severity),
                severity=alert.severity,
                namespace=alert.pod_namespace,
                pod_name=alert.pod_name,
                created_at=datetime.utcnow()
            )
            self.db.add(incident)
            self.db.flush()
            
            # Generate AI analysis asynchronously or in background
            # For now, just create the incident
            
            logger.info(f"Created incident for alert {alert.id}")
        except Exception as e:
            logger.error(f"Error creating incident: {e}")
    
    @staticmethod
    def _get_priority_from_severity(severity: str) -> str:
        """Convert severity to priority"""
        severity_to_priority = {
            "CRITICAL": "CRITICAL",
            "HIGH": "HIGH",
            "MEDIUM": "MEDIUM",
            "LOW": "LOW"
        }
        return severity_to_priority.get(severity, "MEDIUM")
    
    def acknowledge_alert(self, alert_id: int, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""
        try:
            alert = self.db.query(alert_model.Alert).filter_by(id=alert_id).first()
            if not alert:
                return False
            
            alert.status = "ACKNOWLEDGED"
            alert.acknowledged_at = datetime.utcnow()
            alert.acknowledged_by = acknowledged_by
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Error acknowledging alert: {e}")
            return False
    
    def resolve_alert(self, alert_id: int) -> bool:
        """Resolve an alert"""
        try:
            alert = self.db.query(alert_model.Alert).filter_by(id=alert_id).first()
            if not alert:
                return False
            
            alert.status = "RESOLVED"
            alert.resolved_at = datetime.utcnow()
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Error resolving alert: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        self.db.close()
