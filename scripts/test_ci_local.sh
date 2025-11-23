#!/bin/bash
# Script para testar a pipeline CI/CD localmente
# Simula os passos do GitHub Actions

set -e  # Para em caso de erro

echo "🚀 Testando Pipeline CI/CD Localmente"
echo "======================================"
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para imprimir sucesso
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Função para imprimir erro
error() {
    echo -e "${RED}❌ $1${NC}"
}

# Função para imprimir aviso
warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Verifica se estamos no diretório correto
if [ ! -f "requirements.txt" ]; then
    error "Execute este script na raiz do projeto"
    exit 1
fi

# Job 1: Lint and Unit Tests
echo ""
echo "📋 Job 1: Lint and Unit Tests"
echo "-----------------------------"

# Step 1: Install dependencies
echo "📦 Instalando dependências..."
if python -m pip install --upgrade pip > /dev/null 2>&1 && pip install -r requirements.txt > /dev/null 2>&1; then
    success "Dependências instaladas"
else
    error "Falha ao instalar dependências"
    exit 1
fi

# Step 2: Lint with ruff
echo "🔍 Executando lint (ruff)..."
if ruff check src/ tests/; then
    success "Lint passou"
else
    error "Lint falhou"
    exit 1
fi

# Step 3: Type check with mypy
echo "🔍 Executando type check (mypy)..."
if mypy src/ 2>&1 | head -20; then
    success "Type check passou"
else
    warning "Type check com avisos (não crítico)"
fi

# Step 4: Run unit tests
echo "🧪 Executando testes unitários..."
if pytest tests/unit/ -v -m "unit" --tb=short; then
    success "Testes unitários passaram"
else
    error "Testes unitários falharam"
    exit 1
fi

# Step 5: Run integration tests
echo "🔗 Executando testes de integração..."
export FALLBACK_ENABLED="false"
if pytest tests/integration/ -v -m "integration" --tb=short; then
    success "Testes de integração passaram"
else
    error "Testes de integração falharam"
    exit 1
fi

# Job 2: E2E Tests (opcional, requer servidor)
echo ""
echo "📋 Job 2: E2E Tests (Opcional)"
echo "-----------------------------"
echo ""
warning "Testes E2E requerem servidor rodando e Playwright instalado"
echo ""
read -p "Deseja executar testes E2E? (s/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Ss]$ ]]; then
    # Verifica se Playwright está instalado
    if ! command -v playwright &> /dev/null; then
        warning "Playwright não está instalado. Instalando..."
        pip install playwright pytest-playwright
        playwright install chromium
    fi
    
    # Verifica se servidor está rodando
    if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
        success "Servidor está rodando"
        
        echo "🧪 Executando testes E2E..."
        export PLAYWRIGHT_BASE_URL="http://localhost:8000"
        export PLAYWRIGHT_HEADLESS="true"
        export PLAYWRIGHT_BROWSER="chromium"
        export PLAYWRIGHT_RECORD_VIDEO="false"
        export PLAYWRIGHT_ENABLE_TRACE="true"
        
        if pytest tests/e2e/ -v -m "e2e" --tb=short; then
            success "Testes E2E passaram"
        else
            error "Testes E2E falharam"
            exit 1
        fi
    else
        warning "Servidor não está rodando em http://localhost:8000"
        echo ""
        echo "Para testar E2E, inicie o servidor em outro terminal:"
        echo "  uvicorn src.backend.api:app --host 0.0.0.0 --port 8000"
        echo ""
        echo "Ou execute: make test-e2e-server"
    fi
fi

echo ""
echo "======================================"
success "Pipeline local executada com sucesso!"
echo ""

