"""
Gerenciador de Sessões de Chat
/-HALL-DEV Backend
"""

import uuid
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from schemas import ChatSession, ChatMessage, MessageRole, UserProfile
from llm_service import llm_service

class ChatManager:
    """Gerenciador de sessões de chat"""
    
    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}
        self.session_timeout = timedelta(hours=2)  # 2 horas de timeout
    
    def create_session(self, user_id: Optional[str] = None) -> ChatSession:
        """Cria uma nova sessão de chat"""
        session_id = llm_service.create_session_id()
        
        # Criar mensagem de boas-vindas
        welcome_message = ChatMessage(
            role=MessageRole.ASSISTANT,
            content=llm_service.create_welcome_message()
        )
        
        session = ChatSession(
            session_id=session_id,
            user_id=user_id,
            messages=[welcome_message],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_active=True
        )
        
        self.sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Recupera uma sessão de chat"""
        session = self.sessions.get(session_id)
        
        if session and session.is_active:
            # Verificar timeout
            if datetime.now() - session.updated_at > self.session_timeout:
                session.is_active = False
                return None
            
            return session
        
        return None
    
    def add_message(self, session_id: str, role: MessageRole, content: str, metadata: Optional[Dict] = None) -> bool:
        """Adiciona uma mensagem à sessão"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        message = ChatMessage(
            role=role,
            content=content,
            metadata=metadata
        )
        
        session.messages.append(message)
        session.updated_at = datetime.now()
        
        return True
    
    def update_user_profile(self, session_id: str, profile_data: Dict[str, str]) -> bool:
        """Atualiza o perfil do usuário na sessão"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        if not session.user_profile:
            session.user_profile = {}
        
        session.user_profile.update(profile_data)
        session.updated_at = datetime.now()
        
        return True
    
    def end_session(self, session_id: str, reason: Optional[str] = None) -> Optional[ChatSession]:
        """Finaliza uma sessão de chat"""
        session = self.get_session(session_id)
        if not session:
            return None
        
        session.is_active = False
        session.updated_at = datetime.now()
        
        # Aqui você pode implementar lógica adicional
        # como salvar dados do lead, enviar email, etc.
        
        return session
    
    def get_conversation_summary(self, session_id: str) -> Optional[Dict]:
        """Gera um resumo da conversa"""
        session = self.get_session(session_id)
        if not session:
            return None
        
        # Contar mensagens
        user_messages = [msg for msg in session.messages if msg.role == MessageRole.USER]
        assistant_messages = [msg for msg in session.messages if msg.role == MessageRole.ASSISTANT]
        
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
            "duration_minutes": (session.updated_at - session.created_at).total_seconds() / 60,
            "user_profile": user_profile,
            "detected_intents": list(set(intents)),
            "created_at": session.created_at,
            "ended_at": session.updated_at
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
    
    def get_session_stats(self) -> Dict:
        """Retorna estatísticas das sessões"""
        total_sessions = len(self.sessions)
        active_sessions = self.get_active_sessions_count()
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "expired_sessions": total_sessions - active_sessions
        }

# Instância global do gerenciador
chat_manager = ChatManager() 