"""
Validador estricto para verificar si un archivo descargado es realmente un PDF.
"""
import os
import magic
import mimetypes

class PDFValidator:
    """Validador que detecta PDFs reales vs archivos HTML falsos."""
    
    def __init__(self):
        self.logger = None
        
    def setup_logger(self, logger):
        """Configura el logger."""
        self.logger = logger
    
    def validate_pdf_file(self, filepath: str) -> dict:
        """
        Valida si un archivo es realmente un PDF.
        
        Args:
            filepath: Ruta al archivo a validar
            
        Returns:
            Diccionario con resultado de validación detallado
        """
        result = {
            'is_valid_pdf': False,
            'file_exists': False,
            'file_size': 0,
            'size_valid': False,
            'header_valid': False,
            'mime_type_valid': False,
            'is_html': False,
            'error_messages': []
        }
        
        try:
            # 1. Verificar que el archivo existe
            if not os.path.exists(filepath):
                result['error_messages'].append("Archivo no encontrado")
                return result
            
            result['file_exists'] = True
            
            # 2. Obtener tamaño del archivo
            file_size = os.path.getsize(filepath)
            result['file_size'] = file_size
            
            # 3. Validar tamaño mínimo (PDFs científicos deben ser al menos 50KB)
            if file_size < 50000:  # 50KB mínimo
                result['error_messages'].append(f"Archivo muy pequeño ({file_size} bytes). PDFs científicos deben ser >50KB")
            else:
                result['size_valid'] = True
            
            # 4. Verificar header de PDF
            with open(filepath, 'rb') as f:
                header = f.read(10)
                
                if header.startswith(b'%PDF'):
                    result['header_valid'] = True
                    if self.logger:
                        self.logger.info(f"✅ Header PDF válido encontrado")
                else:
                    result['error_messages'].append(f"Header inválido: {header[:10]}")
                    if self.logger:
                        self.logger.warning(f"❌ Header no es PDF: {header[:10]}")
            
            # 5. Verificar que NO sea HTML
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                first_lines = f.read(500)
                
                if '<html>' in first_lines.lower() or 'preparing to download' in first_lines.lower():
                    result['is_html'] = True
                    result['error_messages'].append("Archivo es HTML 'Preparing to download...' no PDF")
                    if self.logger:
                        self.logger.error(f"❌ El archivo es HTML, no PDF")
                else:
                    if self.logger:
                        self.logger.info(f"✅ No hay contenido HTML detectado")
            
            # 6. Verificar MIME type con magic
            try:
                file_mime = magic.from_file(filepath, mime=True)
                if file_mime == 'application/pdf':
                    result['mime_type_valid'] = True
                    if self.logger:
                        self.logger.info(f"✅ MIME type correcto: {file_mime}")
                else:
                    result['error_messages'].append(f"MIME type incorrecto: {file_mime}")
                    if self.logger:
                        self.logger.warning(f"❌ MIME type incorrecto: {file_mime}")
            except Exception:
                # Si magic no funciona, usar método alternativo
                if result['header_valid'] and not result['is_html']:
                    result['mime_type_valid'] = True
            
            # 7. Decisión final
            result['is_valid_pdf'] = (
                result['file_exists'] and
                result['size_valid'] and 
                result['header_valid'] and
                result['mime_type_valid'] and
                not result['is_html']
            )
            
            if result['is_valid_pdf']:
                if self.logger:
                    self.logger.info(f"✅ PDF VÁLIDO verificado: {filepath} ({file_size:,} bytes)")
            else:
                if self.logger:
                    self.logger.error(f"❌ PDF NO VÁLIDO: {'; '.join(result['error_messages'])}")
            
            return result
            
        except Exception as e:
            result['error_messages'].append(f"Error inesperado: {e}")
            if self.logger:
                self.logger.error(f"❌ Error validando PDF {filepath}: {e}")
            return result
    
    def get_expected_pdf_size_estimate(self, article_title: str) -> int:
        """
        Estima el tamaño esperado de un PDF científico basado en el título.
        
        Args:
            article_title: Título del artículo
            
        Returns:
            Tamaño estimado en bytes
        """
        # Títulos científicos normalmente indican artículos largos
        words = len(article_title.split())
        
        # Estimación basada en número de palabras en título
        if words <= 5:
            return 500000  # ~500KB mínimo
        elif words <= 10:
            return 1000000  # ~1MB mínimo  
        elif words <= 15:
            return 1500000  # ~1.5MB mínimo
        else:
            return 2000000  # ~2MB mínimo
    
    def should_retry_download(self, filepath: str, article_title: str) -> bool:
        """
        Determina si debe reintentar la descarga basado en análisis del archivo.
        
        Args:
            filepath: Archivo descargado
            article_title: Título del artículo
            
        Returns:
            True si debe reintentar
        """
        validation = self.validate_pdf_file(filepath)
        
        # Si es HTML o muy pequeño, definitivamente reintentar
        if validation['is_html']:
            return True
        
        if validation['file_size'] < 50000:  # Menos de 50KB
            return True
            
        # Si no pasa validación header o MIME, reintentar
        if not validation['header_valid'] or not validation['mime_type_valid']:
            return True
            
        return False

def test_pdf_validator():
    """Prueba el validador con archivos existentes."""
    validator = PDFValidator()
    
    print("🔍 PROBANDO VALIDADOR DE PDFs:")
    print("=" * 40)
    
    # Probar con todos los archivos descargados
    downloads_dir = "downloads"
    pdf_files = [f for f in os.listdir(downloads_dir) if f.endswith('.pdf')]
    
    invalid_count = 0
    valid_count = 0
    
    for pdf_file in pdf_files[:3]:  # Probar solo los primeros 3
        filepath = os.path.join(downloads_dir, pdf_file)
        print(f"\n📄 Validando: {pdf_file}")
        
        result = validator.validate_pdf_file(filepath)
        
        if result['is_valid_pdf']:
            valid_count += 1
            print(f"✅ VÁLIDO")
        else:
            invalid_count += 1
            print(f"❌ INVÁLIDO: {'; '.join(result['error_messages'])}")
    
    print(f"\n🏁 RESULTADO:")
    print(f"✅ Válidos: {valid_count}")
    print(f"❌ Inválidos: {invalid_count}")
    
    if invalid_count > 0:
        print(f"\n⚠️ Se confirma el problema: Los archivos 'PDF' son en realidad HTML")

if __name__ == "__main__":
    test_pdf_validator()
