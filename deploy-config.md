# 🚀 Guia de Deploy - /-HALL-DEV

## 📋 Pré-requisitos

### Frontend (React)
- Node.js >= 16.0.0
- npm >= 8.0.0
- Conta no Vercel/Netlify

### Backend (FastAPI)
- Python >= 3.9
- Conta no Render/Railway/Heroku

## 🔧 Configuração de Ambiente

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

## 🚀 Deploy do Frontend

### Vercel (Recomendado)
1. Conectar repositório no Vercel
2. Configurar build settings:
   ```bash
   Build Command: npm run build
   Output Directory: build
   Install Command: npm install
   ```
3. Adicionar variáveis de ambiente
4. Deploy automático

### Netlify
1. Conectar repositório no Netlify
2. Configurar build settings:
   ```bash
   Build command: npm run build
   Publish directory: build
   ```
3. Adicionar variáveis de ambiente
4. Deploy automático

## 🐍 Deploy do Backend

### Render (Recomendado)
1. Conectar repositório no Render
2. Configurar:
   ```bash
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
3. Adicionar variáveis de ambiente
4. Deploy automático

### Railway
1. Conectar repositório no Railway
2. Configurar:
   ```bash
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
3. Adicionar variáveis de ambiente
4. Deploy automático

## 📊 Monitoramento

### Frontend
- Vercel Analytics
- Google Analytics
- Error tracking (Sentry)

### Backend
- Render/Railway logs
- Application monitoring
- Error tracking (Sentry)

## 🔒 Segurança

### CORS
```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://seu-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### HTTPS
- Configurar automaticamente nos provedores
- Certificados SSL automáticos

## 📈 Performance

### Frontend
- Code splitting automático
- Lazy loading de componentes
- Bundle optimization
- CDN global

### Backend
- Caching estratégico
- Database connection pooling
- Rate limiting
- Load balancing

## 🧪 Testes

### Frontend
```bash
npm run test
npm run build
npm run type-check
```

### Backend
```bash
pytest
mypy .
flake8 .
```

## 📝 Checklist de Deploy

### Frontend
- [ ] Build sem erros
- [ ] Variáveis de ambiente configuradas
- [ ] CORS configurado
- [ ] Testes passando
- [ ] Performance otimizada
- [ ] SEO configurado

### Backend
- [ ] Dependências instaladas
- [ ] Variáveis de ambiente configuradas
- [ ] CORS configurado
- [ ] Health check funcionando
- [ ] Logs configurados
- [ ] Monitoramento ativo

### Geral
- [ ] Domínio configurado
- [ ] SSL ativo
- [ ] Backup configurado
- [ ] Monitoramento ativo
- [ ] Documentação atualizada

## 🔄 CI/CD

### GitHub Actions
```yaml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm install
      - run: npm test
      - run: npm run build
```

## 📞 Suporte

### Logs
- Vercel: Dashboard > Functions > Logs
- Render: Dashboard > Services > Logs
- Railway: Dashboard > Deployments > Logs

### Debug
- Frontend: Browser DevTools
- Backend: Application logs
- Database: Connection logs

## 🎯 Otimizações Finais

### Frontend
- [ ] Bundle analyzer
- [ ] Image optimization
- [ ] Font optimization
- [ ] Critical CSS

### Backend
- [ ] Database indexing
- [ ] Query optimization
- [ ] Caching layers
- [ ] Rate limiting

## 🚨 Troubleshooting

### Erros Comuns
1. **CORS errors**: Verificar origins no backend
2. **Build failures**: Verificar dependências
3. **Runtime errors**: Verificar variáveis de ambiente
4. **Performance issues**: Otimizar bundle size

### Soluções
1. Verificar logs de deploy
2. Testar localmente
3. Verificar configurações
4. Contatar suporte se necessário 