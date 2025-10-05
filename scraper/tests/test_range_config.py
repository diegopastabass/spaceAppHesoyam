#!/usr/bin/env python3
"""
Demo del sistema de configuración de rango personalizable.
"""
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def demo_range_usage():
    """Demuestra cómo usar el sistema de rango."""
    print("🔧 SISTEMA DE CONFIGURACIÓN DE RANGO")
    print("=" * 50)
    
    print("\n📋 CONFIGURACIÓN ACTUAL:")
    print("   START_INDEX = 1")
    print("   END_INDEX = 10")
    print("   → Procesará artículos del 1 al 10")
    
    print("\n💡 EJEMPLOS DE CONFIGURACIÓN:")
    examples = [
        {"start": 1, "end": 5, "desc": "Primeros 5 artículos"},
        {"start": 25, "end": 35, "desc": "Artículos del 25 al 35"},
        {"start": 100, "end": 110, "desc": "Artículos del 100 al 110"},
        {"start": 50, "end": 60, "desc": "10 artículos específicos del medio"},
    ]
    
    for i, example in enumerate(examples):
        print(f"\n   📋 Ejemplo {i+1}:")
        print(f"      START_INDEX = {example['start']}")
        print(f"      END_INDEX = {example['end']}")
        print(f"      → {example['desc']}")
        print(f"      → Total: {example['end'] - example['start'] + 1} artículos")
    
    print("\n🎯 CÓMO USAR:")
    print("   1. Abre el archivo: scraper_with_range.py")
    print("   2. Busca las líneas:")
    print("      START_INDEX = ?  # Cambia aquí")
    print("      END_INDEX = ?    # Cambia aquí")
    print("   3. Modifica los valores según necesites")
    print("   4. Ejecuta: python3.10 scraper_with_range.py")
    
    print("\n⚠️ LIMITACIONES:")
    print("   • Los índices son 1-based (1 = primer artículo)")
    print("   • END_INDEX debe ser >= START_INDEX")
    print("   • Máximo recomendado: 50 artículos por ejecución")
    print("   • Solo funciona con PDFs PLoS ONE actualmente")

def test_current_configuration():
    """Prueba la configuración actual del scraper."""
    print("\n🧪 PROBANDO CONFIGURACIÓN ACTUAL:")
    print("=" * 40)
    
    try:
        # Importar el scraper con configuración
        from scraper_with_range import START_INDEX, END_INDEX, validate_range_configuration
        
        print(f"📋 Configuración detectada:")
        print(f"   START: {START_INDEX}")
        print(f"   END: {END_INDEX}")
        
        validate_range_configuration()
        
        print(f"✅ Configuración válida")
        
        # Mostrar qué artículos se procesarán
        import pandas as pd
        csv_url = "https://raw.githubusercontent.com/jgalazka/SB_publications/main/SB_publication_PMC.csv"
        df = pd.read_csv(csv_url)
        
        print(f"\n📊 DATASET COMPLETO:")
        print(f"   Total artículos disponibles: {len(df)}")
        
        subset_size = END_INDEX - START_INDEX + 1
        print(f"\n📋 SUBCONJUNTO SELECCIONADO:")
        print(f"   Artículos: {START_INDEX} a {END_INDEX}")
        print(f"   Cantidad: {subset_size}")
        
        # Mostrar algunos títulos del rango seleccionado
        if END_INDEX <= len(df):
            subset = df.iloc[START_INDEX-1:END_INDEX]
            print(f"\n🔍 TÍTULOS SELECCIONADOS:")
            
            for idx, (_, row) in enumerate(subset.iterrows()):
                global_idx = START_INDEX + idx
                title = str(row.get('Title', ''))[:50]
                print(f"   #{global_idx:3d}. {title}...")
        else:
            print(f"⚠️ END_INDEX ({END_INDEX}) excede datos disponibles ({len(df)})")
        
    except Exception as e:
        print(f"❌ Error probando configuración: {e}")

def main():
    """Función principal de demo."""
    demo_range_usage()
    test_current_configuration()
    
    print(f"\n🚀 PARA EJECUTAR CON CONFIGURACIÓN ACTUAL:")
    print(f"   python3.10 scraper_with_range.py")

if __name__ == "__main__":
    main()
