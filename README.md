# 🚀 **Space App Hesoyam - Scientific Article Scraper**

## 📋 **Descripción del Proyecto**

Este sistema automatizado permite descargar artículos científicos de PubMed Central directamente desde sus journals originales, obteniendo PDFs reales (varios MB) en lugar de páginas HTML falsas.

## ⭐ **Características Principales**

- ✅ **Descarga PDFs reales** desde journals PLoS ONE
- ✅ **Selección por rango** - Procesa exactamente los artículos que necesites
- ✅ **Validación automática** - Detecta y elimina archivos HTML falsos
- ✅ **Estadísticas detalladas** - Tasa de éxito, tamaños de archivos
- ✅ **Detección inteligente** - Identifica tipos de journal automáticamente

## 🔧 **Configuración**

### **Archivo Principal:** `scraper_personalizado.py`

Modifica estas líneas según tus necesidades:

```python
# ============================================================================
# 🔧 CONFIGURA TU RANGO AQUÍ - CAMBIA ESTOS VALORES
# ============================================================================
START_INDEX = 1      # Número del artículo inicial
END_INDEX = 10       # Número del artículo final
# ============================================================================
```

## 🎯 **Ejemplos de Configuración**

### 📊 **Rangos Comunes:**

```python
# Primeros 5 artículos
START_INDEX = 1
END_INDEX = 5

# Artículos del 20 al 30  
START_INDEX = 20
END_INDEX = 30

# Solo artículo específico
START_INDEX = 5
END_INDEX = 5

# Rango medio del dataset
START_INDEX = 100
END_INDEX = 110
```

### 🔍 **Rangos por Tipo de Investigación:**

```python
# Para pruebas iniciales (pequeño)
START_INDEX = 1
END_INDEX = 3

# Para procesamiento estándar (mediano)
START_INDEX = 1
END_INDEX = 15

# Para análisis completo (grande)
START_INDEX = 1
END_INDEX = 50
```

## 🚀 **Instalación y Uso**

### **1. Prerrequisitos**
```bash
pip install requests pandas beautifulsoup4 PyPDF2 markdownify
```

### **2. Configurar tu rango**
1. Abre `scraper_personalizado.py`
2. Modifica `START_INDEX` y `END_INDEX`
3. Guarda el archivo

### **3. Ejecutar**
```bash
python3.10 scraper_personalizado.py
```

### **4. Ejecutar sin confirmación**
```bash
python3.10 scraper_personalizado_test.py
```

## 📊 **Estructura de Datos**

### **Input:** CSV de GitHub
- **Fuente:** `https://raw.githubusercontent.com/jgalazka/SB_publications/main/SB_publication_PMC.csv`
- **Total artículos:** 607 títulos científicos sobre microgravedad
- **Formato:** Título + URL de PubMed Central

### **Output:** PDFs Reales
- **Directorio:** `downloads/`
- **Nomenclatura:** `{INDEX}-{PMC_ID}-{TITLE_SHORT}.pdf`
- **Tamaño típico:** 1-25 MB por PDF

## 🔄 **Proceso de Descarga**

### **1. Extracción de Datos**
```python
# Carga CSV completo desde GitHub
df = pd.read_csv(csv_url)

# Extrae subconjunto según rango configurado
subset = df.iloc[START_INDEX-1:END_INDEX]
```

### **2. Detección de Journal**
```python
# Detecta automáticamente tipo de journal
if 'pone' in url.lower():
    return "PLoS ONE"  # ✅ Puede descargar
elif 'ijms' in url.lower():
    return "IJMS"     # ❌ No compatible actualmente
```

### **3. Descarga PDF Real**
```python
# Construye URL PLoS ONE directa
plos_url = f'https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.{pone_id}&type=printable'

# Descarga desde journals.plos.org (sin bloqueos)
response = requests.get(plos_url)
```

### **4. Validación**
```python
# Verifica que sea PDF real
if len(content) > 50000 and content.startswith(b'%PDF'):
    # ✅ Guarda PDF válido
else:
    # ❌ Elimina archivo inválido
```

## 📁 **Archivos del Sistema**

### **🔧 Archivos de Configuración**
- `scraper_personalizado.py` - Script principal **⭐ RECOMENDADO**
- `scraper_personalizado_test.py` - Versión sin confirmación
- `scraper_with_range.py` - Versión avanzada completa
- `config_range.py` - Archivo de configuración ejemplo

### **📊 Archivos de Datos**
- `analysis_results.csv` - Resultados de procesamiento
- `CONFIGURACION_RANGO.md` - Documentación de configuración

### **📂 Directorios de Salida**
- `downloads/` - PDFs reales descargados
- `downloads_plos/` - PDFs PLoS ONE específicos  
- `downloads_range/` - PDFs por rango configurado
- `downloads_functional/` - PDFs usando método funcionar

## 📈 **Resultados Típicos**

