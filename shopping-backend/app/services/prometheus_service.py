"""
Prometheus Service - Query metrics from Prometheus
"""
import logging
import requests
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.database import kubernetes_model
from app.database.database import SessionLocal

logger = logging.getLogger(__name__)


class PrometheusService:
    """Service for querying Prometheus metrics"""
    
    def __init__(self, prometheus_url: str = "http://localhost:9090"):
        """Initialize Prometheus client
        
        Args:
            prometheus_url: URL of Prometheus server
        """
        self.prometheus_url = prometheus_url.rstrip('/')
        self.session = requests.Session()
    
    def query_instant(self, query: str) -> Dict[str, Any]:
        """Execute an instant query"""
        try:
            response = self.session.get(
                f"{self.prometheus_url}/api/v1/query",
                params={"query": query},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error querying Prometheus (instant): {e}")
            return {"status": "error", "data": []}
    
    def query_range(self, query: str, start: datetime, end: datetime, step: str = "15s") -> Dict[str, Any]:
        """Execute a range query"""
        try:
            response = self.session.get(
                f"{self.prometheus_url}/api/v1/query_range",
                params={
                    "query": query,
                    "start": int(start.timestamp()),
                    "end": int(end.timestamp()),
                    "step": step
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error querying Prometheus (range): {e}")
            return {"status": "error", "data": []}
    
    def get_node_cpu(self, node_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get CPU usage for nodes"""
        try:
            if node_name:
                query = f'node_cpu_seconds_total{{node="{node_name}"}}'
            else:
                query = 'node_cpu_seconds_total'
            
            result = self.query_instant(query)
            metrics = []
            
            if result.get("data", {}).get("result"):
                for item in result["data"]["result"]:
                    metrics.append({
                        "node": item["metric"].get("node"),
                        "value": float(item["value"][1]),
                        "timestamp": datetime.fromtimestamp(int(item["value"][0]))
                    })
            
            return metrics
        except Exception as e:
            logger.error(f"Error getting node CPU: {e}")
            return []
    
    def get_node_memory(self, node_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get memory usage for nodes"""
        try:
            if node_name:
                query = f'node_memory_MemAvailable_bytes{{node="{node_name}"}}'
            else:
                query = 'node_memory_MemAvailable_bytes'
            
            result = self.query_instant(query)
            metrics = []
            
            if result.get("data", {}).get("result"):
                for item in result["data"]["result"]:
                    metrics.append({
                        "node": item["metric"].get("node"),
                        "value": float(item["value"][1]),
                        "timestamp": datetime.fromtimestamp(int(item["value"][0]))
                    })
            
            return metrics
        except Exception as e:
            logger.error(f"Error getting node memory: {e}")
            return []
    
    def get_pod_cpu(self, namespace: Optional[str] = None, pod_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get CPU usage for pods"""
        try:
            if namespace and pod_name:
                query = f'container_cpu_usage_seconds_total{{namespace="{namespace}", pod="{pod_name}"}}'
            elif namespace:
                query = f'container_cpu_usage_seconds_total{{namespace="{namespace}"}}'
            else:
                query = 'container_cpu_usage_seconds_total'
            
            result = self.query_instant(query)
            metrics = []
            
            if result.get("data", {}).get("result"):
                for item in result["data"]["result"]:
                    metrics.append({
                        "pod": item["metric"].get("pod"),
                        "namespace": item["metric"].get("namespace"),
                        "container": item["metric"].get("container"),
                        "value": float(item["value"][1]),
                        "timestamp": datetime.fromtimestamp(int(item["value"][0]))
                    })
            
            return metrics
        except Exception as e:
            logger.error(f"Error getting pod CPU: {e}")
            return []
    
    def get_pod_memory(self, namespace: Optional[str] = None, pod_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get memory usage for pods"""
        try:
            if namespace and pod_name:
                query = f'container_memory_usage_bytes{{namespace="{namespace}", pod="{pod_name}"}}'
            elif namespace:
                query = f'container_memory_usage_bytes{{namespace="{namespace}"}}'
            else:
                query = 'container_memory_usage_bytes'
            
            result = self.query_instant(query)
            metrics = []
            
            if result.get("data", {}).get("result"):
                for item in result["data"]["result"]:
                    metrics.append({
                        "pod": item["metric"].get("pod"),
                        "namespace": item["metric"].get("namespace"),
                        "container": item["metric"].get("container"),
                        "value": float(item["value"][1]),
                        "timestamp": datetime.fromtimestamp(int(item["value"][0]))
                    })
            
            return metrics
        except Exception as e:
            logger.error(f"Error getting pod memory: {e}")
            return []
    
    def get_pod_restart_count(self, namespace: Optional[str] = None, pod_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get pod restart counts"""
        try:
            if namespace and pod_name:
                query = f'kube_pod_container_status_restarts_total{{namespace="{namespace}", pod="{pod_name}"}}'
            elif namespace:
                query = f'kube_pod_container_status_restarts_total{{namespace="{namespace}"}}'
            else:
                query = 'kube_pod_container_status_restarts_total'
            
            result = self.query_instant(query)
            metrics = []
            
            if result.get("data", {}).get("result"):
                for item in result["data"]["result"]:
                    metrics.append({
                        "pod": item["metric"].get("pod"),
                        "namespace": item["metric"].get("namespace"),
                        "container": item["metric"].get("container"),
                        "value": int(float(item["value"][1])),
                        "timestamp": datetime.fromtimestamp(int(item["value"][0]))
                    })
            
            return metrics
        except Exception as e:
            logger.error(f"Error getting pod restart counts: {e}")
            return []
    
    def get_pod_status(self, namespace: Optional[str] = None, pod_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get pod status"""
        try:
            if namespace and pod_name:
                query = f'kube_pod_status_phase{{namespace="{namespace}", pod="{pod_name}"}}'
            elif namespace:
                query = f'kube_pod_status_phase{{namespace="{namespace}"}}'
            else:
                query = 'kube_pod_status_phase'
            
            result = self.query_instant(query)
            metrics = []
            
            if result.get("data", {}).get("result"):
                for item in result["data"]["result"]:
                    phase_value = item["value"][1]
                    phase_name = item["metric"].get("phase", "Unknown")
                    
                    if phase_value == "1":  # Status is running
                        metrics.append({
                            "pod": item["metric"].get("pod"),
                            "namespace": item["metric"].get("namespace"),
                            "phase": phase_name,
                            "timestamp": datetime.fromtimestamp(int(item["value"][0]))
                        })
            
            return metrics
        except Exception as e:
            logger.error(f"Error getting pod status: {e}")
            return []
    
    def get_deployment_status(self, namespace: Optional[str] = None, deployment_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get deployment status"""
        try:
            if namespace and deployment_name:
                query = f'kube_deployment_status_replicas_available{{namespace="{namespace}", deployment="{deployment_name}"}}'
            elif namespace:
                query = f'kube_deployment_status_replicas_available{{namespace="{namespace}"}}'
            else:
                query = 'kube_deployment_status_replicas_available'
            
            result = self.query_instant(query)
            metrics = []
            
            if result.get("data", {}).get("result"):
                for item in result["data"]["result"]:
                    metrics.append({
                        "deployment": item["metric"].get("deployment"),
                        "namespace": item["metric"].get("namespace"),
                        "available_replicas": int(float(item["value"][1])),
                        "timestamp": datetime.fromtimestamp(int(item["value"][0]))
                    })
            
            return metrics
        except Exception as e:
            logger.error(f"Error getting deployment status: {e}")
            return []
    
    def get_node_disk_usage(self, node_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get disk usage for nodes"""
        try:
            if node_name:
                query = f'node_filesystem_avail_bytes{{node="{node_name}", device!~"tmpfs"}}'
            else:
                query = 'node_filesystem_avail_bytes{device!~"tmpfs"}'
            
            result = self.query_instant(query)
            metrics = []
            
            if result.get("data", {}).get("result"):
                for item in result["data"]["result"]:
                    metrics.append({
                        "node": item["metric"].get("node"),
                        "device": item["metric"].get("device"),
                        "value": float(item["value"][1]),
                        "timestamp": datetime.fromtimestamp(int(item["value"][0]))
                    })
            
            return metrics
        except Exception as e:
            logger.error(f"Error getting node disk usage: {e}")
            return []
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get current alerts from Alertmanager"""
        try:
            response = self.session.get(
                f"{self.prometheus_url}/api/v1/alerts",
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            
            alerts = []
            if result.get("data", {}).get("alerts"):
                for alert in result["data"]["alerts"]:
                    alerts.append({
                        "name": alert["labels"].get("alertname"),
                        "instance": alert["labels"].get("instance"),
                        "severity": alert["labels"].get("severity", "unknown"),
                        "state": alert["state"],
                        "timestamp": alert.get("activeAt")
                    })
            
            return alerts
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            return []


class MetricsCollector:
    """Collect and store metrics in database"""
    
    def __init__(self, prometheus_service: PrometheusService):
        self.prometheus_service = prometheus_service
        self.db: Session = SessionLocal()
    
    def collect_cluster_metrics(self, cluster_id: int):
        """Collect all metrics for a cluster"""
        try:
            # Collect node metrics
            self._collect_node_metrics(cluster_id)
            
            # Collect pod metrics
            self._collect_pod_metrics(cluster_id)
            
            # Collect deployment metrics
            self._collect_deployment_metrics(cluster_id)
            
            logger.info(f"Successfully collected metrics for cluster {cluster_id}")
        except Exception as e:
            logger.error(f"Error collecting cluster metrics: {e}")
            self.db.rollback()
    
    def _collect_node_metrics(self, cluster_id: int):
        """Collect node metrics"""
        try:
            nodes = self.db.query(kubernetes_model.KubernetesNode).filter_by(cluster_id=cluster_id).all()
            
            for node in nodes:
                # CPU
                cpu_metrics = self.prometheus_service.get_node_cpu(node.name)
                for metric in cpu_metrics:
                    db_metric = kubernetes_model.KubernetesMetric(
                        cluster_id=cluster_id,
                        node_id=node.id,
                        metric_type="node_cpu",
                        metric_name="cpu_usage",
                        value=metric["value"],
                        unit="cores",
                        timestamp=metric["timestamp"]
                    )
                    self.db.add(db_metric)
                
                # Memory
                memory_metrics = self.prometheus_service.get_node_memory(node.name)
                for metric in memory_metrics:
                    db_metric = kubernetes_model.KubernetesMetric(
                        cluster_id=cluster_id,
                        node_id=node.id,
                        metric_type="node_memory",
                        metric_name="memory_available",
                        value=metric["value"],
                        unit="bytes",
                        timestamp=metric["timestamp"]
                    )
                    self.db.add(db_metric)
                
                # Disk
                disk_metrics = self.prometheus_service.get_node_disk_usage(node.name)
                for metric in disk_metrics:
                    db_metric = kubernetes_model.KubernetesMetric(
                        cluster_id=cluster_id,
                        node_id=node.id,
                        metric_type="node_disk",
                        metric_name="disk_available",
                        value=metric["value"],
                        unit="bytes",
                        timestamp=metric["timestamp"]
                    )
                    self.db.add(db_metric)
            
            self.db.commit()
        except Exception as e:
            logger.error(f"Error collecting node metrics: {e}")
            self.db.rollback()
    
    def _collect_pod_metrics(self, cluster_id: int):
        """Collect pod metrics"""
        try:
            pods = self.db.query(kubernetes_model.KubernetesPod).filter_by(cluster_id=cluster_id).all()
            
            for pod in pods:
                # CPU
                cpu_metrics = self.prometheus_service.get_pod_cpu(pod.namespace.name, pod.name)
                for metric in cpu_metrics:
                    db_metric = kubernetes_model.KubernetesMetric(
                        cluster_id=cluster_id,
                        pod_id=pod.id,
                        metric_type="pod_cpu",
                        metric_name="cpu_usage",
                        value=metric["value"],
                        unit="cores",
                        timestamp=metric["timestamp"]
                    )
                    self.db.add(db_metric)
                
                # Memory
                memory_metrics = self.prometheus_service.get_pod_memory(pod.namespace.name, pod.name)
                for metric in memory_metrics:
                    db_metric = kubernetes_model.KubernetesMetric(
                        cluster_id=cluster_id,
                        pod_id=pod.id,
                        metric_type="pod_memory",
                        metric_name="memory_usage",
                        value=metric["value"],
                        unit="bytes",
                        timestamp=metric["timestamp"]
                    )
                    self.db.add(db_metric)
            
            self.db.commit()
        except Exception as e:
            logger.error(f"Error collecting pod metrics: {e}")
            self.db.rollback()
    
    def _collect_deployment_metrics(self, cluster_id: int):
        """Collect deployment metrics"""
        try:
            deployments = self.db.query(kubernetes_model.KubernetesDeployment).filter_by(cluster_id=cluster_id).all()
            
            for deployment in deployments:
                status_metrics = self.prometheus_service.get_deployment_status(deployment.namespace.name, deployment.name)
                for metric in status_metrics:
                    # Check if ready_replicas == desired replicas
                    if metric["available_replicas"] < deployment.replicas:
                        db_metric = kubernetes_model.KubernetesMetric(
                            cluster_id=cluster_id,
                            metric_type="deployment_status",
                            metric_name="available_replicas",
                            value=metric["available_replicas"],
                            unit="count",
                            timestamp=metric["timestamp"]
                        )
                        self.db.add(db_metric)
            
            self.db.commit()
        except Exception as e:
            logger.error(f"Error collecting deployment metrics: {e}")
            self.db.rollback()
    
    def close(self):
        """Close database connection"""
        self.db.close()
