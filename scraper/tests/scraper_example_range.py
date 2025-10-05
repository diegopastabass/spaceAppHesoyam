#!/usr/bin/env python3
"""
Ejemplo específico con rango 5-15 para mostrar funcionalidad.
Copia de scraper_with_range.py pero con configuración diferente.
"""
import requests
import os
import pandas as pd
import re
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# 🔧 CONFIGURACIÓN DE RANGO EJEMPLO - ARTÍCULOS 5 A 15
# ============================================================================
START_INDEX = 5     # Comenzar desde artículo número 5
END_INDEX = 15      # Terminar en artículo número 15
# ============================================================================

def test_range_example():
    """Prueba específica con rango de ejemplo."""
    print("🎯 EJEMPLO: RANGO DE ARTÍCULOS 5 A 15")
    print("=" * 50)
    
    try:
        # Cargar datos
        csv_url = "https://raw.githubusercontent.com/jgalazka/SB_publications/main/SB_publication_PMC.csv"
        df = pd.read_csv(csv_url)
        
        print(f"✅ Dataset completo: {len(df)} artículos")
        
        # Ajustar END_INDEX si es necesario
        max_end = min(END_INDEX, len(df))
        
        # Extraer subconjunto
        subset_df = df.iloc[START_INDEX-1:max_end].copy()
        
        print(f"\n📋 SUBCONJUNTO SELECCIONADO:")
        print(f"   • Posición inicial: {START_INDEX}")
        print(f"   • Posición final: {max_end}")
        print(f"   • Artículos totales: {len(subset_df)}")
        
        print(f"\n🔍 ARTÍCULOS EN EL RANGO:")
        for idx, (_, row) in enumerate(subset_df.iterrows()):
            global_idx = START_INDEX + idx
            title = str(row.get('Title', ''))[:60]
            url = str(row.get('Link', ''))
            
            print(f"\n   📄 Artículo #{global_idx}:")
            print(f"      Título: {title}...")
            print(f"      URL: {url}")
            
            # Detectar tipo de journal
            if 'pone' in url.lower():
                print(f"      🟢 Tipo: PLoS ONE (Probable éxito)")
            elif 'ijms' in url.lower():
                print(f"      🟡 Tipo: International Journal of Molecular Sciences")
            elif 'cells' in url.lower():
                print(f"      🟡 Tipo: Cells journal")
            elif 'nature' in url.lower():
                print(f"      🔵 Tipo: Nature journal")
            else:
                print(f"      ⚪ Tipo: Desconocido")
        
        print(f"\n🎯 EJEMPLOS DE CAMBIO:")
        print(f"   Para processar artículos del 20 al 30:")
        print(f"   START_INDEX = 20")
        print(f"   END_INDEX = 30")
        
        print(f"\n   Para processar solo los primeros 3:")
        print(f"   START_INDEX = 1")
        print(f"   END_INDEX = 3")
        
        print(f"\n   Para processar del medio (100-110):")
        print(f"   START_INDEX = 100")
        print(f"   END_INDEX = 110")
        
    except Exception as e:
        print(f"❌ Error en ejemplo: {e}")
        import traceback
        traceback.print_exc()

def create_config_file():
    """Crea archivo de configuración fácil para el usuario."""
    
    config_content = '''#!/usr/bin/env python3
"""
Archivo de configuración para el scraper.
Modifica estos valores según necesites.
"""

# ============================================================================
# 🔧 CONFIGURACIÓN PERSONALIZADA - CAMBIA ESTOS VALORES
# ============================================================================

# Ejemplos comunes:
START_INDEX = 1    # Artículos 1-10
END_INDEX = 10

# START_INDEX = 5   <｜tool▁call▁begin｜># Artículos 5-15  
# END_INDEX = 15

# START_INDEX = 25   # Artículos 25-35
# END_INDEX = 35

# START_INDEX = 100  # Artículos 100-110
# END_INDEX = 110

# ============================================================================
IMPORT_MESSAGE = f"Rango configurado: artículo {START_INDEX} al {END_INDEX}"
print(f"⚙️ {IMPORT_MESSAGE}")
'''
    
    with open('config_range.py', 'w') as f:
        f.write(config_content)
    
    print("📄 Archivo de configuración creado: config_range.py")

if __name__ == "__main__":
    test_range_example()
    create_config_file()
    
    print(f"\n📋 RESUMEN:")
    print(f"   • Tienes {END_INDEX-START_INDEX+1} artículos en el rango")
    print(f"   • Para cambiar: modifica START_INDEX y END_INDEX")
    print(f"   • Todos los números son base 1 (1 = primer artículo)")
