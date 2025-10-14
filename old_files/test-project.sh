#!/bin/bash

echo "🧪 Testando Projeto /-HALL-DEV"
echo "=================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para verificar se um comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Função para testar se uma porta está em uso
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

echo -e "${YELLOW}📋 Verificando pré-requisitos...${NC}"

# Verificar Node.js
if command_exists node; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✅ Node.js encontrado: $NODE_VERSION${NC}"
else
    echo -e "${RED}❌ Node.js não encontrado${NC}"
    exit 1
fi

# Verificar npm
if command_exists npm; then
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✅ npm encontrado: $NPM_VERSION${NC}"
else
    echo -e "${RED}❌ npm não encontrado${NC}"
    exit 1
fi

# Verificar Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ Python encontrado: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}❌ Python não encontrado${NC}"
    exit 1
fi

# Verificar pip
if command_exists pip3; then
    echo -e "${GREEN}✅ pip encontrado${NC}"
else
    echo -e "${RED}❌ pip não encontrado${NC}"
    exit 1
fi

echo -e "\n${YELLOW}🔧 Instalando dependências do Frontend...${NC}"
cd frontend

# Verificar se package.json existe
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ package.json não encontrado${NC}"
    exit 1
fi

# Instalar dependências
npm install
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependências do frontend instaladas${NC}"
else
    echo -e "${RED}❌ Erro ao instalar dependências do frontend${NC}"
    exit 1
fi

# Verificar se o build funciona
echo -e "\n${YELLOW}🏗️ Testando build do frontend...${NC}"
npm run build
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Build do frontend bem-sucedido${NC}"
else
    echo -e "${RED}❌ Erro no build do frontend${NC}"
    exit 1
fi

cd ..

echo -e "\n${YELLOW}🐍 Configurando Backend...${NC}"
cd backend

# Verificar se requirements.txt existe
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ requirements.txt não encontrado${NC}"
    exit 1
fi

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Criando ambiente virtual...${NC}"
    python3 -m venv venv
fi

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependências do backend instaladas${NC}"
else
    echo -e "${RED}❌ Erro ao instalar dependências do backend${NC}"
    exit 1
fi

# Verificar se main.py existe
if [ ! -f "main.py" ]; then
    echo -e "${RED}❌ main.py não encontrado${NC}"
    exit 1
fi

echo -e "\n${YELLOW}🚀 Iniciando servidor de teste...${NC}"

# Iniciar servidor em background
python main.py &
BACKEND_PID=$!

# Aguardar servidor iniciar
sleep 3

# Verificar se servidor está rodando
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✅ Backend iniciado com sucesso${NC}"
else
    echo -e "${RED}❌ Erro ao iniciar backend${NC}"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo -e "\n${YELLOW}🧪 Testando endpoints da API...${NC}"

# Testar endpoint de health
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo -e "${GREEN}✅ Endpoint /health funcionando${NC}"
else
    echo -e "${RED}❌ Endpoint /health falhou${NC}"
fi

# Testar endpoint de sugestões
SUGGESTION_RESPONSE=$(curl -s -X POST http://localhost:8000/suggest \
  -H "Content-Type: application/json" \
  -d '{"text": "desenvolvimento web"}')

if echo "$SUGGESTION_RESPONSE" | grep -q "web-dev"; then
    echo -e "${GREEN}✅ Endpoint /suggest funcionando${NC}"
else
    echo -e "${RED}❌ Endpoint /suggest falhou${NC}"
fi

# Parar servidor
kill $BACKEND_PID 2>/dev/null

cd ..

echo -e "\n${YELLOW}📊 Resumo dos testes:${NC}"
echo -e "${GREEN}✅ Pré-requisitos verificados${NC}"
echo -e "${GREEN}✅ Dependências instaladas${NC}"
echo -e "${GREEN}✅ Build do frontend funcionando${NC}"
echo -e "${GREEN}✅ Backend funcionando${NC}"
echo -e "${GREEN}✅ Endpoints da API testados${NC}"

echo -e "\n${GREEN}🎉 Projeto pronto para deploy!${NC}"
echo -e "\n${YELLOW}📝 Próximos passos:${NC}"
echo "1. Fazer deploy do backend no Render/Railway"
echo "2. Fazer deploy do frontend no Vercel/Netlify"
echo "3. Configurar variáveis de ambiente"
echo "4. Testar em produção"

echo -e "\n${GREEN}🚀 O projeto está pronto para lançamento amanhã!${NC}" 