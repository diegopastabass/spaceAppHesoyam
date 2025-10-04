#!/usr/bin/env python3
"""
Script para obtener los próximos 10 PDFs reales usando el método PLoS ONE funcionar.
"""
import sys
import os
import pandas as pd

# Agregar directorio scrapers al path
sys.path.append('scrapers')

from journal_pubmed_scraper import JournalPubMedScraper
from github_scraper import GitHubCSVScraper

def main():
    """Obtiene los próximos 10 PDFs reales."""
    print("🎯 OBTENIENDO PRÓXIMOS 10 PDFs REALES")
    print("=" * 50)
    
    try:
        # Paso 1: Obtener datos del CSV
        print("\n📊 Paso 1: Obteniendo datos del CSV de GitHub...")
        github_scraper = GitHubCSVScraper("https://raw.githubusercontent.com/jgalazka/SB_publications/main/SB_publication_PMC.csv")
        articles_df = github_scraper.scrape()
        
        print(f"✅ {len(articles_df)} artículos encontrados en total")
        
        # Paso 2: Seleccionar primeros 10 artículos PLoS ONE
        print("\n🔍 Paso 2: Seleccionando artículos PLoS ONE...")
        
        # Buscar artículos que sean de PLoS ONE (típicamente contienen 'pone' en URL)
        plos_articles = []
        for _, row in articles_df.iterrows():
            url = row['Link']
            title = row['Title']
            
            # Detectar si es PLoS ONE
            if 'pone' in url.lower() or 'plos' in url.lower():
                plos_articles.append({'Title': title, 'Link': url})
                if len(plos_articles) >= 10:
                    break
        
        print(f"📋 Encontrados {len(plos_articles)} artículos PLoS ONE")
        
        if not plos_articles:
            print("⚠️ No se encontraron artículos PLoS ONE en los primeros")
            print("🔄 Usando primeros 10 artículos disponibles...")
            test_articles = articles_df.head(10).to_dict('records')
        else:
            test_articles = plos_articles
        
        # Mostrar qué artículos vamos a procesar
        print(f"\n📋 ARTÍCULOS A PROCESAR ({len(test_articles)}):")
        for i, article in enumerate(test_articles):
            title = article['Title']
            url = article['Link']
            journal = 'PLoS ONE' if 'pone' in url.lower() else 'Unknown'
            print(f"   {i+1:2d}. [{journal}] {title[:50]}...")
            print(f"       URL: {url}")
        
        # Paso 3: Crear scraper de journals
        print(f"\n🔧 Paso 3: Configurando scraper de journals...")
        scraper = JournalPubMedScraper(download_dir="./downloads_functional", delay=1.0)
        
        # Convertir a DataFrame para el scraper
        test_df = pd.DataFrame(test_articles)
        
        # Paso 4: Descargar PDFs reales
        print(f"\n🚀 Paso 4: Descargando PDFs usando métodos específicos de journals...")
        files = scraper.download_multiple_real(test_df, max_articles=len(test_df))
        
        # Paso 5: Análisis de resultados
        print(f"\n📊 RESULTADOS FINALES:")
        print("=" * 40)
        
        if files:
            print(f"✅ ¡ÉXITO! {len(files)} PDFs reales descargados:")
            print()
            
            total_size = 0
            valid_count = 0
            
            for filepath in files:
                size = os.path.getsize(filepath)
                total_size += size
                filename = os.path.basename(filepath)
                
                # Verificar si es PDF válido
                try:
                    with open(filepath, 'rb') as f:
                        header = f.read(10)
                        is_valid = header.startswith(b'%PDF')
                        
                    if is_valid:
                        valid_count += 1
                        status = "✅ VÁLIDO"
                    else:
                        status = "❌ INVÁLIDO"
                        
                    print(f"   📄 {filename}")
                    print(f"      {status} - {size:,} bytes ({size/1024/1024:.2f} MB)")
                    
                except Exception as e:
                    print(f"   📄 {filename}")
                    print(f"      ❌ ERROR: {e}")
            
            print(f"\n📈 RESUMEN:")
            print(f"   • PDFs totales descargados: {len(files)}")
            print(f"   • PDFs válidos: {valid_count}")
            print(f"   • Tasa de éxito: {len(files)}/{len(test_articles)} ({len(files)/len(test_articles)*100:.1f}%)")
            print(f"   • Tamaño total: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")
            
            if len(files) > 0:
                avg_size = total_size / len(files)
                print(f"   • Tamaño promedio: {avg_size:,} bytes ({avg_size/1024/1024:.2f} MB)")
                
                if avg_size > 1000000:  # >1MB promedio
                    print(f"   🎯 ¡Los PDFs son REALES! (Promedio >1MB)")
                elif avg_size > 500000:  # >500KB promedio
                    print(f"   ✅ Los PDFs parecen válidos (Promedio >500KB)")
                else:
                    print(f"   ⚠️ PDFs aún muy pequeños (Promedio <500KB)")
            
            print(f"\n💾 Archivos guardados en: ./downloads_functional/")
            
            # Mostrar archivos creados
            if os.path.exists("./downloads_functional"):
                print(f"\n📁 ARCHIVOS EN DOWNLOADS_FUNCTIONAL:")
                for f in os.listdir("./downloads_functional"):
                    if f.endswith('.pdf'):
                        size = os.path.getsize(os.path.join("./downloads_functional", f))
                        print(f"   📄 {f} ({size:,} bytes)")
        
        else:
            print(f"❌ No se obtuvieron PDFs válidos")
            print(f"💡 Esto puede indicar:")
            print(f"   • Los journals bloquearon automáticamente las descargas")
            print(f"   • Se necesita configuración adicional para Chrome")
            print(f"   • Los artículos no son de PLoS ONE")
        
        print(f"\n🎉 PROCESO COMPLETADO")
        
    except Exception as e:
        print(f"❌ Error en proceso: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
