"""
Sistema de Banco de Dados para /-HALL-DEV
Persistência de Leads e Conversas
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import os

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
            
            # Índices para performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_session_id ON leads(session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_lead_id ON notifications(lead_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read)")
            
            conn.commit()
    
    def save_lead(self, session_id: str, user_profile: Dict[str, Any], 
                  conversation_summary: str, pain_points: List[str], 
                  recommended_solutions: List[str], qualification_score: float = 0.0) -> int:
        """Salva um novo lead no banco de dados"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO leads (
                    session_id, name, email, company, role, pain_points, 
                    interests, qualification_score, conversation_summary, 
                    recommended_solutions, status, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                user_profile.get('name'),
                user_profile.get('email'),
                user_profile.get('company'),
                user_profile.get('role'),
                json.dumps(pain_points),
                json.dumps(user_profile.get('interests', [])),
                qualification_score,
                conversation_summary,
                json.dumps(recommended_solutions),
                'new',
                datetime.now()
            ))
            
            lead_id = cursor.lastrowid
            
            # Criar notificação de novo lead
            self.create_notification(
                lead_id=lead_id,
                notification_type='new_lead',
                message=f"Novo lead: {user_profile.get('name', 'Sem nome')} ({user_profile.get('email', 'Sem email')})"
            )
            
            conn.commit()
            return lead_id
    
    def save_conversation(self, session_id: str, messages: List[Dict[str, Any]]):
        """Salva mensagens da conversa no banco de dados"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for message in messages:
                cursor.execute("""
                    INSERT INTO conversations (session_id, role, content, metadata, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    session_id,
                    message['role'],
                    message['content'],
                    json.dumps(message.get('metadata', {})),
                    message.get('timestamp', datetime.now())
                ))
            
            conn.commit()
    
    def get_lead(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Recupera um lead pelo session_id"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM leads WHERE session_id = ?
            """, (session_id,))
            
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                lead_data = dict(zip(columns, row))
                
                # Converter JSON strings de volta para objetos
                lead_data['pain_points'] = json.loads(lead_data['pain_points'] or '[]')
                lead_data['interests'] = json.loads(lead_data['interests'] or '[]')
                lead_data['recommended_solutions'] = json.loads(lead_data['recommended_solutions'] or '[]')
                
                return lead_data
            
            return None
    
    def get_all_leads(self, status: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Recupera todos os leads com filtros opcionais"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM leads"
            params = []
            
            if status:
                query += " WHERE status = ?"
                params.append(status)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            
            leads = []
            for row in cursor.fetchall():
                columns = [desc[0] for desc in cursor.description]
                lead_data = dict(zip(columns, row))
                
                # Converter JSON strings de volta para objetos
                lead_data['pain_points'] = json.loads(lead_data['pain_points'] or '[]')
                lead_data['interests'] = json.loads(lead_data['interests'] or '[]')
                lead_data['recommended_solutions'] = json.loads(lead_data['recommended_solutions'] or '[]')
                
                leads.append(lead_data)
            
            return leads
    
    def update_lead_status(self, session_id: str, status: str, notes: Optional[str] = None):
        """Atualiza o status de um lead"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE leads SET status = ?, updated_at = ? WHERE session_id = ?
            """, (status, datetime.now(), session_id))
            
            # Criar notificação de mudança de status
            lead_data = self.get_lead(session_id)
            if lead_data:
                self.create_notification(
                    lead_id=lead_data['id'],
                    notification_type=f'lead_{status}',
                    message=f"Lead {lead_data.get('name', 'Sem nome')} marcado como {status}"
                )
            
            conn.commit()
    
    def create_notification(self, lead_id: int, notification_type: str, message: str):
        """Cria uma nova notificação"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO notifications (lead_id, type, message)
                VALUES (?, ?, ?)
            """, (lead_id, notification_type, message))
            
            conn.commit()
    
    def get_notifications(self, unread_only: bool = True) -> List[Dict[str, Any]]:
        """Recupera notificações"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT n.*, l.name as lead_name, l.email as lead_email 
                FROM notifications n
                LEFT JOIN leads l ON n.lead_id = l.id
            """
            params = []
            
            if unread_only:
                query += " WHERE n.is_read = FALSE"
            
            query += " ORDER BY n.created_at DESC"
            
            cursor.execute(query, params)
            
            notifications = []
            for row in cursor.fetchall():
                columns = [desc[0] for desc in cursor.description]
                notification_data = dict(zip(columns, row))
                notifications.append(notification_data)
            
            return notifications
    
    def mark_notification_read(self, notification_id: int):
        """Marca uma notificação como lida"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE notifications SET is_read = TRUE WHERE id = ?
            """, (notification_id,))
            
            conn.commit()
    
    def get_stats(self) -> Dict[str, Any]:
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
            
            # Notificações não lidas
            cursor.execute("SELECT COUNT(*) FROM notifications WHERE is_read = FALSE")
            unread_notifications = cursor.fetchone()[0]
            
            return {
                "total_leads": total_leads,
                "leads_by_status": leads_by_status,
                "total_conversations": total_conversations,
                "unread_notifications": unread_notifications
            }

# Instância global do banco de dados
db_manager = DatabaseManager() 