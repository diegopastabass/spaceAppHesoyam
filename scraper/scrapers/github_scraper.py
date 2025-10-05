"""
Scraper para extraer datos del CSV de GitHub con publicaciones científicas.
"""
import requests
import pandas as pd
from io import StringIO
import logging
from typing import List, Dict
from urllib.parse import urlparse
import time

class GitHubCSVScraper:
    """Scraper especializado para obtener datos del CSV de GitHub."""
    
    def __init__(self, csv_url: str, delay: float = 1.0):
        """
        Inicializa el scraper.
        
        Args:
            csv_url: URL del archivo CSV en GitHub
            delay: Delay entre requests (seconds)
        """
        self.csv_url = csv_url
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def get_csv_data(self) -> pd.DataFrame:
        """
        Obtiene y parsea los datos del CSV.
        
        Returns:
            DataFrame con las columnas 'Title' y 'Link'
        """
        try:
            self.logger.info(f"Obteniendo datos de CSV: {self.csv_url}")
            
            # Convertir GitHub blob URL a raw URL directamente
            raw_url = self.csv_url.replace('/blob/', '/raw/')
            
            self.logger.info(f"URL raw: {raw_url}")
            response = self.session.get(raw_url, timeout=30)
            response.raise_for_status()
            
            # Parsear CSV usando pandas
            csv_content = StringIO(response.text)
            df = pd.read_csv(csv_content)
            
            self.logger.info(f"CSV obtenido exitosamente. {len(df)} registros encontrados.")
            
            # Validar estructura esperada
            required_columns = ['Title', 'Link']
            if not all(col in df.columns for col in required_columns):
                self.logger.warning(f"Columnas esperadas: {required_columns}")
                self.logger.warning(f"Columnas encontradas: {list(df.columns)}")
                # Intentar mapear columnas similares
                if 'title' in df.columns:
                    df = df.rename(columns={'title': 'Title'})
                if 'link' in df.columns or 'url' in df.columns or 'links' in df.columns:
                    link_col = 'link' if 'link' in df.columns else 'url' if 'url' in df.columns else 'links'
                    df = df.rename(columns={link_col: 'Link'})
            
            # Limpiar datos
            df = df.dropna(subset=['Title', 'Link'])
            df = df.reset_index(drop=True)
            
            self.logger.info(f"CSV procesado: {len(df)} registros válidos")
            return df
            
        except requests.RequestException as e:
            self.logger.error(f"Error de conexión: {e}")
            raise
        except pd.errors.EmptyDataError:
            self.logger.error("El CSV está vacío o es inválido")
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado: {e}")
            raise
    
    def validate_links(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Valida que los enlaces sean válidos y de PubMed Central.
        
        Args:
            df: DataFrame con datos del CSV
            
        Returns:
            DataFrame filtrado con enlaces válidos
        """
        valid_entries = []
        
        for idx, row in df.iterrows():
            try:
                link = row['Link'].strip()
                parsed_url = urlparse(link)
                
                # Validar que sea de PubMed Central
                if 'ncbi.nlm.nih.gov/pmc/articles' in link:
                    valid_entries.append({
                        'Title': row['Title'].strip(),
                        'Link': link,
                        'PMC_ID': link.split('/')[-1].rstrip('/')
                    })
                else:
                    self.logger.warning(f"Enlace no válido para PMC: {link}")
                    
            except Exception as e:
                self.logger.error(f"Error validando enlace {idx}: {e}")
                continue
        
        result_df = pd.DataFrame(valid_entries)
        self.logger.info(f"Validación completada: {len(result_df)}/{len(df)} enlaces válidos")
        return result_df
    
    def scrape(self) -> pd.DataFrame:
        """
        Método principal para realizar el scraping completo.
        
        Returns:
            DataFrame con datos validados del CSV
        """
        try:
            df = self.get_csv_data()
            df_validated = self.validate_links(df)
            
            if len(df_validated) == 0:
                raise ValueError("No se encontraron enlaces válidos de PubMed Central")
            
            return df_validated
            
        except Exception as e:
            self.logger.error(f"Error en scraping de GitHub: {e}")
            raise

if __name__ == "__main__":
    # Test del scraper
    scraper = GitHubCSVScraper(
        csv_url="https://raw.githubusercontent.com/jgalazka/SB_publications/main/SB_publication_PMC.csv",
        delay=1.0
    )
    
    try:
        data = scraper.scrape()
        print(f"✅ Scraping exitoso:")
        print(f"📊 Total de artículos: {len(data)}")
        print(f"📝 Primeros títulos:")
        for idx, row in data.head(3).iterrows():
            print(f"   {idx+1}. {row['Title']}")
    except Exception as e:
        print(f"❌ Error: {e}")
