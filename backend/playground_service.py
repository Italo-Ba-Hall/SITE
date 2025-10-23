"""
Serviço de Playground para Transcrição de Vídeos do YouTube
/-HALL-DEV Backend

Funcionalidades:
- Extração de transcrição de vídeos do YouTube
- Sumarização inteligente usando Google Gemini
- Extração de palavras-chave e pontos principais
"""

import hashlib
import os
import re
import time
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
                # Usar gemini-2.5-flash (modelo mais recente disponível)
                self.model = genai.GenerativeModel("gemini-2.5-flash")
            except Exception as e:
                print(f"Erro ao inicializar modelo Gemini: {e}")

        # Cache em memória para sumarizações
        self._cache: dict[str, dict[str, Any]] = {}
        self._cache_ttl: dict[str, float] = {}
        self.CACHE_TTL = 3600  # 1 hora em segundos

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

    def _get_transcript_direct(self, video_id: str) -> dict[str, Any]:
        """
        Obtém transcrição diretamente (método padrão - funciona em ambiente local)

        Args:
            video_id: ID do vídeo do YouTube

        Returns:
            Dicionário com dados da transcrição
        """
        # Criar instância da API
        api = YouTubeTranscriptApi()

        # Obter lista de transcrições disponíveis para o vídeo
        transcript_list = api.list(video_id)

        # Coletar todas as transcrições disponíveis
        # Estratégia: Priorizar transcrições manuais sobre automáticas
        manual_transcripts = []
        generated_transcripts = []

        # Iterar sobre o TranscriptList para separar manuais e automáticas
        for transcript in transcript_list:
            if transcript.is_generated:
                generated_transcripts.append(transcript)
            else:
                manual_transcripts.append(transcript)

        # Escolher a primeira transcrição disponível
        # Prioridade: Manual > Automática (idioma original)
        selected_transcript = None

        if manual_transcripts:
            selected_transcript = manual_transcripts[0]
        elif generated_transcripts:
            selected_transcript = generated_transcripts[0]
        else:
            raise NoTranscriptFound(
                video_id=video_id,
                requested_language_codes=[],
                transcript_data=None
            )

        # Buscar os dados da transcrição selecionada
        transcript_data = selected_transcript.fetch()
        language = selected_transcript.language_code

        if not transcript_data or len(transcript_data) == 0:
            raise ValueError(
                "Não foi possível obter transcrição. "
                "O vídeo pode não ter legendas disponíveis."
            )

        return self._process_transcript_data(video_id, transcript_data, language)

    def _get_transcript_with_scraperapi(self, video_id: str) -> dict[str, Any]:
        """
        Obtém transcrição usando ScraperAPI como proxy (para ambientes cloud bloqueados)

        Args:
            video_id: ID do vídeo do YouTube

        Returns:
            Dicionário com dados da transcrição
        """
        import requests
        import urllib3

        # Desabilitar warnings de SSL (necessário para proxy)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        api_key = os.getenv("SCRAPERAPI_KEY")

        if not api_key:
            raise ValueError("SCRAPERAPI_KEY não configurada")

        # ScraperAPI como proxy HTTP
        proxy_url = f"http://scraperapi:{api_key}@proxy-server.scraperapi.com:8001"
        proxies = {
            "http": proxy_url,
            "https": proxy_url
        }

        # Monkeypatch temporário para injetar proxy na biblioteca
        original_request = requests.get
        original_session_request = requests.Session.request

        def patched_request(*args, **kwargs):
            kwargs['proxies'] = proxies
            kwargs['timeout'] = 30
            kwargs['verify'] = False  # Desabilitar verificação SSL
            return original_request(*args, **kwargs)

        def patched_session_request(self, method, url, **kwargs):
            kwargs['proxies'] = proxies
            kwargs['timeout'] = 30
            kwargs['verify'] = False  # Desabilitar verificação SSL
            return original_session_request(self, method, url, **kwargs)

        # Aplicar patches temporariamente
        requests.get = patched_request
        requests.Session.request = patched_session_request

        try:
            api = YouTubeTranscriptApi()
            transcript_list = api.list(video_id)

            # Priorizar transcrições manuais
            manual_transcripts = []
            generated_transcripts = []

            for transcript in transcript_list:
                if transcript.is_generated:
                    generated_transcripts.append(transcript)
                else:
                    manual_transcripts.append(transcript)

            selected_transcript = None
            if manual_transcripts:
                selected_transcript = manual_transcripts[0]
            elif generated_transcripts:
                selected_transcript = generated_transcripts[0]
            else:
                raise NoTranscriptFound(
                    video_id=video_id,
                    requested_language_codes=[],
                    transcript_data=None
                )

            transcript_data = selected_transcript.fetch()
            language = selected_transcript.language_code

            if not transcript_data or len(transcript_data) == 0:
                raise ValueError("Transcrição vazia")

            return self._process_transcript_data(video_id, transcript_data, language)

        finally:
            # Restaurar funções originais
            requests.get = original_request
            requests.Session.request = original_session_request

    def _process_transcript_data(self, video_id: str, transcript_data: list, language: str) -> dict[str, Any]:
        """
        Processa dados brutos da transcrição em formato padronizado

        Args:
            video_id: ID do vídeo
            transcript_data: Lista de entradas da transcrição
            language: Código do idioma

        Returns:
            Dicionário formatado com transcrição completa
        """
        # Preservar timestamps e criar segments
        transcript_segments = []
        for entry in transcript_data:
            transcript_segments.append({
                "text": entry.text,
                "start": entry.start,
                "duration": entry.duration,
                "end": entry.start + entry.duration
            })

        # Manter compatibilidade: transcrição completa como string
        full_transcript = " ".join([entry.text for entry in transcript_data])

        # Calcular duração aproximada
        duration = None
        if transcript_data:
            last_entry = transcript_data[-1]
            duration = int(last_entry.start + last_entry.duration)

        return {
            "video_id": video_id,
            "video_url": f"https://www.youtube.com/watch?v={video_id}",
            "transcript": full_transcript,
            "language": language,
            "duration": duration,
            "title": None,
            "segments": transcript_segments,
        }

    def get_transcript(
        self, video_url: str
    ) -> dict[str, Any]:
        """
        Obtém a transcrição de um vídeo do YouTube com fallback inteligente

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
                "URL inválida. Por favor, forneça uma URL válida do YouTube."
            )

        # Estratégia 1: Tentar método direto (funciona em dev local)
        try:
            return self._get_transcript_direct(video_id)
        except TranscriptsDisabled:
            raise ValueError(
                "As legendas estão desabilitadas para este vídeo."
            ) from None
        except NoTranscriptFound:
            raise ValueError(
                "Este vídeo não possui legendas disponíveis."
            ) from None
        except VideoUnavailable:
            raise ValueError(
                "Vídeo não disponível ou privado."
            ) from None
        except Exception:
            # Se falhar E tivermos ScraperAPI configurado
            if os.getenv("SCRAPERAPI_KEY"):
                try:
                    # Estratégia 2: Tentar via ScraperAPI (produção)
                    print("Método direto falhou. Tentando via ScraperAPI...")
                    return self._get_transcript_with_scraperapi(video_id)
                except Exception:
                    # Ambos falharam - retornar mensagem amigável
                    raise ValueError(
                        "Não foi possível obter a transcrição. "
                        "Verifique se o vídeo possui legendas disponíveis."
                    ) from None
            else:
                # Sem ScraperAPI - mensagem amigável
                raise ValueError(
                    "Não foi possível obter a transcrição. "
                    "O vídeo pode estar bloqueado ou sem legendas."
                ) from None

    def _get_cache_key(self, transcript: str, context: str | None = None, keywords: list[str] | None = None) -> str:
        """Gera chave única para cache baseada no conteúdo"""
        # Usar primeiros 500 chars para gerar hash (suficiente para identificar transcrição)
        content = f"{transcript[:500]}_{context}_{','.join(keywords or [])}"
        return hashlib.sha256(content.encode()).hexdigest()

    def _is_cache_valid(self, key: str) -> bool:
        """Verifica se cache ainda é válido"""
        if key not in self._cache_ttl:
            return False
        elapsed = time.time() - self._cache_ttl[key]
        return elapsed < self.CACHE_TTL

    def _clear_expired_cache(self) -> None:
        """Remove entradas expiradas do cache"""
        current_time = time.time()
        expired_keys = [
            key for key, ttl in self._cache_ttl.items()
            if current_time - ttl >= self.CACHE_TTL
        ]
        for key in expired_keys:
            self._cache.pop(key, None)
            self._cache_ttl.pop(key, None)

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

        # Limpar cache expirado periodicamente
        self._clear_expired_cache()

        # Verificar cache primeiro
        cache_key = self._get_cache_key(transcript, context, keywords)
        if self._is_cache_valid(cache_key):
            print(f"Cache HIT para sumarização (key: {cache_key[:8]}...)")
            return self._cache[cache_key]

        print(f"Cache MISS para sumarização (key: {cache_key[:8]}...)")

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

            # Verificar se transcrição foi truncada
            _, was_truncated = self._chunk_transcript_intelligently(transcript)

            # Criar resultado
            result = {
                "summary": summary_text,
                "key_points": key_points,
                "keywords_found": keywords_found,
                "sections": sections,
                "confidence": 0.85,  # Confiança estimada
                "was_truncated": was_truncated,
            }

            # Salvar no cache
            self._cache[cache_key] = result
            self._cache_ttl[cache_key] = time.time()
            print(f"Resultado salvo em cache (key: {cache_key[:8]}...)")

            return result

        except Exception as e:
            raise ValueError(f"Erro ao gerar sumarização: {e!s}") from e

    def _chunk_transcript_intelligently(self, transcript: str, max_chunk_size: int = 15000) -> tuple[str, bool]:
        """
        Divide transcrição em segmentos lógicos

        Returns:
            Tupla (texto_processado, foi_cortado)
        """
        if len(transcript) <= max_chunk_size:
            return transcript, False

        # Dividir por sentenças completas (melhor que cortar no meio)
        sentences = transcript.split('. ')
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            test_chunk = current_chunk + sentence + ". "
            if len(test_chunk) > max_chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
            else:
                current_chunk = test_chunk

        if current_chunk:
            chunks.append(current_chunk.strip())

        # Retornar primeiros 3 chunks (mais relevantes geralmente no início)
        processed = " ".join(chunks[:3])
        was_truncated = len(chunks) > 3 or len(transcript) > max_chunk_size

        return processed, was_truncated

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
        prompt = """Você é um especialista em sumarização concisa e eficiente.

