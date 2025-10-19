"""
/-HALL-DEV Backend API
Plataforma Conversacional para Captação e Qualificação de Leads

Tecnologias: FastAPI + Python + Pydantic + Google Gemini LLM
Arquitetura: API-First, Desacoplada do Frontend
"""

import os
from datetime import datetime

import google.generativeai as genai
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from chat_manager import chat_manager
from database import db_manager
from llm_service import llm_service
from notification_service import notification_service
from playground_service import playground_service
from schemas import (
    BaseModel,
    ChatEndRequest,
    ChatEndResponse,
    ChatStartRequest,
    ChatStartResponse,
    EmailStr,
    LLMRequest,
    LLMResponse,
    MessageRole,
    SummarizeRequest,
    SummarizeResponse,
    TranscribeRequest,
    TranscribeResponse,
    UserProfile,
)

# Carregar variáveis de ambiente após todas as importações
load_dotenv()

# Inicializar FastAPI
app = FastAPI(
    title="/-HALL-DEV API",
    description="API Conversacional para Captação de Leads",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configurar CORS para comunicação com frontend
# Produção: adicionar domínio do FTP após deploy
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Desenvolvimento
    "http://localhost:3001",  # Desenvolvimento alternativo
    "https://barrahall.dev.br",  # Produção
    "http://barrahall.dev.br",  # Produção sem SSL
]

# Adicionar origens do .env se existir
load_dotenv()

