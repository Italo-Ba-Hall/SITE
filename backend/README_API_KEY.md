# 🔑 Configuração da API Key do Groq

## 📋 Passos para Obter a API Key

### 1. Criar Conta no Groq
- Acesse: https://console.groq.com/
- Faça login ou crie uma conta gratuita

### 2. Obter API Key
- No console do Groq, vá para "API Keys"
- Clique em "Create API Key"
- Copie a chave gerada (formato: `gsk_...`)

### 3. Configurar no Projeto
Edite o arquivo `.env` no diretório `backend/`:

```bash
GROQ_API_KEY=gsk_sua_chave_real_aqui
```

### 4. Verificar Configuração
```bash
# No diretório backend/
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key configurada:', 'GROQ_API_KEY' in os.environ)"
```

## 🚀 Testar Configuração

Após configurar a API key:

```bash
# Iniciar servidor
python main.py

# Em outro terminal, testar
curl http://localhost:8000/health/detailed
```

## ⚠️ Importante

- **NUNCA** commite a API key no repositório
- Mantenha o arquivo `.env` no `.gitignore`
- Use variáveis de ambiente em produção
- A chave gratuita do Groq tem limites de uso

## 🔧 Troubleshooting

### Erro: "GROQ_API_KEY environment variable"
- Verifique se o arquivo `.env` existe
- Confirme se a chave está correta
- Reinicie o servidor após configurar

### Erro: "Invalid API key"
- Verifique se a chave está correta
- Confirme se a conta do Groq está ativa
- Verifique os limites de uso da conta gratuita 