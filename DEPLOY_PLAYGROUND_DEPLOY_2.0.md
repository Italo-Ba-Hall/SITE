# Guia de Deploy - Playground de Transcrição YouTube (v2.0)

## Resumo da Implementação

Foi implementado um **Playground de Transcrição YouTube** completo com as seguintes funcionalidades:
---
## Arquivos Criados/Modificados

### Backend

#### Novos Arquivos:
1. **`backend/playground_service.py`** - Serviço de transcrição e sumarização
   - Atualizado para usar `youtube-transcript-api==1.2.3` (nova API)
   - Modelo Gemini atualizado para `gemini-2.5-flash`

#### Arquivos Modificados:
1. **`backend/requirements.txt`**
   - ⚠️ **IMPORTANTE**: `youtube-transcript-api==1.2.3`

2. **`backend/schemas.py`** - Schemas adicionados:
   - `TranscribeRequest`
   - `TranscribeResponse`
   - `SummarizeRequest`
   - `SummarizeResponse`
   - `SummarySection`

3. **`backend/main.py`** - Endpoints adicionados:
   - `POST /playground/transcribe`
   - `POST /playground/summarize`

### Frontend

#### Componente Principal:
1. **`frontend/src/components/PlaygroundPage.tsx`** - Página completa do playground
   - Design integrado com `.prompt-container` e classes do site principal
   - Usa `useNavigate` para navegação
   - Formatação de transcrição em parágrafos

#### Hooks:
1. **`frontend/src/hooks/usePlayground.ts`** - Hook para gerenciar estado

#### Arquivos Modificados:
1. **`frontend/package.json`** - Dependência adicionada:
   ```json
   "react-youtube": "^10.1.0"
   ```

2. **`frontend/src/App.tsx`** - Rota adicionada:
   ```typescript
   <Route path="/playground" element={<PlaygroundPage />} />
   ```

3. **`frontend/src/components/MainContent.tsx`**
   - Adicionado link "YouTube Playground →"
   - SessionStorage para não repetir animação ao voltar

4. **`frontend/src/components/AnimationIntro.tsx`**
   - Marca `sessionStorage.setItem('introShown', 'true')` quando completa

---

## Deploy do Backend (PythonAnywhere)

### Passo 1: Instalar/Atualizar Dependências

```bash
# No console do PythonAnywhere, acesse o ambiente virtual
cd ~/2_project_newsite_hall-dev/backend
source venv/bin/activate

# ⚠️ IMPORTANTE: Atualizar biblioteca para versão 1.2.3
pip install --upgrade youtube-transcript-api==1.2.3

# Verificar instalação
pip show youtube-transcript-api
# Deve mostrar: Version: 1.2.3
```

### Passo 2: Upload dos Arquivos

Faça upload dos seguintes arquivos para o PythonAnywhere:

**Arquivos Novos:**
- `backend/playground_service.py`

**Arquivos Modificados:**
- `backend/requirements.txt` (contém `youtube-transcript-api==1.2.3`)
- `backend/schemas.py`
- `backend/main.py`

### Passo 3: Verificar Configuração

Certifique-se de que a variável `GEMINI_API_KEY` está configurada no arquivo `.env`:

```bash
GEMINI_API_KEY=AIzaSyClNj9HhqzUz6n272E_fxZiANQH_hffLWE
```

### Passo 4: Reload da Aplicação

1. Acesse o painel do PythonAnywhere
2. Vá para a seção "Web"
3. Clique em **"Reload"** para reiniciar a aplicação

### Passo 5: Testar Endpoints

```bash
# Testar transcrição
curl -X POST https://barrahall.pythonanywhere.com/playground/transcribe \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'

# Resposta esperada (200 OK):
# {
#   "video_id": "dQw4w9WgXcQ",
#   "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
#   "title": null,
#   "transcript": "Não somos estranhos ao amor...",
#   "language": "pt",
#   "duration": 211
# }
```

---

## Deploy do Frontend (WebFTP)

### Passo 1: Build de Produção (JÁ GERADO)

✅ O build de produção já foi gerado com sucesso!
- Localização: `frontend/build/`
- Tamanho total: ~70 KB (gzipped)
- Sem erros de compilação

### Passo 2: Estrutura de Arquivos no Build

```
frontend/build/
├── static/
│   ├── css/
│   │   └── main.710c78c8.css (1.74 KB)
│   └── js/
│       ├── main.a943cfeb.js (69.94 KB - arquivo principal)
│       ├── 608.5288fe71.chunk.js (8.91 KB)
│       ├── 891.3eef861d.chunk.js (6.02 KB)
│       ├── 509.cec6c077.chunk.js (4.22 KB)
│       └── 206.ed2f3d44.chunk.js (1.72 KB)
├── index.html
├── manifest.json
├── robots.txt
└── favicon.ico
```

