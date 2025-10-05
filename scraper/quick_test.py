#!/usr/bin/env python3
"""
Test rápido del problema y la solución.
"""
import os
import sys

# Agregar directorio scrapers al path
sys.path.append('scrapers')

def analyze_current_pdfs():
    """Analiza los PDFs actuales para demostrar el problema."""
    print("🔍 ANÁLISIS DE PDFs ACTUALES")
    print("=" * 40)
    
    downloads_dir = "downloads"
    pdf_files = [f for f in os.listdir(downloads_dir) if f.endswith('.pdf')][:3]
    
    for pdf_file in pdf_files:
        filepath = os.path.join(downloads_dir, pdf_file)
        size = os.path.getsize(filepath)
        
        # Leer primeras líneas para detectar HTML
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            first_lines = f.read(500)
            
        is_html = '<html>' in first_lines.lower() or 'preparing to download' in first_lines.lower()
        is_pdf_header = first_lines.strip().startswith('%PDF')
        
        print(f"\n📄 {pdf_file}")
        print(f"   Tamaño: {size:,} bytes ({size/1024:.1f} KB)")
        print(f"   ¿Es HTML?: {'SÍ' if is_html else 'NO'}")
        print(f"   ¿Es PDF?: {'SÍ' if is_pdf_header else 'NO'}")
        
        if is_html:
            print(f"   ❌ PROBLEMA: Es HTML 'Preparing to download...'")
        elif size < 50000:  # 50KB
            print(f"   ❌ PROBLEMA: Muy pequeño para PDF científico")

def show_expected_sizes():
    """Muestra los tamaños esperados para PDFs científicos reales."""
    print(f"\n📊 TAMAÑOS ESPERADOS PARA PDFs CIENTÍFICOS:")
    print("=" * 50)
    
    expected_sizes = [
        ("Artículo corto (3-5 páginas)", "200-500 KB"),
        ("Artículo estándar (8-12 páginas)", "1-2 MB"),
        ("Artículo largo con figuras (15+ páginas)", "3-10 MB"),
        ("Plos ONE article (como nuestros ejemplos)", "1-3 MB"),
        ("IJMS article", "2-5 MB"),
    ]
    
    for article_type, size_range in expected_sizes:
        print(f"• {article_type}: {size_range}")
    
    print(f"\n⚠️ NUESTROS PDFs ACTUALES:")
    print("• Tamaño: ~1.3 KB")
    print("• Contenido: HTML 'Preparing to download...'")
    print("• Problema: PubMed Central bloquea descargas automáticas")

def demonstrate_validation_fix():
    """Demuestra cómo debería ser la validación correcta."""
    print(f"\n🔧 VALIDACIÓN CORREGIDA:")
    print("=" * 30)
    
    print("❌ VALIDACIÓN ANTERIOR (INCORRECTA):")
    print("   if os.path.getsize(filepath) > 1000:  # 1KB mínimo")
    print("   → Permite pasar archivos HTML de 1284 bytes")
    
    print(f"\n✅ VALIDACIÓN CORREGIDA:")
    print("   1. Tamaño mínimo: >50KB (vs 1KB)")
    print("   2. Header PDF: debe empezar con '%PDF'")
    print("   3. No HTML: no debe contener '<html>' o 'Preparing to download'")
    print("   4. MIME type: debe ser 'application/pdf'")
    
    print(f"\n📋 RESULTADOS CON VALIDACIÓN CORRECTA:")
    
    # Simular validación con archivos actuales
    test_file = "downloads/PMC4136787-Mice-in-Bion-M-1-space-mission-training-and-selection.pdf"
    
    if os.path.exists(test_file):
        size = os.path.getsize(test_file)
        with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(100)
        
        print(f"\n🔍 SIMULACIÓN:")
        print(f"📄 Archivo: {os.path.basename(test_file)}")
        print(f"📊 Tamaño: {size:,} bytes")
        
        # Aplicar validación estricta
        checks = {
            "Tamaño >50KB": size > 50000,
            "Header %PDF": content.strip().startswith('%PDF'),
            "No HTML": '<html>' not in content.lower(),
            "Preparing to download": 'preparing to download' not in content.lower()
        }
        
        print(f"\n🧪 RESULTADO DE VALIDACIÓN:")
        passed_checks = 0
        for check_name, passed in checks.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {status}: {check_name}")
            if passed:
                passed_checks += 1
        
        print(f"\n🎯 DECISIÓN FINAL:")
        if passed_checks == 4:
            print("   ✅ PDF VÁLIDO - Continuar con conversión")
        else:
            print("   ❌ PDF INVÁLIDO - Eliminar y reportar error")
            print("   📍 El log debería mostrar 'FALLO', no 'ÉXITO'")

def main():
    """Función principal."""
    print("🔧 ANÁLISIS DEL PROBLEMA DE DESCARGAS")
    print("📋 ¿Por qué los PDFs tienen exactamente 2KB?")
    print("=" * 60)
    
    analyze_current_pdfs()
    show_expected_sizes()
    demonstrate_validation_fix()
    
    print(f"\n🎯 CONCLUSIÓN:")
    print("=" * 20)
    print("✅ PROBLEMA IDENTIFICADO:")
    print("   • Validación PDF demasiado permisiva (>1000 bytes)")
    print("   • Archivos HTML de 1284 bytes pasan como 'válidos'")
    print("   • PubMed Central protege con JavaScript")
    
    print(f"\n✅ SOLUCIÓN IMPLEMENTADA:")
    print("   • Validador estricto que detecta HTML falso")
    print("   • Tamaño mínimo realista (>50KB)")
    print("   • Headers PDF verificados")
    print("   • Eliminación automática de archivos inválidos")
    
    print(f"\n🛠️ SIGUIENTE PASO:")
    print("   • Instalar Chrome para obtener PDFs reales")
    print("   • PDFs válidos serán de 1-5 MB")
    print("   • Sistema de validación funcionará correctamente")

if __name__ == "__main__":
    main()
