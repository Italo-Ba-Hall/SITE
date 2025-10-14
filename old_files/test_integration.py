#!/usr/bin/env python3
"""
Script de teste para verificar integração frontend-backend
/-HALL-DEV
"""

import requests
import json
from datetime import datetime

def test_backend_integration():
    """Testa a integração do backend"""
    
    # URLs para testar
    urls_to_test = [
        "https://barrahall.pythonanywhere.com",
        "https://barrahall.pythonanywhere.com/health",
        "https://barrahall.pythonanywhere.com/",
    ]
    
    print("🔍 TESTANDO INTEGRAÇÃO FRONTEND-BACKEND")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    for url in urls_to_test:
        try:
            print(f"📡 Testando: {url}")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Status: {response.status_code}")
                try:
                    data = response.json()
                    print(f"📄 Resposta: {json.dumps(data, indent=2, ensure_ascii=False)}")
                except Exception:
                    print(f"📄 Resposta: {response.text[:200]}...")
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"📄 Erro: {response.text[:200]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro de conexão: {e}")
        
        print("-" * 30)
    
    # Teste de endpoint específico do chat
    print("\n🤖 TESTANDO ENDPOINT DE CHAT")
    print("=" * 50)
    
    chat_url = "https://barrahall.pythonanywhere.com/chat/start"
    test_payload = {
        "user_id": "test-user-123",
        "initial_message": "Olá, preciso de ajuda com desenvolvimento web"
    }
    
    try:
        print(f"📡 Testando: {chat_url}")
        response = requests.post(chat_url, json=test_payload, timeout=15)
        
        if response.status_code == 200:
            print(f"✅ Status: {response.status_code}")
            data = response.json()
            print(f"📄 Resposta: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"📄 Erro: {response.text[:200]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 TESTE CONCLUÍDO")

if __name__ == "__main__":
    test_backend_integration()