INSTRUÇÕES CRÍTICAS:
- Resumo: máximo 200 palavras
- Pontos principais: máximo 5 itens
- Linguagem direta e objetiva
- Zero redundâncias

FORMATO OBRIGATÓRIO:
**RESUMO:** [texto de no máximo 200 palavras]

**PONTOS PRINCIPAIS:**
• [ponto 1]
• [ponto 2]
• [ponto 3]
• [ponto 4]
• [ponto 5]

"""

        if context:
            prompt += f"**CONTEXTO FORNECIDO:** {context}\n"
            prompt += "Analise APENAS aspectos relacionados a este contexto.\n\n"

        if keywords:
            prompt += f"**PALAVRAS-CHAVE PARA DESTACAR:** {', '.join(keywords)}\n"
            prompt += "Identifique e destaque onde essas palavras aparecem.\n\n"

        # Chunking inteligente (remove limite fixo [:8000])
        transcript_processed, was_truncated = self._chunk_transcript_intelligently(transcript)

        if was_truncated:
            prompt += "⚠️ **NOTA:** Transcrição muito longa. Analisando primeiros segmentos.\n\n"

        prompt += f"**TRANSCRIÇÃO:**\n{transcript_processed}\n\n"
        prompt += "---\nRESPONDA APENAS NO FORMATO SOLICITADO. SEJA CONCISO."

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

    def _get_stop_words(self, language: str) -> set[str]:
        """Retorna stop words baseado no idioma"""
        stop_words_pt = {
            'o', 'a', 'os', 'as', 'um', 'uma', 'de', 'da', 'do', 'das', 'dos',
            'em', 'na', 'no', 'nas', 'nos', 'para', 'por', 'com', 'sem',
            'que', 'quando', 'onde', 'como', 'porque', 'então', 'mas', 'e', 'ou',
            'ele', 'ela', 'isso', 'este', 'esse', 'aquele', 'seu', 'sua'
        }

        stop_words_en = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'under', 'again', 'further',
            'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all',
            'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
            'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
            'can', 'will', 'just', 'should', 'now', 'it', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'we', 'they', 'what', 'which', 'who'
        }

        # Detectar idioma
        if language.startswith('pt'):
            return stop_words_pt
        elif language.startswith('en'):
            return stop_words_en
        else:
            # Fallback: união de ambos
            return stop_words_pt | stop_words_en

    def extract_keyword_suggestions(self, transcript: str, language: str = "pt") -> list[str]:
        """
        Extrai sugestões de palavras-chave da transcrição

        Args:
            transcript: Texto da transcrição
            language: Idioma da transcrição (para stop words corretas)

        Returns:
            Lista das 10 palavras mais relevantes
        """
        # Nota: 're' já está importado no topo do arquivo (linha 13)

        # Obter stop words corretas para o idioma
        stop_words = self._get_stop_words(language)

        # Extrair palavras significativas (3+ caracteres, não stop words)
        words = re.findall(r'\b[a-zA-ZÀ-ÿ]{3,}\b', transcript.lower())

        # Contar frequência
        word_count: dict[str, int] = {}
        for word in words:
            if word not in stop_words:
                word_count[word] = word_count.get(word, 0) + 1

        # Retornar top 10 palavras mais frequentes (mínimo 2 ocorrências)
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in sorted_words[:10] if count >= 2]

    def validate_keywords(self, keywords: list[str], transcript: str, language: str = "pt") -> dict[str, Any]:
        """
        Valida e analisa palavras-chave

        Args:
            keywords: Lista de palavras-chave fornecidas
            transcript: Texto da transcrição
            language: Idioma da transcrição

        Returns:
            Dicionário com análise das palavras-chave (inclui contagem de ocorrências)
        """
        found_keywords = []
        not_found_keywords = []

        transcript_lower = transcript.lower()

        for keyword in keywords:
            if keyword.lower() in transcript_lower:
                # Contar ocorrências
                count = transcript_lower.count(keyword.lower())
                found_keywords.append({
                    "keyword": keyword,
                    "count": count
                })
            else:
                not_found_keywords.append(keyword)

        return {
            "found": found_keywords,  # list[dict] com keyword e count
            "not_found": not_found_keywords,
            "suggestions": self.extract_keyword_suggestions(transcript, language)
        }


# Instância global do serviço
playground_service = PlaygroundService()
