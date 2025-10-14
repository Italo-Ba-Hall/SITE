"""
Script de teste detalhado para identificar problema na transcrição
"""
import os
import sys

from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

print("=" * 70)
print("TESTE DETALHADO DE TRANSCRIÇÃO - YouTube Playground")
print("=" * 70)

# 1. Verificar variáveis de ambiente
print("\n1. VERIFICANDO VARIÁVEIS DE AMBIENTE:")
print("-" * 70)
gemini_key = os.getenv("GEMINI_API_KEY")
print(f"GEMINI_API_KEY: {'OK Presente' if gemini_key else 'ERRO AUSENTE'}")
if gemini_key:
    print(f"   Primeiros 20 caracteres: {gemini_key[:20]}...")

# 2. Testar importações
print("\n2. TESTANDO IMPORTAÇÕES:")
print("-" * 70)
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    print("OK youtube_transcript_api importado com sucesso")
except Exception as e:
    print(f"ERRO ao importar youtube_transcript_api: {e}")
    sys.exit(1)

try:
    import google.generativeai as genai
    print("OK google.generativeai importado com sucesso")
except Exception as e:
    print(f"ERRO ao importar google.generativeai: {e}")
    sys.exit(1)

try:
    from playground_service import playground_service
    print("OK playground_service importado com sucesso")
except Exception as e:
    print(f"ERRO ao importar playground_service: {e}")
    sys.exit(1)

# 3. Testar extração de ID do vídeo
print("\n3. TESTANDO EXTRAÇÃO DE ID DO VÍDEO:")
print("-" * 70)
test_urls = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://youtu.be/dQw4w9WgXcQ",
    "dQw4w9WgXcQ"
]

for url in test_urls:
    video_id = playground_service.extract_video_id(url)
    status = "OK" if video_id == "dQw4w9WgXcQ" else "ERRO"
    print(f"{status} URL: {url} -> ID: {video_id}")

# 4. Testar acesso direto à API do YouTube (sem o serviço)
print("\n4. TESTANDO ACESSO DIRETO À API DO YOUTUBE:")
print("-" * 70)

# Vídeos de teste conhecidos com legendas
test_videos = [
    ("dQw4w9WgXcQ", "Rick Astley - Never Gonna Give You Up"),
    ("jNQXAC9IVRw", "Me at the zoo (primeiro vídeo do YouTube)"),
]

for video_id, description in test_videos:
    print(f"\nTestando: {description}")
    print(f"Video ID: {video_id}")
    try:
        # Tentar listar transcrições disponíveis
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        print("  OK Transcricoes encontradas:")

        available = []
        for transcript in transcript_list:
            lang = transcript.language_code
            is_generated = transcript.is_generated
            available.append(f"{lang} ({'auto' if is_generated else 'manual'})")

        print(f"    Disponíveis: {', '.join(available)}")

        # Tentar pegar uma transcrição
        try:
            transcript = transcript_list.find_transcript(['pt', 'pt-BR', 'en'])
            data = transcript.fetch()
            print("   Transcrição obtida com sucesso!")
            print(f"    Idioma: {transcript.language_code}")
            print(f"    Entradas: {len(data)}")
            print(f"    Primeiras 100 caracteres: {data[0]['text'][:100] if data else 'N/A'}...")
            break  # Encontrou um vídeo que funciona
        except Exception as e:
            print(f"   Erro ao buscar transcrição: {e}")

    except Exception as e:
        print(f"   Erro ao listar transcrições: {e}")

# 5. Testar o serviço playground completo
print("\n5. TESTANDO SERVIÇO PLAYGROUND COMPLETO:")
print("-" * 70)

# Usar o vídeo que funcionou acima
test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
print(f"URL de teste: {test_url}")

try:
    result = playground_service.get_transcript(test_url)
    print(" SUCESSO! Transcrição obtida através do serviço")
    print(f"  Video ID: {result['video_id']}")
    print(f"  Idioma: {result['language']}")
    print(f"  Duração: {result['duration']} segundos")
    print(f"  Tamanho da transcrição: {len(result['transcript'])} caracteres")
    print("  Primeiros 200 caracteres:")
    print(f"  {result['transcript'][:200]}...")
except ValueError as e:
    print(f" ERRO (ValueError): {e}")
except Exception as e:
    print(f" ERRO inesperado: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# 6. Verificar modelo Gemini
print("\n6. VERIFICANDO MODELO GEMINI:")
print("-" * 70)
try:
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    print(" Modelo Gemini inicializado com sucesso")

    # Teste simples
    response = model.generate_content("Diga apenas 'OK' se você está funcionando.")
    print(f" Teste de geração: {response.text[:50]}")
except Exception as e:
    print(f" ERRO ao inicializar/testar Gemini: {e}")

print("\n" + "=" * 70)
print("TESTE CONCLUÍDO")
print("=" * 70)