FRONTEND_URL = os.getenv("FRONTEND_URL")
if FRONTEND_URL and FRONTEND_URL not in ALLOWED_ORIGINS:
    ALLOWED_ORIGINS.append(FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === SCHEMAS LEGACY (Mantidos para compatibilidade) ===


class PromptRequest(BaseModel):
    """Schema para requisição de prompt do usuário"""

    text: str
    user_id: str | None = None


class SuggestionResponse(BaseModel):
    """Schema para resposta de sugestões"""

    id: str
    title: str
    description: str
    category: str


class ContentResponse(BaseModel):
    """Schema para resposta de conteúdo detalhado"""

    id: str
    title: str
    content: str
    details: dict


class ContactRequest(BaseModel):
    """Schema para requisição de contato"""

    nome: str
    email: EmailStr
    mensagem: str | None = ""
    suggestion_id: str | None = None


class ContactResponse(BaseModel):
    """Schema para resposta de contato"""

    success: bool
    message: str
    timestamp: datetime


# === ENDPOINTS ===


@app.get("/")
async def root():
    """Endpoint raiz - Health check"""
    return {
        "message": "/-HALL-DEV API está funcionando!",
        "status": "online",
        "version": "1.0.0",
    }


@app.post("/suggest", response_model=list[SuggestionResponse])
async def get_suggestions(request: PromptRequest):
    """
    Endpoint para processar prompt e retornar sugestões

    Lógica inicial: baseada em palavras-chave
    Futuro: substituir por modelo de PLN mais avançado
    """
    text = request.text.lower()
    suggestions = []

    # Lógica de sugestões baseada em palavras-chave (evolutiva)
    if any(word in text for word in ["site", "website", "web", "desenvolvimento"]):
        suggestions.append(
            SuggestionResponse(
                id="web-dev",
                title="Desenvolvimento Web",
                description="Criação de sites e aplicações web modernas",
                category="development",
            )
        )

    if any(word in text for word in ["app", "aplicativo", "mobile"]):
        suggestions.append(
            SuggestionResponse(
                id="mobile-dev",
                title="Desenvolvimento Mobile",
                description="Apps nativos e multiplataforma",
                category="development",
            )
        )

    if any(word in text for word in ["ia", "inteligencia", "artificial", "ai"]):
        suggestions.append(
            SuggestionResponse(
                id="ai-solutions",
                title="Soluções em IA",
                description="Implementação de Inteligência Artificial",
                category="ai",
            )
        )

    # Sugestão padrão se nenhuma palavra-chave for encontrada
    if not suggestions:
        suggestions.append(
            SuggestionResponse(
                id="consultation",
                title="Consultoria Personalizada",
                description="Vamos conversar sobre seu projeto específico",
                category="consultation",
            )
        )

    return suggestions


@app.get("/content/{suggestion_id}", response_model=ContentResponse)
async def get_content(suggestion_id: str):
    """
    Endpoint para retornar conteúdo detalhado de uma sugestão
    """
    content_map = {
        "web-dev": ContentResponse(
            id="web-dev",
            title="Desenvolvimento Web Profissional",
            content="Criamos sites e aplicações web com tecnologias modernas como React, TypeScript e Python.",
            details={
                "technologies": ["React", "TypeScript", "Python", "FastAPI"],
                "timeline": "2-8 semanas",
                "features": ["Responsivo", "SEO Otimizado", "Performance", "Segurança"],
            },
        ),
        "mobile-dev": ContentResponse(
            id="mobile-dev",
            title="Aplicativos Mobile Nativos",
            content="Desenvolvimento de apps para iOS e Android com experiência nativa.",
            details={
                "platforms": ["iOS", "Android", "React Native"],
                "timeline": "4-12 semanas",
                "features": ["Performance Nativa", "UI/UX Moderna", "Integração APIs"],
            },
        ),
        "ai-solutions": ContentResponse(
            id="ai-solutions",
            title="Implementação de IA",
            content="Soluções personalizadas de Inteligência Artificial para automatizar processos.",
            details={
                "services": [
                    "Chatbots",
                    "Machine Learning",
                    "Análise de Dados",
                    "Automação",
                ],
                "timeline": "6-16 semanas",
                "technologies": ["Python", "TensorFlow", "OpenAI", "FastAPI"],
            },
        ),
        "consultation": ContentResponse(
            id="consultation",
            title="Consultoria Tecnológica",
            content="Análise detalhada do seu projeto e recomendações técnicas personalizadas.",
            details={
                "includes": [
                    "Análise de Requisitos",
                    "Arquitetura",
                    "Tecnologias",
                    "Timeline",
                ],
                "timeline": "1-2 semanas",
                "deliverable": "Documento técnico completo",
            },
        ),
    }

    if suggestion_id not in content_map:
        return ContentResponse(
            id="not-found",
            title="Conteúdo não encontrado",
            content="Desculpe, não encontramos informações para esta sugestão.",
            details={},
        )

    return content_map[suggestion_id]


@app.post("/contact", response_model=ContactResponse)
async def submit_contact(request: ContactRequest):
    """
    Endpoint para processar formulários de contato
    """
    try:
        # Aqui você implementaria a lógica de envio de email
        # Por exemplo, usando SMTP, SendGrid, ou outros serviços

        # Simular processamento
        print("Novo contato recebido:")
        print(f"Nome: {request.nome}")
        print(f"Email: {request.email}")
        print(f"Mensagem: {request.mensagem}")
        print(f"Sugestão ID: {request.suggestion_id}")

        # Em produção, você enviaria um email aqui
        # send_email(request.nome, request.email, request.mensagem, request.suggestion_id)

        return ContactResponse(
            success=True,
            message="Mensagem enviada com sucesso! Entraremos em contato em breve.",
            timestamp=datetime.now(),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar contato: {e!s}"
        ) from e


@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    return {"status": "healthy", "api": "/-HALL-DEV"}


# === NOVOS ENDPOINTS DE CHAT LLM ===


@app.post("/chat/start", response_model=ChatStartResponse)
async def start_chat(request: ChatStartRequest):
    """
    Inicia uma nova sessão de chat
    """
    try:
        # Criar nova sessão
        session = chat_manager.create_session(request.user_id)

        # Adicionar mensagem inicial do usuário se fornecida
        if request.initial_message:
            chat_manager.add_message(
                session.session_id, MessageRole.USER, request.initial_message
            )

        return ChatStartResponse(
            session_id=session.session_id,
            welcome_message=session.messages[0].content,
            user_profile=None,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao iniciar chat: {e!s}"
        ) from e


@app.post("/chat/message", response_model=LLMResponse)
async def send_message(request: LLMRequest):
    """
    Envia mensagem para o LLM e retorna resposta
    """
    try:
        # Verificar se sessão existe
        session = chat_manager.get_session(request.session_id)
        if not session:
            raise HTTPException(
                status_code=404, detail="Sessão não encontrada ou expirada"
            )

        # Adicionar mensagem do usuário
        chat_manager.add_message(request.session_id, MessageRole.USER, request.message)

        # Gerar resposta do LLM com contexto completo
        llm_request = LLMRequest(
            session_id=request.session_id,
            message=request.message,
            context={
                "messages": session.messages,
                "phase": session.phase if hasattr(session, "phase") else None,
                "user_profile": session.user_profile or {},
            },
        )

        response = await llm_service.generate_response(llm_request)

        # Adicionar resposta do assistente
        chat_manager.add_message(
            request.session_id, MessageRole.ASSISTANT, response.message
        )

        # Atualizar perfil do usuário se extraído
        if response.user_profile_extracted:
            chat_manager.update_user_profile(
                request.session_id, response.user_profile_extracted
            )

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar mensagem: {e!s}"
        ) from e


