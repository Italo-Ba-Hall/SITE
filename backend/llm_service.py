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
from collections import OrderedDict
import groq
from dotenv import load_dotenv

from schemas import ChatMessage, MessageRole, UserProfile, LLMRequest, LLMResponse

# Carregar variáveis de ambiente
load_dotenv()

class LLMCache:
    """Sistema de cache para respostas do LLM"""
    
    def __init__(self, max_size: int = 1000, ttl_hours: int = 24):
        self.cache: OrderedDict[str, Dict] = OrderedDict()
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
                # Mover para o final (LRU)
                self.cache.move_to_end(key)
                return cached["response"]
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, response: LLMResponse):
        """Armazena resposta no cache"""
        if len(self.cache) >= self.max_size:
            # Remove item mais antigo (primeiro da OrderedDict) - O(1)
            self.cache.popitem(last=False)
        
        self.cache[key] = {
            "response": response,
            "timestamp": datetime.now()
        }
        # Mover para o final (LRU)
        self.cache.move_to_end(key)
    
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
        # Verificar se API key está definida
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY não está definida no ambiente")
        
        self.client = groq.Groq(api_key=api_key)
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
- EXTREMAMENTE CONCISO: Máximo 2-3 frases por resposta
- DIRETO AO PONTO: Sem explicações desnecessárias
- PERGUNTADOR ESTRATÉGICO: Foque apenas em fazer perguntas específicas
- NATURAL: Conduza a conversa de forma orgânica

ESTRATÉGIA DE ABORDAGEM:
1. PRIMEIRO PERGUNTE: Sempre comece com perguntas específicas
2. ENTENDA A DOR: Descubra qual problema o usuário precisa resolver
3. COLETE DADOS NATURALMENTE: Nome e email durante a conversa
4. SUGIRA REUNIÃO: Termine propondo agendamento flexível

PERGUNTAS ESTRATÉGICAS PARA USAR:
- "Que tipo de processo você gostaria de melhorar?"
- "Qual é o maior desafio que você está enfrentando?"
- "Como isso está impactando seus resultados?"
- "Que tipo de solução você imagina que resolveria isso?"
- "Qual seria o impacto ideal para sua empresa?"

SERVIÇOS DA EMPRESA:
- Desenvolvimento de Software
- Business Intelligence (BI)
- Machine Learning
- Automação e RPA
- Inteligência Artificial

INSTRUÇÕES DE FORMATAÇÃO OBRIGATÓRIAS:
IMPORTANTE: SEMPRE use formatação visual para tornar suas respostas mais amigáveis e legíveis:

1. EMOJIS: Use emojis relevantes para tornar o texto mais humano e amigável
   - ✅ Para confirmações
   - 💡 Para ideias/sugestões
   - 🔧 Para soluções técnicas
   - 📊 Para dados/KPIs
   - 🎯 Para objetivos
   - 👋 Para saudações
   - 📧 Para contatos
   - ⚡ Para urgência/eficiência
   - 🤖 Para automação/bots
   - 📅 Para agendamentos
   - 👥 Para equipes/pessoas
   - ❓ Para perguntas

2. ESTRUTURA VISUAL OBRIGATÓRIA:
   - SEMPRE use quebras de linha (\\n) para separar ideias
   - Crie tópicos com • ou - para listas
   - Use espaçamento adequado entre seções
   - Destaque informações importantes
   - SEMPRE pule uma linha antes de listas ou tópicos

3. EXEMPLO DE FORMATAÇÃO CORRETA:
```
👋 Olá! Que prazer em conhecê-lo!

❓ Para te ajudar melhor, me conte:

• Que tipo de processo você gostaria de melhorar?
• Qual é o maior desafio que está enfrentando?

💡 Assim posso entender exatamente como posso te ajudar!
```

