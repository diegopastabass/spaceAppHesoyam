"""
Ejemplo de análisis de los archivos Markdown generados usando IA.
"""
import os
import glob
import pandas as pd
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarkdownAnalyzer:
    """Analizador de archivos Markdown para extraer insights."""
    
    def __init__(self, markdown_dir: str = "./markdown_output"):
        """
        Inicializa el analizador.
        
        Args:
            markdown_dir: Directorio con archivos Markdown
        """
        self.markdown_dir = markdown_dir
        
    def get_all_markdown_files(self) -> List[str]:
        """Obtiene todos los archivos Markdown del directorio."""
        pattern = os.path.join(self.markdown_dir, "*.md")
        return glob.glob(pattern)
    
    def read_markdown_file(self, filepath: str) -> Dict[str, str]:
        """
        Lee un archivo Markdown y extrae sus secciones.
        
        Args:
            filepath: Ruta al archivo Markdown
            
        Returns:
            Diccionario con secciones del artículo
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Dividir en secciones usando los headers
            sections = {}
            current_section = "intro"
            current_content = []
            
            for line in content.split('\n'):
                if line.startswith('## '):
                    if current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = line[3:].lower().replace(' ', '_')
                    current_content = []
                else:
                    current_content.append(line)
            
            if current_content:
                sections[current_section] = '\n'.join(current_content).strip()
            
            sections['filename'] = os.path.basename(filepath)
            sections['full_content'] = content
            
            return sections
            
        except Exception as e:
            logger.error(f"Error leyendo {filepath}: {e}")
            return {}
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        Extrae palabras clave científicas del texto.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Lista de palabras clave
        """
        scientific_terms = [
            'microgravity', 'space', 'astronaut', 'biomedical', 'physiology',
            'bone', 'muscle', 'cardiovascular', 'radiation', 'immune',
            'metabolism', 'neural', 'stress', 'adaptation', 'recovery',
            'tissue', 'cell', 'gene', 'protein', 'mitochondria'
        ]
        
        found_keywords = []
        for term in scientific_terms:
            if term.lower() in text.lower():
                found_keywords.append(term)
        
        return found_keywords
    
    def analyze_all_articles(self) -> pd.DataFrame:
        """
        Analiza todos los archivos Markdown disponibles.
        
        Returns:
            DataFrame con análisis de los artículos
        """
        markdown_files = self.get_all_markdown_files()
        
        if not markdown_files:
            logger.warning("No se encontraron archivos Markdown para analizar")
            return pd.DataFrame()
        
        logger.info(f"📊 Analizando {len(markdown_files)} archivos Markdown...")
        
        analysis_results = []
        
        for filepath in markdown_files:
            try:
                logger.info(f"🔍 Analizando: {os.path.basename(filepath)}")
                
                # Leer contenido del archivo
                article_data = self.read_markdown_file(filepath)
                
                if not article_data:
                    continue
                
                # Extraer información básica
                filename = article_data.get('filename', '')
                
                # Buscar título en el contenido
                title = ""
                full_content = article_data.get('full_content', '').split('\n')
                for line in full_content:
                    if line.startswith('# ') and len(line) < 100:
                        title = line[2:].strip()
                        break
                
                # Extraer palabras clave
                text_to_analyze = ' '.join([
                    article_data.get('abstract', ''),
                    article_data.get('introduction', ''),
                    article_data.get('conclusion', '')
                ])
                
                keywords = self.extract_keywords(text_to_analyze)
                
                # Estadísticas básicas
                total_content_length = len(text_to_analyze)
                
                analysis_results.append({
                    'filename': filename,
                    'title': title[:100] if title else filename,
                    'keywords': ', '.join(keywords),
                    'keyword_count': len(keywords),
                    'content_length': total_content_length,
                    'has_abstract': bool(article_data.get('abstract')),
                    'has_methods': bool(article_data.get('methods')),
                    'has_results': bool(article_data.get('results')),
                    'has_conclusion': bool(article_data.get('conclusion'))
                })
                
            except Exception as e:
                logger.error(f"Error analizando {filepath}: {e}")
                continue
        
        if analysis_results:
            df = pd.DataFrame(analysis_results)
            logger.info(f"✅ Análisis completado de {len(df)} artículos")
            return df
        else:
            logger.warning("No se pudieron analizar artículos")
            return pd.DataFrame()
    
    def generate_summary_report(self, df: pd.DataFrame) -> str:
        """
        Genera un reporte resumen del análisis.
        
        Args:
            df: DataFrame con análisis de artículos
            
        Returns:
            Reporte en formato texto
        """
        if df.empty:
            return "No hay datos para generar reporte"
        
        report = []
        report.append("# Reporte de Análisis de Artículos Científicos")
        report.append("=" * 50)
        report.append("")
        
        # Estadísticas generales
        report.append(f"## Estadísticas Generales")
        report.append(f"- **Total de artículos analizados:** {len(df)}")
        report.append(f"- **Artículos con resumen:** {df['has_abstract'].sum()}")
        report.append(f"- **Artículos con métodos:** {df['has_methods'].sum()}")
        report.append(f"- **Artículos con resultados:** {df['has_results'].sum()}")
        report.append(f"- **Artículos con conclusión:** {df['has_conclusion'].sum()}")
        report.append("")
        
        # Palabras clave más comunes
        all_keywords = []
        for keywords_str in df['keywords']:
            if keywords_str:
                all_keywords.extend([kw.strip() for kw in keywords_str.split(',')])
        
        from collections import Counter
        keyword_counts = Counter(all_keywords)
        common_keywords = keyword_counts.most_common(10)
        
        report.append("## Palabras Clave Más Comunes")
        for keyword, count in common_keywords:
            report.append(f"- **{keyword}:** {count} artículos")
        report.append("")
        
        # Artículos por longitud de contenido
        report.append("## Distribución por Longitud de Contenido")
        length_ranges = pd.cut(df['content_length'], bins=5, labels=['Muy corto', 'Corto', 'Medio', 'Largo', 'Muy largo'])
        length_distribution = length_ranges.value_counts()
        for length_type, count in length_distribution.items():
            report.append(f"- **{length_type}:** {count} artículos")
        report.append("")
        
        # Lista de artículos
        report.append("## Lista de Artículos Analizados")
        for idx, row in df.iterrows():
            report.append(f"{idx+1}. **{row['title']}**")
            report.append(f"   - Archivo: {row['filename']}")
            report.append(f"   - Palabras clave: {row['keywords'] or 'Ninguna'}")
            report.append(f"   - Longitud: {row['content_length']} caracteres")
            report.append("")
        
        return '\n'.join(report)

