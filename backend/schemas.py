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


# === SCHEMAS PARA PLAYGROUND DE TRANSCRIÇÃO YOUTUBE ===


class TranscribeRequest(BaseModel):
    """Schema para requisição de transcrição de vídeo do YouTube"""

    video_url: str = Field(
        ...,
        description="URL completa do vídeo do YouTube",
        examples=["https://www.youtube.com/watch?v=dQw4w9WgXcQ"],
    )


class TranscribeResponse(BaseModel):
    """Schema para resposta de transcrição"""

    video_id: str = Field(..., description="ID do vídeo do YouTube")
    video_url: str = Field(..., description="URL do vídeo")
    title: str | None = Field(None, description="Título do vídeo")
    transcript: str = Field(..., description="Transcrição completa do vídeo")
    language: str = Field(..., description="Idioma da transcrição")
    duration: int | None = Field(None, description="Duração do vídeo em segundos")


class SummarizeRequest(BaseModel):
    """Schema para requisição de sumarização"""

    transcript: str = Field(..., description="Transcrição a ser sumarizada")
    context: str | None = Field(
        None, description="Contexto ou palavras-chave para direcionar a sumarização"
    )
    keywords: list[str] | None = Field(
        None, description="Lista de palavras-chave para destacar"
    )


class SummarySection(BaseModel):
    """Schema para seção do resumo"""

    title: str = Field(..., description="Título da seção")
    content: str = Field(..., description="Conteúdo da seção")


class SummarizeResponse(BaseModel):
    """Schema para resposta de sumarização"""

    summary: str = Field(..., description="Resumo geral do conteúdo")
    key_points: list[str] = Field(..., description="Pontos principais extraídos")
    keywords_found: list[str] | None = Field(
        None, description="Palavras-chave encontradas no texto"
    )
    sections: list[SummarySection] | None = Field(
        None, description="Seções temáticas do resumo"
    )
    confidence: float = Field(
        ge=0.0, le=1.0, description="Confiança na qualidade da sumarização"
    )
