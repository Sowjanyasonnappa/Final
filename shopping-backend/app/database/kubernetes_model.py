from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.database import Base


class KubernetesCluster(Base):
    """Store Kubernetes cluster information"""
    __tablename__ = "kubernetes_clusters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    context = Column(String(255), nullable=False)
    api_server = Column(String(255), nullable=False)
    ca_cert_path = Column(String(500), nullable=True)
    client_cert_path = Column(String(500), nullable=True)
    client_key_path = Column(String(500), nullable=True)
    status = Column(String(50), default="connected")  # connected, disconnected, error
    last_check = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    namespaces = relationship("KubernetesNamespace", back_populates="cluster", cascade="all, delete-orphan")
    nodes = relationship("KubernetesNode", back_populates="cluster", cascade="all, delete-orphan")
    pods = relationship("KubernetesPod", back_populates="cluster", cascade="all, delete-orphan")
    deployments = relationship("KubernetesDeployment", back_populates="cluster", cascade="all, delete-orphan")
    services = relationship("KubernetesService", back_populates="cluster", cascade="all, delete-orphan")
    metrics = relationship("KubernetesMetric", back_populates="cluster", cascade="all, delete-orphan")
    events = relationship("KubernetesEvent", back_populates="cluster", cascade="all, delete-orphan")