@app.get("/chat/inactivity-check/{session_id}")
async def check_inactivity(session_id: str):
    """
    Verifica se deve enviar aviso de inatividade
    """
    try:
        warning_message = chat_manager.check_inactivity_warning(session_id)

        if warning_message:
            # Adicionar aviso como mensagem do sistema
            chat_manager.add_message(session_id, MessageRole.ASSISTANT, warning_message)

            return {
                "should_warn": True,
                "warning_message": warning_message,
                "session_id": session_id,
            }

        return {"should_warn": False, "warning_message": None, "session_id": session_id}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao verificar inatividade: {e!s}"
        ) from e


@app.get("/chat/session/{session_id}")
async def get_session(session_id: str):
    """
    Recupera informações de uma sessão de chat
    """
    session = chat_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    return {
        "session_id": session.session_id,
        "user_id": session.user_id,
        "messages": session.messages,
        "user_profile": session.user_profile,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "is_active": session.is_active,
    }


@app.post("/chat/end", response_model=ChatEndResponse)
async def end_chat(request: ChatEndRequest):
    """
    Finaliza uma sessão de chat
    """
    try:
        session = chat_manager.end_session(request.session_id, request.reason)
        if not session:
            raise HTTPException(status_code=404, detail="Sessão não encontrada")

        # Gerar resumo da conversa
        summary = chat_manager.get_conversation_summary(request.session_id)

        # Determinar se lead foi qualificado
        lead_qualified = False
        if summary and summary.get("user_profile"):
            profile = summary["user_profile"]
            if profile.get("name") and profile.get("email"):
                lead_qualified = True

        return ChatEndResponse(
            session_id=request.session_id,
            summary=summary,
            lead_qualified=lead_qualified,
            user_profile=UserProfile(**summary["user_profile"])
            if summary and summary.get("user_profile")
            else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao finalizar chat: {e!s}"
        ) from e


@app.get("/chat/stats")
async def get_chat_stats():
    """
    Retorna estatísticas das sessões de chat
    """
    return chat_manager.get_session_stats()


# === NOVOS ENDPOINTS DE MONITORAMENTO ===


@app.get("/stats/llm")
async def get_llm_stats():
    """
    Retorna estatísticas do serviço LLM
    """
    return {
        "cache_stats": llm_service.get_cache_stats(),
        "rate_limit": {
            "current_requests": llm_service.request_count,
            "max_requests_per_minute": llm_service.max_requests_per_minute,
            "reset_time": llm_service.last_reset.isoformat(),
        },
    }


@app.post("/stats/cache/clear")
async def clear_cache():
    """
    Limpa o cache do LLM
    """
    llm_service.clear_cache()
    return {"message": "Cache limpo com sucesso"}


