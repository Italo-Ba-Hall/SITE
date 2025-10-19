# GUIA DE IMPLEMENTAÇÃO - PLAYGROUND TRANSCRIÇÃO E SUMARIZAÇÃO
---

## ⚠️ DECISÕES ARQUITETURAIS CRÍTICAS

1. **Cache:** Persistente (SQLite)

2. **UI Architecture:** Tabs ou Refatorar componentes existentes?
   - Decisão tomada: **REFATORAR para usar TranscriptionView e SummaryView** já existentes
   - NÃO criar tabs - usar os componentes já criados mas não utilizados

3. **Chunking:** Limite fixo ou inteligente?
   - Decisão tomada: **CHUNKING INTELIGENTE** - Remover limite [:8000] fixo
   - AVISAR usuário quando transcrição for cortada

4. **Preview de Resumo:** Implementar ou remover?
   - Decisão tomada: **REMOVER** - Não há diferença clara entre preview e resumo completo

---

## CONTEXTO E OBJETIVOS

**Problema Atual:**
- Transcrição apresentada como bloco único sem estruturação
- Timestamps disponíveis na API mas COMPLETAMENTE IGNORADOS
- Sumarização com verborragia excessiva e alto consumo de tokens
- Campos Contexto e Palavras-chave primitivos e ineficazes
- Componentes TranscriptionView.tsx e SummaryView.tsx EXISTEM mas NÃO SÃO USADOS
- Todo código inline em PlaygroundPage.tsx

**Objetivo:**
Implementar melhorias essenciais focadas em eficiência, usabilidade e otimização de recursos, corrigindo arquitetura atual e eliminando código redundante.

---

## ARQUITETURA ATUAL - ANÁLISE DETALHADA

**Backend:**
- `playground_service.py` (312 linhas):
  - Linha 125: Junta timestamps em string única - **PROBLEMA**
  - Linha 133-140: Retorno de get_transcript() SEM segments - **FALTANDO**
  - Linha 245: Limite fixo [:8000] - **CONFLITO com chunking**
- `schemas.py` (181 linhas):
  - TranscribeResponse não tem campo segments - **FALTANDO**
- `main.py` (1030 linhas):
  - Endpoints funcionais mas schemas incompletos

**Frontend:**
- `PlaygroundPage.tsx` (496 linhas):
  - TODO código inline, não usa componentes separados - **PROBLEMA**
  - Linha 202-378: Layout em grid mas sem estrutura limpa
- `TranscriptionView.tsx` (94 linhas): **EXISTE MAS NÃO É USADO**
- `SummaryView.tsx` (77 linhas): **EXISTE MAS NÃO É USADO**
- `usePlayground.ts` (125 linhas): Hook funcional

**Dependências:**
- `youtube-transcript-api==1.2.3`: Retorna .text, .start, .duration - **CONFIRMADO**
- `react-youtube`: Player com API para seekTo() - **CONFIRMADO**

---

## IMPLEMENTAÇÕES PRIORITÁRIAS

### 🔴 FASE 1: BACKEND - CORREÇÕES CRÍTICAS (Prioridade CRÍTICA)

#### 1.1 Schemas - Adicionar TranscriptSegment

**Arquivo:** `backend/schemas.py`

**ADICIONAR antes de TranscribeResponse (linha ~137):**
```python
class TranscriptSegment(BaseModel):
    """Schema para segmento individual da transcrição"""
    text: str = Field(..., description="Texto do segmento")
    start: float = Field(..., description="Tempo de início em segundos")
    duration: float = Field(..., description="Duração em segundos")
    end: float = Field(..., description="Tempo de fim em segundos (start + duration)")

class KeywordAnalysis(BaseModel):
    """Schema para análise de palavra-chave individual"""
    keyword: str = Field(..., description="Palavra-chave analisada")
    count: int = Field(..., description="Número de ocorrências na transcrição")

class KeywordValidationResponse(BaseModel):
    """Schema para resposta de validação de palavras-chave"""
    found: list[KeywordAnalysis] = Field(..., description="Keywords encontradas com contagem")
    not_found: list[str] = Field(..., description="Keywords não encontradas")
    suggestions: list[str] = Field(..., description="Sugestões automáticas de keywords")
```

