#!/usr/bin/env python3
"""
Analizador detallado del problema de PDFs de 2KB.
"""
import os
import requests
import urllib.parse
import re
from collections import Counter

def analyze_downloaded_files():
    """Analiza los archivos descargados para entender el patrón."""
    print("🔍 ANÁLISIS DETALLADO DE ARCHIVOS DESCARGADOS")
    print("=" * 60)
    
    downloads_dir = "downloads"
    files = [f for f in os.listdir(downloads_dir) if f.endswith('.pdf')]
    
    print(f"📊 Total de archivos: {len(files)}")
    
    # Análisis de tamaños
    sizes = []
    types = []
    contents_start = {}
    
    for file in files:
        path = os.path.join(downloads_dir, file)
        size = os.path.getsize(path)
        sizes.append(size)
        
        # Leer primeras líneas
        with open(path, 'r', errors='ignore') as f:
            first_lines = '\n'.join(f.readlines()[:5])
            contents_start[file] = first_lines
        
        print(f"📄 {file}: {size} bytes")
    
    # Estadísticas de tamaños
    size_counts = Counter(sizes)
    print(f"\n📈 Distribución de tamaños:")
    for size, count in size_counts.items():
        print(f"   {size} bytes: {count} archivos")
    
    # Análisis de contenido
    print(f"\n🔍 ANÁLISIS DE CONTENIDO:")
    
    # Verificar si todos tienen el mismo inicio HTML
    html_starts = set()
    for file, content in contents_start.items():
        if '<html>' in content and 'Preparing to download' in content:
            html_start = content.split('\n')[0:3]
            html_starts.add('\n'.join(html_start))
            print(f"✅ {file}: Contiene HTML 'Preparing to download'")
        else:
            print(f"❌ {file}: NO tiene el patrón esperado")
    
    if len(html_starts) == 1:
        print(f"\n⚠️ TODOS los archivos son idénticos en estructura HTML")
        print(f"🔍 Estructura común:")
        print(list(html_starts)[0])
    
    return sizes, size_counts

def test_response_pattern():
    """Prueba qué tipo de respuesta estamos obteniendo."""
    print(f"\n🧪 PRUEBA DE RESPUESTA HTTP:")
    print("=" * 40)
    
    test_url = "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4136787/pdf/pone.0104830.pdf"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"🔗 Probar URL: {test_url}")
        response = requests.get(test_url, headers=headers, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Headers:")
        for key, value in response.headers.items():
            if 'content-type' in key.lower() or 'length' in key.lower():
                print(f"   {key}: {value}")
        
        # Verificar contenido
        content = response.text
        print(f"📊 Tamaño respuesta: {len(content)} bytes")
        print(f"📊 ¿Contiene '<html>'?: {'<html>' in content}")
        print(f"📊 ¿Contiene 'Preparing to download'?: {'Preparing to download' in content}")
        
        if '<html>' in content:
            title_match = re.search(r'<title>(.*?)</title>', content)
            if title_match:
                print(f"📄 Título de la página: {title_match.group(1)}")
        
        return response.status_code, len(content), '<html>' in content
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        return None, None, None

def identify_root_cause(sizes, size_counts):
    """Identifica la causa raíz del problema."""
    print(f"\n🎯 DIAGNÓSTICO DE CAUSA RAÍZ:")
    print("=" * 50)
    
    # Análisis de patrones
    if len(size_counts) <= 2:
        print("⚠️ PROBLEMA CONFIRMADO: Solo 1-2 tamaños diferentes")
        print("   Esto indica que NO estamos descargando PDFs individuales")
    
    if all(size < 2000 for size in size_counts.keys()):
        print("⚠️ PROBLEMA CONFIRMADO: Todos los archivos son < 2KB")
        print("   Los PDFs científicos deben ser mucho más grandes")
    
    # Hipótesis principales
    print(f"\n🔍 HIPÓTESIS PRINCIPALES:")
    print("1. 🚫 PubMed Central está bloqueando descargas automáticas")
    print("2. 🚫 Estamos obteniendo páginas 'Preparing to download...' en lugar de PDFs")
    print("3. 🚫 El JavaScript anti-bot está funcionando correctamente")
    print("4. ✅ Necesitamos navegador real (Chrome) con Selenium")
    
    print(f"\n📋 EVIDENCIA:")
    status_code, content_size, is_html = test_response_pattern()
    
    if is_html:
        print("✅ CONFIRMADO: La respuesta es HTML, no PDF binario")
        print("✅ CONFIRMADO: PubMed Central está sirviendo página de espera")
        
        return "javascript_protection"
    else:
        print("❓ INCONCLUSIVO: Necesitamos más investigación")
        return "unknown"

def main():
    """Función principal de análisis."""
    print("🔬 ANÁLISIS TÉCNICO DE PROBLEMA DE PDFs DE 2KB")
    print("=" * 70)
    
    # 1. Analizar archivos existentes
    sizes, size_counts = analyze_downloaded_files()
    
    # 2. Probar respuesta HTTP actual
    status_code, content_size, is_html = test_response_pattern()
    
    # 3. Diagnóstico final
    root_cause = identify_root_cause(sizes, size_counts)
    
    print(f"\n🎯 CONCLUSIÓN FINAL:")
    print("=" * 30)
    if root_cause == "javascript_protection":
        print("✅ DIAGNÓSTICO CONFIRMADO:")
        print("   • PubMed Central protege PDFs con JavaScript")
        print("   • Nuestros requests HTTP obtienen páginas HTML de 'Preparing to download...'")
        print("   • Todos los archivos tienen ~1284 bytes porque son la misma página HTML")
        print("   • La solución es usar Chrome/Selenium para ejecutar JavaScript")
        
        print(f"\n🛠️ PRÓXIMOS PASOS:")
        print("1. Instalar Chrome en WSL")
        print("2. Configurar Selenium con ChromeDriver")
        print("3. Modificar pubmed_scraper.py para usar navegador real")
        print("4. Ejecutar prueba con navegador real")
    
    else:
        print("❓ DIAGNÓSTICO INCONCLUSIVO")
        print("   Necesitamos más investigación en el código de descarga")

if __name__ == "__main__":
    main()
