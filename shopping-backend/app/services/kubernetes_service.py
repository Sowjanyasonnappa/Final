"""
Kubernetes Service - Interact with Kubernetes clusters and collect metrics/logs
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import asyncio
from kubernetes import client, config, watch
from kubernetes.stream import stream
from sqlalchemy.orm import Session

from app.database import kubernetes_model
from app.database.database import SessionLocal

logger = logging.getLogger(__name__)


class KubernetesService:
    """Service for interacting with Kubernetes clusters"""
    
    def __init__(self, kubeconfig_path: Optional[str] = None, context: Optional[str] = None):
        """Initialize Kubernetes client
        
        Args:
            kubeconfig_path: Path to kubeconfig file (uses default if None)
            context: Kubernetes context to use (uses current if None)
        """
        try:
            if kubeconfig_path:
                config.load_kube_config(config_file=kubeconfig_path, context=context)
            else:
                config.load_incluster_config()
        except Exception as e:
            logger.warning(f"Could not load in-cluster config, trying kubeconfig: {e}")
            try:
                config.load_kube_config(context=context)
            except Exception as e2:
                logger.error(f"Failed to load Kubernetes config: {e2}")
                raise
        
        self.v1_client = client.CoreV1Api()
        self.apps_client = client.AppsV1Api()
        self.batch_client = client.BatchV1Api()
        
    def get_namespaces(self) -> List[Dict[str, Any]]:
        """Get all namespaces in the cluster"""
        try:
            namespaces = self.v1_client.list_namespace()
            result = []
            for ns in namespaces.items:
                result.append({
                    "name": ns.metadata.name,
                    "status": ns.status.phase,
                    "created_at": ns.metadata.creation_timestamp,
                })
            return result
        except Exception as e:
            logger.error(f"Error getting namespaces: {e}")
            return []
    
    def get_nodes(self) -> List[Dict[str, Any]]:
        """Get all nodes in the cluster"""
        try:
            nodes = self.v1_client.list_node()
            result = []
            for node in nodes.items:
                status = "Ready"
                for condition in node.status.conditions or []:
                    if condition.type == "Ready":
                        status = condition.status
                
                result.append({
                    "name": node.metadata.name,
                    "status": status,
                    "role": node.metadata.labels.get("node-role.kubernetes.io/master", "worker"),
                    "cpu_capacity": node.status.capacity.get("cpu"),
                    "memory_capacity": node.status.capacity.get("memory"),
                    "disk_capacity": node.status.capacity.get("ephemeral-storage"),
                    "container_runtime": node.status.node_info.container_runtime_version,
                    "kernel_version": node.status.node_info.kernel_version,
                    "os_image": node.status.node_info.os_image,
                    "kubelet_version": node.status.node_info.kubelet_version,
                    "created_at": node.metadata.creation_timestamp,
                })
            return result
        except Exception as e:
            logger.error(f"Error getting nodes: {e}")
            return []
    
    def get_pods(self, namespace: str = "default") -> List[Dict[str, Any]]:
        """Get all pods in a namespace"""
        try:
            pods = self.v1_client.list_namespaced_pod(namespace)
            result = []
            for pod in pods.items:
                restart_count = 0
                ready_count = 0
                total_containers = len(pod.spec.containers)
                
                for container_status in pod.status.container_statuses or []:
                    restart_count += container_status.restart_count
                    if container_status.ready:
                        ready_count += 1
                
                result.append({
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "status": pod.status.phase,
                    "restart_count": restart_count,
                    "ready_count": ready_count,
                    "container_count": total_containers,
                    "node_name": pod.spec.node_name,
                    "pod_ip": pod.status.pod_ip,
                    "uid": pod.metadata.uid,
                    "created_at": pod.metadata.creation_timestamp,
                })
            return result
        except Exception as e:
            logger.error(f"Error getting pods in {namespace}: {e}")
            return []
    
    def get_pods_all_namespaces(self) -> List[Dict[str, Any]]:
        """Get all pods across all namespaces"""
        try:
            pods = self.v1_client.list_pod_for_all_namespaces()
            result = []
            for pod in pods.items:
                restart_count = 0
                ready_count = 0
                total_containers = len(pod.spec.containers)
                
                for container_status in pod.status.container_statuses or []:
                    restart_count += container_status.restart_count
                    if container_status.ready:
                        ready_count += 1
                
                result.append({
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "status": pod.status.phase,
                    "restart_count": restart_count,
                    "ready_count": ready_count,
                    "container_count": total_containers,
                    "node_name": pod.spec.node_name,
                    "pod_ip": pod.status.pod_ip,
                    "uid": pod.metadata.uid,
                    "created_at": pod.metadata.creation_timestamp,
                })
            return result
        except Exception as e:
            logger.error(f"Error getting pods from all namespaces: {e}")
            return []
    
    def get_deployments(self, namespace: str = "default") -> List[Dict[str, Any]]:
        """Get all deployments in a namespace"""
        try:
            deployments = self.apps_client.list_namespaced_deployment(namespace)
            result = []
            for dep in deployments.items:
                result.append({
                    "name": dep.metadata.name,
                    "namespace": dep.metadata.namespace,
                    "replicas": dep.spec.replicas,
                    "ready_replicas": dep.status.ready_replicas or 0,
                    "updated_replicas": dep.status.updated_replicas or 0,
                    "available_replicas": dep.status.available_replicas or 0,
                    "status": dep.status.conditions[-1].reason if dep.status.conditions else "Unknown",
                    "image": dep.spec.template.spec.containers[0].image if dep.spec.template.spec.containers else None,
                    "uid": dep.metadata.uid,
                    "created_at": dep.metadata.creation_timestamp,
                })
            return result
        except Exception as e:
            logger.error(f"Error getting deployments in {namespace}: {e}")
            return []
    
    def get_deployments_all_namespaces(self) -> List[Dict[str, Any]]:
        """Get all deployments across all namespaces"""
        try:
            deployments = self.apps_client.list_deployment_for_all_namespaces()
            result = []
            for dep in deployments.items:
                result.append({
                    "name": dep.metadata.name,
                    "namespace": dep.metadata.namespace,
                    "replicas": dep.spec.replicas,
                    "ready_replicas": dep.status.ready_replicas or 0,
                    "updated_replicas": dep.status.updated_replicas or 0,
                    "available_replicas": dep.status.available_replicas or 0,
                    "status": dep.status.conditions[-1].reason if dep.status.conditions else "Unknown",
                    "image": dep.spec.template.spec.containers[0].image if dep.spec.template.spec.containers else None,
                    "uid": dep.metadata.uid,
                    "created_at": dep.metadata.creation_timestamp,
                })
            return result
        except Exception as e:
            logger.error(f"Error getting deployments from all namespaces: {e}")
            return []
    
    def get_services(self, namespace: str = "default") -> List[Dict[str, Any]]:
        """Get all services in a namespace"""
        try:
            services = self.v1_client.list_namespaced_service(namespace)
            result = []
            for svc in services.items:
                result.append({
                    "name": svc.metadata.name,
                    "namespace": svc.metadata.namespace,
                    "type": svc.spec.type,
                    "cluster_ip": svc.spec.cluster_ip,
                    "external_ip": svc.status.load_balancer.ingress[0].ip if svc.status.load_balancer and svc.status.load_balancer.ingress else None,
                    "port": svc.spec.ports[0].port if svc.spec.ports else None,
                    "target_port": svc.spec.ports[0].target_port if svc.spec.ports else None,
                    "protocol": svc.spec.ports[0].protocol if svc.spec.ports else "TCP",
                    "uid": svc.metadata.uid,
                    "created_at": svc.metadata.creation_timestamp,
                })
            return result
        except Exception as e:
            logger.error(f"Error getting services in {namespace}: {e}")
            return []
    
    def get_pod_logs(self, namespace: str, pod_name: str, container_name: Optional[str] = None, lines: int = 100) -> str:
        """Get logs from a pod"""
        try:
            if container_name:
                logs = self.v1_client.read_namespaced_pod_log(
                    name=pod_name,
                    namespace=namespace,
                    container=container_name,
                    tail_lines=lines
                )
            else:
                logs = self.v1_client.read_namespaced_pod_log(
                    name=pod_name,
                    namespace=namespace,
                    tail_lines=lines
                )
            return logs
        except Exception as e:
            logger.error(f"Error getting logs for {namespace}/{pod_name}: {e}")
            return ""
    
    def stream_pod_logs(self, namespace: str, pod_name: str, container_name: Optional[str] = None):
        """Stream logs from a pod in real-time"""
        try:
            if container_name:
                return stream(
                    self.v1_client.connect_get_namespaced_pod_exec,
                    pod_name, namespace,
                    command=["tail", "-f", "/dev/stdout"],
                    stderr=True, stdin=False,
                    stdout=True, tty=False,
                    container=container_name
                )
            else:
                return stream(
                    self.v1_client.connect_get_namespaced_pod_exec,
                    pod_name, namespace,
                    command=["tail", "-f", "/dev/stdout"],
                    stderr=True, stdin=False,
                    stdout=True, tty=False
                )
        except Exception as e:
            logger.error(f"Error streaming logs for {namespace}/{pod_name}: {e}")
            return None
    
    def exec_command_in_pod(self, namespace: str, pod_name: str, command: List[str], container_name: Optional[str] = None) -> str:
        """Execute a command inside a pod"""
        try:
            if container_name:
                exec_command = [
                    "/bin/sh", "-c",
                    " ".join(command)
                ]
                resp = stream(
                    self.v1_client.connect_get_namespaced_pod_exec,
                    pod_name, namespace,
                    command=exec_command,
                    stderr=True, stdin=False,
                    stdout=True, tty=False,
                    container=container_name
                )
            else:
                exec_command = [
                    "/bin/sh", "-c",
                    " ".join(command)
                ]
                resp = stream(
                    self.v1_client.connect_get_namespaced_pod_exec,
                    pod_name, namespace,
                    command=exec_command,
                    stderr=True, stdin=False,
                    stdout=True, tty=False
                )
            return resp
        except Exception as e:
            logger.error(f"Error executing command in {namespace}/{pod_name}: {e}")
            return ""
    
    def get_events(self, namespace: str = None) -> List[Dict[str, Any]]:
        """Get events from the cluster"""
        try:
            if namespace:
                events = self.v1_client.list_namespaced_event(namespace)
            else:
                events = self.v1_client.list_event_for_all_namespaces()
            
            result = []
            for event in events.items:
                result.append({
                    "name": event.metadata.name,
                    "namespace": event.metadata.namespace,
                    "involved_object_kind": event.involved_object.kind,
                    "involved_object_name": event.involved_object.name,
                    "reason": event.reason,
                    "message": event.message,
                    "type": event.type,
                    "first_timestamp": event.first_timestamp,
                    "last_timestamp": event.last_timestamp,
                    "count": event.count,
                })
            return result
        except Exception as e:
            logger.error(f"Error getting events: {e}")
            return []
    
    def get_resource_status(self) -> Dict[str, Any]:
        """Get overall cluster status"""
        try:
            nodes = self.v1_client.list_node()
            pods = self.v1_client.list_pod_for_all_namespaces()
            
            ready_nodes = sum(1 for node in nodes.items if any(
                condition.type == "Ready" and condition.status == "True" 
                for condition in node.status.conditions or []
            ))
            
            ready_pods = sum(1 for pod in pods.items if pod.status.phase == "Running")
            
            return {
                "total_nodes": len(nodes.items),
                "ready_nodes": ready_nodes,
                "total_pods": len(pods.items),
                "running_pods": ready_pods,
                "timestamp": datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Error getting cluster status: {e}")
            return {}


class KubernetesDataCollector:
    """Collect and store Kubernetes data in database"""
    
    def __init__(self, k8s_service: KubernetesService):
        self.k8s_service = k8s_service
        self.db: Session = SessionLocal()
    
    def sync_cluster_data(self, cluster_name: str):
        """Sync cluster data to database"""
        try:
            # Get or create cluster
            cluster = self.db.query(kubernetes_model.KubernetesCluster).filter_by(name=cluster_name).first()
            if not cluster:
                cluster = kubernetes_model.KubernetesCluster(
                    name=cluster_name,
                    context=cluster_name,
                    api_server="http://localhost:6443",
                    status="connected"
                )
                self.db.add(cluster)
                self.db.commit()
            
            # Sync namespaces
            self._sync_namespaces(cluster)
            
            # Sync nodes
            self._sync_nodes(cluster)
            
            # Sync pods
            self._sync_pods(cluster)
            
            # Sync deployments
            self._sync_deployments(cluster)
            
            # Sync services
            self._sync_services(cluster)
            
            # Update cluster status
            cluster.last_check = datetime.utcnow()
            cluster.status = "connected"
            self.db.commit()
            
            logger.info(f"Successfully synced cluster data for {cluster_name}")
        except Exception as e:
            logger.error(f"Error syncing cluster data: {e}")
            self.db.rollback()
    
    def _sync_namespaces(self, cluster: kubernetes_model.KubernetesCluster):
        """Sync namespaces to database"""
        try:
            namespaces = self.k8s_service.get_namespaces()
            for ns_data in namespaces:
                ns = self.db.query(kubernetes_model.KubernetesNamespace).filter_by(
                    cluster_id=cluster.id,
                    name=ns_data["name"]
                ).first()
                if not ns:
                    ns = kubernetes_model.KubernetesNamespace(
                        cluster_id=cluster.id,
                        name=ns_data["name"],
                        status=ns_data["status"]
                    )
                    self.db.add(ns)
                else:
                    ns.status = ns_data["status"]
            
            self.db.commit()
        except Exception as e:
            logger.error(f"Error syncing namespaces: {e}")
    
    def _sync_nodes(self, cluster: kubernetes_model.KubernetesCluster):
        """Sync nodes to database"""
        try:
            nodes = self.k8s_service.get_nodes()
            for node_data in nodes:
                node = self.db.query(kubernetes_model.KubernetesNode).filter_by(
                    cluster_id=cluster.id,
                    name=node_data["name"]
                ).first()
                if not node:
                    node = kubernetes_model.KubernetesNode(
                        cluster_id=cluster.id,
                        **node_data
                    )
                    self.db.add(node)
                else:
                    for key, value in node_data.items():
                        if key != "created_at":
                            setattr(node, key, value)
            
            self.db.commit()
        except Exception as e:
            logger.error(f"Error syncing nodes: {e}")
    
    def _sync_pods(self, cluster: kubernetes_model.KubernetesCluster):
        """Sync pods to database"""
        try:
            pods = self.k8s_service.get_pods_all_namespaces()
            for pod_data in pods:
                # Get namespace
                ns = self.db.query(kubernetes_model.KubernetesNamespace).filter_by(
                    cluster_id=cluster.id,
                    name=pod_data["namespace"]
                ).first()
                if not ns:
                    continue
                
                pod = self.db.query(kubernetes_model.KubernetesPod).filter_by(
                    cluster_id=cluster.id,
                    namespace_id=ns.id,
                    name=pod_data["name"]
                ).first()
                
                if not pod:
                    pod = kubernetes_model.KubernetesPod(
                        cluster_id=cluster.id,
                        namespace_id=ns.id,
                        **pod_data
                    )
                    self.db.add(pod)
                else:
                    for key, value in pod_data.items():
                        if key not in ["created_at", "namespace"]:
                            setattr(pod, key, value)
            
            self.db.commit()
        except Exception as e:
            logger.error(f"Error syncing pods: {e}")
    
    def _sync_deployments(self, cluster: kubernetes_model.KubernetesCluster):
        """Sync deployments to database"""
        try:
            deployments = self.k8s_service.get_deployments_all_namespaces()
            for dep_data in deployments:
                # Get namespace
                ns = self.db.query(kubernetes_model.KubernetesNamespace).filter_by(
                    cluster_id=cluster.id,
                    name=dep_data["namespace"]
                ).first()
                if not ns:
                    continue
                
                dep = self.db.query(kubernetes_model.KubernetesDeployment).filter_by(
                    cluster_id=cluster.id,
                    namespace_id=ns.id,
                    name=dep_data["name"]
                ).first()
                
                if not dep:
                    dep = kubernetes_model.KubernetesDeployment(
                        cluster_id=cluster.id,
                        namespace_id=ns.id,
                        **dep_data
                    )
                    self.db.add(dep)
                else:
                    for key, value in dep_data.items():
                        if key not in ["created_at", "namespace"]:
                            setattr(dep, key, value)
            
            self.db.commit()
        except Exception as e:
            logger.error(f"Error syncing deployments: {e}")
    
    def _sync_services(self, cluster: kubernetes_model.KubernetesCluster):
        """Sync services to database"""
        try:
            namespaces = self.k8s_service.get_namespaces()
            for ns_data in namespaces:
                services = self.k8s_service.get_services(ns_data["name"])
                ns = self.db.query(kubernetes_model.KubernetesNamespace).filter_by(
                    cluster_id=cluster.id,
                    name=ns_data["name"]
                ).first()
                if not ns:
                    continue
                
                for svc_data in services:
                    svc = self.db.query(kubernetes_model.KubernetesService).filter_by(
                        cluster_id=cluster.id,
                        namespace_id=ns.id,
                        name=svc_data["name"]
                    ).first()
                    
                    if not svc:
                        svc = kubernetes_model.KubernetesService(
                            cluster_id=cluster.id,
                            namespace_id=ns.id,
                            **svc_data
                        )
                        self.db.add(svc)
                    else:
                        for key, value in svc_data.items():
                            if key not in ["created_at", "namespace"]:
                                setattr(svc, key, value)
            
            self.db.commit()
        except Exception as e:
            logger.error(f"Error syncing services: {e}")
    
    def close(self):
        """Close database connection"""
        self.db.close()
