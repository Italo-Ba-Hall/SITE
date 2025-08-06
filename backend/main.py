"""
/-HALL-DEV Backend API
Plataforma Conversacional para Captação e Qualificação de Leads

Tecnologias: FastAPI + Python + Pydantic
Arquitetura: API-First, Desacoplada do Frontend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import uvicorn
from datetime import datetime

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

# === SCHEMAS PYDANTIC ===

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

# === EXECUÇÃO ===

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    ) 