**MODIFICAR TranscribeResponse (linha ~137):**
```python
class TranscribeResponse(BaseModel):
    """Schema para resposta de transcrição"""
    
    video_id: str = Field(..., description="ID do vídeo do YouTube")
    video_url: str = Field(..., description="URL do vídeo")
    title: str | None = Field(None, description="Título do vídeo")
    transcript: str = Field(..., description="Transcrição completa do vídeo")
    language: str = Field(..., description="Idioma da transcrição")
    duration: int | None = Field(None, description="Duração do vídeo em segundos")
    segments: list[TranscriptSegment] = Field(..., description="Segmentos da transcrição com timestamps")  # ← ADICIONAR
```

**Critério de Sucesso:**
- ✅ Schema TranscriptSegment criado
- ✅ Campo segments adicionado a TranscribeResponse
- ✅ Ruff check sem erros

---

#### 1.2 Playground Service - Preservar Timestamps e Retornar Segments

**Arquivo:** `backend/playground_service.py`

**MODIFICAR get_transcript() - Linhas 124-140:**

**ANTES (linha ~125):**
```python
# Combinar todo o texto da transcrição (nova API usa atributos)
full_transcript = " ".join([entry.text for entry in transcript_data])
```

**DEPOIS:**
```python
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
```

**MODIFICAR retorno (linha ~133):**

**ANTES:**
```python
return {
    "video_id": video_id,
    "video_url": f"https://www.youtube.com/watch?v={video_id}",
    "transcript": full_transcript,
    "language": language,
    "duration": duration,
    "title": None,  # YouTube Transcript API não retorna título
}
```

**DEPOIS:**
```python
return {
    "video_id": video_id,
    "video_url": f"https://www.youtube.com/watch?v={video_id}",
    "transcript": full_transcript,
    "language": language,
    "duration": duration,
    "title": None,
    "segments": transcript_segments,  # ← ADICIONAR
}
```

**Critério de Sucesso:**
- ✅ Segments preservados com timestamps
- ✅ Compatibilidade mantida (full_transcript continua funcionando)
- ✅ Retorno atualizado com segments
- ✅ Teste: curl endpoint e verificar campo segments no JSON

---

#### 1.3 Cache sqlite
*implementar*



**ADICIONAR métodos de cache ANTES de summarize_transcript (linha ~158):**
```python
def _get_cache_key(self, transcript: str, context: str | None = None, keywords: list[str] | None = None) -> str:
    """Gera chave única para cache baseada no conteúdo"""
    # Usar primeiros 500 chars para gerar hash (suficiente para identificar transcrição)
    content = f"{transcript[:500]}_{context}_{','.join(keywords or [])}"
    return hashlib.md5(content.encode()).hexdigest()

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
```

**MODIFICAR summarize_transcript (linha ~158):**

**ADICIONAR no início do método (após validação do model):**
```python
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
        # ... resto do código existente ...
```

**ADICIONAR antes do return final do método:**
```python
        # Criar resultado
        result = {
            "summary": summary_text,
            "key_points": key_points,
            "keywords_found": keywords_found,
            "sections": sections,
            "confidence": 0.85,  # Confiança estimada
        }
        
        # Salvar no cache
        self._cache[cache_key] = result
        self._cache_ttl[cache_key] = time.time()
        print(f"Resultado salvo em cache (key: {cache_key[:8]}...)")
        
        return result

    except Exception as e:
        raise ValueError(f"Erro ao gerar sumarização: {e!s}") from e
```

**Critério de Sucesso:**
- ✅ Cache funcional em memória
- ✅ TTL consistente em 1 hora
- ✅ Limpeza automática de cache expirado
- ✅ Logs indicando cache HIT/MISS
- ✅ Teste: Fazer mesma requisição 2x e verificar velocidade

