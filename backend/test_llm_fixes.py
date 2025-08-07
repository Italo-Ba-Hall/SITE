#!/usr/bin/env python3
"""
Teste para verificar as correções no LLM Service
/-HALL-DEV Backend
"""

import asyncio
import os
from llm_service import LLMService, LLMCache
from schemas import LLMRequest, ChatMessage, MessageRole

async def test_api_key_validation():
    """Testa validação da API key"""
    print("🧪 Testando validação da API key...")
    
    # Simular ambiente sem API key
    original_key = os.getenv("GROQ_API_KEY")
    os.environ.pop("GROQ_API_KEY", None)
    
    try:
        # Deve falhar ao criar instância sem API key
        service = LLMService()
        print("❌ Erro: Deveria ter falhado sem API key")
    except ValueError as e:
        print(f"✅ Validação funcionando: {e}")
    finally:
        # Restaurar API key
        if original_key:
            os.environ["GROQ_API_KEY"] = original_key

def test_cache_performance():
    """Testa performance do cache otimizado"""
    print("\n🧪 Testando performance do cache...")
    
    cache = LLMCache(max_size=5, ttl_hours=1)
    
    # Adicionar itens
    for i in range(10):
        cache.set(f"key_{i}", f"value_{i}")
    
    print(f"✅ Cache size após adicionar 10 itens: {len(cache.cache)}")
    print(f"✅ Cache max_size: {cache.max_size}")
    
    # Testar LRU
    cache.get("key_0")  # Deve mover para o final
    oldest_key = next(iter(cache.cache.keys()))
    print(f"✅ Item mais antigo após LRU: {oldest_key}")

async def test_message_validation():
    """Testa validação de mensagens vazias"""
    print("\n🧪 Testando validação de mensagens...")
    
    # Restaurar API key para teste
    if not os.getenv("GROQ_API_KEY"):
        print("⚠️ GROQ_API_KEY não definida, pulando teste de validação")
        return
    
    try:
        service = LLMService()
        
        # Testar mensagem vazia
        request = LLMRequest(
            session_id="test",
            message="",
            context={"messages": []}
        )
        
        response = await service.generate_response(request)
        print(f"✅ Resposta para mensagem vazia: {response.message[:50]}...")
        
        # Testar mensagem com espaços
        request.message = "   "
        response = await service.generate_response(request)
        print(f"✅ Resposta para mensagem com espaços: {response.message[:50]}...")
        
    except Exception as e:
        print(f"❌ Erro no teste de validação: {e}")

def test_cache_cleanup():
    """Testa limpeza automática do cache"""
    print("\n🧪 Testando limpeza automática do cache...")
    
    service = LLMService()
    
    # Simular cache cheio
    for i in range(600):  # Mais que max_size (500)
        service.cache.set(f"key_{i}", f"value_{i}")
    
    print(f"✅ Cache size antes da limpeza: {len(service.cache.cache)}")
    
    # Executar limpeza automática
    service.auto_cleanup_cache()
    
    print(f"✅ Cache size após limpeza: {len(service.cache.cache)}")

async def main():
    """Executa todos os testes"""
    print("🚀 Testando correções do LLM Service...\n")
    
    await test_api_key_validation()
    test_cache_performance()
    await test_message_validation()
    test_cache_cleanup()
    
    print("\n🎯 Todos os testes concluídos!")

if __name__ == "__main__":
    asyncio.run(main())