class KubernetesNamespace(Base):
    """Store Kubernetes namespaces"""
    __tablename__ = "kubernetes_namespaces"

    id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, ForeignKey("kubernetes_clusters.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cluster = relationship("KubernetesCluster", back_populates="namespaces")
    pods = relationship("KubernetesPod", back_populates="namespace", cascade="all, delete-orphan")
    deployments = relationship("KubernetesDeployment", back_populates="namespace", cascade="all, delete-orphan")


class KubernetesNode(Base):
    """Store Kubernetes node information"""
    __tablename__ = "kubernetes_nodes"

    id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, ForeignKey("kubernetes_clusters.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    status = Column(String(50), default="Ready")  # Ready, NotReady, Unknown
    role = Column(String(50), nullable=True)  # master, worker
    cpu_capacity = Column(String(50), nullable=True)
    memory_capacity = Column(String(50), nullable=True)
    disk_capacity = Column(String(50), nullable=True)
    container_runtime = Column(String(100), nullable=True)
    kernel_version = Column(String(100), nullable=True)
    os_image = Column(String(255), nullable=True)
    kubelet_version = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cluster = relationship("KubernetesCluster", back_populates="nodes")
    metrics = relationship("KubernetesMetric", back_populates="node", cascade="all, delete-orphan")


class KubernetesPod(Base):
    """Store Kubernetes pod information"""
    __tablename__ = "kubernetes_pods"

    id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, ForeignKey("kubernetes_clusters.id", ondelete="CASCADE"), nullable=False, index=True)
    namespace_id = Column(Integer, ForeignKey("kubernetes_namespaces.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    status = Column(String(50), default="Pending")  # Pending, Running, Succeeded, Failed, Unknown
    phase = Column(String(50), nullable=True)
    restart_count = Column(Integer, default=0)
    container_count = Column(Integer, default=1)
    ready_count = Column(Integer, default=0)
    image_pull_errors = Column(Boolean, default=False)
    crash_loop_backoff = Column(Boolean, default=False)
    oom_killed = Column(Boolean, default=False)
    node_name = Column(String(255), nullable=True)
    pod_ip = Column(String(20), nullable=True)
    uid = Column(String(100), nullable=True, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cluster = relationship("KubernetesCluster", back_populates="pods")
    namespace = relationship("KubernetesNamespace", back_populates="pods")
    containers = relationship("KubernetesContainer", back_populates="pod", cascade="all, delete-orphan")
    metrics = relationship("KubernetesMetric", back_populates="pod", cascade="all, delete-orphan")
    logs = relationship("KubernetesLog", back_populates="pod", cascade="all, delete-orphan")


class KubernetesContainer(Base):
    """Store Kubernetes container information"""
    __tablename__ = "kubernetes_containers"

    id = Column(Integer, primary_key=True, index=True)
    pod_id = Column(Integer, ForeignKey("kubernetes_pods.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    image = Column(String(255), nullable=False)
    image_pull_policy = Column(String(50), default="IfNotPresent")
    status = Column(String(50), default="Waiting")  # Waiting, Running, Terminated
    restart_count = Column(Integer, default=0)
    ready = Column(Boolean, default=False)
    started = Column(Boolean, default=False)
    cpu_request = Column(String(50), nullable=True)
    memory_request = Column(String(50), nullable=True)
    cpu_limit = Column(String(50), nullable=True)
    memory_limit = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    pod = relationship("KubernetesPod", back_populates="containers")


class KubernetesDeployment(Base):
    """Store Kubernetes deployment information"""
    __tablename__ = "kubernetes_deployments"

    id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, ForeignKey("kubernetes_clusters.id", ondelete="CASCADE"), nullable=False, index=True)
    namespace_id = Column(Integer, ForeignKey("kubernetes_namespaces.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    replicas = Column(Integer, default=1)
    ready_replicas = Column(Integer, default=0)
    updated_replicas = Column(Integer, default=0)
    available_replicas = Column(Integer, default=0)
    status = Column(String(50), default="Unknown")  # Progressing, Complete, Failed
    image = Column(String(255), nullable=True)
    strategy = Column(String(50), default="RollingUpdate")
    uid = Column(String(100), nullable=True, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cluster = relationship("KubernetesCluster", back_populates="deployments")
    namespace = relationship("KubernetesNamespace", back_populates="deployments")


class KubernetesService(Base):
    """Store Kubernetes service information"""
    __tablename__ = "kubernetes_services"

    id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, ForeignKey("kubernetes_clusters.id", ondelete="CASCADE"), nullable=False, index=True)
    namespace_id = Column(Integer, ForeignKey("kubernetes_namespaces.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    type = Column(String(50), default="ClusterIP")  # ClusterIP, NodePort, LoadBalancer, ExternalName
    cluster_ip = Column(String(20), nullable=True)
    external_ip = Column(String(255), nullable=True)
    port = Column(Integer, nullable=True)
    target_port = Column(Integer, nullable=True)
    protocol = Column(String(50), default="TCP")
    uid = Column(String(100), nullable=True, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cluster = relationship("KubernetesCluster", back_populates="services")


class KubernetesMetric(Base):
    """Store Kubernetes metrics (CPU, Memory, Disk usage)"""
    __tablename__ = "kubernetes_metrics"

    id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, ForeignKey("kubernetes_clusters.id", ondelete="CASCADE"), nullable=False, index=True)
    node_id = Column(Integer, ForeignKey("kubernetes_nodes.id", ondelete="CASCADE"), nullable=True, index=True)
    pod_id = Column(Integer, ForeignKey("kubernetes_pods.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Metric type: node_cpu, node_memory, pod_cpu, pod_memory, container_cpu, etc.
    metric_type = Column(String(50), nullable=False, index=True)
    metric_name = Column(String(255), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=True)  # m (millicores), Mi (mebibytes), etc.
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    cluster = relationship("KubernetesCluster", back_populates="metrics")
    node = relationship("KubernetesNode", back_populates="metrics")
    pod = relationship("KubernetesPod", back_populates="metrics")


class KubernetesEvent(Base):
    """Store Kubernetes cluster events"""
    __tablename__ = "kubernetes_events"

    id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, ForeignKey("kubernetes_clusters.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    namespace = Column(String(255), nullable=True)
    involved_object_kind = Column(String(100), nullable=True)  # Pod, Deployment, Node, etc.
    involved_object_name = Column(String(255), nullable=True)
    reason = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)
    event_type = Column(String(50), default="Normal")  # Normal, Warning
    first_timestamp = Column(DateTime, nullable=True)
    last_timestamp = Column(DateTime, nullable=True)
    count = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    cluster = relationship("KubernetesCluster", back_populates="events")


class KubernetesLog(Base):
    """Store Kubernetes logs"""
    __tablename__ = "kubernetes_logs"

    id = Column(Integer, primary_key=True, index=True)
    pod_id = Column(Integer, ForeignKey("kubernetes_pods.id", ondelete="CASCADE"), nullable=False, index=True)
    container_name = Column(String(255), nullable=False)
    namespace = Column(String(255), nullable=False)
    pod_name = Column(String(255), nullable=False)
    log_level = Column(String(50), default="INFO")  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    message = Column(Text, nullable=False)
    source = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    pod = relationship("KubernetesPod", back_populates="logs")
