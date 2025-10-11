#!/usr/bin/env python3
"""
Script de Teste Automatizado para LLM Integration
/-HALL-DEV Backend

Testa:
- Conexão com Groq API
- Endpoints de chat
- Cache e rate limiting
- Performance e fallbacks
"""

import asyncio
import json
import time
from datetime import datetime

import requests

# Configurações
API_BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 30  # segundos


class LLMTestSuite:
    """Suite de testes para integração LLM"""

    def __init__(self):
        self.results: list[dict] = []
        self.start_time = time.time()

    def log_test(
        self, test_name: str, success: bool, details: str = "", duration: float = 0
    ):
        """Registra resultado de teste"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
        }
        self.results.append(result)

        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name} ({duration:.2f}s)")
        if details:
            print(f"   {details}")

    async def test_health_endpoint(self) -> bool:
        """Testa endpoint de health check"""
        start_time = time.time()
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            duration = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Health Check", True, f"API Status: {data.get('status')}", duration
                )
                return True
            else:
                self.log_test(
                    "Health Check",
                    False,
                    f"Status code: {response.status_code}",
                    duration,
                )
                return False

        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Health Check", False, f"Erro: {e!s}", duration)
            return False

    async def test_detailed_health(self) -> bool:
        """Testa health check detalhado"""
        start_time = time.time()
        try:
            response = requests.get(f"{API_BASE_URL}/health/detailed", timeout=10)
            duration = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                services_healthy = all(
                    service == "healthy"
                    for service in data.get("services", {}).values()
                )

                if services_healthy:
                    self.log_test(
                        "Detailed Health Check",
                        True,
                        "Todos os serviços saudáveis",
                        duration,
                    )
                    return True
                else:
                    self.log_test(
                        "Detailed Health Check",
                        False,
                        "Alguns serviços com problemas",
                        duration,
                    )
                    return False
            else:
                self.log_test(
                    "Detailed Health Check",
                    False,
                    f"Status code: {response.status_code}",
                    duration,
                )
                return False

        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Detailed Health Check", False, f"Erro: {e!s}", duration)
            return False

    async def test_llm_connection(self) -> bool:
        """Testa conexão com LLM"""
        start_time = time.time()
        try:
            response = requests.post(f"{API_BASE_URL}/test/llm", timeout=15)
            duration = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test(
                        "LLM Connection", True, "Conexão com Groq funcionando", duration
                    )
                    return True
                else:
                    self.log_test(
                        "LLM Connection",
                        False,
                        data.get("message", "Erro desconhecido"),
                        duration,
                    )
                    return False
            else:
                self.log_test(
                    "LLM Connection",
                    False,
                    f"Status code: {response.status_code}",
                    duration,
                )
                return False

        except Exception as e:
            duration = time.time() - start_time
            self.log_test("LLM Connection", False, f"Erro: {e!s}", duration)
            return False

    async def test_chat_flow(self) -> bool:
        """Testa fluxo completo de chat"""
        start_time = time.time()
        try:
            # 1. Iniciar chat
            start_response = requests.post(
                f"{API_BASE_URL}/chat/start",
                json={"initial_message": "Teste automatizado", "user_id": "test_user"},
                timeout=10,
            )

            if start_response.status_code != 200:
                duration = time.time() - start_time
                self.log_test(
                    "Chat Flow",
                    False,
                    f"Erro ao iniciar chat: {start_response.status_code}",
                    duration,
                )
                return False

            start_data = start_response.json()
            session_id = start_data["session_id"]

            # 2. Enviar mensagem
            message_response = requests.post(
                f"{API_BASE_URL}/chat/message",
                json={
                    "session_id": session_id,
                    "message": "Este é um teste automatizado do sistema",
                    "context": None,
                },
                timeout=15,
            )

            if message_response.status_code != 200:
                duration = time.time() - start_time
                self.log_test(
                    "Chat Flow",
                    False,
                    f"Erro ao enviar mensagem: {message_response.status_code}",
                    duration,
                )
                return False

            # 3. Finalizar chat
            end_response = requests.post(
                f"{API_BASE_URL}/chat/end",
                json={"session_id": session_id, "reason": "test_completion"},
                timeout=10,
            )

            duration = time.time() - start_time

            if end_response.status_code == 200:
                self.log_test(
                    "Chat Flow", True, "Fluxo completo executado com sucesso", duration
                )
                return True
            else:
                self.log_test(
                    "Chat Flow",
                    False,
                    f"Erro ao finalizar chat: {end_response.status_code}",
                    duration,
                )
                return False

        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Chat Flow", False, f"Erro: {e!s}", duration)
            return False

    async def test_cache_functionality(self) -> bool:
        """Testa funcionalidade de cache"""
        start_time = time.time()
        try:
            # Verificar estatísticas do cache
            stats_response = requests.get(f"{API_BASE_URL}/stats/llm", timeout=5)

            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                cache_stats = stats_data.get("cache_stats", {})

                duration = time.time() - start_time
                self.log_test(
                    "Cache Stats",
                    True,
                    f"Cache size: {cache_stats.get('size', 0)}",
                    duration,
                )
                return True
            else:
                duration = time.time() - start_time
                self.log_test(
                    "Cache Stats",
                    False,
                    f"Status code: {stats_response.status_code}",
                    duration,
                )
                return False

        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Cache Stats", False, f"Erro: {e!s}", duration)
            return False

    async def test_rate_limiting(self) -> bool:
        """Testa rate limiting"""
        start_time = time.time()
        try:
            # Fazer múltiplas requisições rapidamente
            responses = []
            for i in range(5):
                response = requests.post(
                    f"{API_BASE_URL}/chat/start",
                    json={"user_id": f"test_user_{i}"},
                    timeout=5,
                )
                responses.append(response)

            duration = time.time() - start_time

            # Verificar se todas as requisições foram bem-sucedidas
            successful = all(r.status_code == 200 for r in responses)

            if successful:
                self.log_test(
                    "Rate Limiting",
                    True,
                    "5 requisições simultâneas processadas",
                    duration,
                )
                return True
            else:
                failed_count = sum(1 for r in responses if r.status_code != 200)
                self.log_test(
                    "Rate Limiting",
                    False,
                    f"{failed_count} requisições falharam",
                    duration,
                )
                return False

        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Rate Limiting", False, f"Erro: {e!s}", duration)
            return False

    async def test_error_handling(self) -> bool:
        """Testa tratamento de erros"""
        start_time = time.time()
        try:
            # Testar com dados inválidos
            response = requests.post(
                f"{API_BASE_URL}/chat/message", json={"invalid": "data"}, timeout=5
            )

            duration = time.time() - start_time

            # Deve retornar erro 422 (Unprocessable Entity) para dados inválidos
            if response.status_code == 422:
                self.log_test(
                    "Error Handling", True, "Validação de dados funcionando", duration
                )
                return True
            else:
                self.log_test(
                    "Error Handling",
                    False,
                    f"Status code inesperado: {response.status_code}",
                    duration,
                )
                return False

        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Error Handling", False, f"Erro: {e!s}", duration)
            return False

    async def run_all_tests(self):
        """Executa todos os testes"""
        print("🚀 Iniciando Testes de Integração LLM")
        print("=" * 50)

        tests = [
            self.test_health_endpoint,
            self.test_detailed_health,
            self.test_llm_connection,
            self.test_chat_flow,
            self.test_cache_functionality,
            self.test_rate_limiting,
            self.test_error_handling,
        ]

        for test in tests:
            try:
                await test()
            except Exception as e:
                self.log_test(test.__name__, False, f"Exceção: {e!s}", 0)

        self.print_summary()

    def print_summary(self):
        """Imprime resumo dos testes"""
        total_time = time.time() - self.start_time
        passed = sum(1 for r in self.results if r["success"])
        failed = len(self.results) - passed

        print("\n" + "=" * 50)
        print("📊 RESUMO DOS TESTES")
        print("=" * 50)
        print(f"Total de testes: {len(self.results)}")
        print(f"✅ Passou: {passed}")
        print(f"❌ Falhou: {failed}")
        print(f"⏱️  Tempo total: {total_time:.2f}s")

        if failed > 0:
            print("\n❌ TESTES QUE FALHARAM:")
            for result in self.results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")

        # Salvar resultados em arquivo
        with open("test_results.json", "w") as f:
            json.dump(
                {
                    "summary": {
                        "total": len(self.results),
                        "passed": passed,
                        "failed": failed,
                        "total_time": total_time,
                    },
                    "results": self.results,
                },
                f,
                indent=2,
            )

        print("\n📄 Resultados salvos em: test_results.json")

        if failed == 0:
            print("\n🎉 Todos os testes passaram!")
            return True
        else:
            print(f"\n⚠️  {failed} teste(s) falharam. Verifique os logs acima.")
            return False


async def main():
    """Função principal"""
    test_suite = LLMTestSuite()
    success = await test_suite.run_all_tests()

    if success:
        exit(0)
    else:
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
