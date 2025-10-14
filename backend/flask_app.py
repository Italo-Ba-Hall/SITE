"""
/-HALL-DEV Flask App para PythonAnywhere
Wrapper Flask para compatibilidade com WSGI do PythonAnywhere
"""

import asyncio
import sys

from flask import Flask, jsonify, request
from flask_cors import CORS

# Adicionar o diretório do projeto ao path
project_path = '/home/barrahall/mysite'
if project_path not in sys.path:
    sys.path.append(project_path)

# Importar a aplicação FastAPI (após configurar o path)
from main import app as fastapi_app  # noqa: E402

# Criar aplicação Flask
app = Flask(__name__)

# Configurar CORS
CORS(app, origins=[
    "http://localhost:3000",
    "http://localhost:3001",
    "https://barrahall.dev.br",
    "http://barrahall.dev.br"
])

# Middleware para converter requisições Flask em FastAPI
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def catch_all(path):
    """Captura todas as requisições e redireciona para FastAPI"""
    try:
        # Importar aqui para evitar problemas de inicialização

        # Criar request FastAPI a partir da request Flask
        scope = {
            "type": "http",
            "method": request.method,
            "path": f"/{path}" if path else "/",
            "query_string": request.query_string.decode() if request.query_string else "",
            "headers": [(k.lower().encode(), v.encode()) for k, v in request.headers],
            "client": ("127.0.0.1", 0),
            "server": ("localhost", 80),
        }

        # Criar um mock receive para o ASGI
        async def receive():
            return {
                "type": "http.request",
                "body": request.get_data(),
                "more_body": False
            }

        # Executar a aplicação FastAPI usando ASGI
        async def run_fastapi():
            # Criar um mock send para capturar a resposta
            response_data = {}

            async def send(message):
                if message["type"] == "http.response.start":
                    response_data["status"] = message["status"]
                    response_data["headers"] = message["headers"]
                elif message["type"] == "http.response.body":
                    response_data["body"] = message.get("body", b"")

            await fastapi_app(scope, receive, send)
            return response_data

        # Executar de forma síncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response_data = loop.run_until_complete(run_fastapi())

            # Converter resposta ASGI para Flask
            status_code = response_data.get("status", 200)
            headers_list = response_data.get("headers", [])

            # Converter headers para formato Flask (lista de tuplas)
            headers = []
            for header in headers_list:
                if isinstance(header, (list, tuple)) and len(header) == 2:
                    key, value = header
                    if isinstance(key, bytes):
                        key = key.decode('utf-8')
                    if isinstance(value, bytes):
                        value = value.decode('utf-8')
                    headers.append((key, value))

            body = response_data.get("body", b"")

            # Criar resposta Flask
            flask_response = app.response_class(
                response=body,
                status=status_code,
                headers=headers
            )
            return flask_response

        finally:
            loop.close()

    except Exception as e:
        return jsonify({
            "error": "Erro interno do servidor",
            "message": str(e),
            "status": "error"
        }), 500

# Health check específico do Flask
@app.route('/health')
def health_check():
    """Health check específico para Flask"""
    return jsonify({
        "status": "healthy",
        "service": "Flask wrapper for FastAPI",
        "version": "1.0.0"
    })

if __name__ == '__main__':
    # Configuração para desenvolvimento local apenas
    app.run(debug=False, host='127.0.0.1', port=5000)
