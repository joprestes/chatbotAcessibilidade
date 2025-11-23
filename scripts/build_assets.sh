#!/bin/bash

# Script de build para otimizar assets estáticos
# Prepara assets para deploy e CDN

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Diretórios
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="${PROJECT_ROOT}/frontend"
STATIC_DIR="${PROJECT_ROOT}/static"
BUILD_DIR="${PROJECT_ROOT}/build"

echo -e "${GREEN}🚀 Iniciando build de assets...${NC}"

# Criar diretório de build
mkdir -p "${BUILD_DIR}"

# Verificar se diretórios existem
if [ ! -d "${FRONTEND_DIR}" ]; then
    echo -e "${RED}❌ Diretório frontend não encontrado!${NC}"
    exit 1
fi

if [ ! -d "${STATIC_DIR}" ]; then
    echo -e "${YELLOW}⚠️  Diretório static não encontrado, criando...${NC}"
    mkdir -p "${STATIC_DIR}"
fi

# 1. Copiar arquivos do frontend
echo -e "${GREEN}📁 Copiando arquivos do frontend...${NC}"
cp -r "${FRONTEND_DIR}"/* "${BUILD_DIR}/" 2>/dev/null || true

# 2. Copiar assets estáticos
if [ -d "${STATIC_DIR}" ]; then
    echo -e "${GREEN}🖼️  Copiando assets estáticos...${NC}"
    cp -r "${STATIC_DIR}"/* "${BUILD_DIR}/" 2>/dev/null || true
fi

# 3. Minificar CSS (se tiver ferramenta disponível)
if command -v csso &> /dev/null; then
    echo -e "${GREEN}🎨 Minificando CSS...${NC}"
    find "${BUILD_DIR}" -name "*.css" -type f | while read -r file; do
        csso "$file" -o "$file"
    done
elif command -v npx &> /dev/null; then
    echo -e "${GREEN}🎨 Minificando CSS com csso-cli...${NC}"
    find "${BUILD_DIR}" -name "*.css" -type f | while read -r file; do
        npx csso-cli "$file" -o "$file" 2>/dev/null || true
    done
else
    echo -e "${YELLOW}⚠️  csso não encontrado, pulando minificação de CSS${NC}"
fi

# 4. Minificar JavaScript (se tiver ferramenta disponível)
if command -v terser &> /dev/null; then
    echo -e "${GREEN}📜 Minificando JavaScript...${NC}"
    find "${BUILD_DIR}" -name "*.js" -type f | while read -r file; do
        terser "$file" -o "$file" --compress --mangle 2>/dev/null || true
    done
elif command -v npx &> /dev/null; then
    echo -e "${GREEN}📜 Minificando JavaScript com terser...${NC}"
    find "${BUILD_DIR}" -name "*.js" -type f | while read -r file; do
        npx terser "$file" -o "$file" --compress --mangle 2>/dev/null || true
    done
else
    echo -e "${YELLOW}⚠️  terser não encontrado, pulando minificação de JavaScript${NC}"
fi

# 5. Otimizar imagens (se tiver ferramenta disponível)
if command -v imagemin &> /dev/null; then
    echo -e "${GREEN}🖼️  Otimizando imagens...${NC}"
    find "${BUILD_DIR}" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.webp" \) | while read -r file; do
        imagemin "$file" --out-dir="$(dirname "$file")" 2>/dev/null || true
    done
elif command -v npx &> /dev/null; then
    echo -e "${GREEN}🖼️  Otimizando imagens com imagemin-cli...${NC}"
    find "${BUILD_DIR}" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.webp" \) | while read -r file; do
        npx imagemin-cli "$file" --out-dir="$(dirname "$file")" 2>/dev/null || true
    done
else
    echo -e "${YELLOW}⚠️  imagemin não encontrado, pulando otimização de imagens${NC}"
fi

# 6. Gerar hash para cache busting (opcional)
if command -v md5sum &> /dev/null; then
    echo -e "${GREEN}🔐 Gerando hashes para cache busting...${NC}"
    find "${BUILD_DIR}" -type f \( -name "*.css" -o -name "*.js" \) | while read -r file; do
        hash=$(md5sum "$file" | cut -d' ' -f1 | cut -c1-8)
        echo "Hash para $(basename "$file"): $hash"
    done
elif command -v md5 &> /dev/null; then
    echo -e "${GREEN}🔐 Gerando hashes para cache busting...${NC}"
    find "${BUILD_DIR}" -type f \( -name "*.css" -o -name "*.js" \) | while read -r file; do
        hash=$(md5 -q "$file" | cut -c1-8)
        echo "Hash para $(basename "$file"): $hash"
    done
fi

# 7. Criar arquivo de manifest (opcional)
echo -e "${GREEN}📋 Criando manifest de assets...${NC}"
cat > "${BUILD_DIR}/assets-manifest.json" <<EOF
{
  "version": "$(date +%Y%m%d-%H%M%S)",
  "build_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "assets": {
    "css": [
      $(find "${BUILD_DIR}" -name "*.css" -type f | sed 's|.*/||' | sed 's/^/      "/' | sed 's/$/"/' | sed '$!s/$/,/')
    ],
    "js": [
      $(find "${BUILD_DIR}" -name "*.js" -type f | sed 's|.*/||' | sed 's/^/      "/' | sed 's/$/"/' | sed '$!s/$/,/')
    ],
    "images": [
      $(find "${BUILD_DIR}" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.webp" \) | sed 's|.*/||' | sed 's/^/      "/' | sed 's/$/"/' | sed '$!s/$/,/')
    ]
  }
}
EOF

# 8. Estatísticas
echo -e "${GREEN}📊 Estatísticas do build:${NC}"
echo "  - CSS: $(find "${BUILD_DIR}" -name "*.css" -type f | wc -l | tr -d ' ') arquivo(s)"
echo "  - JavaScript: $(find "${BUILD_DIR}" -name "*.js" -type f | wc -l | tr -d ' ') arquivo(s)"
echo "  - Imagens: $(find "${BUILD_DIR}" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.webp" \) | wc -l | tr -d ' ') arquivo(s)"
echo "  - Tamanho total: $(du -sh "${BUILD_DIR}" | cut -f1)"

echo -e "${GREEN}✅ Build concluído!${NC}"
echo -e "${YELLOW}📁 Assets otimizados em: ${BUILD_DIR}${NC}"
echo ""
echo -e "${GREEN}💡 Próximos passos:${NC}"
echo "  1. Revisar assets em ${BUILD_DIR}"
echo "  2. Fazer upload para CDN (Cloudflare, AWS CloudFront, etc.)"
echo "  3. Atualizar referências no código se necessário"
echo "  4. Testar em ambiente de staging"

