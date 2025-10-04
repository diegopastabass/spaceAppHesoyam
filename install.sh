#!/bin/bash

# Script de instalación para el proyecto SpaceBio Publications Scraper

echo "🚀 Instalando SpaceBio Publications Scraper..."

# Verificar Python 3.8+
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "❌ Error: Se requiere Python 3.8 o superior"
    exit 1
fi

echo "✅ Python 3.8+ encontrado"

# Instalar dependencias
echo "📦 Instalando dependencias Python..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Error instalando dependencias Python"
    exit 1
fi

echo "✅ Dependencias Python instaladas"

# Crear directorios necesarios
echo "📁 Creando directorios del proyecto..."
mkdir -p downloads markdown_output logs config

echo "✅ Directorios creados"

# Configurar permisos
echo "🔐 Configurando permisos..."
chmod +x main.py

echo "✅ Permisos configurados"

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo "📝 Creando archivo de configuración..."
    cat > .env << EOF
# Configuración del proyecto de scraping
DOWNLOAD_DIR=./downloads
CSV_FILE_URL=https://raw.githubusercontent.com/jgalazka/SB_publications/main/SB_publication_PMC.csv
MAX_DOWNLOADS_PER_HOUR=50
DELAY_BETWEEN_REQUESTS=2
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
MAX_ARTICLES_TO_DOWNLOAD=10
LOG_LEVEL=INFO
MARKDOWN_OUTPUT_DIR=./markdown_output
EOF
    echo "✅ Archivo .env creado"
fi

echo ""
echo "🎉 ¡Instalación completada exitosamente!"
echo ""
echo "📋 Para usar la aplicación:"
echo "   python3 main.py           # Ejecutar con configuración por defecto"
echo "   python3 main.py test      # Ejecutar con 3 artículos para testing"
echo ""
echo "📁 Los PDFs se descargarán en: ./downloads"
echo "📄 Los Markdown se generarán en: ./markdown_output"
echo ""
echo "🔧 Para personalizar la configuración, edita el archivo .env"
