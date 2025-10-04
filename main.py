"""
Aplicación principal para scraping de artículos científicos de PubMed Central.
"""
import sys
import logging
import time
from pathlib import Path

# Agregar directorios al path
sys.path.append(str(Path(__file__).parent))

from scrapers.github_scraper import GitHubCSVScraper
from scrapers.pubmed_scraper import PubMedScraper
from converters.pdf_to_markdown import PDFToMarkdownConverter
from config.settings import Settings

def setup_logging():
    """Configura el sistema de logging."""
    settings = Settings()
    settings.create_directories()
    
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.FileHandler(f'{settings.LOG_DIR}/scraper.log'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def main():
    """Función principal de la aplicación."""
    logger = setup_logging()
    settings = Settings()
    
    try:
        logger.info("🚀 Iniciando aplicación de scraping de artículos científicos...")
        logger.info(f"📋 Configuración: {settings.get_config_summary()}")
        
        # Paso 1: Extraer datos del CSV de GitHub
        logger.info("📊 Paso 1: Obteniendo datos del CSV de GitHub...")
        github_scraper = GitHubCSVScraper(
            csv_url=settings.CSV_FILE_URL,
            delay=settings.DELAY_BETWEEN_REQUESTS
        )
        
        articles_data = github_scraper.scrape()
        logger.info(f"✅ {len(articles_data)} artículos encontrados en el CSV")
        
        # Mostrar muestra de datos
        logger.info("📝 Muestra de artículos:")
        for idx, row in articles_data.head(3).iterrows():
            logger.info(f"   {idx+1}. {row['Title'][:80]}...")
            logger.info(f"      URL: {row['Link']}")
        
        # Paso 2: Descargar PDFs de PubMed Central
        logger.info("📥 Paso 2: Descargando PDFs de PubMed Central...")
        pubmed_scraper = PubMedScraper(
            download_dir=settings.DOWNLOAD_DIR,
            delay=settings.DELAY_BETWEEN_REQUESTS,
            max_downloads_per_hour=settings.MAX_DOWNLOADS_PER_HOUR
        )
        
        # Limitar descargas para testing (configurable)
        articles_to_download = articles_data.head(settings.MAX_ARTICLES_TO_DOWNLOAD)
        logger.info(f"🔄 Descargando máximo {len(articles_to_download)} artículos...")
        
        downloaded_files = pubmed_scraper.download_multiple_pdfs(articles_to_download)
        logger.info(f"✅ {len(downloaded_files)} PDFs descargados exitosamente")
        
        # Limpiar recursos de scraping
        pubmed_scraper.cleanup()
        
        # Paso 3: Convertir PDFs a Markdown
        if downloaded_files:
            logger.info("📄 Paso 3: Convirtiendo PDFs a formato Markdown...")
            
            converter = PDFToMarkdownConverter(output_dir=settings.MARKDOWN_OUTPUT_DIR)
            markdown_files = converter.convert_multiple_pdfs(downloaded_files)
            
            logger.info(f"✅ {len(markdown_files)} archivos Markdown generados")
            
            # Mostrar archivos generados
            logger.info("📁 Archivos Markdown generados:")
            for markdown_file in markdown_files:
                logger.info(f"   • {markdown_file}")
            
            logger.info("🎉 Proceso completado exitosamente!")
            logger.info(f"📊 Resumen:")
            logger.info(f"   • Artículos encontrados: {len(articles_data)}")
            logger.info(f"   • PDFs descargados: {len(downloaded_files)}")
            logger.info(f"   • Markdown generados: {len(markdown_files)}")
            
        else:
            logger.warning("⚠️  No se descargaron PDFs para convertir")
    
    except KeyboardInterrupt:
        logger.info("⏹️  Proceso interrumpido por el usuario")
        return 1
    
    except Exception as e:
        logger.error(f"❌ Error durante la ejecución: {e}")
        logger.exception("Detalle del error:")
        return 1
    
    finally:
        logger.info("🧹 Limpiando recursos...")
    
    return 0

def run_sample_test():
    """Ejecuta una prueba con un pequeño número de artículos."""
    logger = setup_logging()
    settings = Settings()
    
    logger.info("🧪 Ejecutando prueba de muestra...")
    
    try:
        # Configurar para testing con solo 3 artículos
        original_max = settings.MAX_ARTICLES_TO_DOWNLOAD
        settings.MAX_ARTICLES_TO_DOWNLOAD = 3
        
        return main()
        
    except Exception as e:
        logger.error(f"Error en prueba de muestra: {e}")
        return 1
    
    finally:
        settings.MAX_ARTICLES_TO_DOWNLOAD = original_max

if __name__ == "__main__":
    # Verificar argumentos de comandos
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        exit_code = run_sample_test()
    else:
        exit_code = main()
    
    sys.exit(exit_code)
