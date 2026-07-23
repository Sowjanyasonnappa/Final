"""
AI Chat and Knowledge Base API Routes
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database import alert_model, user_model
from app.schemas import kubernetes_schema
from app.services.ai_service import AIService
from app.auth.oauth2 import get_current_user
from app.utils.role_checker import admin_only

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ai", tags=["AI & Knowledge Base"])


# AI Chat
@router.get("/chats", response_model=List[kubernetes_schema.AIChatResponse])
async def get_chats(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI chats for current user"""
    chats = db.query(alert_model.AIChat).filter_by(user_id=current_user.id).all()
    return chats


@router.post("/chats", response_model=kubernetes_schema.AIChatResponse)
async def create_chat(
    chat: kubernetes_schema.AIChatCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new AI chat"""
    db_chat = alert_model.AIChat(
        user_id=current_user.id,
        **chat.dict()
    )
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat


@router.get("/chats/{chat_id}", response_model=kubernetes_schema.AIChatWithMessagesResponse)
async def get_chat(
    chat_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat with messages"""
    chat = db.query(alert_model.AIChat).filter(
        alert_model.AIChat.id == chat_id,
        alert_model.AIChat.user_id == current_user.id
    ).first()
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    return kubernetes_schema.AIChatWithMessagesResponse(
        id=chat.id,
        title=chat.title,
        messages=[
            kubernetes_schema.AIChatMessageResponse.from_orm(msg)
            for msg in chat.messages
        ],
        created_at=chat.created_at,
        updated_at=chat.updated_at
    )


@router.post("/chats/{chat_id}/messages", response_model=kubernetes_schema.AIChatMessageResponse)
async def send_message(
    chat_id: int,
    message: kubernetes_schema.AIChatMessageCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send message in chat"""
    chat = db.query(alert_model.AIChat).filter(
        alert_model.AIChat.id == chat_id,
        alert_model.AIChat.user_id == current_user.id
    ).first()
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Add user message
    user_msg = alert_model.AIChatMessage(
        chat_id=chat_id,
        role="user",
        content=message.content
    )
    db.add(user_msg)
    db.flush()
    
    # Get AI response
    ai_service = AIService()
    
    # Prepare context
    context = {
        "chat_history": [
            {"role": msg.role, "content": msg.content}
            for msg in chat.messages
        ],
        "cluster_context": chat.context
    }
    
    # Get response based on message type
    if "kubectl" in message.content.lower() or "command" in message.content.lower():
        response_text = ai_service.suggest_kubectl_commands({
            "description": message.content,
            "namespace": chat.context.get("namespace"),
            "resource_type": chat.context.get("resource_type")
        })[0] if ai_service.suggest_kubectl_commands({
            "description": message.content,
            "namespace": chat.context.get("namespace"),
            "resource_type": chat.context.get("resource_type")
        }) else "I couldn't generate kubectl commands for your request."
    elif "yaml" in message.content.lower() or "manifest" in message.content.lower():
        response_text = ai_service.suggest_yaml_fixes(
            message.content,
            "Please fix this YAML manifest"
        )
    else:
        response_text = ai_service.answer_operational_question(
            message.content,
            chat.context
        )
    
    # Add AI response
    ai_msg = alert_model.AIChatMessage(
        chat_id=chat_id,
        role="assistant",
        content=response_text
    )
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)
    
    return kubernetes_schema.AIChatMessageResponse.from_orm(ai_msg)


@router.delete("/chats/{chat_id}")
async def delete_chat(
    chat_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete chat"""
    chat = db.query(alert_model.AIChat).filter(
        alert_model.AIChat.id == chat_id,
        alert_model.AIChat.user_id == current_user.id
    ).first()
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    db.delete(chat)
    db.commit()
    
    return {"message": "Chat deleted"}


# Knowledge Base
@router.get("/knowledge-base", response_model=List[kubernetes_schema.KnowledgeBaseArticleResponse])
async def get_knowledge_base_articles(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get knowledge base articles"""
    query = db.query(alert_model.KnowledgeBaseArticle).filter_by(is_published=True)
    
    if category:
        query = query.filter_by(category=category)
    
    if search:
        query = query.filter(
            alert_model.KnowledgeBaseArticle.title.ilike(f"%{search}%") |
            alert_model.KnowledgeBaseArticle.content.ilike(f"%{search}%")
        )
    
    articles = query.limit(limit).all()
    return articles


@router.get("/knowledge-base/{article_id}", response_model=kubernetes_schema.KnowledgeBaseArticleResponse)
async def get_knowledge_base_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get knowledge base article"""
    article = db.query(alert_model.KnowledgeBaseArticle).filter_by(id=article_id).first()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Increment view count
    article.views_count += 1
    db.commit()
    
    return article


@router.get("/knowledge-base/slug/{slug}", response_model=kubernetes_schema.KnowledgeBaseArticleResponse)
async def get_knowledge_base_article_by_slug(
    slug: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get knowledge base article by slug"""
    article = db.query(alert_model.KnowledgeBaseArticle).filter_by(slug=slug).first()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Increment view count
    article.views_count += 1
    db.commit()
    
    return article


@router.post("/knowledge-base", response_model=kubernetes_schema.KnowledgeBaseArticleResponse)
async def create_knowledge_base_article(
    article: kubernetes_schema.KnowledgeBaseArticleCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create knowledge base article"""
    admin_only(current_user)
    
    # Check if slug already exists
    existing = db.query(alert_model.KnowledgeBaseArticle).filter_by(slug=article.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Article with this slug already exists")
    
    db_article = alert_model.KnowledgeBaseArticle(**article.dict())
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article


@router.put("/knowledge-base/{article_id}", response_model=kubernetes_schema.KnowledgeBaseArticleResponse)
async def update_knowledge_base_article(
    article_id: int,
    article_update: kubernetes_schema.KnowledgeBaseArticleCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update knowledge base article"""
    admin_only(current_user)
    
    article = db.query(alert_model.KnowledgeBaseArticle).filter_by(id=article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    for key, value in article_update.dict().items():
        setattr(article, key, value)
    
    db.commit()
    db.refresh(article)
    return article


@router.delete("/knowledge-base/{article_id}")
async def delete_knowledge_base_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete knowledge base article"""
    admin_only(current_user)
    
    article = db.query(alert_model.KnowledgeBaseArticle).filter_by(id=article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    db.delete(article)
    db.commit()
    
    return {"message": "Article deleted"}


@router.post("/knowledge-base/{article_id}/helpful")
async def mark_article_helpful(
    article_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Mark article as helpful"""
    article = db.query(alert_model.KnowledgeBaseArticle).filter_by(id=article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    article.helpful_count += 1
    db.commit()
    
    return {"message": "Article marked as helpful", "helpful_count": article.helpful_count}


# AI Analysis Endpoints
@router.post("/analyze-logs")
async def analyze_logs(
    request: kubernetes_schema.AILogAnalysisRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Analyze logs with AI"""
    admin_only(current_user)
    
    ai_service = AIService()
    context = {
        "namespace": request.namespace,
        "pod_name": request.pod_name,
        "deployment_name": request.deployment_name
    }
    
    result = ai_service.analyze_logs(request.logs, context)
    return result


@router.post("/generate-alert-suggestions")
async def generate_alert_suggestions(
    request: kubernetes_schema.AIAlertSuggestionRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Generate alert suggestions"""
    admin_only(current_user)
    
    ai_service = AIService()
    result = ai_service.generate_alert_suggestions({
        "alert_type": request.alert_type,
        "value": request.value,
        "threshold": request.threshold,
        "resource": request.resource,
        "namespace": request.namespace
    })
    return result


@router.post("/ask-question")
async def ask_question(
    request: kubernetes_schema.AIQuestionRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Ask AI question about operations"""
    admin_only(current_user)
    
    ai_service = AIService()
    answer = ai_service.answer_operational_question(request.question, request.context)
    return {"answer": answer}


@router.post("/suggest-kubectl-commands")
async def suggest_kubectl_commands(
    scenario: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Suggest kubectl commands"""
    admin_only(current_user)
    
    ai_service = AIService()
    commands = ai_service.suggest_kubectl_commands(scenario)
    return {"commands": commands}


@router.post("/suggest-scaling")
async def suggest_scaling(
    deployment_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Suggest scaling configuration"""
    admin_only(current_user)
    
    ai_service = AIService()
    suggestion = ai_service.suggest_scaling(deployment_data)
    return {"suggestion": suggestion}
