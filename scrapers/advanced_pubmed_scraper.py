"""
Scraper avanzado que simula comportamiento de navegador real para evitar anti-bot.
"""
import requests
import pandas as pd
from bs4 import BeautifulSoup
import os
import time
import logging
from typing import Dict, List, Optional
import re
from urllib.parse import urljoin, urlparse
import json
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class AdvancedPubMedScraper:
    """Scraper avanzado que simula comportamiento de navegador real."""
    
    def __init__(self, download_dir: str = "./downloads", delay: float = 0.1, max_downloads_per_hour: int = 50):
        """
        Inicializa el scraper avanzado.
        
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
        
        # Configurar Session avanzada con retry y comportamiento de navegador real
        self.session = self._create_advanced_session()
    
    def _create_advanced_session(self) -> requests.Session:
        """Crea una sesión avanzada que simula navegador real."""
        
        session = requests.Session()
        
        # Headers realistas de Chrome en Linux
        session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-Ch-Ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Linux"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
        })
        
        # Configurar retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        # Configurar adapter con retry
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _random_delay(self):
        """Agrega delay aleatorio para simular comportamiento humano."""
        delay = self.delay + random.uniform(0.1, 0.5)
        time.sleep(delay)
    
    def _simulate_human_behavior(self):
        """Simula comportamiento humano con headers variables."""
        # Variar headers ligeramente
        accept_languages = [
            'en-US,en;q=0.9',
            'en-US,en;q=0.9,es;q=0.8',
            'en-GB,en-US;q=0.9,en;q=0.8',
            'en-US,en;q=0.9'
        ]
        
        self.session.headers['Accept-Language'] = random.choice(accept_languages)
    
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
    
    def get_pdf_url_from_page_advanced(self, article_url: str) -> Optional[str]:
        """
        Obtiene URL del PDF usando método avanzado que simula navegador real.
        
        Args:
            article_url: URL de la página del artículo
            
        Returns:
            URL del PDF o None si no se encuentra
        """
        try:
            self.logger.info(f"🔍 Analizando página avanzada: {article_url}")
            
            # Simular comportamiento humano
            self._simulate_human_behavior()
            self._random_delay()
            
            # Hacer request inicial a la página principal
            response = self.session.get(article_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Método 1: Buscar directamente el link de PDF
            pdf_links = soup.find_all('a', href=lambda x: x and '.pdf' in x.lower())
            
            for link in pdf_links:
                href = link.get('href')
                if href and any(keyword in href.lower() for keyword in ['pdf', 'download']):
                    pdf_url = urljoin(article_url, href)
                    self.logger.info(f"✅ PDF URL encontrada (método 1): {pdf_url}")
                    return pdf_url
            
            # Método 2: Buscar en scripts JavaScript
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    # Buscar patrones PDF en JavaScript
                    pdf_patterns = [
                        r'https?://[^"\']*\.pdf[^"\']*',
                        r'/pmc/articles/[^"\']*/pdf/[^"\']*\.pdf',
                    ]
                    
                    for pattern in pdf_patterns:
                        matches = re.findall(pattern, script.string)
                        if matches:
                            pdf_url = urljoin(article_url, matches[0])
                            self.logger.info(f"✅ PDF URL encontrada (método 2): {pdf_url}")
                            return pdf_url
            
            # Método 3: Construir URL manualmente basado en PMC ID
            pmc_match = re.search(r'PMC\d+', article_url)
            if pmc_match:
                pmc_id = pmc_match.group()
                
                # Intentar diferentes patrones de URL
                possible_patterns = [
                    f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/pdf/",
                    f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/pdf/main.pdf",
                    f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/pdf/article.pdf",
                ]
                
                for pattern_url in possible_patterns:
                    try:
                        test_response = self.session.get(pattern_url, timeout=10)
                        if test_response.status_code == 200:
                            # Verificar content-type
                            content_type = test_response.headers.get('content-type', '').capitalize()
                            if 'pdf' in content_type.lower():
                                self.logger.info(f"✅ PDF URL encontrada (método 3): {pattern_url}")
                                return pattern_url
                    except:
                        continue
            
            self.logger.warning(f"⚠️ No se encontró URL de PDF válida en: {article_url}")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo PDF URL desde {article_url}: {e}")
            return None
    
    def download_pdf_advanced(self, pdf_url: str, filename: str, article_title: str) -> Optional[str]:
        """
        Descarga PDF usando método avanzado con múltiples técnicas.
        
        Args:
            pdf_url: URL del PDF
            filename: Nombre del archivo local
            article_title: Título del artículo
            
        Returns:
            Ruta del archivo válido o None si falló
        """
        try:
            self.logger.info(f"📥 Descarga avanzada: {pdf_url}")
            
            # Preparar headers específicos para PDF
            pdf_headers = self.session.headers.copy()
            pdf_headers.update({
                'Accept': 'application/pdf,application/octet-stream,*/*;q=0.9',
                'Sec-Fetch-Dest': 'document',
                'Referer': pdf_url.split('/pdf')[0] + '/' if '/pdf' in pdf_url else pdf_url
            })
            
            # Intentar múltiples métodos de descarga
            download_methods = [
                self._download_direct,
                self._download_with_session_page,
                self._download_with_chunked_encoding
            ]
            
            for method in download_methods:
                try:
                    filepath = method(pdf_url, filename, pdf_headers)
                    if filepath and self._validate_pdf_real(filepath):
                        self.logger.info(f"✅ PDF VÁLIDO descargado con método {method.__name__}: {filename}")
                        return filepath
                    elif filepath:
                        # Eliminar archivo inválido
                        os.remove(filepath)
                        self.logger.warning(f"⚠️ PDF inválido eliminado (método {method.__name__})")
                except Exception as e:
                    self.logger.warning(f"⚠️ Método {method.__name__} falló: {e}")
                    continue
            
            self.logger.error(f"❌ Todos los métodos de descarga fallaron: {filename}")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error en descarga avanzada {pdf_url}: {e}")
            return None
    
    def _download_direct(self, pdf_url: str, filename: str, headers: dict) -> Optional[str]:
        """Descarga directa del PDF."""
        response = self.session.get(pdf_url, headers=headers, timeout=60, stream=True)
        response.raise_for_status()
        
        filepath = os.path.join(self.download_dir, filename)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return filepath
    
    def _download_with_session_page(self, pdf_url: str, filename: str, headers: dict) -> Optional[str]:
        """Descarga después de visitar página de sesión."""
        # Visitar página principal primero
        page_url = pdf_url.replace('/pdf', '') if '/pdf' in pdf_url else pdf_url.split('/pdf')[0]
        self.session.get(page_url, timeout=30)
        self._random_delay()
        
        # Luego descargar PDF
        return self._download_direct(pdf_url, filename, headers)
    
    def _download_with_chunked_encoding(self, pdf_url: str, filename: str, headers: dict) -> Optional[str]:
        """Descarga con manejo especial de chunked encoding."""
        headers['Connection'] = 'close'
        response = self.session.get(pdf_url, headers=headers, timeout=60, stream=True)
        response.raise_for_status()
        
        filepath = os.path.join(self.download_dir, filename)
        with open(filepath, 'wb') as f:
            content = response.content
            f.write(content)
        
        return filepath
    
    def _validate_pdf_real(self, filepath: str) -> bool:
        """
        Valida si un archivo es realmente un PDF usando criterios estrictos.
        
        Args:
            filepath: Ruta al archivo
            
        Returns:
            True si es PDF válido
        """
        try:
            file_size = os.path.getsize(filepath)
            
            # Criterio 1: Tamaño mínimo realista (50KB)
            if file_size < 50000:
                return False
            
            # Criterio 2: Header PDF válido
            with open(filepath, 'rb') as f:
                header = f.read(10)
                if not header.startswith(b'%PDF'):
                    return False
            
            # Criterio 3: No debe ser HTML
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content_sample = f.read(500)
                if '<html>' in content_sample.lower() or 'preparing to download' in content_sample.lower():
                    return False
            
            # Criterio 4: Debe tener contenido PDF detectable
            pdf_indicators = ['PDF', '%PDF', 'endobj', 'xref', 'trailer']
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content_full = f.read(10000)
                pdf_count = sum(1 for indicator in pdf_indicators if indicator.lower() in content_full.lower())
                if pdf_count < 2:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def download_multiple_advanced(self, articles_df: pd.DataFrame, max_articles: Optional[int] = None) -> List[str]:
        """
        Descarga múltiples PDFs usando métodos avanzados.
        
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
        
        self.logger.info(f"🚀 Iniciando descarga AVANZADA de {len(articles_df)} artículos...")
        
        for idx, row in articles_df.iterrows():
            try:
                title = row['Title']
                url = row['Link']
                
                self.logger.info(f"📄 Descargando artículo {idx+1}/{len(articles_df)}: {title[:50]}...")
                
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
                
                # Verificar si ya existe un PDF válido
                filepath = os.path.join(self.download_dir, filename)
                if os.path.exists(filepath):
                    if self._validate_pdf_real(filepath):
                        self.logger.info(f"📁 PDF válido ya existe: {filename}")
                        downloaded_files.append(filepath)
                        continue
                    else:
                        self.logger.info(f"🗑️ Eliminando PDF inválido existente: {filename}")
                        os.remove(filepath)
                
                # Obtener URL del PDF usando método avanzado
                pdf_url = self.get_pdf_url_from_page_advanced(url)
                if not pdf_url:
                    self.logger.error(f"❌ No se encontró URL de PDF: {title}")
                    failed_downloads.append(title)
                    continue
                
                # Descargar con método avanzado
                result_filepath = self.download_pdf_advanced(pdf_url, filename, title)
                
                if result_filepath:
                    downloaded_files.append(result_filepath)
                    self.download_count += 1
                    self.logger.info(f"✅ SUCCESS: {title[:50]} - {os.path.getsize(result_filepath):,} bytes")
                else:
                    failed_downloads.append(title)
                    self.logger.error(f"❌ FALLÓ: {title[:50]}")
                
                self._random_delay()
                    
            except Exception as e:
                self.logger.error(f"❌ Error procesando artículo {idx+1}: {e}")
                continue
        
        # Resumen final
        self.logger.info(f"🏁 DESCARGA AVANZADA COMPLETADA:")
        self.logger.info(f"   ✅ PDFs válidos descargados: {len(downloaded_files)}")
        self.logger.info(f"   ❌ Descargas fallidas: {len(failed_downloads)}")
        self.logger.info(f"   📊 Tasa de éxito: {len(downloaded_files)}/{len(articles_df)} ({len(downloaded_files)/len(articles_df)*100:.1f}%)")
        
        return downloaded_files

if __name__ == "__main__":
    # Test del scraper avanzado
    scraper = AdvancedPubMedScraper(download_dir="./downloads_advanced", delay=0.1)
    
    try:
        # Crear DataFrame de prueba
        test_df = pd.DataFrame([
            { 'Title': 'Mice in Bion-M 1 space mission: training and selection', 
              'Link': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4136787/' },
            { 'Title': 'Microgravity induces pelvic bone loss through osteoclastic activity',
              'Link': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3630201/' }
        ])
        
        files = scraper.download_multiple_advanced(test_df, max_articles=2)
        
        if files:
            print(f"✅ ¡Test avanzado exitoso! PDFs válidos:")
            for filepath in files:
                size = os.path.getsize(filepath)
                print(f"   📄 {filepath}: {size:,} bytes")
        else:
            print(f"❌ Test avanzado falló - no se pudieron obtener PDFs válidos")
            
    except Exception as e:
        print(f"❌ Error en test avanzado: {e}")
        import traceback
        traceback.print_exc()
