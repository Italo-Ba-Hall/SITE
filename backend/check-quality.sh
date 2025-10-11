#!/bin/bash
# Script para executar verificações de qualidade de código com Ruff

echo "🔍 Executando verificações de qualidade de código..."

# Ativar ambiente virtual
source venv/Scripts/activate

# Executar Ruff check
echo "📋 Verificando código com Ruff..."
ruff check . --statistics

# Executar Ruff format (verificar formatação)
echo "🎨 Verificando formatação..."
ruff format --check .

# Executar testes se existirem
if [ -f "test_*.py" ] || [ -f "*_test.py" ]; then
    echo "🧪 Executando testes..."
    python -m pytest test_*.py *_test.py -v
fi

echo "✅ Verificações concluídas!"
