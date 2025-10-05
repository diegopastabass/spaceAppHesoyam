#!/usr/bin/env python3
"""
Script que obtiene más PDFs de PLoS ONE usando el método funcionar.
"""
import requests
import os
import pandas as pd
import re
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_doi_from_url(url):
    """Extrae DOI de URL PMCID."""
    try:
        # Para PMC URLs, vamos a la página y extraemos el DOI
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        content = response.text
        
        # Buscar DOI en el contenido HTML
        doi_patterns = [
            r'https?://doi\.org/([^\s<>"]+)',
            r'doi:?\s*([^\s<>"]+)',
            r'https://[^"]*10\.1371/journal\.pone\.\d+',
        ]
        
        for pattern in doi_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                doi = matches[0]
                logger.info(f"📋 DOI encontrado: {doi}")
                return doi
                
        return None
    except Exception as e:
        logger.error(f"❌ Error extrayendo DOI: {e}")
        return None

def construct_plos_url(doi):
    """Construye URL de PLoS ONE desde DOI."""
    try:
        if 'pone' in doi.lower():
            # Extraer número del DOI
            pone_match = re.search(r'pone\.(\d+)', doi, re.IGNORECASE)
            if pone_match:
                pone_id = pone_match.group(1).zfill(7)
                plos_url = f'https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.{pone_id}&type=printable'
                logger.info(f"🔗 URL PLoS construida: {plos_url}")
                return plos_url
        
        return None
    except Exception as e:
        logger.error(f"❌ Error construyendo URL PLoS: {e}")
        return None

