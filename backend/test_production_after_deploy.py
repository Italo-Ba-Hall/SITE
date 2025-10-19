"""
Teste do backend em produção após deploy
"""
import requests
import json

API_URL = "https://site-production-1e79.up.railway.app"

print("=" * 70)
print("TESTE DO BACKEND EM PRODUÇÃO - APÓS DEPLOY")
print("=" * 70)

# Teste completo do fluxo
print("\n[1] Testando /chat/start...")
try:
    response = requests.post(
        f"{API_URL}/chat/start",
        json={"user_id": None},
        headers={
            "Content-Type": "application/json",
            "Origin": "https://barrahall.dev.br"
        },
        timeout=15
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        session_id = data.get("session_id")
        print(f"✓ Chat iniciado com sucesso!")
        print(f"  Session ID: {session_id}")
        
        # Teste 2: Enviar mensagem
        print("\n[2] Testando /chat/message...")
        msg_response = requests.post(
            f"{API_URL}/chat/message",
            json={
                "session_id": session_id,
                "message": "Quais serviços vocês oferecem?",
                "context": None
            },
            headers={
                "Content-Type": "application/json",
                "Origin": "https://barrahall.dev.br"
            },
            timeout=30
        )
        
        print(f"Status: {msg_response.status_code}")
        if msg_response.status_code == 200:
            msg_data = msg_response.json()
            
            # Verificar se é mensagem de fallback ou resposta real
            if msg_data.get("metadata", {}).get("fallback"):
                print("❌ AINDA ESTÁ RETORNANDO FALLBACK!")
                print(f"Erro: {msg_data.get('metadata', {}).get('error')}")
                print("\n⏳ Deploy pode ainda estar em andamento...")
            else:
                print("✅ CHAT FUNCIONANDO PERFEITAMENTE!")
                print(f"\nResposta do LLM:")
                print(f"  {msg_data.get('message')[:200]}...")
                print(f"\n  Modelo: {msg_data.get('metadata', {}).get('model')}")
                print(f"  Tokens: {msg_data.get('metadata', {}).get('tokens_used')}")
                print(f"  Confidence: {msg_data.get('confidence')}")
        else:
            print(f"❌ Erro: {msg_response.status_code}")
            print(msg_response.text)
    else:
        print(f"❌ Erro no /chat/start: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Erro: {e}")

print("\n" + "=" * 70)

