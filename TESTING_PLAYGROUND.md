# YouTube Playground - Guia de Teste

## Status da Implementação

✅ **Frontend**: Completamente implementado
- Página `/playground` com interface integrada ao design do site
- Animação de fundo mantida
- Formulário de transcrição e sumarização
- Player de vídeo embutido

✅ **Backend**: Completamente implementado
- Endpoint `/playground/transcribe` para obter transcrições
- Endpoint `/playground/summarize` para gerar resumos com IA
- Validação de URLs robusta (suporta múltiplos formatos)
- Integração com Google Gemini para sumarização

⚠️ **Limitação Conhecida**: YouTube Transcript API
A biblioteca `youtube-transcript-api` pode ser bloqueada pelo YouTube dependendo do vídeo e da região. Isso é uma limitação conhecida da biblioteca, não um erro na implementação.

## Como Testar Localmente

### 1. Backend

```bash
cd backend
venv\Scripts\activate  # Windows
python start_server.py
```

O backend estará rodando em `http://localhost:8000`

### 2. Frontend

```bash
cd frontend
npm start
```

O frontend estará rodando em `http://localhost:3000`

### 3. Acessar o Playground

1. Navegue para `http://localhost:3000`
2. Clique no link "YouTube Playground →" na página inicial
3. Cole uma URL do YouTube no campo
4. Clique em "Transcrever"

## URLs de Teste Recomendadas

Use vídeos com legendas/transcrições disponíveis:

```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://youtu.be/dQw4w9WgXcQ
https://www.youtube.com/watch?v=VIDEO_ID&t=10s
```

## Formatos de URL Suportados

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `VIDEO_ID` (ID direto)

## Troubleshooting

### Erro 400 na Transcrição

**Causa**: YouTube bloqueou a requisição da biblioteca youtube-transcript-api

**Soluções**:
1. Tentar com outro vídeo (alguns vídeos funcionam, outros não)
2. Vídeos com legendas automáticas habilitadas têm mais chance de funcionar
3. Vídeos educacionais/tutoriais geralmente têm transcrições

### Sumarização não funciona

**Causa**: Chave da API Gemini não configurada

**Solução**: Verificar arquivo `.env` no backend:
```
GEMINI_API_KEY=sua_chave_aqui
```

## Arquivos Principais

### Backend
- `backend/playground_service.py` - Serviço de transcrição/sumarização
- `backend/schemas.py` - Schemas Pydantic
- `backend/main.py` - Endpoints FastAPI

### Frontend
- `frontend/src/components/PlaygroundPage.tsx` - Interface principal
- `frontend/src/hooks/usePlayground.ts` - Lógica de estado
- `frontend/src/App.tsx` - Rotas

## Deploy

Para gerar o build de produção:

```bash
cd frontend
npm run build
```

Os arquivos estarão em `frontend/build/` prontos para upload via FTP.
