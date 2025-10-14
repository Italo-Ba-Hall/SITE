"""
Teste do endpoint real /playground/transcribe
"""
import requests

BASE_URL = "http://localhost:8000"

print("=" * 70)
print("TESTE DO ENDPOINT /playground/transcribe")
print("=" * 70)

# Dados de teste
test_data = {
    "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}

print("\n1. Testando POST /playground/transcribe")
print(f"   URL: {test_data['video_url']}")
print("-" * 70)

try:
    response = requests.post(
        f"{BASE_URL}/playground/transcribe",
        json=test_data,
        timeout=30
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("\n*** SUCESSO! ***")
        print(f"Video ID: {data.get('video_id')}")
        print(f"Idioma: {data.get('language')}")
        print(f"Duracao: {data.get('duration')} segundos")
        print(f"Tamanho transcricao: {len(data.get('transcript', ''))} caracteres")
        print(f"Primeiros 150 chars: {data.get('transcript', '')[:150]}")

        # Testar sumarização
        print("\n2. Testando POST /playground/summarize")
        print("-" * 70)

        summary_data = {
            "transcript": data.get('transcript'),
            "context": "musica pop anos 80",
            "keywords": ["amor", "romance", "dedicacao"]
        }

        summary_response = requests.post(
            f"{BASE_URL}/playground/summarize",
            json=summary_data,
            timeout=30
        )

        print(f"Status Code: {summary_response.status_code}")

        if summary_response.status_code == 200:
            summary = summary_response.json()
            print("\n*** SUMARIZACAO FUNCIONOU! ***")
            print(f"Confianca: {summary.get('confidence') * 100}%")
            print(f"Pontos principais: {len(summary.get('key_points', []))}")
            print(f"Keywords encontradas: {summary.get('keywords_found')}")
            print(f"Resumo (primeiros 200 chars): {summary.get('summary', '')[:200]}")
        else:
            print(f"\nERRO na sumarizacao: {summary_response.text}")

    else:
        print(f"\nERRO: {response.text}")

except requests.exceptions.ConnectionError:
    print("\nERRO: Nao foi possivel conectar ao servidor.")
    print("       Certifique-se de que o backend esta rodando em http://localhost:8000")
except Exception as e:
    print(f"\nERRO inesperado: {e}")

print("\n" + "=" * 70)
print("TESTE CONCLUIDO")
print("=" * 70)
