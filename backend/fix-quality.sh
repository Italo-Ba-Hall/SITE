#!/bin/bash
# Script para corrigir automaticamente issues de qualidade de código

echo "🔧 Corrigindo automaticamente issues de qualidade..."

# Ativar ambiente virtual
source venv/Scripts/activate

# Executar Ruff fix
echo "🛠️ Aplicando correções automáticas do Ruff..."
ruff check --fix .

# Executar Ruff format
echo "🎨 Formatando código..."
ruff format .

echo "✅ Correções aplicadas!"
echo "📋 Executando verificação final..."
ruff check . --statistics
