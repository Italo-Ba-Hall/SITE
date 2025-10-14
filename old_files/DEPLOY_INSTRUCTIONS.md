# 🚀 INSTRUÇÕES DE DEPLOY - /-HALL-DEV

## ✅ O QUE JÁ FOI FEITO (pelo sistema)

- ✅ Build do frontend compilado em `frontend/build/`
- ✅ CORS configurado para aceitar domínio de produção
- ✅ Variáveis de ambiente preparadas
- ✅ Código otimizado e pronto

---

## 📦 PARTE 1: UPLOAD DO FRONTEND PARA O FTP

### Arquivos para enviar ao FTP:

**Pasta `/www` do FTP deve conter:**

```
/www/
├── index.html
├── favicon.ico
├── logo192.png
├── logo512.png
├── manifest.json
├── robots.txt
├── asset-manifest.json
└── static/
    ├── css/
    │   └── main.710c78c8.css
    └── js/
        ├── main.dce658c9.js
        ├── 891.c7022d92.chunk.js
        ├── 509.3d558f74.chunk.js
        └── 206.ed2f3d44.chunk.js
```

### Passos:

1. **Acesse o FTP** (webftp.spcompsolucoes.com.br)
2. **Navegue até `/www`**
3. **Envie TUDO de `frontend/build/`** para `/www`
   - IMPORTANTE: Mantenha a estrutura de pastas (principalmente `static/`)

---

## 🐍 PARTE 2: DEPLOY DO BACKEND (ESCOLHA UMA OPÇÃO)

**ANTES DE FAZER DEPLOY DO BACKEND:**

1. Edite `frontend/.env.production` e adicione a URL do backend
2. Refaça o build: `cd frontend && npm run build`
3. Re-envie os arquivos para o FTP

---

### OPÇÃO A: Railway (Recomendado - Gratuito até 5$/mês)

**1. Criar conta:**
- Acesse: https://railway.app
- Login com GitHub

**2. Deploy:**
```bash
# No terminal, na pasta do projeto:
cd backend

# Instalar Railway CLI (se ainda não tem)
npm install -g @railway/cli

# Login
railway login

# Criar projeto
railway init

# Deploy
railway up
```

**3. Configurar variáveis:**
- No painel Railway, vá em "Variables"
- Adicione:
  ```
  GROQ_API_KEY=sua_chave_aqui
  FRONTEND_URL=http://barrahall.dev.br
  ```

**4. Obter URL:**
- Railway vai gerar uma URL tipo: `https://seu-app.up.railway.app`
- **COPIE ESSA URL** - você vai precisar dela

---

### OPÇÃO B: PythonAnywhere (100% Gratuito com limitações)

**1. Criar conta:**
- Acesse: https://www.pythonanywhere.com
- Crie conta gratuita

**2. Upload dos arquivos:**
- No dashboard, clique em "Files"
- Crie pasta `/home/seu_usuario/hall_dev`
- Upload TODOS os arquivos de `backend/`:
  - main.py
  - chat_manager.py
  - database.py
  - llm_service.py
  - notification_service.py
  - schemas.py
  - requirements.txt
  - .env (criar com suas configurações)

**3. Instalar dependências:**
- Vá em "Consoles" → "Bash"
```bash
cd ~/hall_dev
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**4. Configurar Web App:**
- Vá em "Web"
- "Add a new web app"
- Escolha "Manual configuration" → Python 3.10
- Em "Code":
  - Source code: `/home/seu_usuario/hall_dev`
  - Working directory: `/home/seu_usuario/hall_dev`
- Em "WSGI configuration file", edite:
```python
import sys
path = '/home/seu_usuario/hall_dev'
if path not in sys.path:
    sys.path.append(path)

from main import app as application
```

**5. Variáveis de ambiente:**
- Crie arquivo `.env` na pasta do projeto
- Adicione:
```
GROQ_API_KEY=sua_chave_aqui
FRONTEND_URL=http://barrahall.dev.br
```

**6. Reload:**
- Clique em "Reload" no painel Web
- URL será: `https://seu-usuario.pythonanywhere.com`

---

## 🔧 PARTE 3: CONECTAR FRONTEND E BACKEND

**1. Atualizar URL do Backend no Frontend:**

Edite `frontend/.env.production`:
```env
REACT_APP_API_URL=https://sua-url-do-backend-aqui
```

Substitua `https://sua-url-do-backend-aqui` por:
- Railway: `https://seu-app.up.railway.app`
- PythonAnywhere: `https://seu-usuario.pythonanywhere.com`

**2. Refazer Build:**
```bash
cd frontend
npm run build
```

**3. Re-enviar para FTP:**
- Envie novamente os arquivos de `frontend/build/` para `/www`

---

## ✅ VERIFICAÇÃO FINAL

**1. Testar Backend:**
- Acesse: `https://sua-url-backend/health`
- Deve retornar: `{"status": "healthy", ...}`

**2. Testar Frontend:**
- Acesse: `http://barrahall.dev.br`
- Digite uma mensagem
- Chat deve abrir e responder

**3. Testar Integração:**
- Envie mensagem no chat
- Verifique se recebe resposta da IA

---

## 🚨 TROUBLESHOOTING

**Frontend não carrega:**
- Verifique estrutura de pastas no FTP
- Confirme que `index.html` está em `/www`

**Chat não abre:**
- Verifique URL em `.env.production`
- Confirme CORS no backend

**Backend não responde:**
- Verifique logs no Railway/PythonAnywhere
- Confirme que GROQ_API_KEY está configurada

**Erro de CORS:**
- Verifique `FRONTEND_URL` no backend
- Confirme que URL do FTP está correta

---

**Status:** Projeto pronto para deploy
**Bundle Size:** 67.74 KB (excelente!)
**Próximo passo:** Escolher opção de backend (Railway ou PythonAnywhere)

