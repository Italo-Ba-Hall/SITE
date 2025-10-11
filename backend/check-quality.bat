@echo off
REM Script para executar verificações de qualidade de código com Ruff no Windows

echo 🔍 Executando verificações de qualidade de código...

REM Ativar ambiente virtual
call venv\Scripts\activate.bat

REM Executar Ruff check
echo 📋 Verificando código com Ruff...
ruff check . --statistics

REM Executar Ruff format (verificar formatação)
echo 🎨 Verificando formatação...
ruff format --check .

REM Executar testes se existirem
if exist test_*.py (
    echo 🧪 Executando testes...
    python -m pytest test_*.py -v
)

echo ✅ Verificações concluídas!
pause
