"""
Serviço de Notificação para /-HALL-DEV
Envio de emails e webhooks para equipe
"""

import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Any
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class NotificationService:
    """Serviço para enviar notificações para a equipe"""
    
    def __init__(self):
        # Configurações de email
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        
        # Email da equipe
        self.team_email = os.getenv("TEAM_EMAIL", "equipe@hall-dev.com")
        
        # Webhook URLs
        self.slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
        self.discord_webhook = os.getenv("DISCORD_WEBHOOK_URL")
        
        # Configurações de notificação
        self.notify_new_leads = os.getenv("NOTIFY_NEW_LEADS", "true").lower() == "true"
        self.notify_qualified_leads = os.getenv("NOTIFY_QUALIFIED_LEADS", "true").lower() == "true"
        self.notify_converted_leads = os.getenv("NOTIFY_CONVERTED_LEADS", "true").lower() == "true"
    
    def send_email_notification(self, subject: str, body: str, html_body: Optional[str] = None) -> bool:
        """Envia email para a equipe"""
        if not self.smtp_username or not self.smtp_password:
            print("⚠️ Configurações de email não encontradas. Notificação não enviada.")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🎯 /-HALL-DEV: {subject}"
            msg['From'] = self.smtp_username
            msg['To'] = self.team_email
            
            # Texto simples
            text_part = MIMEText(body, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # HTML (se fornecido)
            if html_body:
                html_part = MIMEText(html_body, 'html', 'utf-8')
                msg.attach(html_part)
            
            # Enviar email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            print(f"✅ Email enviado: {subject}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao enviar email: {str(e)}")
            return False
    
    def send_slack_notification(self, message: str, color: str = "good") -> bool:
        """Envia notificação para Slack"""
        if not self.slack_webhook:
            return False
        
        try:
            payload = {
                "attachments": [
                    {
                        "color": color,
                        "title": "🎯 /-HALL-DEV - Novo Lead",
                        "text": message,
                        "footer": "/-HALL-DEV Bot",
                        "ts": int(datetime.now().timestamp())
                    }
                ]
            }
            
            response = requests.post(self.slack_webhook, json=payload, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Erro ao enviar notificação Slack: {str(e)}")
            return False
    
    def send_discord_notification(self, message: str, color: int = 0x00ff00) -> bool:
        """Envia notificação para Discord"""
        if not self.discord_webhook:
            return False
        
        try:
            payload = {
                "embeds": [
                    {
                        "title": "🎯 /-HALL-DEV - Novo Lead",
                        "description": message,
                        "color": color,
                        "footer": {
                            "text": "/-HALL-DEV Bot"
                        },
                        "timestamp": datetime.now().isoformat()
                    }
                ]
            }
            
            response = requests.post(self.discord_webhook, json=payload, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Erro ao enviar notificação Discord: {str(e)}")
            return False
    
    def notify_new_lead(self, lead_data: Dict[str, Any]) -> bool:
        """Notifica sobre um novo lead"""
        if not self.notify_new_leads:
            return True
        
        name = lead_data.get('name', 'Sem nome')
        email = lead_data.get('email', 'Sem email')
        company = lead_data.get('company', 'Sem empresa')
        role = lead_data.get('role', 'Sem cargo')
        qualification_score = lead_data.get('qualification_score', 0.0)
        
        # Email
        subject = f"Novo Lead Qualificado: {name}"
        body = f"""
🎯 NOVO LEAD CAPTURADO!

👤 Nome: {name}
📧 Email: {email}
🏢 Empresa: {company}
💼 Cargo: {role}
⭐ Score de Qualificação: {qualification_score:.1%}

📊 Resumo da Conversa:
{lead_data.get('conversation_summary', 'Não disponível')}

🎯 Pontos de Dor Identificados:
{chr(10).join([f"• {point}" for point in lead_data.get('pain_points', [])])}

💡 Soluções Recomendadas:
{chr(10).join([f"• {solution}" for solution in lead_data.get('recommended_solutions', [])])}

⏰ Capturado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}

---
/-HALL-DEV Bot 🤖
        """.strip()
        
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #00e5ff;">🎯 NOVO LEAD CAPTURADO!</h2>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3>👤 Informações do Lead</h3>
                <p><strong>Nome:</strong> {name}</p>
                <p><strong>Email:</strong> {email}</p>
                <p><strong>Empresa:</strong> {company}</p>
                <p><strong>Cargo:</strong> {role}</p>
                <p><strong>Score de Qualificação:</strong> {qualification_score:.1%}</p>
            </div>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3>📊 Resumo da Conversa</h3>
                <p>{lead_data.get('conversation_summary', 'Não disponível')}</p>
            </div>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3>🎯 Pontos de Dor Identificados</h3>
                <ul>
                    {chr(10).join([f"<li>{point}</li>" for point in lead_data.get('pain_points', [])])}
                </ul>
            </div>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3>💡 Soluções Recomendadas</h3>
                <ul>
                    {chr(10).join([f"<li>{solution}</li>" for solution in lead_data.get('recommended_solutions', [])])}
                </ul>
            </div>
            
            <p style="color: #666; font-size: 12px;">
                ⏰ Capturado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}<br>
                ---<br>
                /-HALL-DEV Bot 🤖
            </p>
        </div>
        """
        
        # Enviar notificações
        email_sent = self.send_email_notification(subject, body, html_body)
        slack_sent = self.send_slack_notification(body)
        discord_sent = self.send_discord_notification(body)
        
        return email_sent or slack_sent or discord_sent
    
    def notify_lead_status_change(self, lead_data: Dict[str, Any], new_status: str) -> bool:
        """Notifica sobre mudança de status do lead"""
        name = lead_data.get('name', 'Sem nome')
        email = lead_data.get('email', 'Sem email')
        
        subject = f"Lead Atualizado: {name} - {new_status.title()}"
        body = f"""
🔄 STATUS DO LEAD ATUALIZADO

👤 Nome: {name}
📧 Email: {email}
🆕 Novo Status: {new_status.title()}

⏰ Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}

---
/-HALL-DEV Bot 🤖
        """.strip()
        
        return self.send_email_notification(subject, body)
    
    def send_daily_report(self, stats: Dict[str, Any]) -> bool:
        """Envia relatório diário para a equipe"""
        total_leads = stats.get('total_leads', 0)
        leads_by_status = stats.get('leads_by_status', {})
        unread_notifications = stats.get('unread_notifications', 0)
        
        subject = f"📊 Relatório Diário - {total_leads} leads capturados"
        body = f"""
📊 RELATÓRIO DIÁRIO /-HALL-DEV

🎯 Total de Leads: {total_leads}
📈 Leads por Status:
{chr(10).join([f"• {status.title()}: {count}" for status, count in leads_by_status.items()])}

🔔 Notificações Não Lidas: {unread_notifications}

⏰ Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}

---
/-HALL-DEV Bot 🤖
        """.strip()
        
        return self.send_email_notification(subject, body)

# Instância global do serviço de notificação
notification_service = NotificationService() 