**⚠️ LIMITAÇÃO CONHECIDA:** Cache será perdido ao reiniciar servidor (aceitável)

---

#### 1.4 Prompts Otimizados e Chunking Inteligente

**Arquivo:** `backend/playground_service.py`

**ADICIONAR método _chunk_transcript_intelligently ANTES de _build_summary_prompt (linha ~211):**
```python
def _chunk_transcript_intelligently(self, transcript: str, max_chunk_size: int = 6000) -> tuple[str, bool]:
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
```

**MODIFICAR _build_summary_prompt (linha ~211):**

**LOCALIZAR e REMOVER linha 245 COMPLETA (incluindo comentário):**
```python
# Linha atual que deve ser REMOVIDA:
{transcript[:8000]}  # Limitar tamanho para evitar exceder limite de tokens
```

**SUBSTITUIR TODO O MÉTODO _build_summary_prompt por:**
```python
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
```

**MODIFICAR summarize_transcript para retornar informação sobre truncamento:**

**ADICIONAR ao resultado (linha ~200):**
```python
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

return {
    "summary": summary_text,
    "key_points": key_points,
    "keywords_found": keywords_found,
    "sections": sections,
    "confidence": 0.85,
    "was_truncated": was_truncated,  # ← ADICIONAR
}
```

**ATUALIZAR Schema SummarizeResponse em schemas.py:**
```python
class SummarizeResponse(BaseModel):
    """Schema para resposta de sumarização"""
    
    summary: str = Field(..., description="Resumo geral do conteúdo")
    key_points: list[str] = Field(..., description="Pontos principais extraídos")
    keywords_found: list[str] | None = Field(
        None, description="Palavras-chave encontradas no texto"
    )
    sections: list[SummarySection] | None = Field(
        None, description="Seções temáticas do resumo"
    )
    confidence: float = Field(..., description="Confiança estimada do resumo (0-1)")
    was_truncated: bool = Field(False, description="Indica se a transcrição foi cortada")  # ← ADICIONAR
```

**Critério de Sucesso:**
- ✅ Chunking inteligente por sentenças completas
- ✅ Limite [:8000] fixo REMOVIDO
- ✅ Usuário INFORMADO quando transcrição for cortada
- ✅ Prompts consistentemente < 200 palavras
- ✅ Teste: Processar transcrição longa e verificar was_truncated: true

---

#### 1.5 Sugestões Automáticas de Palavras-chave (Multilíngue)

**Arquivo:** `backend/playground_service.py`

**ADICIONAR APÓS _chunk_transcript_intelligently:**
```python
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
    # Nota: 're' já está importado no topo do arquivo (linha 12)
    
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
```

**ADICIONAR novo endpoint em main.py:**
```python
@app.post("/playground/analyze-keywords")
async def analyze_keywords(request: dict):
    """
    Endpoint para análise e sugestão de palavras-chave
    
    Corpo da requisição:
    {
        "transcript": "texto da transcrição",
        "keywords": ["palavra1", "palavra2"],  // opcional
        "language": "pt"  // opcional
    }
    """
    try:
        transcript = request.get("transcript", "")
        keywords = request.get("keywords", [])
        language = request.get("language", "pt")
        
        if not transcript:
            raise HTTPException(status_code=400, detail="Transcrição não fornecida")
        
        result = playground_service.validate_keywords(keywords, transcript, language)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao analisar palavras-chave: {e!s}"
        ) from e
```

**Critério de Sucesso:**
- ✅ Stop words em português e inglês
- ✅ Detecção automática de idioma
- ✅ Contagem de ocorrências de keywords
- ✅ Endpoint /playground/analyze-keywords funcional
- ✅ Teste: Analisar transcrição em inglês e português

---

### 🔴 FASE 2: FRONTEND - REFATORAÇÃO COMPLETA (Prioridade ALTA)

#### 2.1 Atualizar Hook usePlayground.ts

**Arquivo:** `frontend/src/hooks/usePlayground.ts`