def main():
    """Función principal del análisis."""
    analyzer = MarkdownAnalyzer()
    
    # Realizar análisis
    logger.info("🔍 Iniciando análisis de archivos Markdown...")
    analysis_df = analyzer.analyze_all_articles()
    
    if not analysis_df.empty:
        # Guardar resultados en CSV
        output_file = "analysis_results.csv"
        analysis_df.to_csv(output_file, index=False)
        logger.info(f"📊 Resultados guardados en: {output_file}")
        
        # Generar reporte
        report = analyzer.generate_summary_report(analysis_df)
        
        # Guardar reporte
        with open("analysis_report.md", "w", encoding="utf-8") as f:
            f.write(report)
        
        logger.info("📄 Reporte guardado en: analysis_report.md")
        
        # Mostrar resumen en consola
        print("\n" + "="*50)
        print("📊 RESUMEN DEL ANÁLISIS")
        print("="*50)
        print(f"Total de artículos analizados: {len(analysis_df)}")
        print(f"Artículos con resumen: {analysis_df['has_abstract'].sum()}")
        print(f"Archivo de resultados: {output_file}")
        print(f"Reporte completo: analysis_report.md")
        
    else:
        logger.error("❌ No se pudieron analizar artículos. ¿Ejecutaste primero el scraper?")

if __name__ == "__main__":
    main()
