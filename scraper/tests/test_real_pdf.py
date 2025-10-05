#!/usr/bin/env python3
"""
Prueba de métodos alternativos para obtener PDFs reales de PubMed Central.
"""
import urllib.request
import os
import re

def try_alternative_pdf_urls(pmc_url):
    """Intenta diferentes métodos para obtener el PDF real."""
    pmc_id = re.search(r'PMC\d+', pmc_url)
    if not pmc_id:
        return None
    
    pmc_id = pmc_id.group()
    print(f"🔍 PMCID: {pmc_id}")
    
    # Métoded alternativo: Usar formato directo de archivo PMC
    # PubMed Central tiene varias formas de acceder a PDFs
    alternative_urls = [
        f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/pdf/{pmc_id}.pdf",
        f"https://www.ncbi.nlm.nih.gov/pmc/oai/oai.cgi?verb=GetRecord&identifier=oai:pubmedcentral.nih.gov:{pmc_id}&metadataPrefix=pmc",
        f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmc_id}&rettype=pdf",
        f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/pdf/main.pdf",
    ]
    
    for i, url in enumerate(alternative_urls, 1):
        print(f"🔄 Probando método {i}: {url}")
        
        try:
            request = urllib.request.Request(url)
            request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124')
            
            response = urllib.request.urlopen(request, timeout=10)
            data = response.read()
            
            # Verificar si es realmente un PDF
            if len(data) > 1000 and data[:4] == b'%PDF':
                print(f"✅ ¡PDF encontrado con método {i}!")
                return url, data
            elif len(data) > 1000:
                print(f"⚠️ Método {i}: Respuesta grande pero no es PDF ({len(data)} bytes)")
            else:
                print(f"❌ Método {i}: Respuesta muy pequeña ({len(data)} bytes)")
                
        except Exception as e:
            print(f"❌ Método {i} falló: {e}")
    
    return None, None

def download_real_pdf(pmc_url, filename="test_real.pdf"):
    """Descarga PDF real usando URLs alternativas."""
    print(f"📥 Intentando descarga real para: {pmc_url}")
    print("=" * 50)
    
    real_url, pdf_data = try_alternative_pdf_urls(pmc_url)
    
    if pdf_data:
        print(f"✅ ¡PDF real encontrado!")
        print(f"📊 Tamaño: {len(pdf_data):,} bytes")
        print(f"📄 Header: {pdf_data[:10]}")
        
        # Guardar archivo real
        os.makedirs("downloads_real", exist_ok=True)
        filepath = f"downloads_real/{filename}"
        
        with open(filepath, 'wb') as f:
            f.write(pdf_data)
        
        print(f"💾 Guardado en: {filepath}")
        return filepath
    else:
        print("❌ No se pudo obtener PDF real")
        return None

def main():
    """Prueba métodos alternativos con algunos artículos."""
    print("🚀 Probando métodos alternativos para PDFs reales...")
    print("=" * 60)
    
    # Probar con algunos artículos conocidos
    test_urls = [
        "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4136787/",
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n📄 Artículo {i}: {url}")
        result = download_real_pdf(url, f"real_test_{i}.pdf")
        
        if result:
            print(f"🎉 ¡Éxito con artículo {i}!")
            
            # Verificar tipo de archivo
            import subprocess
            result = subprocess.run(['file', result], capture_output=True, text=True)
            print(f"📝 Tipo de archivo: {result.stdout.strip()}")
            break
        else:
            print(f"❌ Falló con artículo {i}")
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN:")
    print("• El problema principal es la protección JavaScript de PubMed Central")
    print("• Los PDFs requieren ejecución de navegador real con JavaScript")
    print("• Métodos alternativos pueden funcionar para algunos artículos")
    print("\n🛠️ SOLUCIONES:")
    print("1. ✅ Instalar Chrome en WSL y usar Selenium")
    print("2. ✅ Usar diferentes servicios académicos")
    print("3. ✅ Descargar desde repositorios alternativos")

if __name__ == "__main__":
    main()
