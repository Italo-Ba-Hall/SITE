"""
/-HALL-DEV Backend API
Plataforma Conversacional para Captação e Qualificação de Leads

Tecnologias: FastAPI + Python + Pydantic + Groq LLM
Arquitetura: API-First, Desacoplada do Frontend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn
from datetime import datetime
import os # Added for os.getenv

# Importar schemas e serviços
from schemas import *
from llm_service import llm_service
from chat_manager import chat_manager
import groq # Added for groq test

# Inicializar FastAPI
app = FastAPI(
    title="/-HALL-DEV API",
    description="API Conversacional para Captação de Leads",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS para comunicação com frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === SCHEMAS LEGACY (Mantidos para compatibilidade) ===

class PromptRequest(BaseModel):
    """Schema para requisição de prompt do usuário"""
    text: str
    user_id: Optional[str] = None

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
    mensagem: Optional[str] = ""
    suggestion_id: Optional[str] = None

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
        "version": "1.0.0"
    }

@app.post("/suggest", response_model=List[SuggestionResponse])
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
        suggestions.append(SuggestionResponse(
            id="web-dev",
            title="Desenvolvimento Web",
            description="Criação de sites e aplicações web modernas",
            category="development"
        ))
    
    if any(word in text for word in ["app", "aplicativo", "mobile"]):
        suggestions.append(SuggestionResponse(
            id="mobile-dev",
            title="Desenvolvimento Mobile",
            description="Apps nativos e multiplataforma",
            category="development"
        ))
    
    if any(word in text for word in ["ia", "inteligencia", "artificial", "ai"]):
        suggestions.append(SuggestionResponse(
            id="ai-solutions",
            title="Soluções em IA",
            description="Implementação de Inteligência Artificial",
            category="ai"
        ))
    
    # Sugestão padrão se nenhuma palavra-chave for encontrada
    if not suggestions:
        suggestions.append(SuggestionResponse(
            id="consultation",
            title="Consultoria Personalizada",
            description="Vamos conversar sobre seu projeto específico",
            category="consultation"
        ))
    
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
                "features": ["Responsivo", "SEO Otimizado", "Performance", "Segurança"]
            }
        ),
        "mobile-dev": ContentResponse(
            id="mobile-dev",
            title="Aplicativos Mobile Nativos",
            content="Desenvolvimento de apps para iOS e Android com experiência nativa.",
            details={
                "platforms": ["iOS", "Android", "React Native"],
                "timeline": "4-12 semanas",
                "features": ["Performance Nativa", "UI/UX Moderna", "Integração APIs"]
            }
        ),
        "ai-solutions": ContentResponse(
            id="ai-solutions",
            title="Implementação de IA",
            content="Soluções personalizadas de Inteligência Artificial para automatizar processos.",
            details={
                "services": ["Chatbots", "Machine Learning", "Análise de Dados", "Automação"],
                "timeline": "6-16 semanas",
                "technologies": ["Python", "TensorFlow", "OpenAI", "FastAPI"]
            }
        ),
        "consultation": ContentResponse(
            id="consultation",
            title="Consultoria Tecnológica",
            content="Análise detalhada do seu projeto e recomendações técnicas personalizadas.",
            details={
                "includes": ["Análise de Requisitos", "Arquitetura", "Tecnologias", "Timeline"],
                "timeline": "1-2 semanas",
                "deliverable": "Documento técnico completo"
            }
        )
    }
    
    if suggestion_id not in content_map:
        return ContentResponse(
            id="not-found",
            title="Conteúdo não encontrado",
            content="Desculpe, não encontramos informações para esta sugestão.",
            details={}
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
        print(f"Novo contato recebido:")
        print(f"Nome: {request.nome}")
        print(f"Email: {request.email}")
        print(f"Mensagem: {request.mensagem}")
        print(f"Sugestão ID: {request.suggestion_id}")
        
        # Em produção, você enviaria um email aqui
        # send_email(request.nome, request.email, request.mensagem, request.suggestion_id)
        
        return ContactResponse(
            success=True,
            message="Mensagem enviada com sucesso! Entraremos em contato em breve.",
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar contato: {str(e)}"
        )

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
                session.session_id,
                MessageRole.USER,
                request.initial_message
            )
        
        return ChatStartResponse(
            session_id=session.session_id,
            welcome_message=session.messages[0].content,
            user_profile=None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao iniciar chat: {str(e)}"
        )

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
                status_code=404,
                detail="Sessão não encontrada ou expirada"
            )
        
        # Adicionar mensagem do usuário
        chat_manager.add_message(
            request.session_id,
            MessageRole.USER,
            request.message
        )
        
        # Gerar resposta do LLM
        llm_request = LLMRequest(
            session_id=request.session_id,
            message=request.message,
            context={"messages": session.messages[:-1]}  # Excluir mensagem atual
        )
        
        response = await llm_service.generate_response(llm_request)
        
        # Adicionar resposta do assistente
        chat_manager.add_message(
            request.session_id,
            MessageRole.ASSISTANT,
            response.message
        )
        
        # Atualizar perfil do usuário se extraído
        if response.user_profile_extracted:
            chat_manager.update_user_profile(
                request.session_id,
                response.user_profile_extracted
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar mensagem: {str(e)}"
        )

@app.get("/chat/session/{session_id}")
async def get_session(session_id: str):
    """
    Recupera informações de uma sessão de chat
    """
    session = chat_manager.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail="Sessão não encontrada"
        )
    
    return {
        "session_id": session.session_id,
        "user_id": session.user_id,
        "messages": session.messages,
        "user_profile": session.user_profile,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "is_active": session.is_active
    }

@app.post("/chat/end", response_model=ChatEndResponse)
async def end_chat(request: ChatEndRequest):
    """
    Finaliza uma sessão de chat
    """
    try:
        session = chat_manager.end_session(request.session_id, request.reason)
        if not session:
            raise HTTPException(
                status_code=404,
                detail="Sessão não encontrada"
            )
        
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
            user_profile=UserProfile(**summary["user_profile"]) if summary and summary.get("user_profile") else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao finalizar chat: {str(e)}"
        )

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
            "reset_time": llm_service.last_reset.isoformat()
        }
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
        # Verificar conexão com Groq (teste simples)
        groq_status = "healthy"
        try:
            # Teste básico de conectividade
            test_client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))
            # Não fazer chamada real, apenas verificar se a chave é válida
        except Exception as e:
            groq_status = f"error: {str(e)}"
        
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
                "groq_api": groq_status,
                "chat_manager": "healthy",
                "llm_service": "healthy"
            },
            "statistics": {
                "chat": chat_stats,
                "llm": llm_stats
            }
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# === ENDPOINTS DE TESTE ===

@app.post("/test/llm")
async def test_llm_connection():
    """
    Testa a conexão com o LLM
    """
    try:
        # Teste simples de geração de resposta
        test_request = LLMRequest(
            session_id="test_session",
            message="Olá, como você está?",
            context={"messages": []}
        )
        
        response = await llm_service.generate_response(test_request)
        
        return {
            "success": True,
            "message": "Conexão com LLM funcionando",
            "response_preview": response.message[:100] + "..." if len(response.message) > 100 else response.message,
            "confidence": response.confidence,
            "metadata": response.metadata
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Erro na conexão com LLM"
        }

@app.post("/test/chat")
async def test_chat_flow():
    """
    Testa o fluxo completo de chat
    """
    try:
        # 1. Iniciar sessão
        start_response = await start_chat(ChatStartRequest(
            initial_message="Teste de fluxo",
            user_id="test_user"
        ))
        
        # 2. Enviar mensagem
        message_response = await send_message(LLMRequest(
            session_id=start_response.session_id,
            message="Este é um teste do sistema de chat",
            context={"messages": []}
        ))
        
        # 3. Finalizar sessão
        end_response = await end_chat(ChatEndRequest(
            session_id=start_response.session_id,
            reason="test_completion"
        ))
        
        return {
            "success": True,
            "message": "Fluxo de chat testado com sucesso",
            "session_id": start_response.session_id,
            "responses": {
                "start": start_response.dict(),
                "message": message_response.dict(),
                "end": end_response.dict()
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Erro no teste do fluxo de chat"
        }

# === EXECUÇÃO ===

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    ) 