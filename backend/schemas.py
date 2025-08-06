"""
Schemas Pydantic para Sistema de Chat LLM
/-HALL-DEV Backend
"""

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    """Roles das mensagens no chat"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    """Schema para mensagens individuais do chat"""
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None

class ChatSession(BaseModel):
    """Schema para sessão de chat"""
    session_id: str
    user_id: Optional[str] = None
    messages: List[ChatMessage] = []
    user_profile: Optional[Dict[str, str]] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True

class LLMRequest(BaseModel):
    """Schema para requisição ao LLM"""
    session_id: str
    message: str
    context: Optional[Dict[str, Any]] = None

class LLMResponse(BaseModel):
    """Schema para resposta do LLM"""
    message: str
    session_id: str
    user_profile_extracted: Optional[Dict[str, str]] = None
    intent_detected: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    metadata: Optional[Dict[str, Any]] = None

class UserProfile(BaseModel):
    """Schema para perfil do usuário"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    company: Optional[str] = None
    role: Optional[str] = None
    pain_points: Optional[List[str]] = None
    interests: Optional[List[str]] = None

class ChatStartRequest(BaseModel):
    """Schema para iniciar conversa"""
    initial_message: Optional[str] = None
    user_id: Optional[str] = None

class ChatStartResponse(BaseModel):
    """Schema para resposta de início de conversa"""
    session_id: str
    welcome_message: str
    user_profile: Optional[UserProfile] = None

class ChatEndRequest(BaseModel):
    """Schema para finalizar conversa"""
    session_id: str
    reason: Optional[str] = None

class ChatEndResponse(BaseModel):
    """Schema para resposta de fim de conversa"""
    session_id: str
    summary: Optional[str] = None
    lead_qualified: bool = False
    user_profile: Optional[UserProfile] = None

class LeadData(BaseModel):
    """Schema para dados do lead qualificado"""
    session_id: str
    user_profile: UserProfile
    conversation_summary: str
    pain_points: List[str]
    recommended_solutions: List[str]
    qualification_score: float = Field(ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.now) 