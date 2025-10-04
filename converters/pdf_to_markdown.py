"""
Conversor de archivos PDF a formato Markdown para análisis posterior.
"""
import PyPDF2
import re
import os
import logging
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
import pandas as pd

class PDFToMarkdownConverter:
    """Conversor especializado para convertir PDFs científicos a Markdown."""
    
    def __init__(self, output_dir: str = "./markdown_output"):
        """
        Inicializa el conversor.
        
        Args:
            output_dir: Directorio donde guardar archivos Markdown
        """
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def extract_text_from_pdf(self, pdf_path: str) -> Dict[str, str]:
        """
        Extrae texto de un archivo PDF.
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Diccionario con contexto del artículo extraído
        """
        try:
            self.logger.info(f"Extrayendo texto de: {pdf_path}")
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = ""
                
                # Extraer texto de todas las páginas
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    text_content += f"\n\n--- PÁGINA {page_num + 1} ---\n\n"
                    text_content += page_text
                
                # Extraer metadatos si están disponibles
                metadata = {}
                if pdf_reader.metadata:
                    metadata = {
                        'title': pdf_reader.metadata.get('/Title', ''),
                        'author': pdf_reader.metadata.get('/Author', ''),
                        'subject': pdf_reader.metadata.get('/Subject', ''),
                        'creator': pdf_reader.metadata.get('/Creator', ''),
                    }
                
                return {
                    'original_text': text_content,
                    'metadata': metadata,
                    'num_pages': len(pdf_reader.pages)
                }
                
        except Exception as e:
            self.logger.error(f"Error extrayendo texto de {pdf_path}: {e}")
            return {
                'original_text': '',
                'metadata': {},
                'num_pages': 0
            }
    
    def clean_text(self, text: str) -> str:
        """
        Limpia y normaliza el texto extraído.
        
        Args:
            text: Texto crudo del PDF
            
        Returns:
            Texto limpio y normalizado
        """
        try:
            # Eliminar caracteres especiales problemáticos
            text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
            
            # Limpiar saltos de línea múltiples
            text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
            
            # Normalizar espacios
            text = re.sub(r'[ \t]+', ' ', text)
            
            # Limpiar caracteres de control
            text = re.sub(r'[\x0c]', '\n', text)
            
            # Limpiar patrones específicos de PDF mal parseado
            text = re.sub(r'\b[A-Z][a-z]+ [A-Z][a-z]+ [A-Z]\b', '', text)  # Patrones de nombres
            text = re.sub(r'\d+\s+PLOS\s+ONE', 'PLOS ONE', text)
            
            return text.strip()
            
        except Exception as e:
            self.logger.error(f"Error limpiando texto: {e}")
            return text
    
    def extract_sections(self, text: str) -> Dict[str, str]:
        """
        Extrae las secciones principales del texto científico.
        
        Args:
            text: Texto del artículo
            
        Returns:
            Diccionario con contenido de cada sección
        """
        sections = {}
        
        # Definir patrones de secciones científicas
        section_patterns = {
            'title': r'(?i)^[A-Z][^.\n]*?(?=\n[A-Z]|\nAbstract|\nIntroduction|\n$|\n[0-9])',
            'abstract': r'(?i)(?:ABSTRACT|Summary)\s*[:\-]?\s*(.*?)(?=\n(?:INTRODUCTION|KEYWORDS|MATERIALS AND METHODS|METHODS|\d|\n[A-Z][^.]*[:\-]))',
            'keywords': r'(?i)(?:KEYWORDS?|KEY\s+WORDS?)\s*[:\-]?\s*(.*?)(?=\n\s*\n|\n(?:INTRODUCTION|MATERIALS AND METHODS|METHODS))',
            'introduction': r'(?i)(?:INTRODUCTION)\s*[:\-]?\s*(.*?)(?=\n(?:MATERIALS AND METHODS|MARKETING|METHODS|\d\.\d|RESULTS))',
            'methods': r'(?i)(?:MATERIALS AND METHODS|METHODS|METHODOLOGY)\s*[:\-]?\s*(.*?)(?=\n(?:RESULTS|FINDINGS|\d\.\d))',
            'results': r'(?i)(?:RESULTS|FINDINGS|DATA)\s*[:\-]?\s*(.*?)(?=\n(?:DISCUSSION|CONCLUSIONS?|\d\.\d))',
            'discussion': r'(?i)(?:DISCUSSION)\s*[:\-]?\s*(.*?)(?=\n(?:CONCLUSIONS?|REFERENCES|\d\.\d|ACKNOWLEDGMENTS?))',
            'conclusion': r'(?i)(?:CONCLUSIONS?|CONCLUSION)\s*[:\-]?\s*(.*?)(?=\n(?:REFERENCES|ACKNOWLEDGMENTS?|\n[A-Z][^.]*[:\-]))',
            'references': r'(?i)(?:REFERENCES|BIBLIOGRAPHY)\s*[:\-]?\s*(.*?)(?=\n\s*\n|\Z)',
            'acknowledgments': r'(?i)(?:ACKNOWLEDGMENTS?|ACKNOWLEDGEMENTS?)\s*[:\-]?\s*(.*?)(?=\n(?:REFERENCES|\n\s*\n|\Z))'
        }
        
        # Intentar extraer cada sección
        for section_name, pattern in section_patterns.items():
            try:
                match = re.search(pattern, text, re.DOTALL | re.MULTILINE)
                if match:
                    content = match.group(1).strip() if match.groups() else match.group(0).strip()
                    if len(content) > 10:  # Solo incluir si tiene contenido significativo
                        sections[section_name] = content
            except Exception as e:
                self.logger.warning(f"Error extrayendo sección {section_name}: {e}")
                continue
        
        return sections
    
    def format_as_markdown(self, title: str, content_data: Dict[str, str], metadata: Dict[str, str]) -> str:
        """
        Formatea el contenido como texto Markdown.
        
        Args:
            title: Título del artículo
            content_data: Datos extraídos del PDF
            metadata: Metadatos del PDF
            
        Returns:
            Texto formateado en Markdown
        """
        try:
            markdown_content = []
            
            # Encabezado con título
            markdown_content.append(f"# {title}\n")
            
            # Metadatos si están disponibles
            if metadata.get('title') and metadata['title'] != title:
                markdown_content.append(f"**Título original:** {metadata['title']}\n")
            if metadata.get('author'):
                markdown_content.append(f"**Autor(es):** {metadata['author']}\n")
            if metadata.get('subject'):
                markdown_content.append(f"**Tema:** {metadata['subject']}\n")
            
            markdown_content.append("---\n")
            
            # Contenido por secciones
            sections = self.extract_sections(content_data['original_text'])
            
            section_order = ['abstract', 'keywords', 'introduction', 'methods', 'results', 
                           'discussion', 'conclusion', 'references', 'acknowledgments']
            
            for section in section_order:
                if section in sections:
                    section_title = section.replace('_', ' ').title()
                    markdown_content.append(f"## {section_title}\n")
                    markdown_content.append(f"{sections[section]}\n\n")
            
            # Si no se extrajeron secciones estructuradas, usar texto completo limpio
            if not sections:
                markdown_content.append("## Contenido Completo\n")
                clean_text = self.clean_text(content_data['original_text'])
                markdown_content.append(f"{clean_text}\n")
            
            # Pie de página con información del documento
            markdown_content.append("---\n")
            markdown_content.append("### Información del Documento\n")
            markdown_content.append(f"- **Páginas:** {content_data['num_pages']}\n")
            markdown_content.append(f"- **Fecha de conversión:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            return '\n'.join(markdown_content)
            
        except Exception as e:
            self.logger.error(f"Error formateando Markdown: {e}")
            return f"# {title}\n\nError procesando el documento: {e}"
    
    def convert_pdf_to_markdown(self, pdf_path: str, custom_title: Optional[str] = None) -> str:
        """
        Convierte un archivo PDF completo a Markdown.
        
        Args:
            pdf_path: Ruta al archivo PDF
            custom_title: Título personalizado (opcional)
            
        Returns:
            Contenido Markdown como string
        """
        try:
            # Obtener título del nombre del archivo si no se proporciona uno
            title = custom_title or os.path.splitext(os.path.basename(pdf_path))[0]
            
            # Extraer contenido del PDF
            pdf_data = self.extract_text_from_pdf(pdf_path)
            
            if not pdf_data['original_text']:
                self.logger.error(f"No se pudo extraer texto de: {pdf_path}")
                return f"# Error\n\nNo se pudo extraer texto del archivo PDF: {pdf_path}"
            
            # Formatear como Markdown
            markdown_content = self.format_as_markdown(title, pdf_data, pdf_data['metadata'])
            
            return markdown_content
            
        except Exception as e:
            self.logger.error(f"Error convirtiendo PDF a Markdown {pdf_path}: {e}")
            return f"# Error\n\nError procesando {pdf_path}: {e}"
    
    def save_markdown(self, markdown_content: str, filename: str) -> str:
        """
        Guarda el contenido Markdown en un archivo.
        
        Args:
            markdown_content: Contenido Markdown
            filename: Nombre del archivo (sin extensión)
            
        Returns:
            Ruta del archivo guardado
        """
        try:
            # Limpiar nombre de archivo
            safe_filename = re.sub(r'[^\w\s-]', '', filename.strip())
            safe_filename = re.sub(r'[-\s]+', '-', safe_filename)
            
            markdown_path = os.path.join(self.output_dir, f"{safe_filename}.md")
            
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            self.logger.info(f"✅ Markdown guardado: {markdown_path}")
            return markdown_path
            
        except Exception as e:
            self.logger.error(f"Error guardando Markdown {filename}: {e}")
            raise
    
    def convert_multiple_pdfs(self, pdf_files: List[str]) -> List[str]:
        """
        Convierte múltiples archivos PDF a Markdown.
        
        Args:
            pdf_files: Lista de rutas a archivos PDF
            
        Returns:
            Lista de archivos Markdown generados
        """
        converted_files = []
        
        self.logger.info(f"🔄 Iniciando conversión de {len(pdf_files)} PDFs...")
        
        for i, pdf_path in enumerate(pdf_files, 1):
            try:
                self.logger.info(f"📄 Convirtiendo {i}/{len(pdf_files)}: {os.path.basename(pdf_path)}")
                
                # Convertir PDF a Markdown
                markdown_content = self.convert_pdf_to_markdown(pdf_path)
                
                # Generar nombre de archivo
                pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
                
                # Guardar archivo Markdown
                markdown_path = self.save_markdown(markdown_content, pdf_name)
                converted_files.append(markdown_path)
                
            except Exception as e:
                self.logger.error(f"Error convirtiendo {pdf_path}: {e}")
                continue
        
        self.logger.info(f"✅ Conversión completada: {len(converted_files)}/{len(pdf_files)} archivos convertidos")
        return converted_files

if __name__ == "__main__":
    # Test del conversor
    converter = PDFToMarkdownConverter()
    
    # Ejemplo de uso
    test_pdf = "./downloads/test-article.pdf"
    if os.path.exists(test_pdf):
        content = converter.convert_pdf_to_markdown(test_pdf)
        output_file = converter.save_markdown(content, "test-converted")
        print(f"✅ Conversión exitosa guardada en: {output_file}")
    else:
        print(f"❌ Archivo de prueba no encontrado: {test_pdf}")
        print("Ejecuta primero el scraper para descargar PDFs")
