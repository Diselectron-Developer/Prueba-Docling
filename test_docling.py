#!/usr/bin/env python3
"""
Archivo de prueba para usar Docling en PyCharm
"""

import os
from pathlib import Path
from docling_converter import DoclingConverter


def main():
    """Función principal de prueba"""

    # Crear directorios si no existen
    documentos_dir = Path("documentos")
    salida_dir = Path("salida_markdown")

    documentos_dir.mkdir(exist_ok=True)
    salida_dir.mkdir(exist_ok=True)

    # Inicializar el conversor
    converter = DoclingConverter(use_ocr=True)

    # Ejemplo 1: Convertir un archivo específico
    print("=== Ejemplo 1: Convertir archivo específico ===")
    archivo_prueba = "documentos/2507.08075v1.pdf"  # Cambia por tu archivo en una carpeta local



    if os.path.exists(archivo_prueba):
        try:
            resultado = converter.convert_file(archivo_prueba, "salida_markdown/test.md")
            print(f"✅ Archivo convertido: {resultado}")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print(f"⚠️  Archivo no encontrado: {archivo_prueba}")
        print("Coloca un archivo PDF en la carpeta 'documentos' para probar")

    # Ejemplo 2: Convertir múltiples archivos
    print("\n=== Ejemplo 2: Convertir múltiples archivos ===")
    try:
        resultados = converter.convert_multiple_files(
            "documentos",
            "salida_markdown",
            ['.pdf', '.docx', '.pptx','.jpeg']
        )
        print(f"✅ Archivos convertidos: {len(resultados)}")
        for resultado in resultados:
            print(f"  - {resultado}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Ejemplo 3: Mostrar formatos soportados
    print("\n=== Ejemplo 3: Formatos soportados ===")
    formatos = converter.get_supported_formats()
    print(f"Formatos soportados: {', '.join(formatos)}")

    print("\n=== Prueba completada ===")


if __name__ == "__main__":
    main()