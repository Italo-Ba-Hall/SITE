"""
Gerenciador de Sessões de Chat
/-HALL-DEV Backend
"""

import logging
from datetime import datetime, timedelta

from database import db_manager
from llm_service import llm_service
from notification_service import notification_service
from schemas import ChatMessage, ChatSession, MessageRole, Phase

# Configurar logger
logger = logging.getLogger(__name__)


class ChatManager:
    """Gerenciador de sessões de chat"""

    def __init__(self):
        self.sessions: dict[str, ChatSession] = {}
        self.session_timeout = timedelta(minutes=15)  # 15 minutos de timeout
        self.warning_timeout = timedelta(minutes=10)  # Aviso após 10 minutos
        self.inactivity_warnings: dict[str, datetime] = {}  # Controle de avisos

    def create_session(self, user_id: str | None = None) -> ChatSession:
        """Cria uma nova sessão de chat"""
        session_id = llm_service.create_session_id()

        # Criar mensagem de boas-vindas
        welcome_message = ChatMessage(
            role=MessageRole.ASSISTANT, content=llm_service.create_welcome_message()
        )

        session = ChatSession(
            session_id=session_id,
            user_id=user_id,
            messages=[welcome_message],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_active=True,
        )

        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> ChatSession | None:
        """Recupera uma sessão de chat"""
        session = self.sessions.get(session_id)

        if session and session.is_active:
            # Verificar timeout
            if datetime.now() - session.updated_at > self.session_timeout:
                session.is_active = False
                return None

            return session

        return None

    def check_inactivity_warning(self, session_id: str) -> str | None:
        """Verifica se deve enviar aviso de inatividade"""
        session = self.get_session(session_id)
        if not session:
            return None

        time_since_update = datetime.now() - session.updated_at

        # Se passou 10 minutos e ainda não foi enviado aviso
        if (
            time_since_update > self.warning_timeout
            and session_id not in self.inactivity_warnings
        ):
            self.inactivity_warnings[session_id] = datetime.now()

            # Calcular tempo restante
            remaining_minutes = int(
                (self.session_timeout - time_since_update).total_seconds() / 60
            )

            return (
                f"⚠️ Olá! Notei que você está inativo há alguns minutos.\n\n"
                f"💡 Para continuarmos nossa conversa, você tem mais {remaining_minutes} minutos.\n\n"
                f"📧 Caso precise de mais tempo, posso salvar seu contato para retomarmos depois.\n\n"
                f"O que gostaria de fazer?"
            )

        return None

    def add_message(
        self,
        session_id: str,
        role: MessageRole,
        content: str,
        metadata: dict | None = None,
    ) -> bool:
        """Adiciona uma mensagem à sessão"""
        session = self.get_session(session_id)
        if not session:
            return False

        message = ChatMessage(role=role, content=content, metadata=metadata)

        session.messages.append(message)
        session.updated_at = datetime.now()

        # Remover aviso de inatividade se usuário respondeu
        if session_id in self.inactivity_warnings:
            del self.inactivity_warnings[session_id]

        # Atualizar fase conforme progresso
        self._advance_phase(session)

        return True

    def update_user_profile(
        self, session_id: str, profile_data: dict[str, str]
    ) -> bool:
        """Atualiza o perfil do usuário na sessão"""
        session = self.get_session(session_id)
        if not session:
            return False

        if not session.user_profile:
            session.user_profile = {}

        session.user_profile.update(profile_data)
        session.updated_at = datetime.now()

        # Atualizar fase ao obter dados do perfil
        self._advance_phase(session)

        # Auto-persistir lead e conversa ao capturar email pela primeira vez
        try:
            has_email = bool(session.user_profile.get("email"))
            if has_email:
                existing = db_manager.get_lead(session.session_id)
                if not existing:
                    self._persist_conversation_messages(session)
                    self._save_lead_from_session(session, save_full_conversation=True)
        except Exception as e:
            logger.warning(f"Erro ao salvar sessão {session_id}: {e}")

        return True

    def _advance_phase(self, session: ChatSession) -> None:
        """Atualiza a fase da sessão com base nas mensagens e dados coletados"""
        try:
            # Se ainda em discovery e já houve pelo menos 1 mensagem do usuário, ir para captura de lead
            if session.phase == Phase.DISCOVERY:
                user_msgs = [m for m in session.messages if m.role == MessageRole.USER]
                if len(user_msgs) >= 1:
                    session.phase = Phase.LEAD_CAPTURE

            # Se já temos nome e email, ir para fase de agendamento
            has_name = bool((session.user_profile or {}).get("name"))
            has_email = bool((session.user_profile or {}).get("email"))
            if has_name and has_email:
                session.phase = Phase.SCHEDULING
        except Exception as e:
            logger.warning(f"Erro ao avançar fase da sessão {session.session_id}: {e}")

    def _persist_conversation_messages(self, session: ChatSession) -> None:
        """Persiste as mensagens atuais da sessão na tabela de conversas."""
        try:
            if not session.messages:
                return
            messages_data: list[dict] = []
            for msg in session.messages:
                messages_data.append(
                    {
                        "role": msg.role.value,
                        "content": msg.content,
                        "metadata": msg.metadata,
                        "timestamp": msg.timestamp,
                    }
                )
            db_manager.save_conversation(session.session_id, messages_data)
        except Exception as e:
            logger.warning(
                f"Erro ao persistir mensagens da sessão {session.session_id}: {e}"
            )

    def end_session(
        self, session_id: str, reason: str | None = None
    ) -> ChatSession | None:
        """Finaliza uma sessão de chat e salva os dados do lead"""
        session = self.get_session(session_id)
        if not session:
            return None

        session.is_active = False
        session.updated_at = datetime.now()

        # Remover aviso de inatividade
        if session_id in self.inactivity_warnings:
            del self.inactivity_warnings[session_id]

        # Salvar conversa no banco de dados
        if session.messages:
            messages_data = []
            for msg in session.messages:
                messages_data.append(
                    {
                        "role": msg.role.value,
                        "content": msg.content,
                        "metadata": msg.metadata,
                        "timestamp": msg.timestamp,
                    }
                )

            db_manager.save_conversation(session_id, messages_data)

        # Salvar lead se tiver dados suficientes
        if session.user_profile and session.user_profile.get("email"):
            self._save_lead_from_session(session, save_full_conversation=True)
        else:
            # Se não tem email, salvar apenas resumo
            self._save_conversation_summary_only(session)

        return session

    def _save_lead_from_session(
        self, session: ChatSession, save_full_conversation: bool = True
    ):
        """Salva lead baseado nos dados da sessão"""
        try:
            # Gerar resumo da conversa
            conversation_summary = self._generate_conversation_summary(session)

            # Detectar pontos de dor
            pain_points = self._detect_pain_points(session)

            # Detectar soluções recomendadas
            recommended_solutions = self._detect_recommended_solutions(session)

            # Calcular score de qualificação
            qualification_score = self._calculate_qualification_score(session)

            # Salvar no banco de dados
            lead_id = db_manager.save_lead(
                session_id=session.session_id,
                user_profile=session.user_profile or {},
                conversation_summary=conversation_summary,
                pain_points=pain_points,
                recommended_solutions=recommended_solutions,
                qualification_score=qualification_score,
                full_conversation=session.messages if save_full_conversation else None,
            )

            # Garantir que exista um resumo em conversation_summaries para o dashboard
            try:
                # Detectar intenções principais
                intents: list[str] = []
                for msg in session.messages:
                    if msg.role == MessageRole.USER:
                        intent = llm_service._detect_intent(msg.content)
                        if intent:
                            intents.append(intent)
                duration_minutes = (
                    session.updated_at - session.created_at
                ).total_seconds() / 60
                db_manager.save_conversation_summary(
                    session_id=session.session_id,
                    summary=conversation_summary,
                    intents=list(set(intents)),
                    duration_minutes=duration_minutes,
                )
            except Exception as e:
                logger.warning(
                    f"Erro ao salvar lead da sessão {session.session_id}: {e}"
                )

            # Notificar equipe
            lead_data = {
                "name": session.user_profile.get("name", "Sem nome"),
                "email": session.user_profile.get("email", "Sem email"),
                "company": session.user_profile.get("company", "Sem empresa"),
                "role": session.user_profile.get("role", "Sem cargo"),
                "qualification_score": qualification_score,
                "conversation_summary": conversation_summary,
                "pain_points": pain_points,
                "recommended_solutions": recommended_solutions,
            }

            notification_service.notify_new_lead(lead_data)

            print(f"✅ Lead salvo com ID: {lead_id}")

        except Exception as e:
            print(f"❌ Erro ao salvar lead: {e!s}")

    def _save_conversation_summary_only(self, session: ChatSession):
        """Salva apenas resumo da conversa quando não há email"""
        try:
            # Gerar resumo conciso
            summary = self._generate_conversation_summary(session)

            # Detectar intenções principais
            intents = []
            for msg in session.messages:
                if msg.role == MessageRole.USER:
                    intent = llm_service._detect_intent(msg.content)
                    if intent:
                        intents.append(intent)

            # Salvar apenas resumo
            db_manager.save_conversation_summary(
                session_id=session.session_id,
                summary=summary,
                intents=list(set(intents)),
                duration_minutes=(
                    session.updated_at - session.created_at
                ).total_seconds()
                / 60,
            )

            print(f"✅ Resumo de conversa salvo para sessão: {session.session_id}")

        except Exception as e:
            print(f"❌ Erro ao salvar resumo: {e!s}")

    def _generate_conversation_summary(self, session: ChatSession) -> str:
        """Gera um resumo da conversa"""
        user_messages = [
            msg.content for msg in session.messages if msg.role == MessageRole.USER
        ]
        assistant_messages = [
            msg.content for msg in session.messages if msg.role == MessageRole.ASSISTANT
        ]

        summary = f"Conversa com {len(user_messages)} mensagens do usuário e {len(assistant_messages)} respostas do assistente."

        if user_messages:
            # Pegar as primeiras mensagens para contexto
            context_messages = user_messages[:3]
            summary += f" Contexto inicial: {' '.join(context_messages[:100])}..."

        return summary

    def _detect_pain_points(self, session: ChatSession) -> list[str]:
        """Detecta pontos de dor mencionados na conversa"""
        pain_points = []
        keywords = [
            "problema",
            "dificuldade",
            "dor",
            "desafio",
            "lento",
            "caro",
            "ineficiente",
            "manual",
            "repetitivo",
            "erro",
            "falha",
            "tempo",
            "custo",
            "processo",
            "sistema",
            "tecnologia",
        ]

        for msg in session.messages:
            if msg.role == MessageRole.USER:
                content_lower = msg.content.lower()
                for keyword in keywords:
                    if keyword in content_lower:
                        # Extrair contexto da dor
                        words = msg.content.split()
                        for i, word in enumerate(words):
                            if keyword in word.lower():
                                start = max(0, i - 3)
                                end = min(len(words), i + 4)
                                context = " ".join(words[start:end])
                                pain_points.append(context)
                                break

        return list(set(pain_points))[:5]  # Máximo 5 pontos de dor

    def _detect_recommended_solutions(self, session: ChatSession) -> list[str]:
        """Detecta soluções recomendadas na conversa"""
        solutions = []
        solution_keywords = [
            "automação",
            "software",
            "sistema",
            "plataforma",
            "dashboard",
            "bi",
            "business intelligence",
            "machine learning",
            "ia",
            "inteligência artificial",
            "rpa",
            "processo",
            "otimização",
            "integração",
            "api",
        ]

        for msg in session.messages:
            if msg.role == MessageRole.ASSISTANT:
                content_lower = msg.content.lower()
                for keyword in solution_keywords:
                    if keyword in content_lower:
                        solutions.append(f"Solução com {keyword}")

        return list(set(solutions))[:3]  # Máximo 3 soluções

    def _calculate_qualification_score(self, session: ChatSession) -> float:
        """Calcula score de qualificação do lead"""
        score = 0.0

        # Critérios de qualificação
        if session.user_profile:
            # Nome fornecido
            if session.user_profile.get("name"):
                score += 0.2

            # Email fornecido
            if session.user_profile.get("email"):
                score += 0.3

            # Empresa mencionada
            if session.user_profile.get("company"):
                score += 0.2

            # Cargo mencionado
            if session.user_profile.get("role"):
                score += 0.1

        # Duração da conversa
        duration_minutes = (
            session.updated_at - session.created_at
        ).total_seconds() / 60
        if duration_minutes > 5:
            score += 0.1
        if duration_minutes > 10:
            score += 0.1

        # Número de mensagens
        user_messages = [
            msg for msg in session.messages if msg.role == MessageRole.USER
        ]
        if len(user_messages) > 3:
            score += 0.1

        return min(score, 1.0)  # Máximo 1.0

    def get_conversation_summary(self, session_id: str) -> dict | None:
        """Gera um resumo da conversa"""
        session = self.get_session(session_id)
        if not session:
            return None

        # Contar mensagens
        user_messages = [
            msg for msg in session.messages if msg.role == MessageRole.USER
        ]
        assistant_messages = [
            msg for msg in session.messages if msg.role == MessageRole.ASSISTANT
        ]

        # Extrair informações do perfil
        user_profile = session.user_profile or {}

        # Detectar intenções principais
        intents = []
        for msg in user_messages:
            intent = llm_service._detect_intent(msg.content)
            if intent:
                intents.append(intent)

        return {
            "session_id": session_id,
            "total_messages": len(session.messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "duration_minutes": (
                session.updated_at - session.created_at
            ).total_seconds()
            / 60,
            "user_profile": user_profile,
            "detected_intents": list(set(intents)),
            "created_at": session.created_at,
            "ended_at": session.updated_at,
        }

    def cleanup_expired_sessions(self) -> int:
        """Remove sessões expiradas"""
        current_time = datetime.now()
        expired_sessions = []

        for session_id, session in self.sessions.items():
            if current_time - session.updated_at > self.session_timeout:
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            del self.sessions[session_id]

        return len(expired_sessions)

    def get_active_sessions_count(self) -> int:
        """Retorna o número de sessões ativas"""
        return len([s for s in self.sessions.values() if s.is_active])

    def get_session_stats(self) -> dict:
        """Retorna estatísticas das sessões"""
        total_sessions = len(self.sessions)
        active_sessions = self.get_active_sessions_count()

        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "expired_sessions": total_sessions - active_sessions,
        }


# Instância global do gerenciador
chat_manager = ChatManager()
