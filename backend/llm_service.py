"""
Serviço de LLM usando Google Gemini
/-HALL-DEV Backend
"""

import hashlib
import json
import logging
import os
import uuid
from collections import OrderedDict
from datetime import datetime, timedelta
from typing import Any

import google.generativeai as genai
from dotenv import load_dotenv

from schemas import (
    ChatMessage,
    LLMRequest,
    LLMResponse,
    MessageRole,
    Phase,
)

# Configurar logger
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()


class LLMCache:
    """Sistema de cache para respostas do LLM"""

    def __init__(self, max_size: int = 1000, ttl_hours: int = 24):
        self.cache: OrderedDict[str, dict] = OrderedDict()
        self.max_size = max_size
        self.ttl = timedelta(hours=ttl_hours)

    def _generate_key(self, messages: list[dict], user_message: str) -> str:
        """Gera chave única para cache baseada no contexto e mensagem"""
        context_str = json.dumps([msg["content"] for msg in messages], sort_keys=True)
        combined = f"{context_str}:{user_message}"
        return hashlib.sha256(combined.encode()).hexdigest()

    def get(self, key: str) -> LLMResponse | None:
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

        self.cache[key] = {"response": response, "timestamp": datetime.now()}
        # Mover para o final (LRU)
        self.cache.move_to_end(key)

    def clear_expired(self):
        """Remove itens expirados do cache"""
        current_time = datetime.now()
        expired_keys = [
            key
            for key, value in self.cache.items()
            if current_time - value["timestamp"] > self.ttl
        ]
        for key in expired_keys:
            del self.cache[key]

    def get_stats(self) -> dict:
        """Retorna estatísticas do cache"""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "ttl_hours": self.ttl.total_seconds() / 3600,
        }


