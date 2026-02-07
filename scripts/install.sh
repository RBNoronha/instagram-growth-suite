#!/bin/bash
# ============================================
# Script de Instalação - Instagram Growth Suite
# Linux/macOS
# ============================================

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  📱 Instagram Growth Suite - Instalação                  ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verifica Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 não encontrado!${NC}"
    echo "Instale o Python 3.8+ e tente novamente."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✅ Python encontrado: $PYTHON_VERSION${NC}"

# Verifica pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip não encontrado!${NC}"
    echo "Instale o pip e tente novamente."
    exit 1
fi

echo -e "${GREEN}✅ pip encontrado${NC}"

# Cria ambiente virtual
echo ""
echo "📦 Criando ambiente virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Ambiente virtual criado${NC}"
else
    echo -e "${YELLOW}⚠️  Ambiente virtual já existe${NC}"
fi

# Ativa ambiente virtual
echo ""
echo "🚀 Ativando ambiente virtual..."
source venv/bin/activate

# Atualiza pip
echo ""
echo "⬆️  Atualizando pip..."
pip install --upgrade pip -q

# Instala dependências
echo ""
echo "📥 Instalando dependências..."
pip install -r requirements.txt -q

echo -e "${GREEN}✅ Dependências instaladas${NC}"

# Cria estrutura de diretórios
echo ""
echo "📁 Criando estrutura de diretórios..."
mkdir -p data
mkdir -p content/images
mkdir -p content/videos
mkdir -p logs
mkdir -p data/chrome_profile

echo -e "${GREEN}✅ Diretórios criados${NC}"

# Cria .env se não existir
echo ""
if [ ! -f ".env" ]; then
    echo "📝 Criando arquivo .env..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Arquivo .env criado!${NC}"
    echo "   Edite o arquivo .env e adicione suas credenciais do Instagram"
else
    echo -e "${YELLOW}⚠️  Arquivo .env já existe${NC}"
fi

# Verifica Chrome
echo ""
if command -v google-chrome &> /dev/null || command -v chromium &> /dev/null || command -v chromium-browser &> /dev/null; then
    echo -e "${GREEN}✅ Chrome/Chromium encontrado${NC}"
else
    echo -e "${YELLOW}⚠️  Chrome não encontrado!${NC}"
    echo "   Instale o Google Chrome:"
    echo "   - Ubuntu/Debian: sudo apt-get install google-chrome-stable"
    echo "   - macOS: brew install --cask google-chrome"
fi

# Permissões
echo ""
echo "🔧 Configurando permissões..."
chmod +x main.py
chmod +x scripts/*.sh 2>/dev/null || true

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ✅ Instalação Concluída!                                ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║                                                          ║"
echo "║  Próximos passos:                                        ║"
echo "║  1. Edite o arquivo .env com suas credenciais           ║"
echo "║  2. Coloque imagens em content/images/                  ║"
echo "║  3. Execute: python main.py                             ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Desativa ambiente virtual
deactivate
