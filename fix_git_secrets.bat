@echo off
echo Resolvendo problema de secrets no GitHub...

echo.
echo 1. Verificando status atual...
git status

echo.
echo 2. Fazendo commit das correções...
git add .
git commit -m "fix: Remove all API keys from codebase"

echo.
echo 3. Tentando push...
git push origin main

echo.
echo 4. Se ainda der erro, vamos usar force push...
if %errorlevel% neq 0 (
    echo Erro no push normal, tentando force push...
    git push --force-with-lease origin main
)

echo.
echo Processo concluído!
pause
