@echo off
REM Script para corrigir automaticamente issues de qualidade de código no Windows

echo 🔧 Corrigindo automaticamente issues de qualidade...

REM Ativar ambiente virtual
call venv\Scripts\activate.bat

REM Executar Ruff fix
echo 🛠️ Aplicando correções automáticas do Ruff...
ruff check --fix .

REM Executar Ruff format
echo 🎨 Formatando código...
ruff format .

echo ✅ Correções aplicadas!
echo 📋 Executando verificação final...
ruff check . --statistics

pause
