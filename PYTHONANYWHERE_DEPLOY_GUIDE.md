# 🐍 DEPLOY NO PYTHONANYWHERE - GUIA COMPLETO

## ✅ ARQUIVOS PREPARADOS AUTOMATICAMENTE:
- ✅ .env configurado com sua API key do Gemini
- ✅ wsgi.py criado para PythonAnywhere
- ✅ requirements.txt otimizado
- ✅ main.py pronto para produção

## 📋 PASSOS PARA DEPLOY:

### 1. CRIAR CONTA NO PYTHONANYWHERE
1. Acesse: https://www.pythonanywhere.com/
2. Clique em "Sign up for a free account"
3. Escolha username e senha
4. Confirme email

### 2. UPLOAD DOS ARQUIVOS
1. Acesse: https://www.pythonanywhere.com/user/seu_usuario/files/
2. Crie pasta: `/home/seu_usuario/mysite/`
3. Faça upload destes arquivos para `/home/seu_usuario/mysite/`:

**ARQUIVOS OBRIGATÓRIOS:**
- main.py
- requirements.txt
- .env
- wsgi.py
- schemas.py
- database.py
- llm_service.py
- chat_manager.py
- notification_service.py

### 3. INSTALAR DEPENDÊNCIAS
1. Abra Bash Console: https://www.pythonanywhere.com/user/seu_usuario/consoles/
2. Execute:
```bash
cd /home/seu_usuario/mysite
pip3.10 install --user -r requirements.txt
```

### 4. CONFIGURAR WEB APP
1. Acesse: https://www.pythonanywhere.com/user/seu_usuario/webapps/
2. Clique em "Add a new web app"
3. Escolha "Manual configuration"
4. Escolha Python 3.10
5. Em "Code", coloque: `/home/seu_usuario/mysite/wsgi.py`
6. Salve

### 5. CONFIGURAR DOMÍNIO
1. Na aba "Static files", adicione:
   - URL: `/static/`
   - Directory: `/home/seu_usuario/mysite/static/`
2. Na aba "Web", configure:
   - Source code: `/home/seu_usuario/mysite/`
   - Working directory: `/home/seu_usuario/mysite/`

### 6. TESTAR
1. Acesse: https://seu_usuario.pythonanywhere.com/health
2. Deve retornar: {"status": "healthy", "timestamp": "..."}

## 🔗 URL FINAL:
https://seu_usuario.pythonanywhere.com

## ⚠️ IMPORTANTE:
- Substitua "seu_usuario" pelo seu username real
- A URL será: https://seu_usuario.pythonanywhere.com
- Use esta URL no frontend (.env.production)

## 📞 SUPORTE:
Se tiver problemas, consulte: https://help.pythonanywhere.com/