@app.post("/stats/cache/cleanup")
async def cleanup_cache():
    """
    Remove itens expirados do cache
    """
    llm_service.cleanup_cache()
    return {"message": "Cache limpo de itens expirados"}


@app.get("/health/detailed")
async def detailed_health_check():
    """
    Health check detalhado com informações do sistema
    """
    try:
        # Verificar conexão com Gemini (teste simples)
        gemini_status = "healthy"
        try:
            # Teste básico de conectividade
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            # Não fazer chamada real, apenas verificar se a chave é válida
        except Exception as e:
            gemini_status = f"error: {e!s}"

        # Estatísticas do chat
        chat_stats = chat_manager.get_session_stats()

        # Estatísticas do LLM
        llm_stats = llm_service.get_cache_stats()

        return {
            "status": "healthy",
            "api": "/-HALL-DEV",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "gemini_api": gemini_status,
                "chat_manager": "healthy",
                "llm_service": "healthy",
            },
            "statistics": {"chat": chat_stats, "llm": llm_stats},
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


# === ENDPOINTS DE DASHBOARD E GERENCIAMENTO ===


@app.get("/dashboard/leads")
async def get_leads_dashboard(status: str | None = None, limit: int = 50):
    """
    Endpoint para dashboard de leads
    """
    try:
        leads = db_manager.get_all_leads(status=status, limit=limit)
        stats = db_manager.get_stats()

        return {"leads": leads, "stats": stats, "total_leads": len(leads)}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao recuperar leads: {e!s}"
        ) from e


@app.get("/dashboard/leads/{session_id}")
async def get_lead_details(session_id: str):
    """
    Endpoint para detalhes de um lead específico
    """
    try:
        lead = db_manager.get_lead(session_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead não encontrado")

        return lead

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao recuperar lead: {e!s}"
        ) from e


@app.put("/dashboard/leads/{session_id}/status")
async def update_lead_status(session_id: str, status: str, notes: str | None = None):
    """
    Endpoint para atualizar status de um lead
    """
    try:
        # Validar status
        valid_statuses = ["new", "contacted", "qualified", "converted", "lost"]
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400, detail=f"Status inválido. Use um dos: {valid_statuses}"
            )

        # Atualizar status
        db_manager.update_lead_status(session_id, status, notes)

        # Recuperar dados do lead para notificação
        lead_data = db_manager.get_lead(session_id)
        if lead_data:
            notification_service.notify_lead_status_change(lead_data, status)

        return {
            "success": True,
            "message": f"Status do lead atualizado para {status}",
            "session_id": session_id,
            "new_status": status,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao atualizar status: {e!s}"
        ) from e


@app.get("/dashboard/notifications")
async def get_notifications(unread_only: bool = True):
    """
    Endpoint para recuperar notificações
    """
    try:
        notifications = db_manager.get_notifications(unread_only=unread_only)

        return {"notifications": notifications, "total": len(notifications)}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao recuperar notificações: {e!s}"
        ) from e


@app.put("/dashboard/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: int):
    """
    Endpoint para marcar notificação como lida
    """
    try:
        db_manager.mark_notification_read(notification_id)

        return {
            "success": True,
            "message": "Notificação marcada como lida",
            "notification_id": notification_id,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao marcar notificação: {e!s}"
        ) from e


@app.get("/dashboard/stats")
async def get_dashboard_stats():
    """
    Endpoint para estatísticas do dashboard
    """
    try:
        db_stats = db_manager.get_stats()
        chat_stats = chat_manager.get_session_stats()
        llm_stats = llm_service.get_stats()

        return {
            "database": db_stats,
            "chat": chat_stats,
            "llm": llm_stats,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao recuperar estatísticas: {e!s}"
        ) from e


@app.get("/dashboard/conversation-summaries")
async def get_conversation_summaries(limit: int = 50, offset: int = 0):
    """
    Endpoint para recuperar resumos de conversa
    """
    try:
        summaries = db_manager.get_all_conversation_summaries(
            limit=limit, offset=offset
        )

        return {"summaries": summaries, "total": len(summaries)}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao recuperar resumos: {e!s}"
        ) from e


