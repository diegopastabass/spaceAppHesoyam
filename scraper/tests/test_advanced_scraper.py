#!/usr/bin/env python3
"""
Test del scraper avanzado para obtener PDFs reales.
"""
import sys
import os
import pandas as pd

# Agregar directorio scrapers al path
sys.path.append('scrapers')

from advanced_pubmed_scraper import AdvancedPubMedScraper
from github_scraper import GitHubCSVScraper

def main():
    """Función principal."""
    print("🚀 PROBANDO SCRAPER AVANZADO PARA PDFs REALES")
    print("=" * 60)
    
    try:
        # Paso 1: Obtener datos del CSV
        print("\n📊 Paso 1: Obteniendo datos del CSV...")
        github_scraper = GitHubCSVScraper("https://raw.githubusercontent.com/jgalazka/SB_publications/main/SB_publication_PMC.csv")
        articles_df = github_scraper.scrape()
        
        print(f"✅ {len(articles_df)} artículos encontrados")
        
        # Paso 2: Crear scraper avanzado
        print("\n🔧 Paso 2: Configurando scraper avanzado...")
        scraper = AdvancedPubMedScraper(download_dir="./downloads_real", delay=2.0)
        
        # Paso 3: Procesar primeros 10 artículos
        print("\n📥 Paso 3: Descargando primeros 10 artículos...")
        max_articles = 10
        
        # Mostrar qué artículos vamos a procesar
        print(f"\n📋 ARTÍCULOS A PROCESAR:")
        for i, (_, row) in enumerate(articles_df.head(max_articles).iterrows()):
            print(f"   {i+1}. {row['Title'][:60]}...")
            print(f"      URL: {row['Link']}")
        
        print(f"\n🚀 Iniciando descarga avanzada...")
        files = scraper.download_multiple_advanced(articles_df, max_articles=max_articles)
        
        # Paso 4: Resultados
        print(f"\n📊 RESULTADOS:")
        print("=" * 30)
        
        if files:
            print(f"✅ ¡ÉXITO! {len(files)} PDFs reales descargados:")
            
            total_size = 0
            for filepath in files:
                size = os.path.getsize(filepath)
                total_size += size
                filename = os.path.basename(filepath)
                print(f"   📄 {filename}")
                print(f"      Tamaño: {size:,} bytes ({size/1024:.1f} KB)")
                
                # Verificar contenido
                try:
                    with open(filepath, 'rb') as f:
                        header = f.read(10)
                        if header.startswith(b'%PDF'):
                            print(f"      ✅ Header PDF válido")
                        else:
                            print(f"      ❌ Header inválido: {header}")
                except Exception as e:
                    print(f"      ❌ Error verificando: {e}")
            
            print(f"\n📈 RESUMEN:")
            print(f"   • PDFs válidos: {len(files)}/{max_articles}")
            print(f"   • Tamaño total: {total_size:,} bytes ({total_size/1024:.1f} KB)")
            print(f"   • Tamaño promedio: {total_size/len(files):,} bytes ({total_size/len(files)/1024:.1f} KB)")
            
            if total_size/len(files) > 1000000:  # >1MB promedio
                print(f"   🎯 ¡Los PDFs son REALES! (Promedio >1MB)")
            elif total_size/len(files) > 500000:  # >500KB promedio  
                print(f"   ✅ Los PDFs parecen válidos (Promedio >500KB)")
            else:
                print(f"   ⚠️ PDFs aún muy pequeños (Promedio <500KB)")
        else:
            print(f"❌ No se obtuvieron PDFs válidos")
            print(f"💡 PubMed Central aún está bloqueando las descargas")
            print(f"🔧 Solución definitiva: Instalar Chrome real")
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
