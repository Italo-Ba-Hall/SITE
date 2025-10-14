**Implementação do Playground de Transcrição YouTube**

## Objetivo
Implementar funcionalidade de playground que permite:
- Inserir URL de vídeo do YouTube
- Obter transcrição literal do conteúdo
- Gerar sumarização inteligente com palavras-chave/contexto
- Visualizar vídeo integrado na interface

## Backend (Python/FastAPI)

### Dependências
- [ ] Adicionar `youtube-transcript-api` ao `requirements.txt`
- [ ] Instalar dependência no ambiente PythonAnywhere

### Novos Endpoints
- [ ] Criar `playground_service.py` com lógica de transcrição
- [ ] Adicionar endpoint `POST /playground/transcribe` em `main.py`
- [ ] Adicionar endpoint `POST /playground/summarize` em `main.py`
- [ ] Implementar validação de URL do YouTube
- [ ] Adicionar tratamento de erros (vídeo privado, sem transcrição)

### Schemas
- [ ] Criar `TranscribeRequest` em `schemas.py`
- [ ] Criar `TranscribeResponse` em `schemas.py`
- [ ] Criar `SummarizeRequest` em `schemas.py`
- [ ] Criar `SummarizeResponse` em `schemas.py`

## Frontend (React/TypeScript)

### Dependências
- [ ] Adicionar `react-youtube` ao `package.json`
- [ ] Instalar dependência: `npm install react-youtube`

### Componentes
- [ ] Criar `components/playground/PlaygroundContainer.tsx`
- [ ] Criar `components/playground/URLInput.tsx`
- [ ] Criar `components/playground/YouTubePlayer.tsx`
- [ ] Criar `components/playground/TranscriptionView.tsx`
- [ ] Criar `components/playground/SummaryView.tsx`

### Hooks
- [ ] Criar `hooks/usePlayground.ts` para gerenciar estado

### Roteamento
- [ ] Adicionar rota `/playground` no `App.tsx`
- [ ] Implementar lazy loading para componentes do playground

## Integração

### API Calls
- [ ] Implementar chamadas para `/playground/transcribe`
- [ ] Implementar chamadas para `/playground/summarize`
- [ ] Adicionar tratamento de loading/erro

### UX/UI
- [ ] Interface intuitiva para inserir URL com desing condizente com as cores temas do site original da /-HALL-DEV
- [ ] Exibição da transcrição com scroll
- [ ] Player de vídeo responsivo
- [ ] Formulário para palavras-chave/contexto da sumarização
- [ ] Feedback visual para processos (loading, sucesso, erro)

## **Deploy**

### Backend (PythonAnywhere)
- [ ] Instalar `youtube-transcript-api` no ambiente
- [ ] Reload da aplicação
- [ ] Testar endpoints: `/playground/transcribe` e `/playground/summarize`

### Frontend (WebFTP)
- [ ] Recompilar: `npm run build`
- [ ] Upload da pasta `build/` **atualizada** (INFORMAR AO USUARIO O QUE FOI INCLUIDO E O QUE DEVE SER ENVIADO PARA O UPLOAD DO DEPLOY)

## Testes

### Validação
- [ ] Testar com vídeos públicos do YouTube
- [ ] Testar com vídeos sem transcrição
- [ ] Testar com URLs inválidas
- [ ] Testar sumarização com diferentes contextos

### Performance
- [ ] Verificar tempo de resposta da transcrição
- [ ] Verificar tempo de resposta da sumarização
- [ ] Monitorar bundle size do frontend