@app.delete("/dashboard/conversations/{session_id}")
async def delete_conversation(session_id: str):
    """Exclui uma conversa (mensagens e resumo) do banco."""
    try:
        result = db_manager.delete_conversation(session_id)
        return {"success": True, "session_id": session_id, **result}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao excluir conversa: {e!s}"
        ) from e


@app.get("/dashboard/conversation-summaries/{session_id}")
async def get_conversation_summary_details(session_id: str):
    """
    Endpoint para detalhes de um resumo de conversa específico
    """
    try:
        summary = db_manager.get_conversation_summary(session_id)
        if not summary:
            raise HTTPException(
                status_code=404, detail="Resumo de conversa não encontrado"
            )

        return summary

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao recuperar resumo: {e!s}"
        ) from e


@app.post("/dashboard/reports/daily")
async def send_daily_report():
    """
    Endpoint para enviar relatório diário
    """
    try:
        stats = db_manager.get_stats()
        success = notification_service.send_daily_report(stats)

        return {
            "success": success,
            "message": "Relatório diário enviado"
            if success
            else "Erro ao enviar relatório",
            "stats": stats,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao enviar relatório: {e!s}"
        ) from e


# === ENDPOINTS DE SALVAR CONVERSAS E EMAIL ===


class SaveConversationRequest(BaseModel):
    """Schema para salvar conversa"""

    session_id: str
    email: str


class SendEmailRequest(BaseModel):
    """Schema para enviar email"""

    session_id: str
    email: str


@app.post("/chat/save-conversation")
async def save_conversation_to_email(request: SaveConversationRequest):
    """
    Salva uma conversa e envia por email
    """
    try:
        # Verificar se sessão existe
        session = chat_manager.get_session(request.session_id)
        if not session:
            raise HTTPException(
                status_code=404, detail="Sessão não encontrada ou expirada"
            )

        # Gerar resumo da conversa
        summary = chat_manager.get_conversation_summary(request.session_id)

        # Salvar no banco de dados
        if summary and summary.get("user_profile"):
            profile = summary["user_profile"]
            db_manager.save_lead(
                session_id=request.session_id,
                user_profile=profile,
                conversation_summary=summary.get("summary", "Conversa salva"),
                pain_points=summary.get("pain_points", []),
                recommended_solutions=summary.get("recommended_solutions", []),
                qualification_score=summary.get("qualification_score", 0.0),
                full_conversation=session.messages,
            )

        # Enviar email com a conversa
        email_sent = notification_service.send_conversation_email(
            email=request.email,
            session_id=request.session_id,
            messages=session.messages,
            summary=summary,
        )

        return {
            "success": True,
            "message": "Conversa salva e email enviado com sucesso",
            "session_id": request.session_id,
            "email": request.email,
            "email_sent": email_sent,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao salvar conversa: {e!s}"
        ) from e


@app.post("/chat/send-email")
async def send_conversation_email(request: SendEmailRequest):
    """
    Envia conversa por email sem salvar no banco
    """
    try:
        # Verificar se sessão existe
        session = chat_manager.get_session(request.session_id)
        if not session:
            raise HTTPException(
                status_code=404, detail="Sessão não encontrada ou expirada"
            )

        # Gerar resumo da conversa
        summary = chat_manager.get_conversation_summary(request.session_id)

        # Enviar email
        email_sent = notification_service.send_conversation_email(
            email=request.email,
            session_id=request.session_id,
            messages=session.messages,
            summary=summary,
        )

        return {
            "success": True,
            "message": "Email enviado com sucesso",
            "session_id": request.session_id,
            "email": request.email,
            "email_sent": email_sent,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao enviar email: {e!s}"
        ) from e


