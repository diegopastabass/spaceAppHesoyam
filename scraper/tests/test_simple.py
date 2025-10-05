#!/usr/bin/env python3
"""
Versión simplificada para pruebas sin dependencias externas complejas.
"""
import sys
import urllib.request
import urllib.parse
import json
import os

def get_csv_data():
    """Obtiene datos del CSV usando solo librerías estándar."""
    csv_url = "https://raw.githubusercontent.com/jgalazka/SB_publications/main/SB_publication_PMC.csv"
    
    print(f"🔍 Obteniendo datos de: {csv_url}")
    
    try:
        # Descargar CSV
        response = urllib.request.urlopen(csv_url)
        csv_content = response.read().decode('utf-8')
        
        # Parsear CSV simple
        lines = csv_content.strip().split('\n')
        headers = lines[0].split(',')
        
        print(f"📊 Headers encontrados: {headers}")
        print(f"📑 Total de líneas: {len(lines)}")
        
        # Extraer primeros 5 artículos
        articles = []
        for i, line in enumerate(lines[1:6], 1):  # Primera línea + 5 artículos
            try:
                # Split simple por comas (puede ser problemático si hay comas en títulos)
                parts = line.split(',', 1)  # Dividir máximo 1 vez
                if len(parts) >= 2:
                    articles.append({
                        'title': parts[0].strip('"'),
                        'link': parts[1].strip('"')
                    })
                    print(f"✅ Artículo {i}: {parts[0][:50]}...")
                else:
                    print(f"⚠️ Línea {i} tiene formato incorrecto: {line[:50]}...")
            except Exception as e:
                print(f"❌ Error procesando línea {i}: {e}")
        
        return articles
        
    except Exception as e:
        print(f"❌ Error descargando CSV: {e}")
        return []

def test_pdf_url(full_article):
    """Prueba si podemos acceder a la URL del artículo."""
    url = full_article['link']
    title = full_article['title']
    
    print(f"🔗 Probando acceso a: {title[:50]}...")
    print(f"   URL: {url}")
    
    try:
        # Intentar acceder a la página
        request = urllib.request.Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124')
        
        response = urllib.request.urlopen(request, timeout=10)
        content = response.read().decode('utf-8')
        
        print(f"✅ Acceso exitoso - Tamaño: {len(content)} bytes")
        
        # Buscar links PDF en el contenido
        pdf_links = []
        if '.pdf' in content.lower():
            print("✅ Se detectó contenido PDF en la página")
        else:
            print("⚠️ No se detectó contenido PDF evidente")
            
        # Buscar textos relacionados con PDFs
        pdf_indicators = ['pdf', 'download', 'descarga']
        found_indicators = []
        for indicator in pdf_indicators:
            if indicator.lower() in content.lower():
                found_indicators.append(indicator)
        
        if found_indicators:
            print(f"🔍 Indicadores PDF encontrados: {', '.join(found_indicators)}")
        else:
            print("⚠️ No se encontraron indicadores claros de descarga PDF")
            
        return True
        
    except Exception as e:
        print(f"❌ Error accediendo a la URL: {e}")
        return False

def main():
    """Función principal de prueba simplificada."""
    print("🚀 Iniciando prueba simplificada del scraper...")
    print("=" * 60)
    
    # Paso 1: Obtener datos del CSV
    print("📊 Paso 1: Obteniendo datos del CSV de GitHub...")
    articles = get_csv_data()
    
    if not articles:
        print("❌ No se pudieron obtener datos del CSV")
        return 1
    
    print(f"✅ {len(articles)} artículos obtenidos exitosamente")
    print()
    
    # Paso 2: Probar acceso a URLs
    print("🔗 Paso 2: Probando acceso a URLs de PubMed Central...")
    successful_access = 0
    
    for i, article in enumerate(articles, 1):
        print(f"Artículo {i}/{len(articles)}:")
        if test_pdf_url(article):
            successful_access += 1
        print()
    
    # Resumen
    print("=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    print(f"✅ Artículos procesados: {len(articles)}")
    print(f"✅ Accesos exitosos: {successful_access}")
    print(f"📈 Tasa de éxito: {successful_access/len(articles)*100:.1f}%")
    
    if successful_access > 0:
        print("\n🎉 ¡El scraper básico funciona correctamente!")
        print("📋 Los datos del CSV son accesibles")
        print("🌐 Las URLs de PubMed Central responden correctamente")
        print("\n💡 Paso siguiente: Instalar dependencias completas para PDFs")
    else:
        print("\n⚠️ Hay problemas con el acceso a las URLs")
        print("🔧 Verificar conectividad y URLs")
    
    return 0 if successful_access > 0 else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)