4. REGRAS OBRIGATÓRIAS:
- SEMPRE use \\n para quebras de linha
- SEMPRE pule uma linha antes de listas
- Use emojis com moderação (não exagere)
- Mantenha o texto bem estruturado
- Faça perguntas específicas
- Colete dados naturalmente durante a conversa
- SEMPRE formate listas com quebras de linha adequadas
- SEJA EXTREMAMENTE CONCISO: Máximo 2-3 frases
- FOCE EM PERGUNTAR: Mais perguntas, menos explicações
- NUNCA IGNORE A PRIMEIRA MENSAGEM: Sempre responda ao conteúdo específico

FORMATO DE RESPOSTA:
Responda de forma natural, amigável e bem estruturada. Use emojis e formatação visual para tornar a experiência mais agradável. SEMPRE aplique quebras de linha adequadas. SEJA EXTREMAMENTE CONCISO E DIRETO. NUNCA IGNORE O CONTEÚDO DA PRIMEIRA MENSAGEM DO USUÁRIO."""

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
            "mentoring": ["mentoria", "mentor"],
            "learning": ["aprender", "estudar", "curso", "treinamento", "formação"],
            "programming": ["programar", "programação", "código", "desenvolver", "coding"],
            "self_learning": ["sozinho", "autodidata", "independente", "por conta própria"],
            "help_request": ["ajudar", "ajuda", "suporte", "assistência"],
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

    def _get_contextual_prompt(self, message: str, detected_intent: Optional[str]) -> str:
        """Gera prompt contextual baseado na intenção detectada"""
        message_lower = message.lower()
        
        # Contexto específico para mentoria e aprendizado
        if detected_intent in ["mentoring", "learning", "programming", "self_learning"]:
            return """Você é um agente especializado da /-HALL-DEV que oferece mentoria e treinamento em programação.

PERSONALIDADE:
- EXTREMAMENTE CONCISO: Máximo 2-3 frases por resposta
- DIRETO AO PONTO: Sem explicações desnecessárias
- PERGUNTADOR ESTRATÉGICO: Foque apenas em fazer perguntas específicas
- NATURAL: Conduza a conversa de forma orgânica

SERVIÇOS DE MENTORIA:
- Mentoria Individual em Programação
- Treinamentos Corporativos
- Cursos Personalizados
- Acompanhamento de Projetos
- Consultoria Técnica

ESTRATÉGIA PARA MENTORIA:
1. ENTENDA O OBJETIVO: Descubra o que o usuário quer aprender
2. AVALIE O NÍVEL: Pergunte sobre experiência prévia
3. SUGIRA ABORDAGEM: Proponha metodologia personalizada
4. COLETE DADOS: Nome, email e disponibilidade
5. AGENDE CONSULTA: Termine propondo sessão gratuita

PERGUNTAS ESTRATÉGICAS PARA MENTORIA:
- "Que linguagem de programação você quer aprender?"
- "Você já tem alguma experiência com programação?"
- "Qual é seu objetivo principal com o aprendizado?"
- "Que tipo de projeto você gostaria de desenvolver?"
- "Qual seria sua disponibilidade para as sessões?"

INSTRUÇÕES DE FORMATAÇÃO OBRIGATÓRIAS:
IMPORTANTE: SEMPRE use formatação visual para tornar suas respostas mais amigáveis e legíveis:

1. EMOJIS: Use emojis relevantes para tornar o texto mais humano e amigável
   - ✅ Para confirmações
   - 💡 Para ideias/sugestões
   - 🔧 Para soluções técnicas
   - 📊 Para dados/KPIs
   - 🎯 Para objetivos
   - 👋 Para saudações
   - 📧 Para contatos
   - ⚡ Para urgência/eficiência
   - 🤖 Para automação/bots
   - 📅 Para agendamentos
   - 👥 Para equipes/pessoas
   - ❓ Para perguntas
   - 🎓 Para educação/mentoria
   - 💻 Para programação/tecnologia

2. ESTRUTURA VISUAL OBRIGATÓRIA:
   - SEMPRE use quebras de linha (\\n) para separar ideias
   - Crie tópicos com • ou - para listas
   - Use espaçamento adequado entre seções
   - Destaque informações importantes
   - SEMPRE pule uma linha antes de listas ou tópicos

