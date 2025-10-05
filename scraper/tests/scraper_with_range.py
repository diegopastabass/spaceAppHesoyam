#!/usr/bin/env python3
"""
Scraper configurable con rango de artículos seleccionable.
"""
import requests
import os
import pandas as pd
import re
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# 🔧 CONFIGURACIÓN DE RANGO - MODIFICA ESTOS VALORES
# ============================================================================
START_INDEX = 5   # Artículo inicial (1 = primer artículo)
END_INDEX = 10      # Artículo final (10 = décimo artículo)
# ============================================================================

def validate_range_configuration():
    """Valida la configuración del rango."""
    if START_INDEX < 1:
        raise ValueError("❌ START_INDEX debe ser >= 1")
    
    if END_INDEX < START_INDEX:
        raise ValueError("❌ END_INDEX debe ser >= START_INDEX")
    
    if END_INDEX - START_INDEX > 50:
        logger.warning(f"⚠️ Rango muy grande: {END_INDEX - START_INDEX + 1} artículos")
    
    logger.info(f"📋 Configuración del rango:")
    logger.info(f"   • Artículo inicial: {START_INDEX}")
    logger.info(f"   • Artículo final: {END_INDEX}")
    logger.info(f"   • Total artículos: {END_INDEX - START_INDEX + 1}")