@app.get("/chat/conversation/{session_id}")
async def get_full_conversation(session_id: str):
    """
    Recupera conversa completa para envio por email
    """
    try:
        session = chat_manager.get_session(session_id)
        if session:
            # Sessão ativa: retornar diretamente da memória
            summary = chat_manager.get_conversation_summary(session_id)
            return {
                "session_id": session_id,
                "messages": session.messages,
                "summary": summary,
                "user_profile": session.user_profile,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
            }

        # Fallback: buscar no banco conversas e resumo persistidos
        persisted_messages = db_manager.get_conversation_messages(session_id)
        persisted_summary = db_manager.get_conversation_summary(session_id)
        if not persisted_messages and not persisted_summary:
            raise HTTPException(status_code=404, detail="Conversa não encontrada")

        # Normalizar mensagens para o frontend
        normalized = [
            {
                "role": (m.get("role") or "system"),
                "content": m.get("content", ""),
                "timestamp": m.get("timestamp"),
            }
            for m in persisted_messages
        ]

        return {
            "session_id": session_id,
            "messages": normalized,
            "summary": persisted_summary,
            "user_profile": None,
            "created_at": persisted_summary.get("created_at")
            if persisted_summary
            else None,
            "updated_at": None,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao recuperar conversa: {e!s}"
        ) from e


# === ENDPOINTS DE TESTE E DESENVOLVIMENTO ===


@app.post("/test/database")
async def test_database():
    """
    Endpoint para testar conexão com banco de dados
    """
    try:
        # Testar criação de lead de exemplo
        test_lead = {
            "name": "Teste Lead",
            "email": "teste@exemplo.com",
            "company": "Empresa Teste",
            "role": "Desenvolvedor",
        }

        lead_id = db_manager.save_lead(
            session_id="test-session-123",
            user_profile=test_lead,
            conversation_summary="Conversa de teste",
            pain_points=["Problema de performance", "Processos manuais"],
            recommended_solutions=["Automação", "Dashboard BI"],
            qualification_score=0.8,
        )

        # Recuperar lead
        lead = db_manager.get_lead("test-session-123")

        # Testar notificações
        notification_sent = notification_service.notify_new_lead(test_lead)

        return {
            "success": True,
            "message": "Teste de banco de dados realizado com sucesso",
            "lead_id": lead_id,
            "lead_data": lead,
            "notification_sent": notification_sent,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro no teste de banco de dados: {e!s}"
        ) from e


# === ENDPOINTS DE PLAYGROUND ===


@app.post("/playground/transcribe", response_model=TranscribeResponse)
async def transcribe_youtube_video(request: TranscribeRequest):
    """
    Endpoint para obter transcrição de vídeo do YouTube

    Args:
        request: TranscribeRequest com video_url

    Returns:
        TranscribeResponse com transcrição e metadados
    """
    try:
        # Obter transcrição
        result = playground_service.get_transcript(request.video_url)

        return TranscribeResponse(**result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar transcrição: {e!s}"
        ) from e


@app.post("/playground/summarize", response_model=SummarizeResponse)
async def summarize_transcript(request: SummarizeRequest):
    """
    Endpoint para sumarizar transcrição usando IA

    Args:
        request: SummarizeRequest com transcript, context e keywords

    Returns:
        SummarizeResponse com resumo e análise
    """
    try:
        # Validar tamanho da transcrição
        if len(request.transcript) < 50:
            raise HTTPException(
                status_code=400,
                detail="Transcrição muito curta. Mínimo de 50 caracteres.",
            )

        if len(request.transcript) > 100000:
            raise HTTPException(
                status_code=400,
                detail="Transcrição muito longa. Máximo de 100.000 caracteres.",
            )

        # Gerar sumarização
        result = playground_service.summarize_transcript(
            transcript=request.transcript,
            context=request.context,
            keywords=request.keywords,
        )

        return SummarizeResponse(**result)

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar sumarização: {e!s}"
        ) from e


# === EXECUÇÃO ===

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, log_level="info")