### **✅ Caso de Éxito (Rango 1-10):**
```
📊 RESULTADOS:
✅ Exitosos: 8/10 (80%)
📏 Total: 43.5 MB
📏 Promedio: 5.44 MB por PDF
🎯 ¡PDFs REALES obtenidos!

📁 ARCHIVOS:
001-PMC4136787-Mice-in-Bion-M-1-space-mission.pdf      (2.37 MB)
002-PMC3630201-Microgravity-induces-pelvic-bo.pdf      (1.47 MB)
003-PMC11988870-Stem-Cell-Health-and-Tissue-Re.pdf     (5.40 MB)
005-PMC5587110-Microgravity-validation-of-a-n.pdf      (25.29 MB)
```

### **❌ Casos de Falla:**
- Solo artículos **PLoS ONE** tienen descarga garantizada
- Otros journals (IJMS, Cells, Nature) requieren métodos adicionales
- La tasa de éxito depende del tipo de journals en el rango

## ⚙️ **Configuración Avanzada**

### **Modificar Comportamiento:**
```python
# Cambiar delay entre descargas
delay = 2.0  # segundos

# Cambiar directorio de salida  
download_dir = './downloads'

# Límite de tamaño mínimo para PDF válido
min_size = 50000  # bytes (50KB)
```

### **Validaciones Estrictas:**
```python
# Verificar header PDF
header_valid = content.startswith(b'%PDF')

# Verificar tamaño mínimo realista
size_valid = len(content) > 50000

# Verificar que NO sea HTML
not_html = '<html>' not in content.lower()
```

## 🔍 **Diagnóstico de Problemas**

### **❌ Errores Comunes:**

**"START_INDEX debe ser >= 1"**
- **Solución:** Cambia START_INDEX a 1 o mayor
- **Causa:** Índices van de 1 a N (no 0 a N-1)

**"END_INDEX debe ser >= START_INDEX"**  
- **Solución:** Asegúrate que END_INDEX >= START_INDEX
- **Ejemplo correcto:** START=5, END=10 ✅

**"Rango muy grande"**
- **Solución:** Divide en lotes ≤ 50 artículos
- **Razon:** Evita sobrecarga del sistema

**"0% tasa de éxito"**
- **Causa:** Ningún artículo es PLoS ONE en el rango
- **Solución:** Cambia rango o verifica tipos de journal

### **✅ Verificaciones de Éxito:**

**PDFs Válidos:**
- ✅ Tamaño >1MB típicamente
- ✅ Header empieza con "%PDF"
- ✅ Contenido no es HTML

**Logs Informativos:**
```
✅ PDF descargado: filename.pdf (2,488,168 bytes)
📊 Tasa: 8/10 (80.0%)
🎯 ¡PDFs REALES obtenidos!
```

## 🎯 **Especificaciones Técnicas**

### **🤖 Automatización:**
- **Detección automática** de journals PLoS ONE
- **Construcción automática** de URLs PLoS directas
- **Validación automática** de contenido PDF
- **Limpieza automática** de archivos inválidos

### **🛡️ Resilencia:**
- **Soporte rate limiting** con delays configurables
- **Manejo de errores** con logs detallados
- **Validaciones múltiples** de contenido
- **Recovery de fallas** por timeout/red

### **📊 Escalabilidad:**
- **Procesamiento por lotes** configurables
- **Memoria eficiente** con stream processing
- **Logging estructurado** para monitoreo
- **Estadísticas detalladas** de resultados

## 🌐 **Ecosistema de Journals**

### **✅ Compatible Actualmente:**
- **PLoS ONE** - Método funcionar completo

### **🔄 En Desarrollo:**
- **MDPI journals** (IJMS, Cells, etc.)
- **Nature journals**
- **Springer journals** 
- **Oxford journals**

### **📋 Métodos Futuros:**
- Selenium WebDriver para journals complejos
- APIs oficiales cuando disponibles
- Métodos de crawling avanzados

## 📚 **Casos de Uso**

### **🎓 Investigación Académica:**
```python
START_INDEX = 1
END_INDEX = 20
# Descarga artículos para revisión sistemática
```

### **🔬 Análisis Específico:**
```python
START_INDEX = 50
END_INDEX = 100
# Foco en un subconjunto específico
```

### **⚡ Testing Rápido:**
```python
START_INDEX = 1
END_INDEX = 5
# Validación rápida del sistema
```

### **📊 Procesamiento Completo:**
```python
START_INDEX = 1
END_INDEX = 100  # Procesar primer centena
```

## 🎉 **Estado del Proyecto**

- ✅ **Sistema Base:** 100% funcional
- ✅ **Configuración Flexible:** Implementada
- ✅ **PDFs Reales:** Descargando correctamente  
- ✅ **Validación Fuerte:** Detectando archivos inválidos
- ✅ **Logging Detallado:** Información completa

**🎯 El sistema está LISTO para uso en producción!**

---

### 📞 **Soporte**
Para problemas o mejoras, revisar logs en consola para detalles específicos de fallas.