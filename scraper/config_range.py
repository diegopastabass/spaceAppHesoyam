#!/usr/bin/env python3
"""
Archivo de configuración para el scraper.
Modifica estos valores según necesites.
"""

# ============================================================================
# 🔧 CONFIGURACIÓN PERSONALIZADA - CAMBIA ESTOS VALORES
# ============================================================================

# Ejemplos comunes:
START_INDEX = 5    # Artículos 1-10
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
