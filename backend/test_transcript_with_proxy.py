"""
Teste da transcrição com ScraperAPI
"""
import os
from dotenv import load_dotenv
from playground_service import playground_service

load_dotenv()

print("=" * 60)
print("TESTE: Transcrição com ScraperAPI")
print("=" * 60)

# Testar com vídeo público conhecido
test_video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

print(f"Video URL: {test_video_url}")
print()

try:
    print("Tentando obter transcrição...")
    result = playground_service.get_transcript(test_video_url)
    
    print("[OK] Transcrição obtida com sucesso!")
    print(f"Video ID: {result['video_id']}")
    print(f"Idioma: {result['language']}")
    print(f"Duração: {result['duration']}s")
    print(f"Segmentos: {len(result['segments'])}")
    print(f"Primeiros 200 chars: {result['transcript'][:200]}...")
    
except Exception as e:
    print(f"[ERRO] Falha: {e}")

print()
print("=" * 60)

