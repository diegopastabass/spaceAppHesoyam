"""
Scraper final que obtiene PDFs reales directamente desde los journals originales.
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

class JournalPubMedScraper:
    """Scraper que obtiene PDFs directamente desde journals originales."""
    
    def __init__(self, download_dir: str = "./downloads_real", delay: float = 2.0):
        """
        Inicializa el scraper.
        
        Args:
            download_dir: Directorio donde guardar los PDFs
            delay: Delay entre requests (segundos)
        """
        self.download_dir = os.path.abspath(download_dir)
        self.delay = delay
        
        # Crear directorio de descargas
        os.makedirs(self.download_dir, exist_ok=True)
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Configurar Session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
        })
        
        # Mapeo de journals a sus métodos de descarga
        self.journal_methods = {
            'journal.pone': self._download_plos_one,
            'journals.plos.org': self._download_plos_one,
            'ijms': self._download_mdpi,
            'cells': self._download_mdpi,
            'brain': self._download_oxford,
            'nature': self._download_nature_direct,
            'springer': self._download_springer_direct,
        }
    
    def _download_plos_one(self, pdf_url: str, filename: str) -> Optional[str]:
        """
        Descarga PDF de PLoS ONE directamente desde journals.plos.org.
        
        Args:
            pdf_url: URL original del PDF en ncbi.nlm.nih.gov
            filename: Nombre del archivo local
            
        Returns:
            Ruta del archivo descargado o None si falló
        """
        try:
            # Extraer PMC ID para construir URL PLoS
            pmc_match = re.search(r'PMC\d+', pdf_url)
            if not pmc_match:
                return None
            
            pmc_id = pmc_match.group()
            
            # Construir URL directa de PLoS ONE
            pois_patterns = [
                f'journal.pone.', 'pone.',
                f'journal.pone.', 'pone.',
            ]
            
            # Buscar patrón pon e.XXXXXXX en la URL PMC
            pdf_match = re.search(r'pone\.(\d+)', pdf_url)
            if pdf_match:
                pone_id = pdf_match.group(1)
                plos_url = f'https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.{pone_id.zfill(7)}&type=printable'
                
                self.logger.info(f"🔄 Descargando PLoS ONE directo: {plos_url}")
                
                response = self.session.get(plos_url, timeout=60)
                response.raise_for_status()
                
                # Verificar que es PDF
                content_type = response.headers.get('content-type', '').lower()
                if 'pdf' not in content_type:
                    self.logger.warning(f"⚠️ URL PLoS no devolvió PDF: {content_type}")
                    return None
                
                filepath = os.path.join(self.download_dir, filename)
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                # Verificar tamaño
                file_size = os.path.getsize(filepath)
                if file_size > 50000:  # Más de 50KB
                    self.logger.info(f"✅ PDF PLoS ONE descargado: {filename} ({file_size:,} bytes)")
                    return filepath
                else:
                    os.remove(filepath)
                    self.logger.warning(f"⚠️ PDF PLoS demasiado pequeño: {file_size} bytes")
                    return None
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error descargando PLoS ONE {pdf_url}: {e}")
            return None
    
    def _download_mdpi(self, pdf_url: str, filename: str) -> Optional[str]:
        """Descarga PDF de journals MDPI."""
        # Implementar descarga para journals MDPI si es necesario
        self.logger.info(f"🔄 Intentando descarga MDPI: {pdf_url}")
        return None
    
    def _download_oxford(self, pdf_url: str, filename: str) -> Optional[str]:
        """Descarga PDF de Oxford journals."""
        self.logger.info(f"🔄 Intentando descarga Oxford: {pdf_url}")
        return None
    
    def _download_nature_direct(self, pdf_url: str, filename: str) -> Optional[str]:
        """Descarga PDF de Nature journals."""
        self.logger.info(f"🔄 Intentando descarga Nature: {pdf_url}")
        return None
    
    def _download_springer_direct(self, pdf_url: str, filename: str) -> Optional[str]:
        """Descarga PDF de Springer journals."""
        self.logger.info(f"🔄 Intentando descarga Springer: {pdf_url}")
        return None
    
    def _detect_journal_type(self, article_url: str) -> str:
        """
        Detecta el tipo de journal para elegir método de descarga.
        
        Args:
            article_url: URL de la página del artículo
            
        Returns:
            Tipo de journal detectado
        """
        text_lower = article_url.lower()
        
        if 'pone' in text_lower or 'plos' in text_lower:
            return 'journal.pone'
        elif 'ijms' in text_lower:
            return 'ijms'
        elif 'cells' in text_lower:
            return 'cells'
        elif 'brain' in text_lower:
            return 'brain'
        elif 'nature' in text_lower:
            return 'nature'
        elif 'springer' in text_lower:
            return 'springer'
        else:
            return 'unknown'
    
    def download_article_pdf_real(self, title: str, url: str) -> Optional[str]:
        """
        Descarga el PDF de un artículo usando el método apropiado para cada journal.
        
        Args:
            title: Título del artículo
            url: URL de la página del artículo
            
        Returns:
            Ruta del archivo descargado exitosamente o None si falló
        """
        try:
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
                file_size = os.path.getsize(filepath)
                if file_size > 50000:  # Probar si es PDF válido
                    self.logger.info(f"📁 PDF válido ya existe: {filename}")
                    return filepath
                else:
                    self.logger.info(f"🗑️ Eliminando PDF inválido existente: {filename}")
                    os.remove(filepath)
            
            # Detectartipo de journal
            journal_type = self._detect_journal_type(url)
            self.logger.info(f"📰 Journal detectado: {journal_type}")
            
            # Intentar obtener URL de PDF desde página PMC
            pdf_url = self._get_pdf_url_from_page(url)
            if not pdf_url:
                self.logger.error(f"❌ No se encontró URL de PDF: {title}")
                return None
            
            # Descargar usando método específico del journal
            if journal_type in self.journal_methods:
                download_method = self.journal_methods[journal_type]
                result_filepath = download_method(pdf_url, filename)
                
                if result_filepath:
                    self.logger.info(f"✅ SUCCESS usando método {journal_type}: {title[:50]}")
                    time.sleep(self.delay)
                    return result_filepath
                else:
                    # Fallback: intentar descarga PMC directa (probablemente falle)
                    self.logger.warning(f"⚠️ Método {journal_type} falló, intentando PMC directo...")
                    return self._download_pmc_fallback(pdf_url, filename, title)
            else:
                # Fallback para journals desconocidos
                self.logger.warning(f"⚠️ Journal desconocido: {journal_type}, usando método PMC")
                return self._download_pmc_fallback(pdf_url, filename, title)
            
        except Exception as e:
            self.logger.error(f"❌ Error descargando artículo {title}: {e}")
            return None
    
    def _get_pdf_url_from_page(self, article_url: str) -> Optional[str]:
        """
        Obtiene la URL del PDF desde la página del artículo.
        
        Args:
            article_url: URL de la página del artículo
            
        Returns:
            URL del PDF o None si no se encuentra
        """
        try:
            self.logger.info(f"🔍 Obteniendo PDF URL desde: {article_url}")
            
            response = self.session.get(article_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar el botón de descarga PDF
            pdf_button = soup.find('a', href=lambda x: x and 'pdf' in x.lower())
            if pdf_button:
                pdf_href = pdf_button.get('href')
                if pdf_href:
                    pdf_url = urljoin(article_url, pdf_href)
                    self.logger.info(f"✅ PDF URL encontrada: {pdf_url}")
                    return pdf_url
            
            # Método alternativo: construcción manual
            pmc_match = re.search(r'PMC\d+', article_url)
            if pmc_match:
                pmc_id = pmc_match.group()
                pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/pdf/"
                self.logger.info(f"✅ PDF URL construida: {pdf_url}")
                return pdf_url
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo PDF URL desde {article_url}: {e}")
            return None
    
    def _download_pmc_fallback(self, pdf_url: str, filename: str, title: str) -> Optional[str]:
        """
        Método de fallback usando descarga PMC directa.
        
        Args:
            pdf_url: URL del PDF
            filename: Nombre del archivo
            title: Título del artículo
            
        Returns:
            Ruta del archivo o None si falló
        """
        try:
            self.logger.info(f"📥 Descarga PMC fallback: {pdf_url}")
            
            response = self.session.get(pdf_url, timeout=60, stream=True)
            response.raise_for_status()
            
            filepath = os.path.join(self.download_dir, filename)
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Validar archivo
            file_size = os.path.getsize(filepath)
            
            with open(filepath, 'rb') as f:
                header = f.read(10)
                is_valid_header = header.startswith(b'%PDF')
            
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content_sample = f.read(500)
                is_not_html = '<html>' not in content_sample.lower() and 'preparing to download' not in content_sample.lower()
            
            if file_size > 50000 and is_valid_header and is_not_html:
                self.logger.info(f"✅ PDF PMC válido descargado: {filename} ({file_size:,} bytes)")
                return filepath
            else:
                self.logger.warning(f"⚠️ PDF PMC inválido (fallback): tamaño={file_size}, header={'PDF' if is_valid_header else 'NO'}, html={'NO' if is_not_html else 'SÍ'}")
                os.remove(filepath)
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error descarga PMC fallback {pdf_url}: {e}")
            return None
    
    def download_multiple_real(self, articles_df: pd.DataFrame, max_articles: Optional[int] = None) -> List[str]:
        """
        Descarga múltiples PDFs usando métodos específicos de cada journal.
        
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
        
        self.logger.info(f"🚀 Iniciando descarga REAL de {len(articles_df)} artículos...")
        
        for idx, row in articles_df.iterrows():
            try:
                title = row['Title']
                url = row['Link']
                
                self.logger.info(f"📄 Descargando artículo {idx+1}/{len(articles_df)}: {title[:50]}...")
                
                filepath = self.download_article_pdf_real(title, url)
                if filepath:
                    downloaded_files.append(filepath)
                    self.logger.info(f"✅ ÉXITO: {title[:50]} - {os.path.getsize(filepath):,} bytes")
                else:
                    failed_downloads.append(title)
                    self.logger.error(f"❌ FALLÓ: {title[:50]}")
                
            except Exception as e:
                self.logger.error(f"❌ Error procesando artículo {idx+1}: {e}")
                continue
        
        # Resumen final
        self.logger.info(f"🏁 DESCARGA REAL COMPLETADA:")
        self.logger.info(f"   ✅ PDFs válidos descargados: {len(downloaded_files)}")
        self.logger.info(f"   ❌ Descargas fallidas: {len(failed_downloads)}")
        self.logger.info(f"   📊 Tasa de éxito: {len(downloaded_files)}/{len(articles_df)} ({len(downloaded_files)/len(articles_df)*100:.1f}%)")
        
        # Mostrar detalles de archivos descargados
        if downloaded_files:
            total_size = sum(os.path.getsize(f) for f in downloaded_files)
            avg_size = total_size / len(downloaded_files)
            self.logger.info(f"   📏 Tamaño total: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")
            self.logger.info(f"   📏 Tamaño promedio: {avg_size:,} bytes ({avg_size/1024:.1f} KB)")
        
        return downloaded_files

if __name__ == "__main__":
    # Test del scraper de journals
    scraper = JournalPubMedScraper(download_dir="./downloads_real", delay=2.0)
    
    try:
        # Crear DataFrame de prueba
        test_df = pd.DataFrame([
            { 'Title': 'Mice in Bion-M 1 space mission: training and selection', 
              'Link': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4136787/' },
            { 'Title': 'Microgravity induces pelvic bone loss through osteoclastic activity',
              'Link': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3630201/' }
        ])
        
        files = scraper.download_multiple_real(test_df, max_articles=2)
        
        if files:
            print(f"✅ ¡Test exitoso! PDFs reales:")
            for filepath in files:
                size = os.path.getsize(filepath)
                print(f"   📄 {filepath}: {size:,} bytes ({size/1024/1024:.2f} MB)")
        else:
            print(f"❌ Test falló - no se pudieron obtener PDFs reales")
            
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()
