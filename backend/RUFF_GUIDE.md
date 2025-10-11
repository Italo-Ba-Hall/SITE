# Guia de Qualidade de Código com Ruff

## 📋 Visão Geral

O Ruff foi instalado e configurado no projeto HALL-DEV para garantir a qualidade do código Python. Ele substitui múltiplas ferramentas (flake8, black, isort, etc.) em uma única ferramenta rápida.

## 🚀 Comandos Principais

### Verificação de Qualidade
```bash
# Verificar issues no código
ruff check .

# Verificar com estatísticas
ruff check . --statistics

# Verificar formatação
ruff format --check .
```

### Correção Automática
```bash
# Corrigir issues automaticamente
ruff check --fix .

# Formatar código
ruff format .
```

### Scripts Disponíveis

#### Windows
- `check-quality.bat` - Verifica qualidade do código
- `fix-quality.bat` - Corrige issues automaticamente

#### Linux/Mac
- `check-quality.sh` - Verifica qualidade do código
- `fix-quality.sh` - Corrige issues automaticamente

## ⚙️ Configuração

O Ruff está configurado no arquivo `pyproject.toml` com as seguintes regras:

### Regras Habilitadas
- **E, W**: pycodestyle (erros e warnings)
- **F**: pyflakes (detecção de erros)
- **I**: isort (organização de imports)
- **B**: flake8-bugbear (bugs comuns)
- **C4**: flake8-comprehensions (compreensões de lista)
- **UP**: pyupgrade (atualizações de sintaxe)
- **N**: pep8-naming (convenções de nomenclatura)
- **S**: bandit (segurança)
- **T20**: flake8-print (detecção de prints)
- **SIM**: flake8-simplify (simplificações)
- **RUF**: regras específicas do Ruff

### Regras Ignoradas
- **E501**: Linha muito longa (gerenciada pelo formatador)
- **S101**: Uso de assert (ok em testes)
- **T201**: Statements de print (ok para debug)
- **B008**: Chamadas de função em argumentos padrão

## 🔧 Integração com IDEs

### VS Code/Cursor
Para integrar o Ruff no seu editor, instale a extensão "Ruff" e configure:

```json
{
    "python.defaultInterpreterPath": "./venv/Scripts/python.exe",
    "python.linting.ruffEnabled": true,
    "python.formatting.ruffEnabled": true,
    "[python]": {
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.fixAll.ruff": true
        }
    }
}
```

## 📊 Status Atual

Após a instalação inicial:
- ✅ **751 issues corrigidos automaticamente**
- ⚠️ **78 issues restantes** (requerem correção manual)

### Issues Restantes por Categoria
- **22x F405**: Uso de imports com `*` (undefined names)
- **19x B904**: Raise sem `from` em except clauses
- **12x W293**: Linhas em branco com espaços
- **7x F841**: Variáveis não utilizadas
- **5x S110**: try-except-pass (considerar logging)
- **5x W291**: Espaços em branco no final
- **2x B007**: Variáveis de loop não utilizadas
- **1x E402**: Import não no topo do arquivo
- **1x E722**: Bare except
- **1x F403**: Import com `*`
- **1x RUF013**: Optional implícito
- **1x S104**: Binding para todas as interfaces
- **1x S324**: Função de hash insegura (MD5)

## 🎯 Próximos Passos

1. **Corrigir imports com `*`**: Substituir `from schemas import *` por imports específicos
2. **Melhorar tratamento de exceções**: Adicionar `from` em raises
3. **Limpar código**: Remover variáveis não utilizadas
4. **Adicionar logging**: Substituir `pass` por logging adequado
5. **Segurança**: Substituir MD5 por SHA-256

## 🔄 Workflow Recomendado

1. **Antes de commitar**: Execute `check-quality.bat` (Windows) ou `check-quality.sh` (Linux/Mac)
2. **Correção rápida**: Execute `fix-quality.bat` (Windows) ou `fix-quality.sh` (Linux/Mac)
3. **Integração contínua**: Configure o Ruff no seu pipeline de CI/CD

## 📈 Benefícios

- **Performance**: Ruff é 10-100x mais rápido que outras ferramentas
- **Consistência**: Uma única ferramenta para todas as verificações
- **Manutenibilidade**: Código mais limpo e padronizado
- **Produtividade**: Correções automáticas e formatação consistente
- **Qualidade**: Detecção precoce de bugs e problemas de segurança
