"""
Schemas Pydantic para Sistema de Chat LLM
/-HALL-DEV Backend
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, EmailStr, Field


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
    metadata: dict[str, Any] | None = None


class Phase(str, Enum):
    """Fases do fluxo de conversa"""

    DISCOVERY = "discovery"
    LEAD_CAPTURE = "lead_capture"
    SCHEDULING = "scheduling"


class ChatSession(BaseModel):
    """Schema para sessão de chat"""

    session_id: str
    user_id: str | None = None
    messages: list[ChatMessage] = Field(default_factory=list)
    user_profile: dict[str, str] | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True
    phase: Phase = Phase.DISCOVERY


class LLMRequest(BaseModel):
    """Schema para requisição ao LLM"""

    session_id: str
    message: str
    context: dict[str, Any] | None = None


class LLMResponse(BaseModel):
    """Schema para resposta do LLM"""

    message: str
    session_id: str
    user_profile_extracted: dict[str, str] | None = None
    intent_detected: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    metadata: dict[str, Any] | None = None


class UserProfile(BaseModel):
    """Schema para perfil do usuário"""

    name: str | None = None
    email: EmailStr | None = None
    company: str | None = None
    role: str | None = None
    pain_points: list[str] | None = None
    interests: list[str] | None = None


class ChatStartRequest(BaseModel):
    """Schema para iniciar conversa"""

    initial_message: str | None = None
    user_id: str | None = None


class ChatStartResponse(BaseModel):
    """Schema para resposta de início de conversa"""

    session_id: str
    welcome_message: str
    user_profile: UserProfile | None = None


class ChatEndRequest(BaseModel):
    """Schema para finalizar conversa"""

    session_id: str
    reason: str | None = None


class ChatEndResponse(BaseModel):
    """Schema para resposta de fim de conversa"""

    session_id: str
    summary: str | None = None
    lead_qualified: bool = False
    user_profile: UserProfile | None = None


class LeadData(BaseModel):
    """Schema para dados do lead qualificado"""

    session_id: str
    user_profile: UserProfile
    conversation_summary: str
    pain_points: list[str]
    recommended_solutions: list[str]
    qualification_score: float = Field(ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.now)