class LLMService:
    """Serviço para integração com Google Gemini LLM"""

    def __init__(self):
        # Verificar se API key está definida
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY não está definida no ambiente")

        genai.configure(api_key=api_key)
        
        self.model_name = "gemini-2.5-flash"
        self.max_tokens = 1500
        self.temperature = 0.25

        # Cache de respostas
        self.cache = LLMCache(max_size=500, ttl_hours=12)

        # Rate limiting
        self.request_count = 0
        self.last_reset = datetime.now()
        self.max_requests_per_minute = 60

        # Personalidade do agente
        self.system_prompt = """Você é um agente conversacional especializado da /-HALL-DEV.

PERSONALIDADE:
- EXTREMAMENTE CONCISO (2-3 frases)
- DIRETO AO PONTO
- NATURAL E AMIGÁVEL

FLUXO OBRIGATÓRIO (REGRA DE 2 TURNOS):
1) Discovery: responda à primeira mensagem do usuário com no máximo 2 perguntas específicas e pertinentes ao tema.
2) Lead Capture: após a primeira resposta do usuário, SE nome e email ainda não foram coletados, peça os DOIS em UMA ÚNICA frase, de forma simples e clara.
3) Scheduling: assim que nome e email forem coletados, proponha AGENDAMENTO (apresente opções de horário ou peça disponibilidade) e ofereça UMA ESCOLHA: receber “explicações técnicas rápidas” antes ou “ir direto para o agendamento”.
4) Se o usuário disser “não sei” ou pedir orientação, reduza perguntas, colete nome/email e avance para o agendamento.

SERVIÇOS:
- Desenvolvimento de Software, BI, Machine Learning, Automação/RPA, IA

FORMATAÇÃO VISUAL OBRIGATÓRIA:
- Use quebras de linha (\\n) e listas com •
- Emojis pontuais: 👋 ❓ 💡 📧 📅 💻 🎯

REGRAS GERAIS:
- Sempre responda ao conteúdo específico do usuário
- Mantenha 2-3 frases; sem parágrafos longos
- No máximo 2 perguntas por resposta
- Priorize avançar o fluxo (coleta e agendamento)
"""

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

    def _build_conversation_context(
        self, messages: list[ChatMessage]
    ) -> list[dict[str, str]]:
        """Constrói o contexto da conversa para o LLM"""
        context = [{"role": "system", "content": self.system_prompt}]

        for message in messages:
            context.append({"role": message.role.value, "content": message.content})

        return context

    def _get_phase_from_context(self, ctx: dict[str, Any] | None) -> str | None:
        if not ctx:
            return None
        phase_val = ctx.get("phase")
        if isinstance(phase_val, Phase):
            return phase_val.value
        if isinstance(phase_val, str):
            return phase_val.lower()
        return None

    def _compose_policy_instructions(
        self,
        ctx: dict[str, Any] | None,
        user_message: str,
    ) -> str:
        """Gera instruções de política contextuais para garantir coleta e agendamento."""
        policy_parts: list[str] = []

        # Detectar incerteza para encurtar e conduzir
        user_lower = user_message.lower()
        uncertainty = any(
            k in user_lower
            for k in [
                "não sei",
                "nao sei",
                "preciso de orienta",
                "não entendo",
                "nao entendo",
            ]
        )

        phase = self._get_phase_from_context(ctx)
        profile = (ctx or {}).get("user_profile") or {}
        has_name = bool(profile.get("name"))
        has_email = bool(profile.get("email"))

        # Contar mensagens do usuário no contexto para gatilho de captura
        user_count = 0
        for m in (ctx or {}).get("messages", []) or []:
            try:
                if getattr(m, "role", None) == MessageRole.USER or (
                    isinstance(m, dict)
                    and (m.get("role") == "user" or m.get("role") == MessageRole.USER)
                ):
                    user_count += 1
            except Exception as e:
                logger.warning(f"Erro ao processar mensagem do contexto: {e}")

        # Regra: após a 1ª mensagem do usuário, pedir nome e email se faltarem
        if user_count >= 1 and (not has_name or not has_email):
            if uncertainty:
                policy_parts.append(
                    "Usuário incerto: reduza perguntas. Peça NOME e EMAIL agora em UMA frase curta, então conduza para agendamento."
                )
            else:
                policy_parts.append(
                    "Se NOME/EMAIL faltarem, peça ambos AGORA em UMA frase curta. No máximo 1 pergunta adicional."
                )

        # Se já coletou nome e email, avançar para agendamento com a bifurcação
        if has_name and has_email:
            policy_parts.append(
                "Proponha AGENDAMENTO imediatamente e ofereça escolha: 'explicações técnicas rápidas' OU 'agendar agora'."
            )

        # Fase específica pode reforçar comportamento
        if phase == "lead_capture" and (not has_name or not has_email):
            policy_parts.append(
                "Estamos em LEAD_CAPTURE: priorize coletar NOME e EMAIL nesta resposta."
            )
        if phase == "scheduling" and has_name and has_email:
            policy_parts.append(
                "Estamos em SCHEDULING: foque em confirmar data/horário de reunião."
            )

        # Sempre limitar perguntas
        policy_parts.append("No máximo 2 perguntas na resposta.")

        return " ".join(policy_parts).strip()

    def _extract_user_profile(self, message: str) -> dict[str, str] | None:
        """Extrai informações do usuário da mensagem"""
        # Lógica simples de extração - pode ser melhorada
        profile = {}

        # Extrair nome (padrões comuns)
        import re

        name_patterns = [
            r"meu nome é\s+([\wÀ-ÖØ-öø-ÿ\s]{2,})",
            r"eu sou\s+([\wÀ-ÖØ-öø-ÿ\s]{2,})",
            r"chamo-me\s+([\wÀ-ÖØ-öø-ÿ\s]{2,})",
            r"sou\s+([\wÀ-ÖØ-öø-ÿ\s]{2,})",
        ]

        for pattern in name_patterns:
            match = re.search(pattern, message.lower())
            if match:
                profile["name"] = match.group(1).strip().title()
                break

        # Extrair email
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        email_match = re.search(email_pattern, message)
        if email_match:
            profile["email"] = email_match.group(0)

        return profile if profile else None

    def _detect_intent(self, message: str) -> str | None:
        """Detecta a intenção da mensagem do usuário"""
        message_lower = message.lower()

        intents = {
            "greeting": ["olá", "oi", "bom dia", "boa tarde", "boa noite"],
            "mentoring": ["mentoria", "mentor"],
            "learning": ["aprender", "estudar", "curso", "treinamento", "formação"],
            "programming": [
                "programar",
                "programação",
                "código",
                "desenvolver",
                "coding",
            ],
            "self_learning": [
                "sozinho",
                "autodidata",
                "independente",
                "por conta própria",
            ],
            "help_request": ["ajudar", "ajuda", "suporte", "assistência"],
            "problem_description": [
                "problema",
                "dificuldade",
                "dor",
                "preciso",
                "quero",
            ],
            "service_inquiry": ["serviço", "solução", "desenvolvimento", "software"],
            "contact_info": ["contato", "email", "telefone", "whatsapp"],
            "pricing": ["preço", "valor", "custo", "orçamento"],
            "technical": ["tecnologia", "programação", "código", "sistema"],
        }

        for intent, keywords in intents.items():
            if any(keyword in message_lower for keyword in keywords):
                return intent

        return None

    def _get_contextual_prompt(self, message: str, detected_intent: str | None) -> str:
        """Gera prompt contextual baseado na intenção detectada"""

        # Contexto específico para mentoria e aprendizado
        if detected_intent in ["mentoring", "learning", "programming", "self_learning"]:
            return """Você é um agente da /-HALL-DEV para mentoria/treinamento em programação.

PERSONALIDADE:
- EXTREMAMENTE CONCISO (2-3 frases)
- DIRETO AO PONTO
- NATURAL

SERVIÇOS DE MENTORIA:
- Mentoria Individual em Programação
- Treinamentos Corporativos
- Cursos Personalizados
- Acompanhamento de Projetos
- Consultoria Técnica

FLUXO OBRIGATÓRIO (2 TURNOS):
1) Discovery: no máximo 2 perguntas específicas;
2) Lead Capture: após a 1ª resposta do usuário, peça nome e email em UMA frase;
3) Scheduling: após coletar nome e email, proponha agendamento e ofereça opção: “explicações técnicas rápidas” ou “marcar agora”.

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
- Faça no máximo 2 perguntas
- Peça nome e email após a 1ª resposta do usuário (se ainda não coletados)
- SEMPRE formate listas com quebras de linha adequadas
- SEJA EXTREMAMENTE CONCISO: Máximo 2-3 frases
- NUNCA IGNORE A PRIMEIRA MENSAGEM: Responda ao conteúdo específico

FORMATO DE RESPOSTA:
Responda de forma natural e estruturada, com 2-3 frases. Sempre aplique quebras de linha e ofereça a decisão: “explica rápido” vs “agendar”."""

        # Contexto específico para solicitações de ajuda
        elif detected_intent == "help_request":
            return """Você é um agente da /-HALL-DEV para ajuda e suporte técnico.

PERSONALIDADE:
- EXTREMAMENTE CONCISO (2-3 frases)
- DIRETO AO PONTO
- NATURAL

SERVIÇOS DE AJUDA:
- Suporte Técnico
- Consultoria Especializada
- Resolução de Problemas
- Implementação de Soluções
- Treinamento e Capacitação

FLUXO OBRIGATÓRIO (2 TURNOS):
1) Discovery: no máximo 2 perguntas sobre o problema e impacto;
2) Lead Capture: após a 1ª resposta do usuário, peça nome e email em UMA frase;
3) Scheduling: após coletar, proponha agendamento e ofereça opção: “explicações técnicas rápidas” ou “marcar agora”.

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
- Faça no máximo 2 perguntas
- Peça nome e email após a 1ª resposta do usuário (se ainda não coletados)
- SEMPRE formate listas com quebras de linha adequadas
- SEJA EXTREMAMENTE CONCISO: Máximo 2-3 frases
- NUNCA IGNORE A PRIMEIRA MENSAGEM: Responda ao conteúdo específico

FORMATO DE RESPOSTA:
Responda de forma natural e estruturada, com 2-3 frases. Sempre aplique quebras de linha e ofereça a decisão: “explica rápido” vs “agendar”."""

        # Contexto padrão para outras intenções
        else:
            return self.system_prompt

    def _optimize_prompt_size(
        self, context: list[dict[str, str]]
    ) -> list[dict[str, str]]:
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
                    metadata={"error": "empty_message"},
                )

            # Verificar rate limit
            if not self._check_rate_limit():
                return LLMResponse(
                    message="Desculpe, estamos com muitas solicitações no momento. Tente novamente em alguns instantes.",
                    session_id=request.session_id,
                    confidence=0.0,
                    metadata={"error": "rate_limit_exceeded"},
                )

            # Construir contexto da conversa
            messages = (request.context or {}).get("messages", [])
            conversation_context = self._build_conversation_context(messages)

            # Otimizar tamanho do prompt
            optimized_context = self._optimize_prompt_size(conversation_context)

            # Adicionar mensagem atual do usuário
            optimized_context.append({"role": "user", "content": request.message})

            # Verificar cache
            cache_key = self.cache._generate_key(
                optimized_context[:-1], request.message
            )
            cached_response = self.cache.get(cache_key)

            if cached_response:
                cached_response.session_id = request.session_id
                cached_response.metadata = {
                    **cached_response.metadata,
                    "cached": True,
                    "cache_hit": True,
                }
                return cached_response

            # Detectar intenção
            detected_intent = self._detect_intent(request.message)

            # Gerar prompt contextual
            contextual_prompt = self._get_contextual_prompt(
                request.message, detected_intent
            )

            # Injetar política determinística de captura/agendamento
            policy_instructions = self._compose_policy_instructions(
                request.context, request.message
            )
            if policy_instructions:
                contextual_prompt = f"{contextual_prompt}\n\nPOLÍTICA ATUAL (OBRIGATÓRIA): {policy_instructions}"

            # Criar modelo com system instruction contextual
            model = genai.GenerativeModel(
                self.model_name,
                system_instruction=contextual_prompt
            )

            # Converter histórico para formato Gemini
            history_parts = []
            for msg in optimized_context[1:]:  # Pular system prompt (já está no model)
                role = "user" if msg["role"] == "user" else "model"
                history_parts.append({
                    "role": role,
                    "parts": [msg["content"]]
                })

            # Criar chat com histórico
            chat = model.start_chat(history=history_parts)

            # Enviar mensagem atual
            gemini_response = chat.send_message(
                request.message,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.max_tokens,
                    temperature=self.temperature,
                )
            )

            # Extrair resposta
            response_content = gemini_response.text

            # Extrair informações do usuário
            user_profile = self._extract_user_profile(request.message)

            # Usar a intenção já detectada
            intent = detected_intent

            # Calcular confiança baseada na resposta
            confidence = 0.8  # Base inicial, pode ser melhorada

            # Extrair tokens usados
            tokens_used = None
            if hasattr(gemini_response, 'usage_metadata'):
                tokens_used = gemini_response.usage_metadata.total_token_count

            response = LLMResponse(
                message=response_content,
                session_id=request.session_id,
                user_profile_extracted=user_profile,
                intent_detected=intent,
                confidence=confidence,
                metadata={
                    "model": self.model_name,
                    "tokens_used": tokens_used,
                    "timestamp": datetime.now().isoformat(),
                    "cached": False,
                    "cache_hit": False,
                },
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
                metadata={"error": str(e), "fallback": True},
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

    def get_cache_stats(self) -> dict:
        """Retorna estatísticas do cache"""
        return self.cache.get_stats()

    def get_stats(self) -> dict:
        """Retorna estatísticas gerais do LLM Service"""
        return {
            "model": self.model_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "cache_stats": self.cache.get_stats(),
            "request_count": self.request_count,
            "max_requests_per_minute": self.max_requests_per_minute,
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
