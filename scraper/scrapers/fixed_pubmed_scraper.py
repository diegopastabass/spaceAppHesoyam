"""
Versión corregida del scraper de PubMed que detecta correctamente PDFs inválidos.
"""
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import logging
from typing import Dict, List, Optional
import re
from urllib.parse import urljoin, urlparse
import hashlib
import sys
import os
sys.path.append(os.path.dirname(__file__))
from pdf_validator import PDFValidator

class FixedPubMedScraper:
    """Scraper corregido que valida correctamente los PDFs descargados."""
    
    def __init__(self, download_dir: str = "./downloads", delay: float = 2.0, max_downloads_per_hour: int = 50):
        """
        Inicializa el scraper corregido.
        
        Args:
            download_dir: Directorio donde guardar los PDFs
            delay: Delay entre requests (segundos)
            max_downloads_per_hour: Máximo de descargas por hora
        """
        self.download_dir = os.path.abspath(download_dir)
        self.delay = delay
        self.max_downloads_per_hour = max_downloads_per_hour
        self.download_count = 0
        self.start_time = time.time()
        
        # Crear directorio de descargas
        os.makedirs(self.download_dir, exist_ok=True)
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Configurar Session de requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Configurar validador PDF
        self.pdf_validator = PDFValidator()
        self.pdf_validator.setup_logger(self.logger)
        
        # Configurar Selenium WebDriver
        self.driver = None
        self._setup_driver()
    
    def _setup_driver(self):
        """Configura el WebDriver de Selenium."""
        try:
            self.logger.info("🚀 Intentando configurar Chrome WebDriver...")
            
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-web-security')
            
            # Configurar descargas
            prefs = {
                "download.default_directory": self.download_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "plugins.always_open_pdf_externally": True
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                self.logger.info("✅ Chrome WebDriver configurado exitosamente")
            except Exception as chrome_error:
                self.logger.warning(f"⚠️ Chrome WebDriver no disponible: {chrome_error}")
                self.logger.info("🔄 Usando modo fallback sin navegador")
                self.driver = None
            
        except Exception as e:
            self.logger.error(f"❌ Error configurando WebDriver: {e}")
            self.driver = None
    
    def _check_rate_limit(self):
        """Verifica y respeta el rate limiting."""
        current_time = time.time()
        elapsed_hour = (current_time - self.start_time) / 3600
        
        if elapsed_hour >= 1:
            self.download_count = 0
            self.start_time = current_time
        elif self.download_count >= self.max_downloads_per_hour:
            wait_time = 3600 - (current_time - self.start_time)
            self.logger.warning(f"⏰ Rate limit alcanzado. Esperando {wait_time:.0f}s...")
            time.sleep(wait_time)
            self.download_count = 0
            self.start_time = time.time()
    
    def get_pdf_url_from_page(self, article_url: str) -> Optional[str]:
        """
        Obtiene la URL del PDF desde la página del artículo.
        
        Args:
            article_url: URL de la página del artículo
            
        Returns:
            URL del PDF o None si no se encuentra
        """
        try:
            self.logger.info(f"🔍 Analizando página: {article_url}")
            
            response = self.session.get(article_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar el botón de descarga PDF
            pdf_button = soup.find('a', href=lambda x: x and 'pdf' in x.lower())
            if not pdf_button:
                actions_section = soup.find('div', class_='actions')
                if actions_section:
                    pdf_button = actions_section.find('a', href=lambda x: x and 'pdf' in x.lower())
            
            if pdf_button:
                pdf_href = pdf_button.get('href')
                if pdf_href:
                    pdf_url = urljoin(article_url, pdf_href)
                    self.logger.info(f"✅ PDF URL encontrada: {pdf_url}")
                    return pdf_url
            
            # Método alternativo: buscar patrones en el HTML
            pdf_patterns = [
                r'https?://[^"]*\.pdf[^"]*',
                r'pmc\.ncbi\.nlm\.nih\.gov/articles/[^"]*/pdf/[^"]*',
            ]
            
            html_text = str(soup)
            for pattern in pdf_patterns:
                matches = re.findall(pattern, html_text)
                if matches:
                    pdf_url = matches[0]
                    self.logger.info(f"✅ PDF URL encontrada con regex: {pdf_url}")
                    return pdf_url
            
            self.logger.warning(f"⚠️ No se encontró URL de PDF en: {article_url}")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo PDF URL desde {article_url}: {e}")
            return None
    
    def download_pdf_with_validation(self, pdf_url: str, filename: str, article_title: str) -> Optional[str]:
        """
        Descarga PDF y VALIDA que sea realmente un PDF.
        
        Args:
            pdf_url: URL del PDF
            filename: Nombre del archivo local
            article_title: Título del artículo
            
        Returns:
            Ruta del archivo válido o None si falló
        """
        try:
            self.logger.info(f"📥 Descargando con validación estricta: {pdf_url}")
            
            # Descargar archivo
            response = self.session.get(pdf_url, timeout=60, stream=True)
            response.raise_for_status()
            
            filepath = os.path.join(self.download_dir, filename)
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.logger.info(f"📊 Archivo descargado: {os.path.getsize(filepath):,} bytes")
            
            # VALIDA CIÓN ESTRICTA usando nuestro validador
            validation = self.pdf_validator.validate_pdf_file(filepath)
            
            if validation['is_valid_pdf']:
                self.logger.info(f"✅ PDF VÁLIDO confirmado: {filename}")
                return filepath
            else:
                self.logger.error(f"❌ PDF INVÁLIDO detectado: {filename}")
                self.logger.error(f"❌ Razones: {'; '.join(validation['error_messages'])}")
                
                # Eliminar archivo inválido
                os.remove(filepath)
                
                # Intentar con método alternativo si Chrome está disponible
                if self.driver is not None:
                    self.logger.info(f"🔄 Intentando método Chrome para: {article_title}")
                    alternative_filepath = self.download_with_chrome(pdf_url, filename, article_title)
                    if alternative_filepath:
                        return alternative_filepath
                
                return None
            
        except Exception as e:
            self.logger.error(f"❌ Error descargando PDF {pdf_url}: {e}")
            return None
    
    def download_with_chrome(self, pdf_url: str, filename: str, article_title: str) -> Optional[str]:
        """
        Descarga PDF usando Chrome/Selenium para casos complejos.
        
        Args:
            pdf_url: URL del PDF
            filename: Nombre del archivo
            article_title: Título para logging
            
        Returns:
            Ruta del archivo válido o None
        """
        try:
            self.logger.info(f"🌐 Usando Chrome para descarga: {article_title[:50]}...")
            
            # Simular navegación humana
            article_page = pdf_url.replace('/pdf/', '/').strip('.pdf')
            self.driver.get(article_page)
            time.sleep(3)
            
            # Buscar y hacer click en botón PDF
            try:
                pdf_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'pdf')]"))
                )
                pdf_button.click()
                time.sleep(5)
                
                # Verificar descarga
                filepath = os.path.join(self.download_dir, filename)
                if os.path.exists(filepath):
                    validation = self.pdf_validator.validate_pdf_file(filepath)
                    if validation['is_valid_pdf']:
                        self.logger.info(f"✅ PDF válido descargado con Chrome: {filename}")
                        return filepath
                    else:
                        os.remove(filepath)
                        
            except Exception as chrome_error:
                self.logger.warning(f"⚠️ Error con navegador Chrome: {chrome_error}")
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error en descarga con Chrome {article_title}: {e}")
            return None
    
    def download_article_pdf_fixed(self, title: str, url: str) -> Optional[str]:
        """
        Descarga el PDF de un artículo con validación estricta.
        
        Args:
            title: Título del artículo
            url: URL de la página del artículo
            
        Returns:
            Ruta del archivo descargado exitosamente o None si falló
        """
        try:
            self._check_rate_limit()
            
            # Crear nombre de archivo seguro
            safe_title = re.sub(r'[^\w\s-]', '', title.strip())
            safe_title = re.sub(r'[-\s]+', '-', safe_title)[:100]
            
            pmc_id = ""
            if "PMC" in url:
                pmc_match = re.search(r'PMC\d+', url)
                if pmc_match:
                    pmc_id = pmc_match.group()
                    
            filename = f"{pmc_id}-{safe_title}.pdf" if pmc_id else f"{safe_title}.pdf"
            filename = filename.replace(" ", "-")
            
            # Verificar si el archivo ya existe y es válido
            filepath = os.path.join(self.download_dir, filename)
            if os.path.exists(filepath):
                validation = self.pdf_validator.validate_pdf_file(filepath)
                if validation['is_valid_pdf']:
                    self.logger.info(f"📁 PDF válido ya existe: {filename}")
                    return filepath
                else:
                    self.logger.info(f"🗑️ Eliminando PDF inválido existente: {filename}")
                    os.remove(filepath)
            
            # Obtener URL del PDF
            pdf_url = self.get_pdf_url_from_page(url)
            if not pdf_url:
                self.logger.error(f"❌ No se encontró URL de PDF: {title}")
                return None
            
            # Descargar con validación estricta
            result_filepath = self.download_pdf_with_validation(pdf_url, filename, title)
            
            if result_filepath:
                self.download_count += 1
                time.sleep(self.delay)
                return result_filepath
            else:
                self.logger.error(f"❌ Falló descarga con validación: {title}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error descargando artículo {title}: {e}")
            return None
    
    def download_multiple_pdfs_fixed(self, articles_df: pd.DataFrame, max_articles: Optional[int] = None) -> List[str]:
        """
        Descarga múltiples PDFs con validación estricta.
        
        Args:
            articles_df: DataFrame con información de artículos
            max_articles: Máximo número de artículos a descargar
            
        Returns:
            Lista de archivos PDF válidos descargados
        """
        downloaded_files = []
        failed_downloads = []
        
        if max_articles:
            articles_df = articles_df.head(max_articles)
        
        self.logger.info(f"🚀 Iniciando descarga VALIDADA de {len(articles_df)} artículos...")
        
        for idx, row in articles_df.iterrows():
            try:
                title = row['Title']
                url = row['Link']
                
                self.logger.info(f"📄 Descargando artículo {idx+1}/{len(articles_df)}: {title[:50]}...")
                
                filepath = self.download_article_pdf_fixed(title, url)
                if filepath:
                    downloaded_files.append(filepath)
                    self.logger.info(f"✅ ÉXITO: {title[:50]} - {os.path.getsize(filepath):,} bytes")
                else:
                    failed_downloads.append(title)
                    
            except Exception as e:
                self.logger.error(f"❌ Error procesando artículo {idx+1}: {e}")
                continue
        
        # Resumen final
        self.logger.info(f"🏁 DESCARGA COMPLETADA CON VALIDACIÓN:")
        self.logger.info(f"   ✅ PDFs válidos descargados: {len(downloaded_files)}")
        self.logger.info(f"   ❌ Descargas fallidas: {len(failed_downloads)}")
        self.logger.info(f"   📊 Tasa de éxito: {len(downloaded_files)}/{len(articles_df)} ({len(downloaded_files)/len(articles_df)*100:.1f}%)")
        
        return downloaded_files
    
    def cleanup(self):
        """Limpia recursos utilizados."""
        if self.driver:
            self.driver.quit()
            self.logger.info("🌐 WebDriver cerrado")

if __name__ == "__main__":
    # Test del scraper corregido
    scraper = FixedPubMedScraper(download_dir="./downloads_validated", delay=2.0)
    
    try:
        # Crear DataFrame de prueba
        test_df = pd.DataFrame([
            { 'Title': 'Mice in Bion-M 1 space mission: training and selection', 
              'Link': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4136787/' }
        ])
        
        files = scraper.download_multiple_pdfs_fixed(test_df, max_articles=1)
        
        if files:
            print(f"✅ ¡Test exitoso! PDF válido en: {files[0]}")
        else:
            print(f"❌ Test falló - no se pudo obtener PDF válido")
            
    finally:
        scraper.cleanup()