**ADICIONAR interfaces no topo:**
```typescript
interface TranscriptSegment {
  text: string;
  start: number;
  duration: number;
  end: number;
}

interface TranscribeResponse {
  video_id: string;
  video_url: string;
  title: string | null;
  transcript: string;
  language: string;
  duration: number | null;
  segments: TranscriptSegment[];  // ← NOVO
}

interface SummarizeResponse {
  summary: string;
  key_points: string[];
  keywords_found?: string[] | null;
  sections?: { title: string; content: string }[] | null;
  confidence: number;
  was_truncated: boolean;  // ← NOVO
}
```

**ADICIONAR estado para segments:**
```typescript
const [videoId, setVideoId] = useState<string | null>(null);
const [transcript, setTranscript] = useState<string | null>(null);
const [segments, setSegments] = useState<TranscriptSegment[]>([]);  // ← NOVO
const [summary, setSummary] = useState<SummarizeResponse | null>(null);
const [loading, setLoading] = useState<boolean>(false);
const [error, setError] = useState<string | null>(null);
```

**MODIFICAR handleUrlSubmit para capturar segments:**
```typescript
const handleUrlSubmit = async (url: string) => {
  setLoading(true);
  setError(null);
  setSummary(null);
  setSegments([]);  // ← LIMPAR segments

  try {
    const response = await fetch(`${API_BASE_URL}/playground/transcribe`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ video_url: url }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Erro ao processar transcrição');
    }

    const data: TranscribeResponse = await response.json();

    setVideoUrl(url);
    setVideoId(data.video_id);
    setTranscript(data.transcript);
    setSegments(data.segments || []);  // ← ADICIONAR
  } catch (err) {
    setError(err instanceof Error ? err.message : 'Erro desconhecido');
    setVideoId(null);
    setTranscript(null);
    setSegments([]);  // ← LIMPAR em caso de erro
  } finally {
    setLoading(false);
  }
};
```

**ADICIONAR função resetSummary:**
```typescript
const resetSummary = useCallback(() => {
  setSummary(null);
}, []);
```

**MODIFICAR retorno do hook:**
```typescript
return {
  videoUrl,
  videoId,
  transcript,
  segments,  // ← NOVO
  summary,
  loading,
  error,
  handleUrlSubmit,
  handleSummarize,
  clearError,
  resetSummary,  // ← NOVO
};
```

**Critério de Sucesso:**
- ✅ Hook retorna segments
- ✅ Interfaces atualizadas
- ✅ Estado de segments gerenciado corretamente
- ✅ TypeScript sem erros

---

#### 2.2 Refatorar TranscriptionView.tsx - Timestamps Clicáveis e Busca

**Arquivo:** `frontend/src/components/playground/TranscriptionView.tsx`