3. EXEMPLO DE FORMATAÇÃO CORRETA:
```
🎓 Que ótimo! Vamos te ajudar a aprender programação!

❓ Para personalizar sua mentoria, me conte:

• Que linguagem de programação você quer aprender?
• Você já tem alguma experiência com código?

💻 Assim posso criar um plano de estudos perfeito para você!
```

4. REGRAS OBRIGATÓRIAS:
- SEMPRE use \\n para quebras de linha
- SEMPRE pule uma linha antes de listas
- Use emojis com moderação (não exagere)
- Mantenha o texto bem estruturado
- Faça perguntas específicas sobre mentoria
- Colete dados naturalmente durante a conversa
- SEMPRE formate listas com quebras de linha adequadas
- SEJA EXTREMAMENTE CONCISO: Máximo 2-3 frases
- FOCE EM PERGUNTAR: Mais perguntas, menos explicações
- NUNCA IGNORE A PRIMEIRA MENSAGEM: Sempre responda ao conteúdo específico sobre mentoria

FORMATO DE RESPOSTA:
Responda de forma natural, amigável e bem estruturada. Use emojis e formatação visual para tornar a experiência mais agradável. SEMPRE aplique quebras de linha adequadas. SEJA EXTREMAMENTE CONCISO E DIRETO. NUNCA IGNORE O CONTEÚDO DA PRIMEIRA MENSAGEM DO USUÁRIO."""

        # Contexto específico para solicitações de ajuda
        elif detected_intent == "help_request":
            return """Você é um agente especializado da /-HALL-DEV que oferece ajuda e suporte técnico.

PERSONALIDADE:
- EXTREMAMENTE CONCISO: Máximo 2-3 frases por resposta
- DIRETO AO PONTO: Sem explicações desnecessárias
- PERGUNTADOR ESTRATÉGICO: Foque apenas em fazer perguntas específicas
- NATURAL: Conduza a conversa de forma orgânica

SERVIÇOS DE AJUDA:
- Suporte Técnico
- Consultoria Especializada
- Resolução de Problemas
- Implementação de Soluções
- Treinamento e Capacitação

ESTRATÉGIA PARA AJUDA:
1. ENTENDA O PROBLEMA: Descubra exatamente o que precisa ser resolvido
2. AVALIE A URGÊNCIA: Pergunte sobre prazos e impacto
3. SUGIRA SOLUÇÃO: Proponha abordagem adequada
4. COLETE DADOS: Nome, email e contexto do problema
5. AGENDE SUPORTE: Termine propondo consulta gratuita

PERGUNTAS ESTRATÉGICAS PARA AJUDA:
- "Que tipo de problema você está enfrentando?"
- "Qual é o impacto disso no seu trabalho?"
- "Você já tentou alguma solução?"
- "Qual seria o prazo ideal para resolver?"
- "Que tipo de suporte você imagina que resolveria?"

INSTRUÇÕES DE FORMATAÇÃO OBRIGATÓRIAS:
IMPORTANTE: SEMPRE use formatação visual para tornar suas respostas mais amigáveis e legíveis:

1. EMOJIS: Use emojis relevantes para tornar o texto mais humano e amigável
   - ✅ Para confirmações
   - 💡 Para ideias/sugestões
   - 🔧 Para soluções técnicas
   - 📊 Para dados/KPIs
   - 🎯 Para objetivos
   - 👋 Para saudações
   - 📧 Para contatos
   - ⚡ Para urgência/eficiência
   - 🤖 Para automação/bots
   - 📅 Para agendamentos
   - 👥 Para equipes/pessoas
   - ❓ Para perguntas
   - 🆘 Para ajuda/suporte
   - ⚠️ Para problemas/alertas

