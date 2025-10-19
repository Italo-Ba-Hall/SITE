#!/usr/bin/env python3
"""
Script para iniciar o servidor com variáveis de ambiente
"""

import os

import uvicorn
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Definir variável de ambiente se não estiver definida
if not os.getenv("GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY"] = (
        "SUA_CHAVE_GEMINI_AQUI"
    )

if __name__ == "__main__":
    print("Iniciando servidor /-HALL-DEV...")
    print(f"GEMINI_API_KEY: {os.getenv('GEMINI_API_KEY')[:20]}...")
    print("Servidor disponivel em: http://localhost:8000")
    print("Documentacao: http://localhost:8000/docs")

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, log_level="info")
