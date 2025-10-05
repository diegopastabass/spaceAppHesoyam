"""
Configuración central del proyecto de scraping.
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Settings:
    """Configuración centralizada del proyecto."""
    
    # URLs y archivos
    CSV_FILE_URL = os.getenv('CSV_FILE_URL', 'https://raw.githubusercontent.com/jgalazka/SB_publications/main/SB_publication_PMC.csv')
    
    # Directorios
    DOWNLOAD_DIR = os.getenv('DOWNLOAD_DIR', './downloads')
    MARKDOWN_OUTPUT_DIR = os.getenv('MARKDOWN_OUTPUT_DIR', './markdown_output')
    LOG_DIR = os.getenv('LOG_DIR', './logs')
    
    # Configuración de scraping
    MAX_DOWNLOADS_PER_HOUR = int(os.getenv('MAX_DOWNLOADS_PER_HOUR', '50'))
    DELAY_BETWEEN_REQUESTS = float(os.getenv('DELAY_BETWEEN_REQUESTS', '2.0'))
    MAX_ARTICLES_TO_DOWNLOAD = int(os.getenv('MAX_ARTICLES_TO_DOWNLOAD', '10'))  # Limitar para testing
    
    # User Agent
    USER_AGENT = os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    # Configuración de logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def create_directories(cls):
        """Crea todos los directorios necesarios."""
        directories = [
            cls.DOWNLOAD_DIR,
            cls.MARKDOWN_OUTPUT_DIR,
            cls.LOG_DIR
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @classmethod
    def get_config_summary(cls) -> dict:
        """Retorna un resumen de la configuración actual."""
        return {
            'csv_url': cls.CSV_FILE_URL,
            'download_dir': cls.DOWNLOAD_DIR,
            'markdown_dir': cls.MARKDOWN_OUTPUT_DIR,
            'max_downloads_per_hour': cls.MAX_DOWNLOADS_PER_HOUR,
            'delay_between_requests': cls.DELAY_BETWEEN_REQUESTS,
            'max_articles': cls.MAX_ARTICLES_TO_DOWNLOAD,
            'log_level': cls.LOG_LEVEL
        }
