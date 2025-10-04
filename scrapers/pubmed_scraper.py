"""
Scraper para descargar PDFs desde PubMed Central.
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

class PubMedScraper:
    """Scraper especializado para descargar PDFs de PubMed Central."""
    
    def __init__(self, download_dir: str = "./downloads", delay: float = 2.0, max_downloads_per_hour: int = 50):
        """
        Inicializa el scraper de PubMed Central.
        
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
        
        # Configurar Selenium WebDriver
        self.driver = None
        self._setup_driver()
    
    def _setup_driver(self):
        """Configura el WebDriver de Selenium."""
        try:
            self.logger.info("Inicializando WebDriver...")
            
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--headless')  # Ejecutar sin interfaz
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--disable-features=VizDisplayCompositor')
            
            # Configurar descargas
            prefs = {
                "download.default_directory": self.download_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,
                "plugins.plugins_disabled": ["Chrome PDF Viewer"],
                "plugins.always_open_pdf_externally": True
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Intentar encontrar ChromeDriver manualmente o usar instancia local
            try:
                # Intentar usar webdriver-manager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                self.logger.info("WebDriver configurado con ChromeDriverManager exitosamente")
            except Exception as chrome_error:
                self.logger.warning(f"ChromeDriverManager falló: {chrome_error}")
                self.logger.info("Intentando método alternativo sin Chrome...")
                
                # Configurar para usar solo requests como fallback
                self.driver = None
                self.logger.warning("WebDriver no disponible - usando solo requests como fallback")
            
        except Exception as e:
            self.logger.error(f"Error configurando WebDriver: {e}")
            self.logger.info("Continuando sin WebDriver - solo utilizará métodos HTTP")
            self.driver = None
    
    def _check_rate_limit(self):
        """Verifica y respeta el rate limiting."""
        current_time = time.time()
        elapsed_hour = (current_time - self.start_time) / 3600
        
        if elapsed_hour >= 1:
            # Reiniciar contador cada hora
            self.download_count = 0
            self.start_time = current_time
        elif self.download_count >= self.max_downloads_per_hour:
            wait_time = 3600 - (current_time - self.start_time)
            self.logger.warning(f"Rate limit alcanzado. Esperando {wait_time:.0f} segundos...")
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
            self.logger.info(f"Obteniendo PDF URL desde: {article_url}")
            
            # Usar requests primero para obtener el HTML
            response = self.session.get(article_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar el botón de descarga PDF
            pdf_button = soup.find('a', href=lambda x: x and 'pdf' in x.lower())
            if not pdf_button:
                # Buscar en el contenido de las acciones
                actions_section = soup.find('div', class_='actions')
                if actions_section:
                    pdf_button = actions_section.find('a', href=lambda x: x and 'pdf' in x.lower())
            
            if pdf_button:
                pdf_href = pdf_button.get('href')
                if pdf_href:
                    # Construir URL completa si es relativa
                    pdf_url = urljoin(article_url, pdf_href)
                    self.logger.info(f"PDF URL encontrada: {pdf_url}")
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
                    self.logger.info(f"PDF URL encontrada con regex: {pdf_url}")
                    return pdf_url
            
            self.logger.warning(f"No se encontró URL de PDF en: {article_url}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error obteniendo PDF URL desde {article_url}: {e}")
            return None
    
    def download_pdf_simple(self, pdf_url: str, filename: str) -> bool:
        """
        Descarga un PDF usando requests (método simple).
        
        Args:
            pdf_url: URL del PDF
            filename: Nombre del archivo local
            
        Returns:
            True si la descarga fue exitosa
        """
        try:
            self.logger.info(f"Descargando PDF simp le: {pdf_url}")
            
            response = self.session.get(pdf_url, timeout=60, stream=True)
            response.raise_for_status()
            
            filepath = os.path.join(self.download_dir, filename)
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verificar que el archivo se descargó correctamente con validación estricta
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                
                # Validación estricta: tamaño, header PDF, no HTML
                is_valid_size = file_size > 50000  # Min 50KB para PDF científico
                
                # Verificar header PDF
                with open(filepath, 'rb') as f:
                    header = f.read(10)
                    is_valid_header = header.startswith(b'%PDF')
                
                # Verificar que NO sea HTML
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content_sample = f.read(500)
                    is_not_html = '<html>' not in content_sample.lower() and 'preparing to download' not in content_sample.lower()
                
                if is_valid_size and is_valid_header and is_not_html:
                    self.logger.info(f"✅ PDF VÁLIDO descargado: {filename} ({file_size:,} bytes)")
                    return True
                else:
                    self.logger.error(f"❌ PDF INVÁLIDO detectado: {filename}")
                    self.logger.error(f"❌ Razones: tamaño={file_size:,} bytes, header={'PDF' if is_valid_header else 'NO_PDF'}, html={'NON_HTML' if is_not_html else 'IS_HTML'}")
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    return False
            else:
                self.logger.error(f"❌ Archivo no creado: {filename}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error descargando PDF simp le {pdf_url}: {e}")
            return False
    
    def download_pdf_selenium(self, article_url: str, filename: str) -> bool:
        """
        Descarga un PDF usando Selenium (método avanzado).
        
        Args:
            article_url: URL de la página del artículo
            filename: Nombre del archivo local
            
        Returns:
            True si la descarga fue exitosa
        """
        try:
            self.logger.info(f"Descargando PDF con Selenium: {article_url}")
            
            # Navegar a la página del artículo
            self.driver.get(article_url)
            time.sleep(3)  # Esperar carga inicial
            
            # Buscar y hacer click en el botón de descarga PDF
            try:
                # Esperar a que aparezca el botón de PDF
                pdf_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'pdf') or contains(text(), 'PDF')]"))
                )
                pdf_button.click()
                
                # Esperar a que se complete la descarga
                time.sleep(5)
                
                # Verificar que el archivo se descargó
                filepath = os.path.join(self.download_dir, filename)
                if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
                    self.logger.info(f"✅ PDF descargado con Selenium: {filename}")
                    return True
                    
            except Exception as click_error:
                self.logger.warning(f"No se pudo hacer click en PDF button: {click_error}")
                
                # Método alternativo: obtener URL directamente
                try:
                    page_source = self.driver.page_source
                    soup = BeautifulSoup(page_source, 'html.parser')
                    pdf_button = soup.find('a', href=lambda x: x and 'pdf' in x.lower())
                    
                    if pdf_button:
                        pdf_url = pdf_button.get('href')
                        pdf_url = urljoin(article_url, pdf_url)
                        return self.download_pdf_simple(pdf_url, filename)
                        
                except Exception as fallback_error:
                    self.logger.error(f"Error en método alternativo: {fallback_error}")
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error descargando PDF con Selenium {article_url}: {e}")
            return False
    
    def download_article_pdf(self, title: str, url: str) -> Optional[str]:
        """
        Descarga el PDF de un artículo específico.
        
        Args:
            title: Título del artículo
            url: URL de la página del artículo
            
        Returns:
            Ruta del archivo descargado o None si falló
        """
        try:
            self._check_rate_limit()
            
            # Crear nombre de archivo seguro
            safe_title = re.sub(r'[^\w\s-]', '', title.strip())
            safe_title = re.sub(r'[-\s]+', '-', safe_title)[:100]  # Limitar longitud
            
            # Obtener ID de PubMed si está disponible
            pmc_id = ""
            if "PMC" in url:
                pmc_match = re.search(r'PMC\d+', url)
                if pmc_match:
                    pmc_id = pmc_match.group()
                    
            filename = f"{pmc_id}-{safe_title}.pdf" if pmc_id else f"{safe_title}.pdf"
            filename = filename.replace(" ", "-")
            
            # Verificar si el archivo ya existe
            filepath = os.path.join(self.download_dir, filename)
            if os.path.exists(filepath):
                self.logger.info(f"📁 Archivo ya existe: {filename}")
                return filepath
            
            # Intentar obtener URL del PDF
            pdf_url = self.get_pdf_url_from_page(url)
            
            # Intentar descarga con diferentes métodos
            download_success = False
            
            if pdf_url:
                # Método 1: Descarga directa
                download_success = self.download_pdf_simple(pdf_url, filename)
            
            if not download_success:
                # Método 2: Selenium
                download_success = self.download_pdf_selenium(url, filename)
            
            if download_success:
                self.download_count += 1
                time.sleep(self.delay)  # Delay entre descargas
                return filepath
            else:
                self.logger.error(f"❌ Falló la descarga de: {title}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error descargando artículo {title}: {e}")
            return None
    
    def download_multiple_pdfs(self, articles_df: pd.DataFrame, max_articles: Optional[int] = None) -> List[str]:
        """
        Descarga múltiples PDFs desde una lista de artículos.
        
        Args:
            articles_df: DataFrame con información de artículos
            max_articles: Máximo número de artículos a descargar
            
        Returns:
            Lista de archivos descargados exitosamente
        """
        downloaded_files = []
        
        if max_articles:
            articles_df = articles_df.head(max_articles)
        
        self.logger.info(f"🚀 Iniciando descarga de {len(articles_df)} artículos...")
        
        for idx, row in articles_df.iterrows():
            try:
                title = row['Title']
                url = row['Link']
                
                self.logger.info(f"📄 Descargando artículo {idx+1}/{len(articles_df)}: {title[:50]}...")
                
                filepath = self.download_article_pdf(title, url)
                if filepath:
                    downloaded_files.append(filepath)
                    
            except Exception as e:
                self.logger.error(f"Error procesando artículo {idx+1}: {e}")
                continue
        
        self.logger.info(f"✅ Descarga completada. {len(downloaded_files)}/{len(articles_df)} archivos descargados")
        return downloaded_files
    
    def cleanup(self):
        """Limpia recursos utilizados."""
        if self.driver:
            self.driver.quit()
            self.logger.info("WebDriver cerrado")

if __name__ == "__main__":
    # Test de la clase
    scraper = PubMedScraper(download_dir="./downloads", delay=2.0)
    
    try:
        # Ejemplo de uso
        test_url = "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4136787/"
        test_title = "Mice in Bion-M 1 space mission: training and selection"
        
        filepath = scraper.download_article_pdf(test_title, test_url)
        if filepath:
            print(f"✅ PDF descargado en: {filepath}")
        else:
            print("❌ Falló la descarga del PDF")
            
    finally:
        scraper.cleanup()
