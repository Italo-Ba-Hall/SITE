"""
Configuração de Produção para /-HALL-DEV Backend
"""

import os

from dotenv import load_dotenv

load_dotenv()


class ProductionConfig:
    """Configurações para ambiente de produção"""

    # API Keys
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    # URLs
    FRONTEND_URL = os.getenv("FRONTEND_URL", "")

    # Banco de Dados
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hall_dev.db")

    # Email
    EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
    EMAIL_USER = os.getenv("EMAIL_USER", "")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

    # Webhooks
    SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
    DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")

    # Servidor
    PORT = int(os.getenv("PORT", "8000"))
    HOST = os.getenv("HOST", "0.0.0.0")  # noqa: S104 - Necessário para produção

    # Ambiente
    ENVIRONMENT = "production"
    DEBUG = False

    @classmethod
    def validate(cls):
        """Valida se todas as configurações obrigatórias estão presentes"""
        required_vars = ["GROQ_API_KEY"]
        missing = [var for var in required_vars if not getattr(cls, var)]

        if missing:
            raise ValueError(
                f"Variáveis de ambiente obrigatórias faltando: {', '.join(missing)}"
            )

        return True


# Instância de configuração
config = ProductionConfig()
