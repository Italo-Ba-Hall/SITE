"""
/-HALL-DEV Flask App para PythonAnywhere
Versão simplificada sem dependências do FastAPI
"""

from flask import Flask, jsonify, request
from flask_cors import CORS

# Criar aplicação Flask
app = Flask(__name__)

# Configurar CORS
CORS(app, origins=[
    "http://localhost:3000",
    "http://localhost:3001",
    "https://barrahall.dev.br",
    "http://barrahall.dev.br"
])

@app.route('/')
def root():
    """Endpoint raiz - Health check"""
    return jsonify({
        "message": "/-HALL-DEV API está funcionando!",
        "status": "online",
        "version": "1.0.0",
        "service": "Flask wrapper"
    })

@app.route('/health')
def health_check():
    """Health check específico para Flask"""
    return jsonify({
        "status": "healthy",
        "service": "Flask wrapper for FastAPI",
        "version": "1.0.0"
    })

@app.route('/chat/start', methods=['POST'])
def start_chat():
    """Endpoint de teste para chat"""
    try:
        _ = request.get_json() or {}  # Recebe dados mas não usa neste endpoint de teste
        return jsonify({
            "session_id": "test-session-123",
            "welcome_message": "Olá! Como posso ajudá-lo hoje?",
            "user_profile": None,
            "status": "success"
        })
    except Exception as e:
        return jsonify({
            "error": "Erro ao iniciar chat",
            "message": str(e)
        }), 500

@app.route('/suggest', methods=['POST'])
def get_suggestions():
    """Endpoint de teste para sugestões"""
    try:
        data = request.get_json() or {}
        text = data.get('text', '').lower()

        suggestions = []

        # Lógica simples de sugestões
        if any(word in text for word in ["site", "website", "web", "desenvolvimento"]):
            suggestions.append({
                "id": "web-dev",
                "title": "Desenvolvimento Web",
                "description": "Criação de sites e aplicações web modernas",
                "category": "development"
            })

        if any(word in text for word in ["app", "aplicativo", "mobile"]):
            suggestions.append({
                "id": "mobile-dev",
                "title": "Desenvolvimento Mobile",
                "description": "Apps nativos e multiplataforma",
                "category": "development"
            })

        if not suggestions:
            suggestions.append({
                "id": "consultation",
                "title": "Consultoria Personalizada",
                "description": "Vamos conversar sobre seu projeto específico",
                "category": "consultation"
            })

        return jsonify(suggestions)

    except Exception as e:
        return jsonify({
            "error": "Erro ao processar sugestões",
            "message": str(e)
        }), 500

@app.route('/content/<suggestion_id>')
def get_content(suggestion_id):
    """Endpoint de teste para conteúdo"""
    content_map = {
        "web-dev": {
            "id": "web-dev",
            "title": "Desenvolvimento Web Profissional",
            "content": "Criamos sites e aplicações web com tecnologias modernas como React, TypeScript e Python.",
            "details": {
                "technologies": ["React", "TypeScript", "Python", "FastAPI"],
                "timeline": "2-8 semanas",
                "features": ["Responsivo", "SEO Otimizado", "Performance", "Segurança"]
            }
        },
        "mobile-dev": {
            "id": "mobile-dev",
            "title": "Aplicativos Mobile Nativos",
            "content": "Desenvolvimento de apps para iOS e Android com experiência nativa.",
            "details": {
                "platforms": ["iOS", "Android", "React Native"],
                "timeline": "4-12 semanas",
                "features": ["Performance Nativa", "UI/UX Moderna", "Integração APIs"]
            }
        },
        "consultation": {
            "id": "consultation",
            "title": "Consultoria Tecnológica",
            "content": "Análise detalhada do seu projeto e recomendações técnicas personalizadas.",
            "details": {
                "includes": ["Análise de Requisitos", "Arquitetura", "Tecnologias", "Timeline"],
                "timeline": "1-2 semanas",
                "deliverable": "Documento técnico completo"
            }
        }
    }

    if suggestion_id not in content_map:
        return jsonify({
            "id": "not-found",
            "title": "Conteúdo não encontrado",
            "content": "Desculpe, não encontramos informações para esta sugestão.",
            "details": {}
        })

    return jsonify(content_map[suggestion_id])

# Capturar todas as outras rotas
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def catch_all(path):
    """Captura todas as outras requisições"""
    return jsonify({
        "error": "Endpoint não implementado",
        "path": path,
        "message": "Este endpoint ainda não foi implementado na versão simplificada",
        "status": "not_found"
    }), 404

if __name__ == '__main__':
    # Configuração para desenvolvimento local apenas
    app.run(debug=False, host='127.0.0.1', port=5000)
