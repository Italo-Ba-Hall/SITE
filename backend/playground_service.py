"""
Serviço de Playground para Transcrição de Vídeos do YouTube
/-HALL-DEV Backend

Funcionalidades:
- Extração de transcrição de vídeos do YouTube
- Sumarização inteligente usando Google Gemini
- Extração de palavras-chave e pontos principais
"""

import os
import re
from typing import Any

import google.generativeai as genai
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)

# Carregar variáveis de ambiente
load_dotenv()

# Configurar Google Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


class PlaygroundService:
    """Serviço para operações de playground"""

    def __init__(self):
        """Inicializa o serviço de playground"""
        self.model = None
        if GEMINI_API_KEY:
            try:
                self.model = genai.GenerativeModel("gemini-1.5-flash")
            except Exception as e:
                print(f"Erro ao inicializar modelo Gemini: {e}")

    def extract_video_id(self, url: str) -> str | None:
        """
        Extrai o ID do vídeo de uma URL do YouTube

        Args:
            url: URL do vídeo do YouTube

        Returns:
            ID do vídeo ou None se não for possível extrair
        """
        # Padrões de URL do YouTube (mais flexíveis)
        patterns = [
            r"(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})",
            r"youtube\.com\/watch\?.*[&?]v=([a-zA-Z0-9_-]{11})",
            r"^([a-zA-Z0-9_-]{11})$",  # ID direto
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    def get_transcript(
        self, video_url: str
    ) -> dict[str, Any]:
        """
        Obtém a transcrição de um vídeo do YouTube

        Args:
            video_url: URL do vídeo do YouTube

        Returns:
            Dicionário com informações da transcrição

        Raises:
            ValueError: Se a URL for inválida ou o vídeo não tiver transcrição
        """
        # Extrair ID do vídeo
        video_id = self.extract_video_id(video_url)
        if not video_id:
            raise ValueError(
                f"URL inválida: '{video_url}'. Por favor, forneça uma URL válida do YouTube "
                "(ex: https://www.youtube.com/watch?v=VIDEO_ID ou https://youtu.be/VIDEO_ID)"
            )

        try:
            # Tentar obter transcrição em português primeiro
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

                # Tentar português primeiro
                try:
                    transcript = transcript_list.find_transcript(["pt", "pt-BR"])
                    language = "pt"
                except Exception:
                    # Se não houver em português, tentar inglês
                    try:
                        transcript = transcript_list.find_transcript(["en"])
                        language = "en"
                    except Exception:
                        # Pegar o primeiro disponível
                        transcript = transcript_list.find_generated_transcript(["pt", "pt-BR", "en"])
                        language = transcript.language_code

                transcript_data = transcript.fetch()

            except Exception:
                # Fallback: tentar obter qualquer transcrição disponível
                transcript_data = YouTubeTranscriptApi.get_transcript(
                    video_id, languages=["pt", "pt-BR", "en"]
                )
                language = "pt"  # Assumir português como padrão

            # Combinar todo o texto da transcrição
            full_transcript = " ".join([entry["text"] for entry in transcript_data])

            # Calcular duração aproximada
            duration = None
            if transcript_data:
                last_entry = transcript_data[-1]
                duration = int(last_entry.get("start", 0) + last_entry.get("duration", 0))

            return {
                "video_id": video_id,
                "video_url": f"https://www.youtube.com/watch?v={video_id}",
                "transcript": full_transcript,
                "language": language,
                "duration": duration,
                "title": None,  # YouTube Transcript API não retorna título
            }

        except TranscriptsDisabled as exc:
            raise ValueError(
                "As transcrições estão desabilitadas para este vídeo."
            ) from exc
        except NoTranscriptFound as exc:
            raise ValueError(
                "Nenhuma transcrição disponível para este vídeo. "
                "O vídeo pode não ter legendas ou transcrição automática."
            ) from exc
        except VideoUnavailable as exc:
            raise ValueError(
                "Vídeo não disponível. Verifique se o vídeo existe e é público."
            ) from exc
        except Exception as e:
            raise ValueError(f"Erro ao obter transcrição: {e!s}") from e

    def summarize_transcript(
        self, transcript: str, context: str | None = None, keywords: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Sumariza uma transcrição usando Google Gemini

        Args:
            transcript: Texto da transcrição
            context: Contexto ou instruções adicionais
            keywords: Lista de palavras-chave para destacar

        Returns:
            Dicionário com o resumo e informações extraídas
        """
        if not self.model:
            raise ValueError(
                "Serviço de sumarização não disponível. Verifique a configuração da API Gemini."
            )

        try:
            # Construir prompt para o Gemini
            prompt = self._build_summary_prompt(transcript, context, keywords)

            # Gerar resumo
            response = self.model.generate_content(prompt)

            # Processar resposta
            summary_text = response.text

            # Extrair seções do resumo
            sections = self._extract_sections(summary_text)

            # Extrair pontos principais
            key_points = self._extract_key_points(summary_text)

            # Identificar palavras-chave encontradas
            keywords_found = None
            if keywords:
                keywords_found = [
                    kw for kw in keywords if kw.lower() in transcript.lower()
                ]

            return {
                "summary": summary_text,
                "key_points": key_points,
                "keywords_found": keywords_found,
                "sections": sections,
                "confidence": 0.85,  # Confiança estimada
            }

        except Exception as e:
            raise ValueError(f"Erro ao gerar sumarização: {e!s}") from e

    def _build_summary_prompt(
        self, transcript: str, context: str | None, keywords: list[str] | None
    ) -> str:
        """
        Constrói o prompt para sumarização

        Args:
            transcript: Texto da transcrição
            context: Contexto adicional
            keywords: Palavras-chave para destacar

        Returns:
            Prompt formatado
        """
        prompt = """Você é um assistente especializado em análise de conteúdo e sumarização.

Analise a seguinte transcrição de vídeo do YouTube e forneça:

1. **RESUMO GERAL**: Um resumo conciso (2-3 parágrafos) do conteúdo principal
2. **PONTOS PRINCIPAIS**: Liste os 5-7 pontos mais importantes (formato bullet points)
3. **SEÇÕES TEMÁTICAS**: Se aplicável, divida o conteúdo em seções temáticas

"""

        if context:
            prompt += f"\n**CONTEXTO FORNECIDO**: {context}\n"

        if keywords:
            prompt += f"\n**PALAVRAS-CHAVE PARA DESTACAR**: {', '.join(keywords)}\n"

        prompt += f"""
---

**TRANSCRIÇÃO**:
{transcript[:8000]}  # Limitar tamanho para evitar exceder limite de tokens

---

Por favor, forneça uma análise estruturada e clara do conteúdo.
"""

        return prompt

    def _extract_sections(self, summary_text: str) -> list[dict[str, str]] | None:
        """
        Extrai seções do texto de resumo

        Args:
            summary_text: Texto do resumo

        Returns:
            Lista de seções ou None
        """
        sections = []

        # Tentar identificar seções com marcadores **TÍTULO**:
        section_pattern = r"\*\*([^*]+)\*\*:\s*([^\n]+(?:\n(?!\*\*)[^\n]+)*)"
        matches = re.finditer(section_pattern, summary_text)

        for match in matches:
            title = match.group(1).strip()
            content = match.group(2).strip()
            sections.append({"title": title, "content": content})

        return sections if sections else None

    def _extract_key_points(self, summary_text: str) -> list[str]:
        """
        Extrai pontos principais do resumo

        Args:
            summary_text: Texto do resumo

        Returns:
            Lista de pontos principais
        """
        key_points = []

        # Procurar por listas com marcadores (-, *, •, números)
        bullet_patterns = [
            r"[-*•]\s*([^\n]+)",  # - ou * ou •
            r"\d+\.\s*([^\n]+)",  # Números com ponto
        ]

        for pattern in bullet_patterns:
            matches = re.finditer(pattern, summary_text)
            for match in matches:
                point = match.group(1).strip()
                if len(point) > 10 and point not in key_points:  # Evitar duplicatas e pontos muito curtos
                    key_points.append(point)

        # Se não encontrar pontos estruturados, dividir por sentenças
        if not key_points:
            sentences = [s.strip() for s in summary_text.split(".") if len(s.strip()) > 20]
            key_points = sentences[:7]  # Limitar a 7 pontos

        return key_points[:10]  # Limitar a 10 pontos principais


# Instância global do serviço
playground_service = PlaygroundService()
