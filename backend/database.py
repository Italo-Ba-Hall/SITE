"""
Sistema de Banco de Dados para /-HALL-DEV
Persistência de Leads e Conversas
"""

import json
import sqlite3
from datetime import datetime
from typing import Any


class DatabaseManager:
    """Gerenciador de banco de dados SQLite"""

    def __init__(self, db_path: str = "hall_dev.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Inicializa o banco de dados com as tabelas necessárias"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Tabela de leads
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    name TEXT,
                    email TEXT,
                    company TEXT,
                    role TEXT,
                    pain_points TEXT,  -- JSON array
                    interests TEXT,    -- JSON array
                    qualification_score REAL DEFAULT 0.0,
                    conversation_summary TEXT,
                    recommended_solutions TEXT,  -- JSON array
                    status TEXT DEFAULT 'new',  -- new, contacted, qualified, converted
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Tabela de conversas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,  -- user, assistant, system
                    content TEXT NOT NULL,
                    metadata TEXT,  -- JSON object
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Tabela de notificações
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lead_id INTEGER,
                    type TEXT NOT NULL,  -- new_lead, lead_qualified, lead_converted
                    message TEXT NOT NULL,
                    is_read BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (lead_id) REFERENCES leads (id)
                )
            """)

            # Tabela de resumos de conversa
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    summary TEXT NOT NULL,
                    intents TEXT,  -- JSON array
                    duration_minutes REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Tabela de atividades do Playground (Transcrição/Sumarização)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS playground_activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_name TEXT NOT NULL,
                    user_email TEXT NOT NULL,
                    video_url TEXT NOT NULL,
                    video_id TEXT NOT NULL,
                    action_type TEXT NOT NULL,  -- 'transcribe' ou 'summarize'
                    exported BOOLEAN DEFAULT 0,
                    export_format TEXT,  -- 'txt', 'pdf', ou NULL
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Índices para performance
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_leads_session_id ON leads(session_id)"
            )
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email)")
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_notifications_lead_id ON notifications(lead_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_playground_email ON playground_activities(user_email)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_playground_video_id ON playground_activities(video_id)"
            )

            conn.commit()

    def save_lead(
        self,
        session_id: str,
        user_profile: dict[str, Any],
        conversation_summary: str,
        pain_points: list[str],
        recommended_solutions: list[str],
        qualification_score: float = 0.0,
        full_conversation: list | None = None,
    ) -> int:
        """Salva um novo lead no banco de dados"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO leads (
                    session_id, name, email, company, role, pain_points,
                    interests, qualification_score, conversation_summary,
                    recommended_solutions, status, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    session_id,
                    user_profile.get("name"),
                    user_profile.get("email"),
                    user_profile.get("company"),
                    user_profile.get("role"),
                    json.dumps(pain_points),
                    json.dumps(user_profile.get("interests", [])),
                    qualification_score,
                    conversation_summary,
                    json.dumps(recommended_solutions),
                    "new",
                    datetime.now(),
                ),
            )

            lead_id = cursor.lastrowid
            if lead_id is None:
                raise ValueError("Falha ao criar lead no banco de dados")

            # Criar notificação de novo lead
            self.create_notification(
                lead_id=lead_id,
                notification_type="new_lead",
                message=f"Novo lead: {user_profile.get('name', 'Sem nome')} ({user_profile.get('email', 'Sem email')})",
            )

            conn.commit()
            return lead_id

    def save_conversation(self, session_id: str, messages: list[dict[str, Any]]):
        """Salva mensagens da conversa no banco de dados"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            for message in messages:
                cursor.execute(
                    """
                    INSERT INTO conversations (session_id, role, content, metadata, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        session_id,
                        message["role"],
                        message["content"],
                        json.dumps(message.get("metadata", {})),
                        message.get("timestamp", datetime.now()),
                    ),
                )

            conn.commit()

    def save_conversation_summary(
        self, session_id: str, summary: str, intents: list[str], duration_minutes: float
    ):
        """Salva apenas um resumo da conversa quando não há email"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Criar tabela de resumos se não existir
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    summary TEXT NOT NULL,
                    intents TEXT,  -- JSON array
                    duration_minutes REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute(
                """
                INSERT OR REPLACE INTO conversation_summaries (
                    session_id, summary, intents, duration_minutes, created_at
                ) VALUES (?, ?, ?, ?, ?)
            """,
                (
                    session_id,
                    summary,
                    json.dumps(intents),
                    duration_minutes,
                    datetime.now(),
                ),
            )

            conn.commit()

    def get_conversation_summary(self, session_id: str) -> dict[str, Any] | None:
        """Recupera resumo de conversa"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM conversation_summaries WHERE session_id = ?
            """,
                (session_id,),
            )

            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                summary_data = dict(zip(columns, row, strict=False))

                # Converter JSON strings de volta para objetos
                summary_data["intents"] = json.loads(summary_data["intents"] or "[]")

                return summary_data

            return None

    def get_all_conversation_summaries(
        self, limit: int = 100, offset: int = 0
    ) -> list[dict[str, Any]]:
        """Recupera todos os resumos de conversa com paginação opcional"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM conversation_summaries
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """,
                (limit, offset),
            )

            summaries = []
            for row in cursor.fetchall():
                columns = [desc[0] for desc in cursor.description]
                summary_data = dict(zip(columns, row, strict=False))

                # Converter JSON strings de volta para objetos
                summary_data["intents"] = json.loads(summary_data["intents"] or "[]")

                summaries.append(summary_data)

            return summaries

    def get_conversation_messages(self, session_id: str) -> list[dict[str, Any]]:
        """Recupera mensagens de uma conversa salva (fallback para sessões expiradas)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT role, content, metadata, timestamp
                FROM conversations
                WHERE session_id = ?
                ORDER BY timestamp ASC
                """,
                (session_id,),
            )

            messages: list[dict[str, Any]] = []
            for row in cursor.fetchall():
                role, content, metadata_json, ts = row
                try:
                    metadata = json.loads(metadata_json) if metadata_json else {}
                except Exception:
                    metadata = {}
                messages.append(
                    {
                        "role": role,
                        "content": content,
                        "metadata": metadata,
                        "timestamp": ts,
                    }
                )

            return messages

    def delete_conversation(self, session_id: str) -> dict[str, int]:
        """Exclui mensagens e resumo de conversa para um session_id"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Deletar mensagens
            cursor.execute(
                "DELETE FROM conversations WHERE session_id = ?", (session_id,)
            )
            deleted_messages = cursor.rowcount if hasattr(cursor, "rowcount") else 0

            # Deletar resumo
            cursor.execute(
                "DELETE FROM conversation_summaries WHERE session_id = ?", (session_id,)
            )
            deleted_summaries = cursor.rowcount if hasattr(cursor, "rowcount") else 0

            conn.commit()
            return {
                "deleted_messages": int(deleted_messages or 0),
                "deleted_summaries": int(deleted_summaries or 0),
            }

    def get_lead(self, session_id: str) -> dict[str, Any] | None:
        """Recupera um lead pelo session_id"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM leads WHERE session_id = ?
            """,
                (session_id,),
            )

            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                lead_data = dict(zip(columns, row, strict=False))

                # Converter JSON strings de volta para objetos
                lead_data["pain_points"] = json.loads(lead_data["pain_points"] or "[]")
                lead_data["interests"] = json.loads(lead_data["interests"] or "[]")
                lead_data["recommended_solutions"] = json.loads(
                    lead_data["recommended_solutions"] or "[]"
                )

                return lead_data

            return None

    def get_all_leads(
        self, status: str | None = None, limit: int = 100
    ) -> list[dict[str, Any]]:
        """Recupera todos os leads com filtros opcionais"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM leads"
            params: list[Any] = []

            if status:
                query += " WHERE status = ?"
                params.append(status)

            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)

            leads = []
            for row in cursor.fetchall():
                columns = [desc[0] for desc in cursor.description]
                lead_data = dict(zip(columns, row, strict=False))

                # Converter JSON strings de volta para objetos
                lead_data["pain_points"] = json.loads(lead_data["pain_points"] or "[]")
                lead_data["interests"] = json.loads(lead_data["interests"] or "[]")
                lead_data["recommended_solutions"] = json.loads(
                    lead_data["recommended_solutions"] or "[]"
                )

                leads.append(lead_data)

            return leads

    def update_lead_status(
        self, session_id: str, status: str, notes: str | None = None
    ):
        """Atualiza o status de um lead"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE leads SET status = ?, updated_at = ? WHERE session_id = ?
            """,
                (status, datetime.now(), session_id),
            )

            # Criar notificação de mudança de status
            lead_data = self.get_lead(session_id)
            if lead_data:
                self.create_notification(
                    lead_id=lead_data["id"],
                    notification_type=f"lead_{status}",
                    message=f"Lead {lead_data.get('name', 'Sem nome')} marcado como {status}",
                )

            conn.commit()

    def create_notification(self, lead_id: int, notification_type: str, message: str):
        """Cria uma nova notificação"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO notifications (lead_id, type, message)
                VALUES (?, ?, ?)
            """,
                (lead_id, notification_type, message),
            )

            conn.commit()

    def get_notifications(self, unread_only: bool = True) -> list[dict[str, Any]]:
        """Recupera notificações"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            query = """
                SELECT n.*, l.name as lead_name, l.email as lead_email
                FROM notifications n
                LEFT JOIN leads l ON n.lead_id = l.id
            """
            params: list[Any] = []

            if unread_only:
                query += " WHERE n.is_read = FALSE"

            query += " ORDER BY n.created_at DESC"

            cursor.execute(query, params)

            notifications = []
            for row in cursor.fetchall():
                columns = [desc[0] for desc in cursor.description]
                notification_data = dict(zip(columns, row, strict=False))
                notifications.append(notification_data)

            return notifications

    def mark_notification_read(self, notification_id: int):
        """Marca uma notificação como lida"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE notifications SET is_read = TRUE WHERE id = ?
            """,
                (notification_id,),
            )

            conn.commit()

    def save_playground_activity(
        self,
        user_name: str,
        user_email: str,
        video_url: str,
        video_id: str,
        action_type: str,  # 'transcribe' ou 'summarize'
    ) -> int:
        """Salva uma atividade do Playground"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO playground_activities (
                    user_name, user_email, video_url, video_id, action_type
                ) VALUES (?, ?, ?, ?, ?)
            """,
                (user_name, user_email, video_url, video_id, action_type),
            )

            activity_id = cursor.lastrowid
            if activity_id is None:
                raise ValueError("Falha ao criar atividade no banco de dados")
            conn.commit()
            return activity_id

    def update_playground_export(
        self, activity_id: int, export_format: str  # 'txt' ou 'pdf'
    ):
        """Atualiza registro quando usuário exporta"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE playground_activities
                SET exported = 1, export_format = ?
                WHERE id = ?
            """,
                (export_format, activity_id),
            )

            conn.commit()

    def get_all_playground_activities(
        self, limit: int = 1000, offset: int = 0
    ) -> list[dict[str, Any]]:
        """Recupera todas as atividades do Playground"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM playground_activities
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """,
                (limit, offset),
            )

            activities = []
            for row in cursor.fetchall():
                columns = [desc[0] for desc in cursor.description]
                activity_data = dict(zip(columns, row, strict=False))
                activities.append(activity_data)

            return activities

    def get_stats(self) -> dict[str, Any]:
        """Retorna estatísticas do banco de dados"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Total de leads
            cursor.execute("SELECT COUNT(*) FROM leads")
            total_leads = cursor.fetchone()[0]

            # Leads por status
            cursor.execute("""
                SELECT status, COUNT(*) FROM leads GROUP BY status
            """)
            leads_by_status = dict(cursor.fetchall())

            # Total de conversas
            cursor.execute("SELECT COUNT(*) FROM conversations")
            total_conversations = cursor.fetchone()[0]

            # Total de resumos de conversa
            cursor.execute("SELECT COUNT(*) FROM conversation_summaries")
            total_summaries = cursor.fetchone()[0]

            # Notificações não lidas
            cursor.execute("SELECT COUNT(*) FROM notifications WHERE is_read = FALSE")
            unread_notifications = cursor.fetchone()[0]

            # Média de duração das conversas (resumos)
            cursor.execute("SELECT AVG(duration_minutes) FROM conversation_summaries")
            avg_duration = cursor.fetchone()[0] or 0

            # Estatísticas do Playground
            cursor.execute("SELECT COUNT(*) FROM playground_activities")
            total_playground = cursor.fetchone()[0]

            cursor.execute("""
                SELECT action_type, COUNT(*) FROM playground_activities GROUP BY action_type
            """)
            playground_by_action = dict(cursor.fetchall())

            return {
                "total_leads": total_leads,
                "leads_by_status": leads_by_status,
                "total_conversations": total_conversations,
                "total_summaries": total_summaries,
                "unread_notifications": unread_notifications,
                "avg_conversation_duration": round(avg_duration, 2),
                "total_playground_activities": total_playground,
                "playground_by_action": playground_by_action,
            }


# Instância global do banco de dados
db_manager = DatabaseManager()
