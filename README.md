# 🚀 SpaceBio Publications Scraper

Este proyecto descarga automáticamente artículos científicos relacionados con biología espacial desde GitHub y PubMed Central, convirtiendo los PDFs a formato Markdown para análisis posterior con IA.

## 📋 Funcionalidades

- ✅ **Scraping de GitHub**: Extrae datos del CSV con títulos y enlaces de artículos
- ✅ **Descarga de PDFs**: Descarga automática desde PubMed Central con múltiples métodos
- ✅ **Conversión a Markdown**: Transforma PDFs científicos a formato estructurado
- ✅ **Análisis de contenido**: Ejemplo de análisis de textos científicos
- ✅ **Gestión de errores**: Sistema robusto con reintentos y manejo de límites
- ✅ **Rate limiting**: Respeta límites de descarga por hora
- ✅ **Logging completo**: Seguimiento detallado de todas las operaciones

## 🛠️ Tecnologías Utilizadas

### Scraping Web
- **Requests + BeautifulSoup**: Para páginas estáticas
- **Selenium**: Para contenido dinámico y navegación automatizada
- **Pandas**: Manipulación de datos CSV

### Conversión de Documentos
- **PyPDF2**: Extracción de texto de PDFs
- **Regex**: Procesamiento y limpieza de texto científico
- **Markdown**: Formato estructurado para análisis

### Infraestructura
- **Python 3.8+**: Lenguaje principal
- **WebDriver Manager**: Gestión automática de drivers
- **Logging**: Sistema completo de registro

## 🚫 Limitaciones del Web Scraping

### Técnicas
1. **Política de robots.txt**: Sitios que prohíben scraping automático
2. **Rate limiting**: Límites estrictos de peticiones por tiempo
3. **Captchas**: Sistemas anti-bot complejos
4. **Contenido dinámico**: JavaScript que requiere ejecución del navegador
5. **Cambios frecuentes**: Sitios que modifican estructura regularmente
6. **Antimalware**: Sistemas que detectan y bloquean bots

### Legales y Éticas
1. **Copyright**: Respeto a derechos de propiedad intelectual
2. **Términos de servicio**: Violación de condiciones de uso
3. **Privacidad**: Protección de datos personales
4. **Volumen**: Uso excesivo de recursos del servidor

## 📊 Flujo del Sistema

```
GitHub CSV → CSV Scraper → Artículos List
     ↓
PubMed URLs → PDF Scraper → PDF Downloads
     ↓
PDF Files → Markdown Converter → Structured Text
     ↓
Markdown Files → AI Analysis → Scientific Insights
```

## 🚀 Instalación Rápida

```bash
# Descargar e instalar
git clone <repo-url>
cd spaceAppHesoyam

# Ejecutar instalación automática
./install.sh
```

## 📖 Instalación Manual

```bash
# Instalar dependencias
pip install -r requirements.txt

# Crear directorios
mkdir -p downloads markdown_output logs

# Configurar (editar .env si es necesario)
cp .env.example .env
```

## ▶️ Uso

### Ejecución Básica
```bash
# Descargar y convertir artículos (configurable en .env)
python main.py

# Ejecutar prueba con 3 artículos
python main.py test
```

### Análisis de Resultados
```bash
# Analizar archivos Markdown generados
python analysis_example.py
```

## 📁 Estructura del Proyecto

```
spaceAppHesoyam/
├── scrapers/              # Módulos de scraping
│   ├── github_scraper.py  # CSV de GitHub
│   └── pubmed_scraper.py  # PDFs de PubMed Central
├── converters/             # Conversores de formato
│   └── pdf_to_markdown.py # PDF → Markdown
├── config/                # Configuración
│   └── settings.py        # Configuración centralizada
├── downloads/             # PDFs descargados (creado automáticamente)
├── markdown_output/       # Archivos Markdown (creado automáticamente)
├── logs/                  # Archivos de log (creado automático)
├── main.py               # Aplicación principal
├── analysis_example.py   # Ejemplo de análisis con IA
├── requirements.txt      # Dependencias Python
├── install.sh           # Script de instalación
└── README.md            # Esta documentación
```

