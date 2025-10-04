#!/usr/bin/env python3
"""
Scraper personalizable con configuración de rango fácil.
Modifica START_INDEX y END_INDEX según necesites.
"""
import requests
import os
import pandas as pd
import re
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# 🔧 CONFIGURA TU RANGO AQUÍ - CAMBIA ESTOS VALORES
# ============================================================================
START_INDEX = 1      # Número del artículo inicial (ej: 1 = primer artículo)
END_INDEX = 10       # Número del artículo final (ej: 10 = décimo artículo)
# ============================================================================

def validar_configuracion():
    """Valida que la configuración sea correcta."""
    if START_INDEX < 1:
        raise ValueError("❌ START_INDEX debe ser >= 1")
    if END_INDEX < START_INDEX:
        raise ValueError("❌ END_INDEX debe ser >= START_INDEX")
    
    total_articulos = END_INDEX - START_INDEX + 1
    if total_articulos > 50:
        logger.warning(f"⚠️ Rango grande: {total_articulos} artículos")
    
    logger.info(f"📋 Configuración válida:")
    logger.info(f"   • Artículos: {START_INDEX} a {END_INDEX}")
    logger.info(f"   • Total: {total_articulos} artículos")

def obtener_articulos_rango():
    """Obtiene los artículos del rango especificado."""
    csv_url = "https://raw.githubusercontent.com/jgalazka/SB_publications/main/SB_publication_PMC.csv"
    df = pd.read_csv(csv_url)
    
    logger.info(f"📊 Dataset completo: {len(df)} artículos")
    
    # Ajustar si END_INDEX excede límites
    max_end = min(END_INDEX, len(df))
    if END_INDEX > len(df):
        logger.warning(f"⚠️ Ajustando END_INDEX de {END_INDEX} a {max_end}")
    
    # Extraer subconjunto
    subset = df.iloc[START_INDEX-1:max_end].copy()
    
    logger.info(f"📋 Artículos seleccionados: {len(subset)}")
    
    # Mostrar lista
    logger.info(f"\n📄 LISTA DE ARTÍCULOS:")
    for idx, (_, row) in enumerate(subset.iterrows()):
        global_idx = START_INDEX + idx
        title = str(row.get('Title', ''))[:50]
        url = str(row.get('Link', ''))
        tipo = detectar_tipo_journal(url)
        
        logger.info(f"   #{global_idx:3d}. [{tipo}] {title}...")
    
    return subset

def detectar_tipo_journal(url):
    """Detecta el tipo de journal para mostrar información."""
    if 'pone' in url.lower():
        return "PLoS ONE"
    elif 'ijms' in url.lower():
        return "IJMS"
    elif 'cells' in url.lower():
        return "Cells"
    elif 'nature' in url.lower():
        return "Nature"
    elif 'springer' in url.lower():
        return "Springer"
    else:
        return "Unknown"

def descargar_pdf_real(url, filename):
    """Intenta descargar un PDF real."""
    try:
        # Método 1: Extraer DOI y usar PLoS ONE
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.9'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        content = response.text
        
        # Buscar DOI
        doi_patterns = [
            r'https?://doi\.org/([^\s<>"]+)',
            r'doi:?\s*([^\s<>"]+)',
            r'10\.1371/journal\.pone\.\d+',
        ]
        
        plos_url = None
        for pattern in doi_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if 'pone' in match.lower():
                    pone_match = re.search(r'pone\.(\d+)', match, re.IGNORECASE)
                    if pone_match:
                        pone_id = pone_match.group(1).zfill(7)
                        plos_url = f'https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.{pone_id}&type=printable'
                        break
        
        # Método 2: Construir URL PLoS directamente de PMC ID
        if not plos_url and 'pone' in url.lower():
            pone_match = re.search(r'pone\.(\d+)', url)
            if pone_match:
                pone_id = pone_match.group(1).zfill(7)
                plos_url = f'https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.{pone_id}&type=printable'
        
        if plos_url:
            logger.info(f"🔗 Intentando PLoS: {plos_url}")
            
            response = requests.get(plos_url, timeout=60)
            content_type = response.headers.get('content-type', '').lower()
            
            if 'pdf' in content_type and len(response.content) > 50000:
                filepath = os.path.join('downloads', filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"✅ PDF descargado: {filename} ({len(response.content):,} bytes)")
                return filepath
        
        # Mostrar información detallada cuando falle
        logger.error(f"❌ FALLA EN DESCARGA:")
        logger.error(f"   📄 Archivo: {filename}")
        logger.error(f"   🔗 URL original: {url}")
        if plos_url:
            logger.error(f"   🔗 URL PLoS construida: {plos_url}")
        
        # Analizar tipo de journal
        journal_type = detectar_tipo_journal(url)
        logger.error(f"   📰 Journal: {journal_type}")
        
        # Sugerir métodos alternativos
        logger.error(f"   💡 MÉTODOS ALTERNATIVOS:")
        if 'pone' in url.lower():
            logger.error(f"      → Es PLoS ONE pero falló")
            logger.error(f"      → Verificar disponibilidad manualmente")
            logger.error(f"      → URL directa: {url.replace('/pdf', '/').strip('.pdf')}")
        elif 'ijms' in url.lower():
            logger.error(f"      → International Journal of Molecular Sciences")
            logger.error(f"      → Requiere método MDPI específico")
            logger.error(f"      → URL: https://www.mdpi.com/")
        elif 'cells' in url.lower():
            logger.error(f"      → Cells journal")
            logger.error(f"      → Requiere método MDPI específico")
            logger.error(f"      → URL: https://www.mdpi.com/")
        elif 'nature' in url.lower():
            logger.error(f"      → Nature journal")
            logger.error(f"      → Requiere método Nature específico")
            logger.error(f"      → URL: https://www.nature.com/")
        else:
            logger.error(f"      → Journal desconocido: {journal_type}")
            logger.error(f"      → Requiere investigación manual")
            logger.error(f"      → Verificar disponibilidad del PDF")
        
        return None
        
    except Exception as e:
        logger.error(f"❌ Error descargando: {e}")
        return None

