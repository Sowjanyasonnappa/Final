"""
Kubernetes and Monitoring Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Kubernetes Cluster Schemas
class KubernetesClusterBase(BaseModel):
    name: str = Field(..., description="Cluster name")
    context: str = Field(..., description="Kubernetes context")
    api_server: str = Field(..., description="API server URL")


class KubernetesClusterCreate(KubernetesClusterBase):
    ca_cert_path: Optional[str] = None
    client_cert_path: Optional[str] = None
    client_key_path: Optional[str] = None


class KubernetesClusterResponse(KubernetesClusterBase):
    id: int
    status: str
    last_check: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# Kubernetes Namespace Schemas
class KubernetesNamespaceResponse(BaseModel):
    id: int
    name: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# Kubernetes Node Schemas
class KubernetesNodeResponse(BaseModel):
    id: int
    name: str
    status: str
    role: Optional[str] = None
    cpu_capacity: Optional[str] = None
    memory_capacity: Optional[str] = None
    disk_capacity: Optional[str] = None
    container_runtime: Optional[str] = None
    kernel_version: Optional[str] = None
    os_image: Optional[str] = None
    kubelet_version: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Kubernetes Pod Schemas
class KubernetesPodResponse(BaseModel):
    id: int
    name: str
    namespace: str
    status: str
    restart_count: int = 0
    ready_count: int = 0
    container_count: int = 0
    image_pull_errors: bool = False
    crash_loop_backoff: bool = False
    oom_killed: bool = False
    node_name: Optional[str] = None
    pod_ip: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Kubernetes Deployment Schemas
class KubernetesDeploymentResponse(BaseModel):
    id: int
    name: str
    namespace: str
    replicas: int
    ready_replicas: int
    updated_replicas: int
    available_replicas: int
    status: str
    image: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Kubernetes Service Schemas
class KubernetesServiceResponse(BaseModel):
    id: int
    name: str
    namespace: str
    type: str
    cluster_ip: Optional[str] = None
    external_ip: Optional[str] = None
    port: Optional[int] = None
    target_port: Optional[int] = None
    protocol: str = "TCP"
    created_at: datetime

    class Config:
        from_attributes = True


# Kubernetes Metrics Schemas
class KubernetesMetricResponse(BaseModel):
    id: int
    metric_type: str
    metric_name: str
    value: float
    unit: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


# Kubernetes Events Schemas
class KubernetesEventResponse(BaseModel):
    id: int
    name: str
    namespace: Optional[str] = None
    involved_object_kind: Optional[str] = None
    involved_object_name: Optional[str] = None
    reason: str
    message: Optional[str] = None
    event_type: str
    first_timestamp: Optional[datetime] = None
    last_timestamp: Optional[datetime] = None
    count: int

    class Config:
        from_attributes = True


# Kubernetes Logs Schemas
class KubernetesLogResponse(BaseModel):
    id: int
    pod_name: str
    namespace: str
    container_name: str
    log_level: str
    message: str
    source: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


# Cluster Status Response
class ClusterStatusResponse(BaseModel):
    total_nodes: int
    ready_nodes: int
    total_pods: int
    running_pods: int
    timestamp: datetime


# Alert Rule Schemas
class AlertRuleBase(BaseModel):
    name: str = Field(..., description="Alert rule name")
    description: Optional[str] = None
    rule_type: str = Field(..., description="Rule type (cpu_usage, memory_usage, pod_restart_count, etc.)")
    metric_name: str = Field(..., description="Metric name to check")
    operator: str = Field(..., description="Operator (>, <, >=, <=, ==, !=)")
    threshold: float = Field(..., description="Threshold value")
    duration: int = Field(default=300, description="Duration in seconds before alerting")
    severity: str = Field(default="WARNING", description="Alert severity (CRITICAL, HIGH, MEDIUM, LOW)")
    enabled: bool = Field(default=True)


class AlertRuleCreate(AlertRuleBase):
    namespace: Optional[str] = None
    pod_name_pattern: Optional[str] = None
    deployment_name: Optional[str] = None
    auto_create_incident: bool = True
    notify_channels: Dict[str, List[str]] = {}


class AlertRuleResponse(AlertRuleBase):
    id: int
    namespace: Optional[str] = None
    pod_name_pattern: Optional[str] = None
    deployment_name: Optional[str] = None
    auto_create_incident: bool
    notify_channels: Dict[str, List[str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Alert Schemas
class AlertBase(BaseModel):
    title: str
    description: str
    severity: str = "WARNING"
    status: str = "FIRING"


class AlertResponse(AlertBase):
    id: int
    rule_id: int
    value: float
    pod_name: Optional[str] = None
    pod_namespace: Optional[str] = None
    deployment_name: Optional[str] = None
    node_name: Optional[str] = None
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None

    class Config:
        from_attributes = True


class AlertUpdateRequest(BaseModel):
    status: Optional[str] = None
    acknowledged_by: Optional[str] = None


# Incident Schemas
class IncidentBase(BaseModel):
    title: str
    description: str
    status: str = "OPEN"
    priority: str = "MEDIUM"
    severity: str = "MEDIUM"


class IncidentCreate(IncidentBase):
    namespace: Optional[str] = None
    pod_name: Optional[str] = None
    deployment_name: Optional[str] = None
    node_name: Optional[str] = None
    assigned_to: Optional[str] = None


class IncidentResponse(IncidentBase):
    id: int
    alert_id: Optional[int] = None
    root_cause_analysis: Optional[str] = None
    suggested_fix: Optional[str] = None
    recommended_action: Optional[str] = None
    preventive_action: Optional[str] = None
    impact: Optional[str] = None
    namespace: Optional[str] = None
    pod_name: Optional[str] = None
    deployment_name: Optional[str] = None
    node_name: Optional[str] = None
    assigned_to: Optional[str] = None
    tags: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class IncidentUpdateRequest(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    notes: Optional[str] = None
    root_cause_analysis: Optional[str] = None
    suggested_fix: Optional[str] = None


# RCA Schemas
class RCABase(BaseModel):
    title: str
    summary: str
    root_cause: str


class RCACreate(RCABase):
    contributing_factors: Optional[Dict[str, Any]] = {}
    timeline: Optional[Dict[str, Any]] = {}
    corrective_actions: Optional[Dict[str, Any]] = {}
    preventive_measures: Optional[Dict[str, Any]] = {}


class RCAResponse(RCABase):
    id: int
    incident_id: int
    contributing_factors: Dict[str, Any]
    timeline: Dict[str, Any]
    impact_analysis: Optional[str] = None
    corrective_actions: Dict[str, Any]
    preventive_measures: Dict[str, Any]
    ai_generated: bool = False
    ai_model: Optional[str] = None
    ai_confidence: Optional[float] = None
    mttr: Optional[int] = None
    mtbf: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Knowledge Base Schemas
class KnowledgeBaseArticleBase(BaseModel):
    title: str
    slug: str
    content: str
    category: str


class KnowledgeBaseArticleCreate(KnowledgeBaseArticleBase):
    keywords: List[str] = []
    related_alert_types: List[str] = []
    author: Optional[str] = None


class KnowledgeBaseArticleResponse(KnowledgeBaseArticleBase):
    id: int
    keywords: List[str]
    related_alert_types: List[str]
    is_published: bool
    author: Optional[str] = None
    views_count: int
    helpful_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# AI Chat Schemas
class AIChatMessageBase(BaseModel):
    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")


class AIChatMessageCreate(AIChatMessageBase):
    pass


class AIChatMessageResponse(AIChatMessageBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AIChatBase(BaseModel):
    title: Optional[str] = None
    context: Dict[str, Any] = {}


class AIChatCreate(AIChatBase):
    pass


class AIChatResponse(AIChatBase):
    id: int
    messages: List[AIChatMessageResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AIChatWithMessagesResponse(BaseModel):
    id: int
    title: Optional[str] = None
    messages: List[AIChatMessageResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# AI Analysis Request Schemas
class AIRCARequest(BaseModel):
    incident_id: int
    logs: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None


class AILogAnalysisRequest(BaseModel):
    logs: str
    namespace: Optional[str] = None
    pod_name: Optional[str] = None
    deployment_name: Optional[str] = None


class AIAlertSuggestionRequest(BaseModel):
    alert_type: str
    value: float
    threshold: float
    resource: str
    namespace: Optional[str] = None


class AIQuestionRequest(BaseModel):
    question: str
    context: Optional[Dict[str, Any]] = None


# Batch Operations Schemas
class BulkAlertRuleUpdate(BaseModel):
    rule_ids: List[int]
    enabled: Optional[bool] = None
    severity: Optional[str] = None


class BulkIncidentUpdate(BaseModel):
    incident_ids: List[int]
    status: Optional[str] = None
    assigned_to: Optional[str] = None


# Dashboard Schemas
class DashboardMetrics(BaseModel):
    total_alerts_firing: int
    total_incidents_open: int
    total_nodes: int
    total_pods: int
    ready_nodes: int
    running_pods: int
    avg_cpu_usage: float
    avg_memory_usage: float
    timestamp: datetime