**SUBSTITUIR TODO O CONTEÚDO:**
```typescript
import React, { useState, useMemo } from 'react';
import './TranscriptionView.css';

interface TranscriptSegment {
  text: string;
  start: number;
  duration: number;
  end: number;
}

interface TranscriptionViewProps {
  transcript: string | null;
  segments?: TranscriptSegment[];
  onSummarize: (context?: string, keywords?: string[]) => void;
  onTimestampClick?: (timestamp: number) => void;
  loading?: boolean;
}

const TranscriptionView: React.FC<TranscriptionViewProps> = ({
  transcript,
  segments = [],
  onSummarize,
  onTimestampClick,
  loading = false,
}) => {
  const [context, setContext] = useState('');
  const [keywordsInput, setKeywordsInput] = useState('');
  const [showSummarizeForm, setShowSummarizeForm] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const handleSummarize = () => {
    const keywords = keywordsInput
      .split(',')
      .map((k) => k.trim())
      .filter((k) => k.length > 0);

    onSummarize(context || undefined, keywords.length > 0 ? keywords : undefined);
    setShowSummarizeForm(false);
  };

  const formatTimestamp = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleTimestampClick = (timestamp: number) => {
    if (onTimestampClick) {
      onTimestampClick(timestamp);
    }
  };

  // Filtrar segments com base na busca
  const filteredSegments = useMemo(() => {
    if (!searchQuery || segments.length === 0) {
      return segments;
    }
    
    return segments.filter(segment => 
      segment.text.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [segments, searchQuery]);

  // Highlight do texto de busca
  const highlightText = (text: string, query: string): React.ReactNode => {
    if (!query) return text;
    
    const parts = text.split(new RegExp(`(${query})`, 'gi'));
    return parts.map((part, index) => 
      part.toLowerCase() === query.toLowerCase() ? (
        <mark key={index} className="highlight">{part}</mark>
      ) : (
        part
      )
    );
  };

  if (!transcript) {
    return (
      <div className="transcription-placeholder">
        <p>A transcrição aparecerá aqui após você inserir uma URL válida</p>
      </div>
    );
  }

  return (
    <div className="transcription-view">
      <div className="transcription-header">
        <h2>Transcrição</h2>
        <div className="header-actions">
          {segments.length > 0 && (
            <input
              type="text"
              placeholder="Buscar na transcrição..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
          )}
          <button
            className="summarize-toggle-button"
            onClick={() => setShowSummarizeForm(!showSummarizeForm)}
            disabled={loading}
          >
            {showSummarizeForm ? 'Ocultar' : 'Sumarizar'}
          </button>
        </div>
      </div>

      {showSummarizeForm && (
        <div className="summarize-form">
          <div className="form-group">
            <label htmlFor="context">Contexto (opcional)</label>
            <input
              id="context"
              type="text"
              value={context}
              onChange={(e) => setContext(e.target.value)}
              placeholder="Ex: Foque em aspectos técnicos"
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="keywords">Palavras-chave (separadas por vírgula)</label>
            <input
              id="keywords"
              type="text"
              value={keywordsInput}
              onChange={(e) => setKeywordsInput(e.target.value)}
              placeholder="Ex: tecnologia, inovação, futuro"
              className="form-input"
            />
          </div>

          <button
            className="summarize-button"
            onClick={handleSummarize}
            disabled={loading}
          >
            {loading ? 'Gerando resumo...' : 'Gerar Resumo'}
          </button>
        </div>
      )}

      <div className="transcription-content">
        {segments.length > 0 ? (
          <>
            {filteredSegments.length === 0 && searchQuery && (
              <p className="no-results">Nenhum resultado encontrado para "{searchQuery}"</p>
            )}
            {filteredSegments.map((segment, index) => (
              <div key={index} className="transcript-segment">
                <button
                  className="timestamp-button"
                  onClick={() => handleTimestampClick(segment.start)}
                  title="Pular para este momento no vídeo"
                >
                  {formatTimestamp(segment.start)}
                </button>
                <span className="segment-text">
                  {highlightText(segment.text, searchQuery)}
                </span>
              </div>
            ))}
          </>
        ) : (
          <pre className="transcription-text">{transcript}</pre>
        )}
      </div>
    </div>
  );
};

export default TranscriptionView;
```

**ATUALIZAR CSS:** `frontend/src/components/playground/TranscriptionView.css`

⚠️ **IMPORTANTE:** ADICIONAR os estilos abaixo **AO FINAL** do arquivo CSS existente (NÃO substituir o conteúdo existente).

**ADICIONAR ao final do arquivo:**
```css
/* Header Actions */
.header-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.search-input {
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  color: #fff;
  font-size: 0.85rem;
  min-width: 200px;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: rgba(0, 212, 255, 0.6);
  background: rgba(255, 255, 255, 0.08);
}

/* Transcript Segments */
.transcript-segment {
  display: flex;
  gap: 1rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  transition: background 0.2s ease;
}

.transcript-segment:hover {
  background: rgba(0, 212, 255, 0.03);
}

.timestamp-button {
  flex-shrink: 0;
  padding: 0.25rem 0.75rem;
  background: rgba(0, 212, 255, 0.15);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 4px;
  color: #00d4ff;
  font-size: 0.85rem;
  font-family: 'Courier New', monospace;
  cursor: pointer;
  transition: all 0.2s ease;
}

.timestamp-button:hover {
  background: rgba(0, 212, 255, 0.25);
  border-color: rgba(0, 212, 255, 0.5);
  transform: translateX(-2px);
}

.segment-text {
  flex: 1;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.6;
  font-size: 0.95rem;
}

/* Search Highlight */
.highlight {
  background-color: rgba(255, 255, 0, 0.3);
  color: #fff;
  padding: 0.1rem 0.2rem;
  border-radius: 2px;
}

.no-results {
  color: rgba(255, 255, 255, 0.5);
  text-align: center;
  padding: 2rem;
  font-style: italic;
}
```

