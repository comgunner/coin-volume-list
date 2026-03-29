#!/bin/bash
# ===========================================
# Script: Crear ZIP de distribución
# ===========================================
# Uso: ./scripts/create-release-zip.sh [version]
# Ejemplo: ./scripts/create-release-zip.sh v1.0.0
# ===========================================

set -e  # Exit on error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ===========================================
# Configuración
# ===========================================
VERSION=${1:-"manual-$(date +%Y%m%d-%H%M)"}
ZIP_NAME="coin-volume-list-${VERSION}.zip"
DIST_DIR="dist"

# Archivos a incluir
FILES=(
    "volume_sorted_coin_list.py"
    "exchanges.py"
    "requirements.txt"
    "LICENSE"
    "README.md"
    "README.es.md"
)

# ===========================================
# Funciones
# ===========================================

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ===========================================
# Script principal
# ===========================================

echo "============================================"
echo "📦 Creando ZIP de distribución"
echo "============================================"
echo "Versión: ${VERSION}"
echo "ZIP: ${ZIP_NAME}"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "volume_sorted_coin_list.py" ]; then
    log_error "No se encontró volume_sorted_coin_list.py"
    log_error "Ejecuta este script desde el directorio raíz del proyecto"
    exit 1
fi

# Crear directorio de distribución
log_info "Creando directorio ${DIST_DIR}/..."
rm -rf "${DIST_DIR}"
mkdir -p "${DIST_DIR}"

# Copiar archivos principales
log_info "Copiando archivos principales..."
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "${DIST_DIR}/"
        log_info "  ✓ Copiado: $file"
    else
        log_warn "  ✗ No encontrado: $file"
    fi
done

# Copiar .env.example (opcional)
if [ -f ".env.example" ]; then
    cp ".env.example" "${DIST_DIR}/"
    log_info "  ✓ Copiado: .env.example"
fi

# Copiar directorio docs (opcional)
if [ -d "docs" ]; then
    cp -r "docs" "${DIST_DIR}/"
    log_info "  ✓ Copiado: docs/"
fi

# Copiar directorio output con .gitkeep (opcional)
if [ -d "output" ]; then
    cp -r "output" "${DIST_DIR}/"
    log_info "  ✓ Copiado: output/"
fi

# Crear ZIP
log_info "Creando archivo ZIP..."
cd "${DIST_DIR}"
zip -r "../${ZIP_NAME}" ./*
cd ..

# Mostrar información del ZIP
ZIP_SIZE=$(du -h "${ZIP_NAME}" | cut -f1)
log_info "✓ ZIP creado exitosamente"
echo ""
echo "============================================"
echo "📊 Resumen"
echo "============================================"
echo "Archivo: ${ZIP_NAME}"
echo "Tamaño:  ${ZIP_SIZE}"
echo ""
echo "Contenido:"
unzip -l "${ZIP_NAME}"
echo "============================================"
echo ""
log_info "ZIP listo para distribuir"

# Opcional: Limpiar directorio dist
read -p "¿Eliminar directorio ${DIST_DIR}/? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "${DIST_DIR}"
    log_info "Directorio ${DIST_DIR}/ eliminado"
fi
