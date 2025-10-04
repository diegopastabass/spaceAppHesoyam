#!/usr/bin/env python3
"""
Test directo para verificar si podemos obtener PDFs reales usando diferentes técnicas.
"""
import requests
import os

def test_alternative_urls():
    """Prueba URLs alternativas para obtener PDFs."""
    print("🔍 PROBANDO URLs ALTERNATIVAS PARA PDFs REALES")
    print("=" * 60)
    
    # Primeros artículos del CSV para probar
    test_cases = [
        {
            'title': 'Mice in Bion-M 1 space mission',
            'pmc_id': 'PMC4136787',
            'urls': [
                'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4136787/pdf/pone.0104830.pdf',
                'http://www.ncbi.nlm.nih.gov/pmc/articles/PMC4136787/pdf/pone.0104830.pdf',
                'https://ncbi.nlm.nih.gov/pmc/articles/PMC4136787/pdf/pone.0104830.pdf',
                'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4136787/pdf/',
                'https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0104830&type=printable',
            ]
        },
        {
            'title': 'Microgravity induces pelvic bone loss',
            'pmc_id': 'PMC3630201', 
            'urls': [
                'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3630201/pdf/pone.0061372.pdf',
                'https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0061372&type=printable',
                'http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3630201/pdf/',
            ]
        }
    ]
    
    # Crear directorio para pruebas
    os.makedirs('downloads_test', exist_ok=True)
    
    success_count = 0
    
    for test_case in test_cases:
        print(f"\n📄 Probando: {test_case['title']}")
        print(f"📝 PMC ID: {test_case['pmc_id']}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Accept': 'application/pdf,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        for i, url in enumerate(test_case['urls']):
            try:
                print(f"\n   🔗 Intentando URL {i+1}: {url}")
                
                response = requests.get(url, headers=headers, timeout=30, stream=True)
                print(f"   📊 Status: {response.status_code}")
                print(f"   📋 Content-Type: {response.headers.get('content-type', 'N/A')}")
                print(f"   📏 Content-Length: {response.headers.get('content-length', 'N/A')}")
                
                if response.status_code == 200:
                    # Leer contenido en chunks
                    content = b''
                    for chunk in response.iter_content(chunk_size=8192):
                        content += chunk
                    
                    content_size = len(content)
                    print(f"   📊 Tamaño descargado: {content_size:,} bytes")
                    
                    # Verificar si es PDF real
                    is_pdf = content.startswith(b'%PDF')
                    is_html = b'<html>' in content[:1000] or b'Preparing to download' in content[:1000]
                    
                    if is_pdf and not is_html and content_size > 50000:
                        # Guardar PDF válido
                        filename = f"{test_case['pmc_id']}-{test_case['title'].replace(' ', '-')[:30]}.pdf"
                        filepath = os.path.join('downloads_test', filename)
                        
                        with open(filepath, 'wb') as f:
                            f.write(content)
                        
                        print(f"   ✅ PDF VÁLIDO descargado: {filename}")
                        print(f"   📏 Tamaño: {content_size:,} bytes ({content_size/1024/1024:.2f} MB)")
                        success_count += 1
                        break
                    else:
                        print(f"   ❌ No es PDF válido:")
                        print(f"      - Header PDF: {'SÍ' if is_pdf else 'NO'}")
                        print(f"      - No HTML: {'SÍ' if not is_html else 'NO'}")
                        print(f"      - Tamaño suficiente: {'SÍ' if content_size > 50000 else 'NO'}")
                        
                        # Mostrar primeras líneas para debugging
                        try:
                            preview = content[:100].decode('utf-8', errors='ignore')
                            print(f"      - Preview: {preview[:50]}...")
                        except:
                            print(f"      - Preview: [bytes binarios]")
                else:
                    print(f"   ❌ Error HTTP: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    print(f"\n🏁 RESULTADO FINAL:")
    print(f"=" * 30)
    print(f"✅ PDFs válidos obtenidos: {success_count}")
    print(f"📊 Tasa de éxito: {success_count}/{len(test_cases)} artículos")
    
    if success_count > 0:
        print(f"🎯 ¡ENCONTRAMOS MÉTODO FUNCIONAL!")
        print(f"💡 Podemos obtener PDFs reales")
    else:
        print(f"❌ PubMed Central protege todos los métodos HTTP")
        print(f"🔧 SOLUCIÓN DEFINITIVA: Instalar Chrome real")

if __name__ == "__main__":
    test_alternative_urls()
