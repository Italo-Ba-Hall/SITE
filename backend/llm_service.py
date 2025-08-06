"""
Serviço de LLM usando Groq
/-HALL-DEV Backend
"""

import os
import json
import uuid
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import groq
from dotenv import load_dotenv

from schemas import ChatMessage, MessageRole, UserProfile, LLMRequest, LLMResponse

# Carregar variáveis de ambiente
load_dotenv()

class LLMCache:
    """Sistema de cache para respostas do LLM"""
    
    def __init__(self, max_size: int = 1000, ttl_hours: int = 24):
        self.cache: Dict[str, Dict] = {}
        self.max_size = max_size
        self.ttl = timedelta(hours=ttl_hours)
    
    def _generate_key(self, messages: List[Dict], user_message: str) -> str:
        """Gera chave única para cache baseada no contexto e mensagem"""
        context_str = json.dumps([msg["content"] for msg in messages], sort_keys=True)
        combined = f"{context_str}:{user_message}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[LLMResponse]:
        """Recupera resposta do cache"""
        if key in self.cache:
            cached = self.cache[key]
            if datetime.now() - cached["timestamp"] < self.ttl:
                return cached["response"]
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, response: LLMResponse):
        """Armazena resposta no cache"""
        if len(self.cache) >= self.max_size:
            # Remove item mais antigo
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]["timestamp"])
            del self.cache[oldest_key]
        
        self.cache[key] = {
            "response": response,
            "timestamp": datetime.now()
        }
    
    def clear_expired(self):
        """Remove itens expirados do cache"""
        current_time = datetime.now()
        expired_keys = [
            key for key, value in self.cache.items()
            if current_time - value["timestamp"] > self.ttl
        ]
        for key in expired_keys:
            del self.cache[key]
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas do cache"""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "ttl_hours": self.ttl.total_seconds() / 3600
        }

class LLMService:
    """Serviço para integração com Groq LLM"""
    
    def __init__(self):
        self.client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))
        # Modelo mais robusto: Llama-3-70B vs 8B anterior
        self.model = "llama3-70b-8192"  # Modelo premium gratuito do Groq
        self.max_tokens = 1500  # Aumentado para aproveitar modelo maior
        self.temperature = 0.7
        
        # Cache de respostas
        self.cache = LLMCache(max_size=500, ttl_hours=12)
        
        # Rate limiting
        self.request_count = 0
        self.last_reset = datetime.now()
        self.max_requests_per_minute = 60
        
        # Personalidade do agente
        self.system_prompt = """Você é um agente conversacional especializado da /-HALL-DEV, uma empresa de soluções tecnológicas.

PERSONALIDADE:
- Educado, caloroso e profissional
- Direto e objetivo nas respostas
- Orientado a soluções e resultados
- Focado em entender a dor do cliente

OBJETIVOS:
1. Entender o problema/dor do usuário
2. Coletar nome e email de forma natural durante a conversa
3. Direcionar para soluções de código/tecnologia
4. Qualificar leads efetivamente

SERVIÇOS DA EMPRESA:
- Desenvolvimento de Software
- Business Intelligence (BI)
- Machine Learning
- Automação e RPA
- Inteligência Artificial

INSTRUÇÕES:
- Seja conciso mas completo
- Sempre pergunte sobre o nome e email naturalmente
- Identifique problemas que podem ser resolvidos com tecnologia
- Sugira soluções baseadas em código/automação
- Mantenha o foco em reduzir custos e aumentar eficiência