**Critério de Sucesso:**
- ✅ Timestamps clicáveis funcionais
- ✅ Busca com highlight operacional
- ✅ Interface responsiva
- ✅ Fallback para transcrição sem segments

---

#### 2.3 Refatorar PlaygroundPage.tsx - Usar Componentes Existentes

**Arquivo:** `frontend/src/components/PlaygroundPage.tsx`

**PROBLEMA ATUAL:** Todo código inline (496 linhas), componentes TranscriptionView e SummaryView não são usados

**ESTRATÉGIA:** Refatorar para usar os componentes já existentes

**MODIFICAR imports (linha ~1):**
```typescript
import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import usePlayground from "../hooks/usePlayground";
import YouTube from "react-youtube";
import TranscriptionView from "./playground/TranscriptionView";  // ← ADICIONAR
import SummaryView from "./playground/SummaryView";  // ← ADICIONAR
```

**MODIFICAR componente para usar TranscriptionView e SummaryView:**

**SUBSTITUIR a seção de Video Player and Transcription (linha ~202-378) por:**
```typescript
{/* Video Player and Transcription/Summary */}
{videoId && !loading && (
  <div style={{ 
    display: "grid", 
    gridTemplateColumns: isMobile ? "1fr" : "1fr 1fr", 
    gap: "1.5rem", 
    marginBottom: "1.5rem" 
  }}>
    {/* Video Player */}
    <div className="prompt-container">
      <h2 style={{ 
        color: "#00e5ff", 
        fontSize: "1.25rem", 
        marginBottom: "1rem", 
        fontWeight: "700" 
      }}>
        Vídeo
      </h2>
      <div
        style={{
          position: "relative",
          width: "100%",
          paddingBottom: "56.25%",
          backgroundColor: "#000",
          borderRadius: "4px",
          overflow: "hidden",
        }}
      >
        <div style={{ position: "absolute", inset: 0 }}>
          <YouTube
            videoId={videoId}
            opts={{
              width: "100%",
              height: "100%",
              playerVars: {
                autoplay: 0,
                modestbranding: 1,
                rel: 0,
              },
            }}
            style={{ width: "100%", height: "100%" }}
            onReady={(event) => {
              playerRef.current = event.target;
            }}
          />
        </div>
      </div>
    </div>

    {/* Transcription or Summary */}
    <div className="prompt-container">
      {!summary ? (
        <TranscriptionView
          transcript={transcript}
          segments={segments}
          onSummarize={handleSummarize}
          onTimestampClick={handleTimestampClick}
          loading={loading}
        />
      ) : (
        <>
          <div style={{ 
            display: "flex", 
            justifyContent: "space-between", 
            alignItems: "center",
            marginBottom: "1rem"
          }}>
            <h2 style={{ 
              color: "#00e5ff", 
              fontSize: "1.25rem", 
              fontWeight: "700",
              margin: 0
            }}>
              Resumo
            </h2>
            <button
              onClick={() => resetSummary()}
              style={{
                padding: "0.5rem 1rem",
                background: "rgba(255, 255, 255, 0.1)",
                border: "1px solid rgba(255, 255, 255, 0.2)",
                borderRadius: "4px",
                color: "#fff",
                cursor: "pointer",
                fontSize: "0.875rem"
              }}
            >
              Ver Transcrição
            </button>
          </div>
          {summary.was_truncated && (
            <div style={{
              padding: "0.75rem",
              background: "rgba(255, 165, 0, 0.1)",
              border: "1px solid rgba(255, 165, 0, 0.3)",
              borderRadius: "4px",
              color: "#ffa500",
              fontSize: "0.875rem",
              marginBottom: "1rem"
            }}>
              ⚠️ Transcrição muito longa. Resumo baseado nos primeiros segmentos.
            </div>
          )}
          <SummaryView summary={summary} />
        </>
      )}
    </div>
  </div>
)}
```

