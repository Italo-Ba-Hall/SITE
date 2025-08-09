# 🚀 /-HALL-DEV - Plataforma Conversacional

Uma plataforma web conversacional moderna para captação e qualificação de leads de forma inteligente. A interface utiliza um agente de IA que guia o usuário a soluções personalizadas através de um sistema de sugestões dinâmicas.

## ✨ Características

- **Interface Conversacional**: Abandona a navegação tradicional em favor de um agente de IA
- **Sugestões Inteligentes**: Sistema baseado em palavras-chave que evolui para PLN
- **Design Minimalista**: Estética moderna e dinâmica refletindo vanguarda tecnológica
- **Performance Otimizada**: Code splitting, lazy loading, cache estratégico
- **Responsivo**: Mobile-first design com animações fluidas
- **Acessibilidade**: Error boundaries, loading states, feedback visual

## 🛠️ Tecnologias

### Frontend
- **React 19** com TypeScript
- **TailwindCSS** para estilização
- **Hooks personalizados** para API management
- **Error Boundaries** para tratamento de erros
- **Lazy loading** e code splitting

### Backend
- **FastAPI** com Python
- **Pydantic** para validação de dados
- **Uvicorn** como ASGI server
- **CORS** configurado para frontend

## 📦 Instalação

### Pré-requisitos
- Node.js >= 16.0.0
- npm >= 8.0.0
- Python >= 3.9
- pip

### 1. Clone o repositório
```bash
git clone <repository-url>
cd 2_project_newsite_hall-dev
```

### 2. Instale as dependências do Frontend
```bash
cd frontend
npm install
```

### 3. Instale as dependências do Backend
```bash
cd ../backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate.bat  # Windows
pip install -r requirements.txt
```

## 🚀 Executando o Projeto

### Desenvolvimento

#### Backend
```bash
cd backend
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate.bat  # Windows
python main.py
```
O backend estará disponível em: http://localhost:8000

#### Frontend
```bash
cd frontend
npm start
```
O frontend estará disponível em: http://localhost:3000

### Teste Automatizado
Execute o script de teste para validar o funcionamento:

**Linux/Mac:**
```bash
./test-project.sh
```

**Windows:**
```bash
test-project.bat
```

## 🧪 Testando

### Frontend
```bash
cd frontend
npm test
npm run type-check
npm run lint
```

### Backend
```bash
cd backend
source venv/bin/activate
python -m pytest
```

### Build de Produção
```bash
cd frontend
npm run build
```

## 📡 API Endpoints

### Health Check
```
GET /health
```

### Sugestões
```
POST /suggest
Content-Type: application/json
{
  "text": "desenvolvimento web"
}
```

### Conteúdo Detalhado
```
GET /content/{suggestion_id}
```

### Contato
```
POST /contact
Content-Type: application/json
{
  "nome": "João Silva",
  "email": "joao@email.com",
  "mensagem": "Gostaria de saber mais sobre desenvolvimento web",
  "suggestion_id": "web-dev"
}
```

## 🏗️ Estrutura do Projeto

```
2_project_newsite_hall-dev/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AnimationIntro.tsx
│   │   │   ├── BackgroundCanvas.tsx
│   │   │   ├── ErrorBoundary.tsx
│   │   │   ├── MainContent.tsx
│   │   │   ├── Navbar.tsx
│   │   │   ├── ResultModal.tsx
│   │   │   └── SuggestionsDropdown.tsx
│   │   ├── hooks/
│   │   │   └── useApi.ts
│   │   ├── config/
│   │   │   └── performance.ts
│   │   ├── App.tsx
│   │   └── index.css
│   ├── package.json
│   ├── tailwind.config.js
│   └── postcss.config.js
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── venv/
├── CHECKLIST_PROJECT.md
├── deploy-config.md
├── test-project.sh
├── test-project.bat
└── README.md
```

## 🚀 Deploy

### Frontend (Vercel/Netlify)
1. Conecte o repositório no Vercel/Netlify
2. Configure as variáveis de ambiente:
   ```
   REACT_APP_API_URL=https://seu-backend.vercel.app
   ```
3. Deploy automático

### Backend (Render/Railway)
1. Conecte o repositório no Render/Railway
2. Configure:
   ```
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
3. Adicione variáveis de ambiente
4. Deploy automático

## 🔧 Configurações

### Variáveis de Ambiente

#### Frontend (.env.production)
```bash
REACT_APP_API_URL=https://seu-backend.vercel.app
REACT_APP_ENVIRONMENT=production
```

#### Backend (.env)
```bash
DATABASE_URL=sua_url_do_banco
EMAIL_SERVICE_API_KEY=sua_chave_email
CORS_ORIGINS=https://seu-frontend.vercel.app
```

## 📊 Performance

### Otimizações Implementadas
- ✅ Code splitting automático
- ✅ Lazy loading de componentes
- ✅ Cache estratégico para API calls
- ✅ Debounce para evitar requisições excessivas
- ✅ Bundle optimization
- ✅ Error boundaries
- ✅ Responsive design
- ✅ Accessibility features

### Métricas Esperadas
- **First Contentful Paint**: < 1.5s
- **Largest Contentful Paint**: < 2.5s
- **Cumulative Layout Shift**: < 0.1
- **First Input Delay**: < 100ms

## 🎯 Funcionalidades

### Fluxo do Usuário
1. **Entrada**: Usuário digita no prompt "No que você trabalha?..."
2. **Análise**: Sistema processa o texto e gera sugestões relevantes
3. **Sugestões**: Dropdown mostra opções personalizadas
4. **Seleção**: Usuário clica em uma sugestão
5. **Detalhes**: Modal exibe informações detalhadas
6. **Contato**: Formulário para capturar lead

### Sugestões Disponíveis
- **Desenvolvimento Web**: Sites e aplicações web modernas
- **Desenvolvimento Mobile**: Apps nativos e multiplataforma
- **Soluções em IA**: Implementação de Inteligência Artificial
- **Consultoria Personalizada**: Análise específica do projeto

## 🔒 Segurança

- Validação de dados com Pydantic
- CORS configurado adequadamente
- Sanitização de inputs
- Error handling robusto
- HTTPS em produção

## 📈 Monitoramento

### Frontend
- Error boundaries para capturar erros
- Performance monitoring
- User analytics

### Backend
- Health check endpoints
- Logging estruturado
- API monitoring

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

Para suporte, entre em contato através do formulário no site ou abra uma issue no repositório.

---

**🎉 O projeto está pronto para lançamento!**

Para mais detalhes sobre o deploy, consulte o arquivo `deploy-config.md`. 