FORMATO DE RESPOSTA:
Responda de forma natural e conversacional. Se identificar dados do usuário, extraia-os mas mantenha a conversa fluida."""

    def _check_rate_limit(self) -> bool:
        """Verifica se não excedeu o rate limit"""
        current_time = datetime.now()
        
        # Reset contador a cada minuto
        if current_time - self.last_reset > timedelta(minutes=1):
            self.request_count = 0
            self.last_reset = current_time
        
        if self.request_count >= self.max_requests_per_minute:
            return False
        
        self.request_count += 1
        return True

    def _build_conversation_context(self, messages: List[ChatMessage]) -> List[Dict[str, str]]:
        """Constrói o contexto da conversa para o LLM"""
        context = [{"role": "system", "content": self.system_prompt}]
        
        for message in messages:
            context.append({
                "role": message.role.value,
                "content": message.content
            })
        
        return context

    def _extract_user_profile(self, message: str) -> Optional[Dict[str, str]]:
        """Extrai informações do usuário da mensagem"""
        # Lógica simples de extração - pode ser melhorada
        profile = {}
        
        # Extrair nome (padrões comuns)
        import re
        name_patterns = [
            r"meu nome é (\w+)",
            r"eu sou (\w+)",
            r"chamo-me (\w+)",
            r"sou (\w+)"
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, message.lower())
            if match:
                profile["name"] = match.group(1).title()
                break
        
        # Extrair email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, message)
        if email_match:
            profile["email"] = email_match.group(0)
        
        return profile if profile else None

    def _detect_intent(self, message: str) -> Optional[str]:
        """Detecta a intenção da mensagem do usuário"""
        message_lower = message.lower()
        
        intents = {
            "greeting": ["olá", "oi", "bom dia", "boa tarde", "boa noite"],
            "problem_description": ["problema", "dificuldade", "dor", "preciso", "quero"],
            "service_inquiry": ["serviço", "solução", "desenvolvimento", "software"],
            "contact_info": ["contato", "email", "telefone", "whatsapp"],
            "pricing": ["preço", "valor", "custo", "orçamento"],
            "technical": ["tecnologia", "programação", "código", "sistema"]
        }
        
        for intent, keywords in intents.items():
            if any(keyword in message_lower for keyword in keywords):
                return intent
        
        return None

    def _optimize_prompt_size(self, context: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Otimiza o tamanho do prompt para reduzir tokens"""
        if len(context) <= 10:  # Se já é pequeno, retorna como está
            return context
        
        # Manter system prompt e últimas 8 mensagens
        optimized = [context[0]]  # System prompt
        optimized.extend(context[-8:])  # Últimas 8 mensagens
        
        return optimized

    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        """Gera resposta usando Groq LLM com cache e otimizações"""
        try:
            # Verificar rate limit
            if not self._check_rate_limit():
                return LLMResponse(
                    message="Desculpe, estamos com muitas solicitações no momento. Tente novamente em alguns instantes.",
                    session_id=request.session_id,
                    confidence=0.0,
                    metadata={"error": "rate_limit_exceeded"}
                )
            
            # Construir contexto da conversa
            conversation_context = self._build_conversation_context(request.context.get("messages", []))
            
            # Otimizar tamanho do prompt
            optimized_context = self._optimize_prompt_size(conversation_context)
            
            # Adicionar mensagem atual do usuário
            optimized_context.append({
                "role": "user",
                "content": request.message
            })
            
            # Verificar cache
            cache_key = self.cache._generate_key(optimized_context[:-1], request.message)
            cached_response = self.cache.get(cache_key)
            
            if cached_response:
                cached_response.session_id = request.session_id
                cached_response.metadata = {
                    **cached_response.metadata,
                    "cached": True,
                    "cache_hit": True
                }
                return cached_response
            
            # Chamar Groq API
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=optimized_context,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stream=False
            )
            
            # Extrair resposta
            response_content = completion.choices[0].message.content
            
            # Extrair informações do usuário
            user_profile = self._extract_user_profile(request.message)
            
            # Detectar intenção
            intent = self._detect_intent(request.message)
            
            # Calcular confiança baseada na resposta
            confidence = 0.8  # Base inicial, pode ser melhorada
            
            response = LLMResponse(
                message=response_content,
                session_id=request.session_id,
                user_profile_extracted=user_profile,
                intent_detected=intent,
                confidence=confidence,
                metadata={
                    "model": self.model,
                    "tokens_used": completion.usage.total_tokens if hasattr(completion, 'usage') else None,
                    "timestamp": datetime.now().isoformat(),
                    "cached": False,
                    "cache_hit": False
                }
            )
            
            # Armazenar no cache
            self.cache.set(cache_key, response)
            
            return response
            
        except Exception as e:
            # Fallback em caso de erro
            fallback_response = "Desculpe, estou com dificuldades técnicas no momento. Pode tentar novamente em alguns instantes?"
            
            return LLMResponse(
                message=fallback_response,
                session_id=request.session_id,
                confidence=0.0,
                metadata={"error": str(e), "fallback": True}
            )

    def create_welcome_message(self) -> str:
        """Cria mensagem de boas-vindas personalizada"""
        return """Olá! 👋 

Sou o assistente da /-HALL-DEV, especialista em soluções tecnológicas.

Estou aqui para entender como posso ajudar você ou sua empresa a:
• Reduzir custos operacionais
• Aumentar a precisão e eficiência
• Elevar o padrão tecnológico
• Automatizar processos

Como posso te ajudar hoje? Qual desafio você está enfrentando?"""

    def create_session_id(self) -> str:
        """Cria ID único para sessão"""
        return f"session_{uuid.uuid4().hex[:8]}"
    
    def get_cache_stats(self) -> Dict:
        """Retorna estatísticas do cache"""
        return self.cache.get_stats()
    
    def clear_cache(self):
        """Limpa o cache"""
        self.cache.cache.clear()
    
    def cleanup_cache(self):
        """Remove itens expirados do cache"""
        self.cache.clear_expired()

# Instância global do serviço
llm_service = LLMService() 