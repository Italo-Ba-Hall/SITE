#!/usr/bin/env python3
"""
Teste de Performance Rápido
/-HALL-DEV Backend
"""

import time
import requests
from typing import Dict

API_BASE_URL = "http://localhost:8000"

def test_basic_performance():
    """Teste básico de performance"""
    print("🚀 Teste de Performance Rápido")
    print("=" * 40)
    
    endpoints = [
        ("/health", "GET"),
        ("/health/detailed", "GET"),
        ("/stats/llm", "GET"),
        ("/chat/start", "POST", {"user_id": "perf_test"})
    ]
    
    results = {}
    
    for endpoint, method, *data in endpoints:
        test_data = data[0] if data else None
        times = []
        
        print(f"📊 Testando {endpoint}...")
        
        for i in range(3):  # Apenas 3 testes por endpoint
            start_time = time.time()
            try:
                if method == "GET":
                    response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
                elif method == "POST":
                    response = requests.post(f"{API_BASE_URL}{endpoint}", json=test_data, timeout=5)
                
                if response.status_code == 200:
                    duration = time.time() - start_time
                    times.append(duration)
                    print(f"  ✅ Teste {i+1}: {duration:.3f}s")
                else:
                    print(f"  ❌ Teste {i+1}: Erro {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ Teste {i+1}: Erro - {str(e)}")
        
        if times:
            avg_time = sum(times) / len(times)
            results[endpoint] = {
                "avg_time": avg_time,
                "min_time": min(times),
                "max_time": max(times),
                "success_rate": len(times) / 3
            }
            print(f"  📈 Média: {avg_time:.3f}s")
        else:
            results[endpoint] = {"error": "Nenhum teste bem-sucedido"}
            print(f"  ❌ Falhou")
    
    # Resumo
    print("\n" + "=" * 40)
    print("📊 RESUMO DE PERFORMANCE")
    print("=" * 40)
    
    successful_endpoints = 0
    total_avg_time = 0
    
    for endpoint, result in results.items():
        if "error" not in result:
            successful_endpoints += 1
            total_avg_time += result["avg_time"]
            print(f"✅ {endpoint}: {result['avg_time']:.3f}s avg")
        else:
            print(f"❌ {endpoint}: {result['error']}")
    
    if successful_endpoints > 0:
        overall_avg = total_avg_time / successful_endpoints
        print(f"\n📈 Tempo médio geral: {overall_avg:.3f}s")
        print(f"📊 Endpoints funcionando: {successful_endpoints}/{len(endpoints)}")
        
        if overall_avg < 3.0:
            print("🎉 Performance EXCELENTE!")
        elif overall_avg < 5.0:
            print("✅ Performance BOA!")
        else:
            print("⚠️  Performance pode ser melhorada")
    else:
        print("❌ Nenhum endpoint funcionando")

def test_cache_performance():
    """Teste rápido de cache"""
    print("\n💾 Teste de Cache")
    print("-" * 20)
    
    try:
        # Primeira requisição
        start_time = time.time()
        response1 = requests.post(
            f"{API_BASE_URL}/chat/start",
            json={"user_id": "cache_test"},
            timeout=5
        )
        first_time = time.time() - start_time
        
        if response1.status_code == 200:
            session_data = response1.json()
            session_id = session_data["session_id"]
            
            # Segunda requisição (deve usar cache)
            start_time = time.time()
            response2 = requests.post(
                f"{API_BASE_URL}/chat/message",
                json={
                    "session_id": session_id,
                    "message": "Teste de cache",
                    "context": None
                },
                timeout=5
            )
            second_time = time.time() - start_time
            
            print(f"Primeira requisição: {first_time:.3f}s")
            print(f"Segunda requisição: {second_time:.3f}s")
            
            if second_time < first_time:
                improvement = ((first_time - second_time) / first_time) * 100
                print(f"✅ Cache funcionando! Melhoria: {improvement:.1f}%")
            else:
                print("⚠️  Cache não detectado")
                
        else:
            print("❌ Erro ao iniciar chat para teste de cache")
            
    except Exception as e:
        print(f"❌ Erro no teste de cache: {str(e)}")

if __name__ == "__main__":
    test_basic_performance()
    test_cache_performance()
    print("\n🎯 Teste de performance concluído!") 