### Passo 3: Upload via WebFTP

**IMPORTANTE: Fazer backup antes de substituir arquivos!**

#### Estrutura de Upload para `public_html/`:

```
public_html/
├── static/
│   ├── css/
│   │   └── main.710c78c8.css
│   └── js/
│       ├── main.a943cfeb.js
│       ├── 608.5288fe71.chunk.js
│       ├── 891.3eef861d.chunk.js
│       ├── 509.cec6c077.chunk.js
│       └── 206.ed2f3d44.chunk.js
├── index.html (SUBSTITUIR)
├── manifest.json
├── robots.txt
└── (manter arquivos existentes)
```

#### Checklist de Upload:

- [ ] Deletar pasta `public_html/static/` antiga (se existir)
- [ ] Upload de **TODA** a pasta `build/static/` (CSS e JS)
- [ ] Substituir `index.html`
- [ ] Manter `favicon.ico`, `manifest.json`, `robots.txt`
- [ ] Verificar permissões dos arquivos (644 para arquivos, 755 para pastas)

### Passo 4: Verificar Deploy

Após upload, testar no navegador:

1. **Página Principal**: `http://barrahall.dev.br/`
   - Deve carregar normalmente
   - Link "YouTube Playground →" deve estar visível

2. **Página Playground**: `http://barrahall.dev.br/playground`
   - Deve carregar com o design /-HALL-DEV
   - Botão "← Voltar" no canto superior direito
   - Campo de input com estilo da página principal

3. **Testar Funcionalidade**:
   - Cole uma URL do YouTube (ex: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`)
   - Clique em "Transcrever" ou pressione Enter
   - Deve aparecer o player e a transcrição formatada
   - Testar botão "Sumarizar"

---

## Solução de Problemas

### Backend

**Problema: Erro "No module named 'youtube_transcript_api'"**
```bash
# Solução: Reinstalar biblioteca
pip uninstall youtube-transcript-api
pip install youtube-transcript-api==1.2.3
```

**Problema: Erro 400 na transcrição**
- Verificar se a biblioteca está na versão 1.2.3
- A versão 0.6.2 antiga NÃO funciona (YouTube bloqueou)

**Problema: Erro do Gemini "model not found"**
- Verificar se `playground_service.py` usa `gemini-2.5-flash`
- Versão antiga `gemini-1.5-flash` não existe mais

### Frontend

**Problema: Página playground não aparece**
- Limpar cache do navegador (Ctrl+Shift+Delete)
- Verificar se arquivo `index.html` foi substituído
- Verificar se todos os arquivos JS foram carregados (F12 > Network)

**Problema: Botão "Voltar" não funciona**
- Verificar console do navegador (F12)
- Confirmar que `AnimationIntro.tsx` e `MainContent.tsx` foram atualizados

**Problema: Transcrição aparece sem formatação**
- Confirmar que `PlaygroundPage.tsx` tem a função `formatTranscript`
- Verificar se o build inclui as últimas alterações

---

## Notas Importantes

1. **Biblioteca YouTube Transcript API**:
   - ⚠️ Versão 1.2.3 é OBRIGATÓRIA
   - API mudou completamente entre 0.6.2 e 1.2.3
   - Código foi adaptado para nova API

2. **Modelo Gemini**:
   - Usando `gemini-2.5-flash` (mais recente)
   - Modelo antigo `gemini-1.5-flash` não existe

3. **Design**:
   - Totalmente integrado com `.prompt-container`
   - Usa mesma fonte: `Roboto Mono`
   - Cores consistentes: `#00e5ff` (cyan)

4. **Performance**:
   - Build otimizado sem source maps
   - Total: ~70 KB gzipped
   - Lazy loading de componentes

---

## Testes de Qualidade Executados

✅ **Backend**:
- Ruff: Passou sem erros
- Testes manuais: Transcrição e sumarização funcionando

✅ **Frontend**:
- ESLint: Passou sem erros
- TypeScript: Passou sem erros de tipo
- Build: Gerado com sucesso

---

## Comandos Úteis

### Backend (Local)
```bash
cd backend
venv/Scripts/activate  # Windows
source venv/bin/activate  # Linux/Mac
python start_server.py
```

### Frontend (Local)
```bash
cd frontend
npm start  # Desenvolvimento
npm run build  # Produção
npm run lint:fix  # Corrigir erros
```

---

## Suporte

Em caso de problemas durante o deploy:

1. Verificar logs do PythonAnywhere (Error log)
2. Verificar console do navegador (F12)
3. Testar endpoints diretamente com curl
4. Verificar se todas as dependências foram instaladas

**Deploy realizado em**: 2025-10-14
**Versão**: 2.0
**Status**: ✅ Pronto para produção
