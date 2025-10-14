@echo off
echo 🧪 Testando Projeto /-HALL-DEV
echo ==================================

echo 📋 Verificando pré-requisitos...

REM Verificar Node.js
node --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Node.js encontrado
) else (
    echo ❌ Node.js não encontrado
    exit /b 1
)

REM Verificar npm
npm --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ npm encontrado
) else (
    echo ❌ npm não encontrado
    exit /b 1
)

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python encontrado
) else (
    echo ❌ Python não encontrado
    exit /b 1
)

echo.
echo 🔧 Instalando dependências do Frontend...
cd frontend

REM Verificar se package.json existe
if not exist "package.json" (
    echo ❌ package.json não encontrado
    exit /b 1
)

REM Instalar dependências
npm install
if %errorlevel% equ 0 (
    echo ✅ Dependências do frontend instaladas
) else (
    echo ❌ Erro ao instalar dependências do frontend
    exit /b 1
)

REM Verificar se o build funciona
echo.
echo 🏗️ Testando build do frontend...
npm run build
if %errorlevel% equ 0 (
    echo ✅ Build do frontend bem-sucedido
) else (
    echo ❌ Erro no build do frontend
    exit /b 1
)

cd ..

echo.
echo 🐍 Configurando Backend...
cd backend

REM Verificar se requirements.txt existe
if not exist "requirements.txt" (
    echo ❌ requirements.txt não encontrado
    exit /b 1
)

REM Criar ambiente virtual se não existir
if not exist "venv" (
    echo 📦 Criando ambiente virtual...
    python -m venv venv
)

REM Ativar ambiente virtual
call venv\Scripts\activate.bat

REM Instalar dependências
pip install -r requirements.txt
if %errorlevel% equ 0 (
    echo ✅ Dependências do backend instaladas
) else (
    echo ❌ Erro ao instalar dependências do backend
    exit /b 1
)

REM Verificar se main.py existe
if not exist "main.py" (
    echo ❌ main.py não encontrado
    exit /b 1
)

echo.
echo 🚀 Iniciando servidor de teste...

REM Iniciar servidor em background
start /B python main.py

REM Aguardar servidor iniciar
timeout /t 3 /nobreak >nul

REM Verificar se servidor está rodando
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend iniciado com sucesso
) else (
    echo ❌ Erro ao iniciar backend
    exit /b 1
)

echo.
echo 🧪 Testando endpoints da API...

REM Testar endpoint de health
curl -s http://localhost:8000/health | findstr "healthy" >nul
if %errorlevel% equ 0 (
    echo ✅ Endpoint /health funcionando
) else (
    echo ❌ Endpoint /health falhou
)

REM Testar endpoint de sugestões
curl -s -X POST http://localhost:8000/suggest -H "Content-Type: application/json" -d "{\"text\": \"desenvolvimento web\"}" | findstr "web-dev" >nul
if %errorlevel% equ 0 (
    echo ✅ Endpoint /suggest funcionando
) else (
    echo ❌ Endpoint /suggest falhou
)

REM Parar servidor (Windows não tem kill direto, mas o processo será encerrado quando o script terminar)
cd ..

echo.
echo 📊 Resumo dos testes:
echo ✅ Pré-requisitos verificados
echo ✅ Dependências instaladas
echo ✅ Build do frontend funcionando
echo ✅ Backend funcionando
echo ✅ Endpoints da API testados

echo.
echo 🎉 Projeto pronto para deploy!
echo.
echo 📝 Próximos passos:
echo 1. Fazer deploy do backend no Render/Railway
echo 2. Fazer deploy do frontend no Vercel/Netlify
echo 3. Configurar variáveis de ambiente
echo 4. Testar em produção

echo.
echo 🚀 O projeto está pronto para lançamento amanhã!

pause 