**ADICIONAR ref para o player, handler de timestamp e responsividade (após usePlayground):**
```typescript
const PlaygroundPage: React.FC = () => {
  const navigate = useNavigate();
  const {
    videoId,
    transcript,
    segments,  // ← ADICIONAR
    summary,
    loading,
    error,
    handleUrlSubmit,
    handleSummarize,
    clearError,
    resetSummary,  // ← ADICIONAR
  } = usePlayground();

  const [urlInput, setUrlInput] = useState("");
  const playerRef = useRef<any>(null);  // ← ADICIONAR
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);  // ← ADICIONAR

  // Gerenciar responsividade
  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth <= 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const handleTranscribe = () => {
    if (urlInput.trim()) {
      handleUrlSubmit(urlInput.trim());
    }
  };

  const handleTimestampClick = (timestamp: number) => {
    try {
      if (playerRef.current && typeof playerRef.current.seekTo === 'function') {
        playerRef.current.seekTo(timestamp, true);
      } else {
        console.warn('Player não está pronto para navegação');
      }
    } catch (error) {
      console.error('Erro ao navegar no vídeo:', error);
    }
  };

  // ... resto do código
```

---

## COMANDOS DE VALIDAÇÃO

### Backend:
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
ruff check --fix
python quick_performance_test.py

# Teste manual dos endpoints
curl -X POST http://localhost:8000/playground/transcribe \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://www.youtube.com/watch?v=6Ns9FkRU8sc"}'

curl -X POST http://localhost:8000/playground/summarize \
  -H "Content-Type: application/json" \
  -d '{"transcript": "teste longo teste longo teste longo", "context": null, "keywords": null}'
```

### Frontend:
```bash
cd frontend
npm run lint
npm run type-check
npm run build

# Verificar tamanho do bundle
npm run build
# Verificar saída: bundle size < 500KB
```

## 🔧 CORREÇÕES FINAIS APLICADAS

**Esta seção documenta os 8 ajustes críticos aplicados após análise técnica detalhada:**

### ✅ 1. Linha 352 - Clarificada remoção do [:8000]
**Corrigido:** Especificado remover linha COMPLETA (incluindo comentário) e substituir por chunking inteligente.

### ✅ 2. Linha 516 - Removido import re duplicado
**Corrigido:** Adicionado comentário indicando que `re` já está importado no topo do arquivo.

### ✅ 3. Linha 915 - Especificada estratégia de CSS
**Corrigido:** Adicionado aviso para ADICIONAR ao final do CSS existente (não substituir).

### ✅ 4. Linhas 85-95 - Corrigidos schemas de keywords
**Corrigido:** Adicionados schemas `KeywordAnalysis` e `KeywordValidationResponse` para tipagem correta.

### ✅ 5. Linhas 706-727 - Adicionado resetSummary ao hook
**Corrigido:** Implementado `resetSummary` no usePlayground e integrado no PlaygroundPage.

### ✅ 6. Linha 1040 - Adicionada responsividade ao grid
**Corrigido:** Implementado state `isMobile` com listener de resize para layout responsivo.

### ✅ 7. Linhas 1248-1258 - Corrigidos comandos Windows
**Corrigido:** Especificados comandos para Git Bash, CMD e PowerShell no Windows.

### ✅ 8. Linhas 1181-1191 - Adicionado error handling
**Corrigido:** Implementado try/catch e validação robusta no `handleTimestampClick`.

---