def download_plos_pdf(plos_url, filename):
    """Descarga PDF de PLoS ONE."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/pdf,*/*;q=0.9'
        }
        
        response = requests.get(plos_url, headers=headers, timeout=60)
        response.raise_for_status()
        
        # Verificar contenido
        content_type = response.headers.get('content-type', '').lower()
        if 'pdf' not in content_type:
            logger.warning(f"⚠️ URL no devolvió PDF: {content_type}")
            return None
        
        filepath = os.path.join('downloads_plos', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        file_size = os.path.getsize(filepath)
        if file_size > 50000:  # Más de 50KB
            logger.info(f"✅ PDF PLoS descargado: {filename} ({file_size:,} bytes)")
            return filepath
        else:
            os.remove(filepath)
            logger.warning(f"⚠️ PDF demasiado pequeño: {file_size} bytes")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error descargando PDF PLoS: {e}")
        return None

def process_articles_batch(article_df):
    """Procesa un lote de artículos."""
    success_count = 0
    
    logger.info(f"🚀 Procesando {len(article_df)} artículos para PLoS ONE...")
    
    for idx, (_, row) in enumerate(article_df.iterrows()):
        title = row['Title']
        url = row['Link']
        
        logger.info(f"\n📄 Artículo {idx+1}: {title[:60]}...")
        
        # Crear nombre de archivo
        pmc_match = re.search(r'PMC\d+', url)
        pmc_id = pmc_match.group() if pmc_match else f"PMC{idx}"
        
        safe_title = re.sub(r'[^\w\s-]', '', title.replace(' ', '-')[:50])
        filename = f"{pmc_id}-{safe_title}.pdf"
        
        # Intentar extraer DOI y construir URL PLoS
        doi = get_doi_from_url(url)
        if doi:
            plos_url = construct_plos_url(doi)
            if plos_url:
                filepath = download_plos_pdf(plos_url, filename)
                if filepath:
                    success_count += 1
                    logger.info(f"✅ ÉXITO: {filename}")
                    continue
        
        # Método alternativo: detectar directamente si es PLoS ONE
        if 'pone' in url.lower():
            logger.info(f"🔍 Detectado PLoS ONE directo en URL...")
            
            # Extraer el patrón pon e.XXXXXXX
            pone_match = re.search(r'pone\.(\d+)', url)
            if pone_match:
                pone_id = pone_match.group(1).zfill(7)
                
                # URLs alternativas de PLoS ONE
                plos_urls = [
                    f'https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.{pone_id}&type=printable',
                    f'https://journals.plos.org/plosone/article/file?doi=10.1371/journal.pone.{pone_id}&type=printable',
                    f'https://journals.plos.org/plosone/article/json?datasetId=10.1371/journal.pone.{pone_id}',
                ]
                
                for plos_url in plos_urls:
                    logger.info(f"🔗 Probando: {plos_url}")
                    filepath = download_plos_pdf(plos_url, filename)
                    if filepath:
                        success_count += 1
                        logger.info(f"✅ ÉXITO con método alternativo: {filename}")
                        break
                else:
                    logger.warning(f"⚠️ Falló método alternativo para: {title[:50]}")
        
        logger.info(f"❌ FALLÓ: {title[:50]}")
    
    return success_count

def main():
    """Función principal."""
    print("🎯 OBTENIENDO PDFs DE PLOS ONE USANDO MÉTODO FUNCIONAR")
    print("=" * 60)
    
    try:
        # Cargar CSV y obtener primeros artículos
        print("\n📊 Cargando datos desde CSV...")
        
        csv_url = "https://raw.githubusercontent.com/jgalazka/SB_publications/main/SB_publication_PMC.csv"
        df = pd.read_csv(csv_url)
        
        print(f"✅ {len(df)} artículos encontrados")
        
        # Buscar específicamente artículos PLoS ONE
        print("\n🔍 Buscando artículos PLoS ONE...")
        
        plos_articles = []
        seen_titles = set()
        
        for _, row in df.iterrows():
            title = str(row.get('Title', ''))
            url = str(row.get('Link', ''))
            
            # Verificar si es PLoS ONE y no duplicado
            if ('pone' in url.lower() or 'plos' in title.lower()) and title not in seen_titles:
                plos_articles.append({'Title': title, 'Link': url})
                seen_titles.add(title)
                
                if len(plos_articles) >= 10:
                    break
        
        if not plos_articles:
            print("⚠️ No se encontraron artículos PLoS ONE específicos")
            print("🔄 Usando primeros artículos disponibles...")
            plos_articles = df.head(10).to_dict('records')
        
        print(f"\n📋 Procesando {len(plos_articles)} artículos:")
        for i, article in enumerate(plos_articles):
            print(f"   {i+1:2d}. {article['Title'][:60]}...")
            print(f"       {article['Link']}")
        
        # Procesar artículos
        article_df = pd.DataFrame(plos_articles)
        success_count = process_articles_batch(article_df)
        
        # Mostrar resultados
        print(f"\n🎉 PROCESO COMPLETADO!")
        print("=" * 40)
        print(f"✅ PDFs exitosos: {success_count}")
        print(f"❌ PDFs fallidos: {len(plos_articles) - success_count}")
        print(f"📊 Tasa de éxito: {success_count}/{len(plos_articles)} ({success_count/len(plos_articles)*100:.1f}%)")
        
        # Mostrar archivos creados
        downloads_dir = './downloads_plos'
        if os.path.exists(downloads_dir):
            files = [f for f in os.listdir(downloads_dir) if f.endswith('.pdf')]
            if files:
                print(f"\n📁 ARCHIVOS DESCARGADOS:")
                total_size = 0
                for file in files:
                    filepath = os.path.join(downloads_dir, file)
                    size = os.path.getsize(filepath)
                    total_size += size
                    print(f"   📄 {file}: {size:,} bytes ({size/1024/1024:.2f} MB)")
                
                avg_size = total_size / len(files)
                print(f"\n📏 RESUMEN:")
                print(f"   • Total archivos: {len(files)}")
                print(f"   • Tamaño total: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")
                print(f"   • Tamaño promedio: {avg_size:,} bytes ({avg_size/1024/1024:.2f} MB)")
                
                if avg_size > 1_000:  # >1MB promedio
                    print(f"   🎯 ¡PDFs REALES obtenidos! (Promedio >1MB)")
        
    except Exception as e:
        print(f"❌ Error en proceso: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