2. ESTRUTURA VISUAL OBRIGATÓRIA:
   - SEMPRE use quebras de linha (\\n) para separar ideias
   - Crie tópicos com • ou - para listas
   - Use espaçamento adequado entre seções
   - Destaque informações importantes
   - SEMPRE pule uma linha antes de listas ou tópicos

3. EXEMPLO DE FORMATAÇÃO CORRETA:
```
🆘 Entendo! Vamos te ajudar a resolver isso!

❓ Para te dar o melhor suporte, me conte:

• Que tipo de problema você está enfrentando?
• Qual é o impacto disso no seu trabalho?

🔧 Assim posso conectar você com a solução ideal!
```

4. REGRAS OBRIGATÓRIAS:
- SEMPRE use \\n para quebras de linha
- SEMPRE pule uma linha antes de listas
- Use emojis com moderação (não exagere)
- Mantenha o texto bem estruturado
- Faça perguntas específicas sobre o problema
- Colete dados naturalmente durante a conversa
- SEMPRE formate listas com quebras de linha adequadas
- SEJA EXTREMAMENTE CONCISO: Máximo 2-3 frases
- FOCE EM PERGUNTAR: Mais perguntas, menos explicações
- NUNCA IGNORE A PRIMEIRA MENSAGEM: Sempre responda ao conteúdo específico sobre ajuda

FORMATO DE RESPOSTA:
Responda de forma natural, amigável e bem estruturada. Use emojis e formatação visual para tornar a experiência mais agradável. SEMPRE aplique quebras de linha adequadas. SEJA EXTREMAMENTE CONCISO E DIRETO. NUNCA IGNORE O CONTEÚDO DA PRIMEIRA MENSAGEM DO USUÁRIO."""

        # Contexto padrão para outras intenções
        else:
            return self.system_prompt

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
            # Validar entrada
            if not request.message or not request.message.strip():
                return LLMResponse(
                    message="Por favor, digite uma mensagem para que eu possa te ajudar.",
                    session_id=request.session_id,
                    confidence=0.0,
                    metadata={"error": "empty_message"}
                )
            
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
            
            # Detectar intenção
            detected_intent = self._detect_intent(request.message)
            
            # Gerar prompt contextual
            contextual_prompt = self._get_contextual_prompt(request.message, detected_intent)
            
            # Substituir o prompt do sistema pelo contextual
            optimized_context[0] = {"role": "system", "content": contextual_prompt}
            
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
            
            # Usar a intenção já detectada
            intent = detected_intent
            
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
        return """👋 Olá! Que prazer em conhecê-lo!

❓ Para te ajudar melhor, me conte:

• Que tipo de processo você gostaria de melhorar?
• Qual é o maior desafio que está enfrentando?

💡 Assim posso entender exatamente como posso te ajudar!"""

    def create_session_id(self) -> str:
        """Cria ID único para sessão"""
        return f"session_{uuid.uuid4().hex[:8]}"
    
    def get_cache_stats(self) -> Dict:
        """Retorna estatísticas do cache"""
        return self.cache.get_stats()
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas gerais do LLM Service"""
        return {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "cache_stats": self.cache.get_stats(),
            "request_count": self.request_count,
            "max_requests_per_minute": self.max_requests_per_minute
        }
    
    def clear_cache(self):
        """Limpa o cache"""
        self.cache.clear()
    
    def cleanup_cache(self):
        """Remove itens expirados do cache"""
        self.cache.clear_expired()
    
    def auto_cleanup_cache(self):
        """Limpeza automática do cache - chamar periodicamente"""
        if len(self.cache.cache) > self.cache.max_size * 0.8:  # Se 80% cheio
            self.cache.clear_expired()
            # Se ainda estiver cheio, remover 20% dos itens mais antigos
            if len(self.cache.cache) > self.cache.max_size * 0.8:
                items_to_remove = int(len(self.cache.cache) * 0.2)
                for _ in range(items_to_remove):
                    if self.cache.cache:
                        self.cache.cache.popitem(last=False)

# Instância global do serviço
llm_service = LLMService() 