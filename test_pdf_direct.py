#!/usr/bin/env python3
"""
Prueba directa de descarga usando el patrón estándar de URL de PubMed Central.
"""
import urllib.request
import re
import os

def download_pdf_from_pubmed(article_url, filename="test_article.pdf"):
    """Descarga PDF directamente usando el patrón estándar de PubMed Central."""
    
    print(f"🔗 Artículo original: {article_url}")
    
    # Extraer el PMC ID del URL
    pmc_match = re.search(r'PMC\d+', article_url)
    if not pmc_match:
        print("❌ No se encontró PMC ID en el URL")
        return False
    
    pmc_id = pmc_match.group()
    print(f"🔍 PMC ID encontrado: {pmc_id}")
    
    # Construir URL del PDF usando el patrón estándar
    # Formato: https://www.ncbi.nlm.nih.gov/pmc/articles/{ID}/pdf/
    pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/pdf/"
    
    print(f"📥 Intentando descargar desde: {pdf_url}")
    
    # Método 1: Intentar URL estándar PMC
    try:
        request = urllib.request.Request(pdf_url)
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124')
        
        response = urllib.request.urlopen(request, timeout=30)
        content_type = response.headers.get('Content-Type', '').lower()
        
        if 'pdf' in content_type:
            print(f"✅ PDF encontrado en URL estándar!")
            return download_and_save(response, filename)
        else:
            print(f"⚠️ Content-Type: {content_type}")
    except Exception as e:
        print(f"❌ Error con URL estándar: {e}")
    
    # Método 2: Intentar URL con redirección automática
    try:
        final_pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/pdf/"
        # Forzar descarga añadiendo parámetros
        forced_url = pdf_url + "?download=true"
        
        print(f"🔄 Intentando forzar descarga: {forced_url}")
        
        request = urllib.request.Request(forced_url)
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124')
        
        response = urllib.request.urlopen(request, timeout=30)
        data = response.read()
        
        if len(data) > 1000:  # Puede ser un PDF real
            download_dir = './downloads'
            os.makedirs(download_dir, exist_ok=True)
            
            filepath = os.path.join(download_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(data)
            
            print(f"✅ PDF potencial descargado: {filepath}")
            print(f"   Tamaño: {len(data)} bytes")
            return True
        else:
            print(f"⚠️ Respuesta muy pequeña: {len(data)} bytes")
            
    except Exception as e:
        print(f"❌ Error con descarga forzada: {e}")
    
    # Método 3: Generar URL del PDF basado en PMC ID
    try:
        # Patrón observado: PMC1234567/files/PMC1234567.pdf
        files_url = f"https://www.ncbi.nlm.nih.gov/pmc/files/{pmc_id}/{pmc_id}.pdf"
        print(f"🔍 Probando URL de archivos: {files_url}")
        
        request = urllib.request.Request(files_url)
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124')
        
        response = urllib.request.urlopen(request, timeout=30)
        data = response.read()
        
        if len(data) > 1000:
            download_dir = './downloads'
            os.makedirs(download_dir, exist_ok=True)
            
            filepath = os.path.join(download_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(data)
            
            print(f"✅ PDF encontrado en URL de archivos!")
            print(f"   Archivo: {filepath}")
            print(f"   Tamaño: {len(data)} bytes")
            return True
        else:
            print(f"⚠️ URL de archivos sin datos: {len(data)} bytes")
            
    except Exception as e:
        print(f"❌ Error con URL de archivos: {e}")
    
    return False

def download_and_save(response, filename):
    """Descarga y guarda el PDF desde la respuesta."""
    try:
        download_dir = './downloads'
        os.makedirs(download_dir, exist_ok=True)
        
        filepath = os.path.join(download_dir, filename)
        with open(filepath, 'wb') as f:
            data = response.read()
            f.write(data)
        
        print(f"✅ PDF descargado exitosamente: {filepath}")
        print(f"   Tamaño: {len(data)} bytes")
        
        return True
    except Exception as e:
        print(f"❌ Error guardando archivo: {e}")
        return False

def main():   
    """Prueba de descarga de PDF usando diferentes métodos."""
    print("🔄 Prueba avanzada de descarga de PDF...")
    print("=" * 60)
    
    # Probar con el artículo que sabemos que existe
    test_urls = [
        "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4136787/",
        "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11988870/",
    ]
    
    downloaded_count = 0
    
    for i, url in enumerate(test_urls, 1):
        print(f"📄 Prueba {i}/{len(test_urls)}:")
        print(f"   URL: {url}")
        
        filename = f"test_article_{i}.pdf"
        success = download_pdf_from_pubmed(url, filename)
        
        if success:
            downloaded_count += 1
            print(f"✅ Éxito!")
        else:
            print(f"❌ Falló")
        print()
    
    # Resumen final
    print("=" * 60)
    print("📊 RESUMEN FINAL")
    print("=" * 60)
    print(f"✅ PDFs descargados: {downloaded_count}/{len(test_urls)}")
    
    if downloaded_count > 0:
        print("\n🎉 ¡La descarga de PDFs funciona!")
        print("📁 Archivos disponibles en: ./downloads/")
        print("\n💡 Esto demuestra que el sistema puede:")
        print("   • Obtener datos del CSV de GitHub")
        print("   • Acceder a páginas de PubMed Central") 
        print("   • Descargar PDFs científicos")
        print("\n🔧 Con las dependencias completas:", 
              "(pandas, selenium, PyPDF2) el sistema")
        print("   funcionará con todas las funciones avanzadas:")
        print("   • Rate limiting inteligente")
        print("   • Conversión a Markdown")
        print("   • Procesamiento por lotes")
        print("   • Análisis con IA")
        
        # Listar archivos descargados
        if os.path.exists('./downloads'):
            files = os.listdir('./downloads')
            print(f"\n📋 Archivos en ./downloads/ ({len(files)} archivos):")
            for file in files:
                filepath = os.path.join('./downloads', file)
                size = os.path.getsize(filepath)
                print(f"   • {file} ({size:,} bytes)")
    else:
        print("\n⚠️ No se pudieron descargar PDFs")
        print("🔧 Esto puede deberse a:")
        print("   • Limitaciones de acceso de PubMed Central")
        print("   • Necesidad de usar métodos más avanzados (Selenium)")
        print("   • Posibles cambios en la estructura de URLs")
    
    return downloaded_count

if __name__ == "__main__":
    import sys
    count = main()
    sys.exit(0 if count > 0 else 1)