def get_doi_from_url(url):
    """Extrae DOI de URL PMCID."""
    try:
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
            return None
        
        filepath = os.path.join('downloads_range', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        file_size = os.path.getsize(filepath)
        if file_size > 50000:  # Más de 50KB
            return filepath
        else:
            os.remove(filepath)
            return None
            
    except Exception as e:
        logger.error(f"❌ Error descargando PDF PLoS: {e}")
        return None

def get_subset_articles():
    """Obtiene subconjunto de artículos según el rango configurado."""
    try:
        logger.info(f"📊 Cargando datos desde CSV completo...")
        
        csv_url = "https://raw.githubusercontent.com/jgalazka/SB_publications/main/SB_publication_PMC.csv"
        df = pd.read_csv(csv_url)
        
        logger.info(f"✅ CSV cargado: {len(df)} artículos disponibles")
        
        # Validar que el rango es válido
        max_end = min(END_INDEX, len(df))
        if END_INDEX > len(df):
            logger.warning(f"⚠️ END_INDEX ({END_INDEX}) excede el total de artículos ({len(df)})")
            logger.info(f"🔧 Usando END_INDEX ajustado: {max_end}")
        
        # Extraer subconjunto según el rango (pandas usa indexación base 0)
        subset_df = df.iloc[START_INDEX-1:max_end].copy()
        
        logger.info(f"📋 Subconjunto seleccionado:")
        logger.info(f"   • Filas {START_INDEX} a {END_INDEX}")
        logger.info(f"   • Total artículos: {len(subset_df)}")
        
        # Mostrar lista de artículos seleccionados
        logger.info(f"\n📋 ARTÍCULOS SELECCIONADOS:")
        for idx, (_, row) in enumerate(subset_df.iterrows()):
            global_idx = START_INDEX + idx
            title = str(row.get('Title', ''))[:60]
            url = str(row.get('Link', ''))
            logger.info(f"   #{global_idx:3d}. {title}...")
            logger.info(f"        {url}")
        
        return subset_df
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo subconjunto de artículos: {e}")
        return pd.DataFrame()

def process_articles_range(article_df):
    """Procesa el rango específico de artículos."""
    success_count = 0
    total_articles = len(article_df)
    
    logger.info(f"\n🚀 PROCESANDO RANGO CONFIGURADO:")
    logger.info(f"   • Artículos a procesar: {total_articles}")
    logger.info(f"   • Rango: {START_INDEX} a {END_INDEX}")
    
    for idx, (_, row) in enumerate(article_df.iterrows()):
        global_idx = START_INDEX + idx
        title = row['Title']
        url = row['Link']
        
        logger.info(f"\n📄 Procesando artículo #{global_idx}/{END_INDEX}: {title[:60]}...")
        
        # Crear nombre de archivo
        pmc_match = re.search(r'PMC\d+', url)
        pmc_id = pmc_match.group() if pmc_match else f"PMC{global_idx}"
        
        safe_title = re.sub(r'[^\w\s-]', '', title.replace(' ', '-')[:50])
        filename = f"{global_idx:03d}-{pmc_id}-{safe_title}.pdf"
        
        # Intentar descarga PDF
        pdf_downloaded = False
        
        # Método 1: Extraer DOI y construir URL PLoS
        doi = get_doi_from_url(url)
        if doi:
            plos_url = construct_plos_url(doi)
            if plos_url:
                logger.info(f"🔗 Probando método PLoS ONE: {plos_url}")
                filepath = download_plos_pdf(plos_url, filename)
                if filepath:
                    pdf_downloaded = True
                    success_count += 1
                    logger.info(f"✅ ÉXITO método PLoS: #{global_idx}")
        
        # Método 2: Detectar PLoS ONE directo en URL
        if not pdf_downloaded and 'pone' in url.lower():
            logger.info(f"🔗 Probando detección directa PLoS ONE...")
            pone_match = re.search(r'pone\.(\d+)', url)
            if pone_match:
                pone_id = pone_match.group(1).zfill(7)
                plos_url = f'https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.{pone_id}&type=printable'
                logger.info(f"🔗 URL PLoS construida: {plos_url}")
                filepath = download_plos_pdf(plos_url, filename)
                if filepath:
                    pdf_downloaded = True
                    success_count += 1
                    logger.info(f"✅ ÉXITO método directo: #{global_idx}")
        
        if not pdf_downloaded:
            logger.warning(f"❌ FALLÓ documento #{global_idx}: {title[:50]}")
    
    return success_count

def show_summary_results(success_count, total_articles):
    """Muestra resumen de resultados."""
    logger.info(f"\n🎉 PROCESO DEL RANGO COMPLETADO!")
    logger.info(f"=" * 50)
    logger.info(f"📊 RESUMEN:")
    logger.info(f"   • Artículos procesados: {total_articles}")
    logger.info(f"   • PDFs exitosos: {success_count}")
    logger.info(f"   • PDFs fallidos: {total_articles - success_count}")
    logger.info(f"   • Tasa de éxito: {success_count}/{total_articles} ({success_count/total_articles*100:.1f}%)")
    
    # Mostrar archivos creados
    downloads_dir = './downloads_range'
    if os.path.exists(downloads_dir):
        files = [f for f in os.listdir(downloads_dir) if f.endswith('.pdf')]
        if files:
            logger.info(f"\n📁 ARCHIVOS DESCARGADOS EN downloads_range/:")
            total_size = 0
            files.sort()  # Ordenar por número de índice
            
            for file in files:
                filepath = os.path.join(downloads_dir, file)
                size = os.path.getsize(filepath)
                total_size += size
                logger.info(f"   📄 {file}: {size:,} bytes ({size/1024/1024:.2f} MB)")
            
            avg_size = total_size / len(files) if files else 0
            logger.info(f"\n📏 ESTADÍSTICAS:")
            logger.info(f"   • Total archivos: {len(files)}")
            logger.info(f"   • Tamaño total: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")
            logger.info(f"   • Tamaño promedio: {avg_size:,} bytes ({avg_size/1024/1024:.2f} MB)")
            
            if avg_size > 1_000_000:  # >1MB promedio
                logger.info(f"   🎯 ¡PDFs REALES obtenidos! (Promedio >1MB)")
            elif avg_size > 500_000:  # >500KB promedio
                logger.info(f"   ✅ Los PDFs parecen válidos (Promedio >500KB)")
            else:
                logger.info(f"   ⚠️ PDFs muy pequeños (Promedio <500KB)")

def main():
    """Función principal."""
    print("🎯 SCRAPER CONFIGURABLE - SELECCIÓN POR RANGO")
    print("=" * 60)
    
    try:
        # Validar configuración
        validate_range_configuration()
        
        # Obtener subconjunto de artículos
        article_df = get_subset_articles()
        
        if article_df.empty:
            logger.error("❌ No se pudieron obtener artículos")
            return
        
        # Procesar artículos del rango
        success_count = process_articles_range(article_df)
        
        # Mostrar resultados
        show_summary_results(success_count, len(article_df))
        
        logger.info(f"\n💡 PARA CAMBIAR EL RANGO:")
        logger.info(f"   Modifica las variables START_INDEX y END_INDEX en el código")
        logger.info(f"   Ejemplo: START_INDEX = 5, END_INDEX = 15 para artículos 5-15")
        
    except Exception as e:
        logger.error(f"❌ Error en proceso: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