def procesar_articulos():
    """Procesa todos los artículos del rango."""
    try:
        validar_configuracion()
        
        subset_df = obtener_articulos_rango()
        
        logger.info(f"\n🚀 INICIANDO DESCARGA...")
        
        exitos = 0
        fallidos = 0
        
        for idx, (_, row) in enumerate(subset_df.iterrows()):
            global_idx = START_INDEX + idx
            title = row['Title']
            url = row['Link']
            
            logger.info(f"\n📄 Procesando #{global_idx}: {title[:40]}...")
            
            # Crear nombre archivo
            pmc_match = re.search(r'PMC\d+', url)
            pmc_id = pmc_match.group() if pmc_match else f"PMC{global_idx}"
            safe_title = re.sub(r'[^\w\s-]', '', title.replace(' ', '-')[:30])
            filename = f"{global_idx:03d}-{pmc_id}-{safe_title}.pdf"
            
            # Mostrar información del artículo
            logger.info(f"   🔍 Tipo de journal: {detectar_tipo_journal(url)}")
            logger.info(f"   📝 Archivo esperado: {filename}")
            
            # Intentar descarga
            filepath = descargar_pdf_real(url, filename)
            
            if filepath:
                exitos += 1
                logger.info(f"   ✅ RESULTADO: PDF obtenido exitosamente")
            else:
                fallidos += 1
                logger.error(f"   ❌ RESULTADO: Falló descarga - Revisar sugerencias arriba")
        
        # Mostrar resultados
        logger.info(f"\n🎉 PROCESO COMPLETADO!")
        logger.info(f"=" * 40)
        logger.info(f"✅ Exitosos: {exitos}")
        logger.info(f"❌ Fallidos: {fallidos}")
        logger.info(f"📊 Tasa: {exitos}/{len(subset_df)} ({exitos/len(subset_df)*100:.1f}%)")
        
        # Mostrar archivos
        if os.path.exists('downloads'):
            files = [f for f in os.listdir('downloads') if f.endswith('.pdf')]
            if files:
                logger.info(f"\n📁 ARCHIVOS EN downloads/:")
                total_size = 0
                for file in sorted(files):
                    size = os.path.getsize(os.path.join('downloads', file))
                    total_size += size
                    logger.info(f"   📄 {file}: {size:,} bytes ({size/1024/1024:.2f} MB)")
                
                avg_size = total_size / len(files)
                logger.info(f"\n📏 Total: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")
                logger.info(f"📏 Promedio: {avg_size:,} bytes ({avg_size/1024/1024:.2f} MB)")
                
                if avg_size > 1_000_000:
                    logger.info(f"🎯 ¡PDFs REALES obtenidos!")
        
    except Exception as e:
        logger.error(f"❌ Error en proceso: {e}")
        import traceback
        traceback.print_exc()

def mostrar_ejemplos():
    """Muestra ejemplos de diferentes configuraciones."""
    logger.info(f"\n💡 EJEMPLOS DE CONFIGURACIÓN:")
    logger.info(f"   Primeros 5:      START_INDEX = 1,  END_INDEX = 5")
    logger.info(f"   Artículos 10-20: START_INDEX = 10, END_INDEX = 20")
    logger.info(f"   Solo uno:        START_INDEX = 1,  END_INDEX = 1")
    logger.info(f"   Rango medio:     START_INDEX = 50, END_INDEX = 60")
    
    logger.info(f"\n🔧 PARA CAMBIAR:")
    logger.info(f"   1. Modifica START_INDEX y END_INDEX en la línea 12-13")
    logger.info(f"   2. Ejecuta: python3.10 scraper_personalizado.py")

def main():
    """Función principal."""
    print("🎯 SCRAPER PERSONALIZADO - RANGO DE ARTÍCULOS")
    print("=" * 60)
    
    mostrar_ejemplos()
    
    logger.info(f"\n⚙️ CONFIGURACIÓN ACTUAL:")
    logger.info(f"   START_INDEX = {START_INDEX}")
    logger.info(f"   END_INDEX = {END_INDEX}")
    
    confirmar = input(f"\n¿Procesar artículos {START_INDEX} a {END_INDEX}? (y/N): ").lower()
    
    if confirmar in ['y', 'yes', 'si', 's']:
        procesar_articulos()
    else:
        logger.info(f"❌ Proceso cancelado")
        logger.info(f"💡 Modifica START_INDEX y END_INDEX si quieres cambiar el rango")

if __name__ == "__main__":
    main()
