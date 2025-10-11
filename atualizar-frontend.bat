@echo off
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                    /-HALL-DEV - ATUALIZAR FRONTEND                           ║
echo ║                        Após deploy do backend                                ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo 📋 INSTRUÇÕES:
echo.
echo 1. Cole a URL do seu backend (Railway ou PythonAnywhere)
echo 2. O script irá atualizar o .env.production automaticamente
echo 3. Fazer novo build do frontend
echo 4. Preparar arquivos para upload no FTP
echo.
set /p BACKEND_URL="🔗 Cole a URL do backend aqui: "

echo.
echo ✅ Atualizando .env.production...
echo REACT_APP_API_URL=%BACKEND_URL% > frontend\.env.production
echo REACT_APP_ENV=production >> frontend\.env.production
echo GENERATE_SOURCEMAP=false >> frontend\.env.production

echo.
echo 🔨 Fazendo build do frontend...
cd frontend
call npm run build

echo.
echo ✅ Build concluído! Arquivos prontos em frontend/build/
echo.
echo 📤 PRÓXIMO PASSO: Upload dos arquivos para FTP
echo    • Origem: frontend/build/
echo    • Destino: webftp.spcompsolucoes.com.br/www/
echo.
pause