## ⚙️ Configuración Avanzada

### Variables de Entorno (.env)
```env
# URLs y archivos
CSV_FILE_URL=https://raw.githubusercontent.com/jgalazka/SB_publications/main/SB_publication_PMC.csv

# Directorios
DOWNLOAD_DIR=./downloads
MARKDOWN_OUTPUT_DIR=./markdown_output

# Configuración de scraping
MAX_DOWNLOADS_PER_HOUR=50
DELAY_BETWEEN_REQUESTS=2.0
MAX_ARTICLES_TO_DOWNLOAD=10

# User Agent
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64)...

# Logging
LOG_LEVEL=INFO
```

## 📊 Métodos de Scraping Implementados

### 1. GitHub CSV Scraper
- **Request HTTP** → Obtiene CSV raw desde GitHub
- **Pandas parsing** → Procesa estructura CSV
- **Validación** → Verifica enlaces PubMed Central
- **Limpieza** → Filtrado de datos inconsistentes

### 2. PubMed PDF Scraper
- **Doble método**: Requests + Selenium
- **Detección automática** de URLs PDF
- **Rate limiting** inteligente (50 descargas/hora)
- **Reintentos** automáticos en caso de fallo
- **Validación** de archivos descargados

### 3. PDF to Markdown Converter
- **Extracción de texto** con PyPDF2
- **Identificación de secciones** científicas (Abstract, Methods, Results, etc.)
- **Formateo Markdown** estructurado
- **Metadatos** preservados (título, autor, fecha)

## 🎯 Casos de Uso

1. **Investigación científica**: Descarga masiva de papers
2. **Análisis bibliométrico**: Estudios de tendencias en biología espacial
3. **Entrada de IA**: Preparación de datos para modelos de lenguaje
4. **Data mining**: Extracción de información de literatura científica

## 🛡️ Consideraciones Éticas

- ⚠️ **Respetar robots.txt** de otros sitios web
- ⚠️ **Usar con moderación**: No sobrecargar servidores
- ⚠️ **Respeta copyright**: Solo para uso académico/investigación
- ⚠️ **Verifica términos**: Condiciones de uso de cada sitio

## 🔧 Resolución de Problemas

### Error: "No module named ..."
```bash
pip install -r requirements.txt
```

### Error: "WebDriver not found"
```bash
# El sistema instala automáticamente ChromeDriver
# Si persiste el error:
pip install --upgrade webdriver-manager
```

### Error: "Permission denied"
```bash
chmod +x install.sh
sudo ./install.sh
```

### Problemas de memoria con muchos PDFs
```bash
# Reducir MAX_ARTICLES_TO_DOWNLOAD en .env
MAX_ARTICLES_TO_DOWNLOAD=5
```

## 📈 Rendimiento Esperado

- **GitHub CSV**: ~100 artículos en 30 segundos
- **Descarga PDFs**: ~50 PDFs por hora (respetando límites)
- **Conversión Markdown**: ~1 PDF por segundo
- **Análisis completo**: ~600 artículos en 14 horas

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Algunas áreas de mejora:

- [ ] Detección automática de Captchas
- [ ] Soporte para más repositorios académicos
- [ ] Análisis de sentimientos científico
- [ ] Generación automática de resúmenes

## 📄 Licencia

Este proyecto es para uso educativo y de investigación únicamente. Respeta las políticas de uso de los sitios web objetivo.

## 🆘 Soporte

Si tienes problemas:

1. Revisa los logs en `./logs/scraper.log`
2. Verifica la configuración en `.env`
3. Ejecuta primero `python main.py test`
4. Consulta los errores comunes arriba

---

**¡Disfruta explorando la ciencia espacial con IA! 🛸📚**
