#!/usr/bin/env python3
"""
Prueba específica de descarga de PDF usando solo librerías estándar.
"""
import urllib.request
import re
import os

def find_pdf_url(article_url):
    """Busca URL de PDF en la página del artículo."""
    try:
        print(f"🔍 Analizando página: {article_url}")
        
        request = urllib.request.Request(article_url)
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124')
        
        response = urllib.request.urlopen(request, timeout=10)
        content = response.read().decode('utf-8')
        
        # Buscar URLs PDF en el contenido HTML
        pdf_urls = []
        
        # Patrón 1: Enlaces PDF directos  
        pdf_pattern = r'href="([^"]*\.pdf[^"]*)"'
        matches = re.findall(pdf_pattern, content, re.IGNORECASE)
        pdf_urls.extend(matches)
        
        # Patrón 2: URLs que contienen '/pdf/'
        pdf_pattern2 = r'href="([^"]*/pdf/[^"]*)"'
        matches2 = re.findall(pdf_pattern2, content, re.IGNORECASE)
        pdf_urls.extend(matches2)
        
        # Patrón 3: URL correcta del artículo PMC con formato de descarga
        # Usar el formato: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{ID}/pdf/
        if '/articles/PMC' in article_url:
            pmc_id = re.search(r'PMC\d+', article_url)
            if pmc_id:
                pubmed_formatted_url = article_url.replace('/articles/', '/pdf/') + '.pdf'
                pdf_urls.append(pubmed_formatted_url)
        
        # Limpiar URLs encontradas
        clean_urls = []
        for url in pdf_urls:
            if url.startswith('/'):
                # URL relativa, convertir a absoluta
                base_url = '/'.join(article_url.split('/')[:3])
                url = base_url + url
            elif not url.startswith('http'):
                # URL relativa sin slash inicial
                base_url = '/'.join(article_url.split('/')[:4])
                url = base_url + '/' + url
                
            if url.endswith('.pdf') or '/pdf/' in url:
                clean_urls.append(url)
        
        print(f"🔗 URLs PDF encontradas: {len(clean_urls)}")
        for i, url in enumerate(clean_urls[:3], 1):  # Mostrar máximo 3
            print(f"   {i}. {url}")
        
        return clean_urls
        
    except Exception as e:
        print(f"❌ Error analizando página: {e}")
        return []

def download_pdf_test(pdf_url, filename="test_article.pdf"):
    """Intenta descargar un PDF."""
    try:
        print(f"📥 Descargando PDF: {filename}")
        print(f"   URL: {pdf_url}")
        
        request = urllib.request.Request(pdf_url)
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124')
        
        response = urllib.request.urlopen(request, timeout=30)
        
        # Verificar que realmente es un PDF
        content_type = response.headers.get('Content-Type', '').lower()
        if 'pdf' not in content_type:
            print(f"⚠️ Content-Type: {content_type} (puede no ser PDF)")
        else:
            print(f"✅ Content-Type: {content_type}")
        
        # Descargar el archivo
        data = response.read()
        
        if len(data) < 1000:  # Menos de 1KB probablemente sea error
            print(f"❌ Archivo muy pequeño ({len(data)} bytes) - probablemente error")
            return False
        
        # Guardar archivo
        download_dir = './downloads'
        os.makedirs(download_dir, exist_ok=True)
        
        filepath = os.path.join(download_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(data)
        
        print(f"✅ PDF descargado exitosamente: {filepath}")
        print(f"   Tamaño: {len(data)} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error descargando PDF: {e}")
        return False

def main():   
    """Prueba específica de descarga de PDF."""
    print("🔄 Prueba de descarga de PDF individual...")
    print("=" * 50)
    
    # Usar el primer artículo que sabemos que funciona
    test_url = "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4136787/"
    
    # Paso 1: Buscar URL del PDF
    pdf_urls = find_pdf_url(test_url)
    
    if not pdf_urls:
        print("❌ No se encontraron URLs PDF")
        return 1
    
    # Paso 2: Intentar descargar el primer PDF encontrado
    pdf_url = pdf_urls[0]
    success = download_pdf_test(pdf_url, "test_mice_space_mission.pdf")
    
    if success:
        print("\n🎉 ¡Descarga de PDF exitosa!")
        print("✅ El sistema básico puede:")
        print("   • Acceder a páginas de PubMed Central")
        print("   • Encontrar URLs de PDFs")
        print("   • Descargar archivos PDF")
        print("\n📁 Archivo guardado en: ./downloads/test_mice_space_mission.pdf")
        
        # Verificar si el archivo existe
        filepath = './downloads/test_mice_space_mission.pdf'
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"📊 Tamaño final: {size:,} bytes")
            
            # Verificar contenido básico
            with open(filepath, 'rb') as f:
                header = f.read(10)
                if header.startswith(b'%PDF'):
                    print("✅ Archivo válido: Contiene header PDF")
                else:
                    print("⚠️ Archivo puede estar corrupto")
    else:
        print("\n❌ La descarga de PDF falló")
    
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
