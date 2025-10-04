# 🎯 Sistema de Configuración de Rango de Artículos

## 📋 **Descripción**

Este sistema te permite seleccionar exactamente qué artículos procesar modificando dos variables simples: `START_INDEX` y `END_INDEX`.

## 🔧 **Configuración Rápida**

### Variables Principales:
- **`START_INDEX`**: Número del artículo inicial
- **`END_INDEX`**: Número del artículo final

### 📊 Ejemplos de Uso:

```
START_INDEX = 1     END_INDEX = 10     → Primeros 10 artículos
START_INDEX = 5     END_INDEX = 15     → Artículos del 5 al 15  
START_INDEX = 25    END_INDEX = 35     → Artículos del 25 al 35
START_INDEX = 100   END_INDEX = 110    → Artículos del 100 al 110
```

## 🚀 **Archivos Disponibles**

### 1. **scraper_personalizado.py** ⭐ (Recomendado)
```python
START_INDEX = 1      # Cambia aquí
END_INDEX = 10       # Cambia aquí
```

**Uso:**
```bash
python3.10 scraper_personalizado.py
```

### 2. **scraper_with_range.py** 
Versión completa con más funcionalidades

### 3. **scraper_example_range.py**
Ejemplo específico con artículos 5-15

## 📝 **Cómo Modificar**

1. **Abre el archivo** `scraper_personalizado.py`
2. **Busca las líneas:**
   ```python
   START_INDEX = 1
   END_INDEX = 10
   ```
3. **Modifica los valores** según necesites
4. **Ejecuta** el script

## ⚠️ **Reglas Importantes**

- ✅ **START_INDEX >= 1** (Primer artículo es número 1)
- ✅ **END_INDEX >= START_INDEX** 
- ✅ **Números base 1** (No base 0)
- ⚠️ **Recomendado**: Máximo 50 artículos por ejecución
- ⚠️ **Solo funciona** con PDFs PLoS ONE actualmente

## 📊 **Ejemplos Específicos**

### Para Estudiantes/Testing:
```python
START_INDEX = 1
END_INDEX = 5
# Procesa solo los primeros 5 artículos
```

### Para Procesamiento Rango Medio:
```python
START_INDEX = 50
END_INDEX = 65
# Procesa 15 artículos del medio del dataset
```

### Para Análisis Específico:
```python
START_INDEX = 100
END_INDEX = 105
# Procesa 5 artículos específicos
```

## 🎯 **Resultado Final**

El sistema te dará:
- 📄 **PDFs válidos** descargados en carpeta `downloads/`
- 📊 **Estadísticas** de éxito/fallo
- 📏 **Tamaños** de archivos descargados
- 🔍 **Análisis** de qué tipos de journals funcionan

## 🛠️ **Solución de Problemas**

**❌ Error: "START_INDEX debe ser >= 1"**
- **Solución**: Cambia START_INDEX a 1 o mayor

**❌ Error: "END_INDEX debe ser >= START_INDEX"**
- **Solución**: Asegúrate que END_INDEX sea >= START_INDEX

**⚠️ Advertencia: "Rango muy grande"**
- **Solución**: Divide en lotes más pequeños (máximo 50 artículos)

**❌ 0% tasa de éxito**
- **Causa**: Solo funciona con PLoS ONE actualmente
- **Solución**: Busca artículos PLoS ONE específicamente

## 💡 **Tips Útiles**

1. **Ejecuta primero** con rango pequeño (1-5) para probar
2. **Verifica tipos** de journal antes de procesar muchos
3. **Monitorea espacio** en disco para rangos grandes
4. **Guarda configuración** que funcione bien

## 📂 **Archivos Generados**

```
downloads/
├── 001-PMC4136787-Mice-in-Bion-M-1-space-mission.pdf  (2.4 MB)
├── 002-PMC3630201-Microgravity-induces-pelvic-bone.pdf (1.5 MB)
└── 003-PMC5587110-Microgravity-validation.pdf         (25 MB)
```

---

🎉 **¡Configuración lista! Podrás procesar exactamente los artículas del rango que necesites.**
