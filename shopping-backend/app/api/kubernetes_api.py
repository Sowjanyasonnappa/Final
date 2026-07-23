"""
Kubernetes Monitoring API Routes
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database import kubernetes_model
from app.schemas import kubernetes_schema
from app.services.kubernetes_service import KubernetesService, KubernetesDataCollector
from app.auth.oauth2 import get_current_user
from app.utils.role_checker import admin_only

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/kubernetes", tags=["Kubernetes"])


@router.get("/clusters", response_model=List[kubernetes_schema.KubernetesClusterResponse])
async def get_clusters(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all registered Kubernetes clusters"""
    admin_only(current_user)
    
    clusters = db.query(kubernetes_model.KubernetesCluster).all()
    return clusters


@router.post("/clusters", response_model=kubernetes_schema.KubernetesClusterResponse)
async def create_cluster(
    cluster: kubernetes_schema.KubernetesClusterCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Register a new Kubernetes cluster"""
    admin_only(current_user)
    
    # Check if cluster already exists
    existing = db.query(kubernetes_model.KubernetesCluster).filter_by(name=cluster.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Cluster already registered")
    
    db_cluster = kubernetes_model.KubernetesCluster(**cluster.dict())
    db.add(db_cluster)
    db.commit()
    db.refresh(db_cluster)
    return db_cluster


@router.get("/clusters/{cluster_id}", response_model=kubernetes_schema.KubernetesClusterResponse)
async def get_cluster(
    cluster_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get cluster details"""
    admin_only(current_user)
    
    cluster = db.query(kubernetes_model.KubernetesCluster).filter_by(id=cluster_id).first()
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return cluster


@router.post("/clusters/{cluster_id}/sync")
async def sync_cluster(
    cluster_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Sync cluster data from Kubernetes"""
    admin_only(current_user)
    
    cluster = db.query(kubernetes_model.KubernetesCluster).filter_by(id=cluster_id).first()
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    try:
        k8s_service = KubernetesService(context=cluster.context)
        collector = KubernetesDataCollector(k8s_service)
        collector.sync_cluster_data(cluster.name)
        collector.close()
        
        return {"message": "Cluster data synced successfully"}
    except Exception as e:
        logger.error(f"Error syncing cluster: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Namespaces
@router.get("/clusters/{cluster_id}/namespaces", response_model=List[kubernetes_schema.KubernetesNamespaceResponse])
async def get_namespaces(
    cluster_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get namespaces in a cluster"""
    admin_only(current_user)
    
    namespaces = db.query(kubernetes_model.KubernetesNamespace).filter_by(cluster_id=cluster_id).all()
    return namespaces


# Nodes
@router.get("/clusters/{cluster_id}/nodes", response_model=List[kubernetes_schema.KubernetesNodeResponse])
async def get_nodes(
    cluster_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get nodes in a cluster"""
    admin_only(current_user)
    
    nodes = db.query(kubernetes_model.KubernetesNode).filter_by(cluster_id=cluster_id).all()
    return nodes


@router.get("/clusters/{cluster_id}/nodes/{node_id}", response_model=kubernetes_schema.KubernetesNodeResponse)
async def get_node(
    cluster_id: int,
    node_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get node details"""
    admin_only(current_user)
    
    node = db.query(kubernetes_model.KubernetesNode).filter(
        kubernetes_model.KubernetesNode.id == node_id,
        kubernetes_model.KubernetesNode.cluster_id == cluster_id
    ).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node


# Pods
@router.get("/clusters/{cluster_id}/pods", response_model=List[kubernetes_schema.KubernetesPodResponse])
async def get_pods(
    cluster_id: int,
    namespace: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get pods in a cluster"""
    admin_only(current_user)
    
    query = db.query(kubernetes_model.KubernetesPod).filter_by(cluster_id=cluster_id)
    
    if namespace:
        query = query.join(kubernetes_model.KubernetesNamespace).filter(
            kubernetes_model.KubernetesNamespace.name == namespace
        )
    
    if status:
        query = query.filter_by(status=status)
    
    pods = query.all()
    return pods


@router.get("/clusters/{cluster_id}/pods/{pod_id}", response_model=kubernetes_schema.KubernetesPodResponse)
async def get_pod(
    cluster_id: int,
    pod_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get pod details"""
    admin_only(current_user)
    
    pod = db.query(kubernetes_model.KubernetesPod).filter(
        kubernetes_model.KubernetesPod.id == pod_id,
        kubernetes_model.KubernetesPod.cluster_id == cluster_id
    ).first()
    if not pod:
        raise HTTPException(status_code=404, detail="Pod not found")
    return pod


@router.get("/clusters/{cluster_id}/pods/{pod_id}/logs", response_model=List[kubernetes_schema.KubernetesLogResponse])
async def get_pod_logs(
    cluster_id: int,
    pod_id: int,
    limit: int = Query(100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get logs for a pod"""
    admin_only(current_user)
    
    logs = db.query(kubernetes_model.KubernetesLog).filter_by(pod_id=pod_id).order_by(
        kubernetes_model.KubernetesLog.timestamp.desc()
    ).limit(limit).all()
    return logs


# Deployments
@router.get("/clusters/{cluster_id}/deployments", response_model=List[kubernetes_schema.KubernetesDeploymentResponse])
async def get_deployments(
    cluster_id: int,
    namespace: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get deployments in a cluster"""
    admin_only(current_user)
    
    query = db.query(kubernetes_model.KubernetesDeployment).filter_by(cluster_id=cluster_id)
    
    if namespace:
        query = query.join(kubernetes_model.KubernetesNamespace).filter(
            kubernetes_model.KubernetesNamespace.name == namespace
        )
    
    deployments = query.all()
    return deployments


@router.get("/clusters/{cluster_id}/deployments/{deployment_id}", response_model=kubernetes_schema.KubernetesDeploymentResponse)
async def get_deployment(
    cluster_id: int,
    deployment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get deployment details"""
    admin_only(current_user)
    
    deployment = db.query(kubernetes_model.KubernetesDeployment).filter(
        kubernetes_model.KubernetesDeployment.id == deployment_id,
        kubernetes_model.KubernetesDeployment.cluster_id == cluster_id
    ).first()
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return deployment


# Services
@router.get("/clusters/{cluster_id}/services", response_model=List[kubernetes_schema.KubernetesServiceResponse])
async def get_services(
    cluster_id: int,
    namespace: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get services in a cluster"""
    admin_only(current_user)
    
    query = db.query(kubernetes_model.KubernetesService).filter_by(cluster_id=cluster_id)
    
    if namespace:
        query = query.join(kubernetes_model.KubernetesNamespace).filter(
            kubernetes_model.KubernetesNamespace.name == namespace
        )
    
    services = query.all()
    return services


# Metrics
@router.get("/clusters/{cluster_id}/metrics", response_model=List[kubernetes_schema.KubernetesMetricResponse])
async def get_metrics(
    cluster_id: int,
    metric_type: Optional[str] = Query(None),
    limit: int = Query(100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get recent metrics for a cluster"""
    admin_only(current_user)
    
    query = db.query(kubernetes_model.KubernetesMetric).filter_by(cluster_id=cluster_id)
    
    if metric_type:
        query = query.filter_by(metric_type=metric_type)
    
    metrics = query.order_by(kubernetes_model.KubernetesMetric.timestamp.desc()).limit(limit).all()
    return metrics


@router.get("/clusters/{cluster_id}/nodes/{node_id}/metrics", response_model=List[kubernetes_schema.KubernetesMetricResponse])
async def get_node_metrics(
    cluster_id: int,
    node_id: int,
    limit: int = Query(100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get metrics for a node"""
    admin_only(current_user)
    
    metrics = db.query(kubernetes_model.KubernetesMetric).filter(
        kubernetes_model.KubernetesMetric.cluster_id == cluster_id,
        kubernetes_model.KubernetesMetric.node_id == node_id
    ).order_by(kubernetes_model.KubernetesMetric.timestamp.desc()).limit(limit).all()
    return metrics


@router.get("/clusters/{cluster_id}/pods/{pod_id}/metrics", response_model=List[kubernetes_schema.KubernetesMetricResponse])
async def get_pod_metrics(
    cluster_id: int,
    pod_id: int,
    limit: int = Query(100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get metrics for a pod"""
    admin_only(current_user)
    
    metrics = db.query(kubernetes_model.KubernetesMetric).filter(
        kubernetes_model.KubernetesMetric.cluster_id == cluster_id,
        kubernetes_model.KubernetesMetric.pod_id == pod_id
    ).order_by(kubernetes_model.KubernetesMetric.timestamp.desc()).limit(limit).all()
    return metrics


# Events
@router.get("/clusters/{cluster_id}/events", response_model=List[kubernetes_schema.KubernetesEventResponse])
async def get_events(
    cluster_id: int,
    limit: int = Query(100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get recent events in a cluster"""
    admin_only(current_user)
    
    events = db.query(kubernetes_model.KubernetesEvent).filter_by(cluster_id=cluster_id).order_by(
        kubernetes_model.KubernetesEvent.created_at.desc()
    ).limit(limit).all()
    return events


# Cluster Status
@router.get("/clusters/{cluster_id}/status", response_model=kubernetes_schema.ClusterStatusResponse)
async def get_cluster_status(
    cluster_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get cluster status summary"""
    admin_only(current_user)
    
    from datetime import datetime
    
    # Count nodes and pods
    total_nodes = db.query(kubernetes_model.KubernetesNode).filter_by(cluster_id=cluster_id).count()
    ready_nodes = db.query(kubernetes_model.KubernetesNode).filter(
        kubernetes_model.KubernetesNode.cluster_id == cluster_id,
        kubernetes_model.KubernetesNode.status == "Ready"
    ).count()
    
    total_pods = db.query(kubernetes_model.KubernetesPod).filter_by(cluster_id=cluster_id).count()
    running_pods = db.query(kubernetes_model.KubernetesPod).filter(
        kubernetes_model.KubernetesPod.cluster_id == cluster_id,
        kubernetes_model.KubernetesPod.status == "Running"
    ).count()
    
    return kubernetes_schema.ClusterStatusResponse(
        total_nodes=total_nodes,
        ready_nodes=ready_nodes,
        total_pods=total_pods,
        running_pods=running_pods,
        timestamp=datetime.utcnow()
    )
