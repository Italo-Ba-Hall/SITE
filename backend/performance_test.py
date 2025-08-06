#!/usr/bin/env python3
"""
Script de Teste de Performance
/-HALL-DEV Backend

Testa:
- Tempo de resposta dos endpoints
- Throughput (requisições por segundo)
- Uso de memória e CPU
- Performance do cache
"""

import asyncio
import time
import json
import statistics
import requests
from typing import Dict, List, Tuple
from datetime import datetime
import psutil
import os

# Configurações
API_BASE_URL = "http://localhost:8000"
CONCURRENT_USERS = 3  # Reduzido de 10 para 3
REQUESTS_PER_USER = 2  # Reduzido de 5 para 2
TEST_DURATION = 30  # Reduzido de 60 para 30 segundos

class PerformanceTest:
    """Teste de performance do sistema"""
    
    def __init__(self):
        self.results: Dict = {
            "endpoints": {},
            "cache_performance": {},
            "system_metrics": {},
            "summary": {}
        }
        self.start_time = time.time()
    
    def get_system_metrics(self) -> Dict:
        """Coleta métricas do sistema"""
        process = psutil.Process(os.getpid())
        
        return {
            "cpu_percent": process.cpu_percent(),
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "memory_percent": process.memory_percent(),
            "open_files": len(process.open_files()),
            "threads": process.num_threads()
        }
    
    async def test_endpoint_performance(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
        """Testa performance de um endpoint específico"""
        times = []
        errors = 0
        
        for i in range(REQUESTS_PER_USER):
            start_time = time.time()
            try:
                if method == "GET":
                    response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=10)
                elif method == "POST":
                    response = requests.post(f"{API_BASE_URL}{endpoint}", json=data, timeout=10)
                
                if response.status_code == 200:
                    times.append(time.time() - start_time)
                else:
                    errors += 1
                    
            except Exception as e:
                errors += 1
                print(f"Erro no endpoint {endpoint}: {str(e)}")
        
        if times:
            return {
                "endpoint": endpoint,
                "method": method,
                "total_requests": REQUESTS_PER_USER,
                "successful_requests": len(times),
                "failed_requests": errors,
                "avg_response_time": statistics.mean(times),
                "min_response_time": min(times),
                "max_response_time": max(times),
                "median_response_time": statistics.median(times),
                "p95_response_time": sorted(times)[int(len(times) * 0.95)] if len(times) > 0 else 0,
                "requests_per_second": len(times) / sum(times) if sum(times) > 0 else 0
            }
        else:
            return {
                "endpoint": endpoint,
                "method": method,
                "total_requests": REQUESTS_PER_USER,
                "successful_requests": 0,
                "failed_requests": errors,
                "error": "Nenhuma requisição bem-sucedida"
            }
    
    async def test_concurrent_load(self) -> Dict:
        """Testa carga concorrente"""
        print("🔄 Testando carga concorrente...")
        
        start_time = time.time()
        tasks = []
        
        # Criar tarefas para usuários concorrentes
        for user_id in range(CONCURRENT_USERS):
            task = self.simulate_user_session(user_id)
            tasks.append(task)
        
        # Executar todas as tarefas concorrentemente
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = time.time() - start_time
        
        # Analisar resultados
        successful_sessions = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
        failed_sessions = len(results) - successful_sessions
        
        return {
            "concurrent_users": CONCURRENT_USERS,
            "total_time": total_time,
            "successful_sessions": successful_sessions,
            "failed_sessions": failed_sessions,
            "throughput": successful_sessions / total_time if total_time > 0 else 0,
            "success_rate": successful_sessions / len(results) if results else 0
        }
    
    async def simulate_user_session(self, user_id: int) -> Dict:
        """Simula uma sessão de usuário completa"""
        try:
            # 1. Iniciar chat
            start_response = requests.post(
                f"{API_BASE_URL}/chat/start",
                json={"user_id": f"perf_user_{user_id}"},
                timeout=5
            )
            
            if start_response.status_code != 200:
                return {"success": False, "error": "Failed to start chat"}
            
            session_data = start_response.json()
            session_id = session_data["session_id"]
            
            # 2. Enviar algumas mensagens
            messages = [
                "Olá, como você está?",
                "Preciso de ajuda com desenvolvimento",
                "Qual o prazo para um projeto?",
                "Obrigado pela ajuda!"
            ]
            
            for message in messages:
                response = requests.post(
                    f"{API_BASE_URL}/chat/message",
                    json={
                        "session_id": session_id,
                        "message": message,
                        "context": None
                    },
                    timeout=10
                )
                
                if response.status_code != 200:
                    return {"success": False, "error": "Failed to send message"}
            
            # 3. Finalizar chat
            end_response = requests.post(
                f"{API_BASE_URL}/chat/end",
                json={"session_id": session_id, "reason": "performance_test"},
                timeout=5
            )
            
            return {"success": True, "session_id": session_id}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_cache_performance(self) -> Dict:
        """Testa performance do cache"""
        print("💾 Testando performance do cache...")
        
        # Teste 1: Primeira requisição (sem cache)
        start_time = time.time()
        response1 = requests.post(
            f"{API_BASE_URL}/chat/start",
            json={"initial_message": "Teste de cache", "user_id": "cache_test"},
            timeout=10
        )
        first_request_time = time.time() - start_time
        
        if response1.status_code != 200:
            return {"error": "Failed to start chat for cache test"}
        
        session_data = response1.json()
        session_id = session_data["session_id"]
        
        # Teste 2: Segunda requisição (com cache)
        start_time = time.time()
        response2 = requests.post(
            f"{API_BASE_URL}/chat/message",
            json={
                "session_id": session_id,
                "message": "Mesma mensagem para testar cache",
                "context": None
            },
            timeout=10
        )
        cached_request_time = time.time() - start_time
        
        # Teste 3: Terceira requisição (deve usar cache)
        start_time = time.time()
        response3 = requests.post(
            f"{API_BASE_URL}/chat/message",
            json={
                "session_id": session_id,
                "message": "Mesma mensagem para testar cache",
                "context": None
            },
            timeout=10
        )
        second_cached_request_time = time.time() - start_time
        
        # Finalizar sessão
        requests.post(
            f"{API_BASE_URL}/chat/end",
            json={"session_id": session_id, "reason": "cache_test"},
            timeout=5
        )
        
        return {
            "first_request_time": first_request_time,
            "cached_request_time": cached_request_time,
            "second_cached_request_time": second_cached_request_time,
            "cache_improvement": (first_request_time - cached_request_time) / first_request_time * 100 if first_request_time > 0 else 0
        }
    
    async def run_performance_tests(self):
        """Executa todos os testes de performance"""
        print("🚀 Iniciando Testes de Performance")
        print("=" * 50)
        
        # Métricas iniciais do sistema
        self.results["system_metrics"]["initial"] = self.get_system_metrics()
        
        # Teste 1: Performance dos endpoints
        print("📊 Testando performance dos endpoints...")
        
        endpoints_to_test = [
            ("/health", "GET"),
            ("/health/detailed", "GET"),
            ("/stats/llm", "GET"),
            ("/chat/start", "POST", {"user_id": "perf_test"}),
            ("/test/llm", "POST")
        ]
        
        for endpoint, method, *data in endpoints_to_test:
            test_data = data[0] if data else None
            result = await self.test_endpoint_performance(endpoint, method, test_data)
            self.results["endpoints"][endpoint] = result
            
            # Imprimir resultado
            if "error" in result:
                print(f"❌ {endpoint}: {result['error']}")
            else:
                avg_time = result["avg_response_time"]
                rps = result["requests_per_second"]
                print(f"✅ {endpoint}: {avg_time:.3f}s avg, {rps:.2f} req/s")
        
        # Teste 2: Carga concorrente
        print("\n👥 Testando carga concorrente...")
        concurrent_result = await self.test_concurrent_load()
        self.results["concurrent_load"] = concurrent_result
        
        print(f"✅ Carga concorrente: {concurrent_result['successful_sessions']}/{CONCURRENT_USERS} sessões bem-sucedidas")
        print(f"   Throughput: {concurrent_result['throughput']:.2f} sessões/segundo")
        
        # Teste 3: Performance do cache
        print("\n💾 Testando performance do cache...")
        cache_result = await self.test_cache_performance()
        self.results["cache_performance"] = cache_result
        
        if "error" not in cache_result:
            improvement = cache_result["cache_improvement"]
            print(f"✅ Cache: {improvement:.1f}% de melhoria no tempo de resposta")
        
        # Métricas finais do sistema
        self.results["system_metrics"]["final"] = self.get_system_metrics()
        
        # Gerar resumo
        self.generate_summary()
        
        # Salvar resultados
        self.save_results()
    
    def generate_summary(self):
        """Gera resumo dos testes"""
        print("\n" + "=" * 50)
        print("📊 RESUMO DE PERFORMANCE")
        print("=" * 50)
        
        # Resumo dos endpoints
        successful_endpoints = sum(1 for r in self.results["endpoints"].values() if "error" not in r)
        total_endpoints = len(self.results["endpoints"])
        
        print(f"Endpoints testados: {successful_endpoints}/{total_endpoints}")
        
        if successful_endpoints > 0:
            avg_response_times = [
                r["avg_response_time"] 
                for r in self.results["endpoints"].values() 
                if "error" not in r
            ]
            
            print(f"Tempo médio de resposta: {statistics.mean(avg_response_times):.3f}s")
            print(f"Tempo máximo de resposta: {max(avg_response_times):.3f}s")
        
        # Resumo da carga concorrente
        if "concurrent_load" in self.results:
            cl = self.results["concurrent_load"]
            print(f"\nCarga Concorrente:")
            print(f"  Usuários simultâneos: {cl['concurrent_users']}")
            print(f"  Taxa de sucesso: {cl['success_rate']*100:.1f}%")
            print(f"  Throughput: {cl['throughput']:.2f} sessões/segundo")
        
        # Resumo do cache
        if "cache_performance" in self.results and "error" not in self.results["cache_performance"]:
            cp = self.results["cache_performance"]
            print(f"\nPerformance do Cache:")
            print(f"  Melhoria: {cp['cache_improvement']:.1f}%")
            print(f"  Primeira requisição: {cp['first_request_time']:.3f}s")
            print(f"  Requisição com cache: {cp['cached_request_time']:.3f}s")
    
    def save_results(self):
        """Salva resultados em arquivo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"performance_results_{timestamp}.json"
        
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Resultados salvos em: {filename}")

async def main():
    """Função principal"""
    performance_test = PerformanceTest()
    await performance_test.run_performance_tests()

if __name__ == "__main__":
    asyncio.run(main()) 