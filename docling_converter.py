#!/usr/bin/env python3
"""
Conversor de documentos a Markdown usando Docling
Soporta PDF, DOCX, PPTX y otros formatos
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional, List
import logging

try:
    from docling.document_converter import DocumentConverter
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import PdfFormatOption
except ImportError:
    print("Error: Docling no está instalado. Instálalo con:")
    print("pip install docling")
    sys.exit(1)

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DoclingConverter:
    """Clase para convertir documentos a Markdown usando Docling"""

    def __init__(self, use_ocr: bool = False):
        """
        Inicializar el conversor

        Args:
            use_ocr: Si usar OCR para PDFs escaneados
        """
        self.use_ocr = use_ocr
        self.converter = None
        self._setup_converter()

    def _setup_converter(self):
        """Configurar el conversor con opciones optimizadas"""
        try:
            # Configurar opciones para PDF
            pdf_options = PdfPipelineOptions()
            pdf_options.do_ocr = self.use_ocr
            pdf_options.do_table_structure = True

            # Crear el conversor con opciones específicas
            format_options = {
                InputFormat.PDF: PdfFormatOption(pipeline_options=pdf_options)
            }

            self.converter = DocumentConverter(format_options=format_options)
            logger.info("Conversor inicializado correctamente")

        except Exception as e:
            logger.error(f"Error al inicializar el conversor: {e}")
            raise

    def convert_file(self, input_path: str, output_path: Optional[str] = None) -> str:
        """
        Convertir un archivo a Markdown

        Args:
            input_path: Ruta del archivo de entrada
            output_path: Ruta del archivo de salida (opcional)

        Returns:
            Ruta del archivo Markdown generado
        """
        input_file = Path(input_path)

        # Verificar que el archivo existe
        if not input_file.exists():
            raise FileNotFoundError(f"El archivo {input_path} no existe")

        # Determinar archivo de salida
        if output_path is None:
            output_path = input_file.with_suffix('.md')

        logger.info(f"Convirtiendo {input_path} a {output_path}")

        try:
            # Convertir el documento
            result = self.converter.convert(input_path)

            # Obtener el contenido en Markdown
            markdown_content = result.document.export_to_markdown()

            # Guardar el archivo
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            logger.info(f"Conversión completada: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error durante la conversión: {e}")
            raise

    def convert_multiple_files(self, input_dir: str, output_dir: Optional[str] = None,
                               file_extensions: List[str] = None) -> List[str]:
        """
        Convertir múltiples archivos de un directorio

        Args:
            input_dir: Directorio con archivos de entrada
            output_dir: Directorio de salida (opcional)
            file_extensions: Extensiones de archivo a procesar

        Returns:
            Lista de archivos convertidos
        """
        if file_extensions is None:
            file_extensions = ['.pdf', '.docx', '.pptx', '.doc', '.ppt']

        input_path = Path(input_dir)
        if not input_path.exists():
            raise FileNotFoundError(f"El directorio {input_dir} no existe")

        # Crear directorio de salida si no existe
        if output_dir is None:
            output_dir = input_path / "markdown_output"

        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        converted_files = []

        # Buscar archivos con las extensiones especificadas
        for ext in file_extensions:
            for file_path in input_path.glob(f"*{ext}"):
                try:
                    output_file = output_path / f"{file_path.stem}.md"
                    result = self.convert_file(str(file_path), str(output_file))
                    converted_files.append(result)
                except Exception as e:
                    logger.error(f"Error convirtiendo {file_path}: {e}")
                    continue

        return converted_files

    def get_supported_formats(self) -> List[str]:
        """Obtener lista de formatos soportados"""
        return ['.pdf', '.docx', '.pptx', '.doc', '.ppt', '.html', '.txt']


def main():
    """Función principal con interfaz de línea de comandos"""
    parser = argparse.ArgumentParser(
        description="Convertir documentos a Markdown usando Docling",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python docling_converter.py documento.pdf
  python docling_converter.py documento.pdf -o salida.md
  python docling_converter.py -d /ruta/documentos/ -od /ruta/salida/
  python docling_converter.py documento.pdf --ocr
        """
    )

    # Argumentos principales
    parser.add_argument('input', nargs='?', help='Archivo de entrada a convertir')
    parser.add_argument('-o', '--output', help='Archivo de salida (opcional)')
    parser.add_argument('-d', '--directory', help='Directorio con archivos a convertir')
    parser.add_argument('-od', '--output-dir', help='Directorio de salida para conversión masiva')
    parser.add_argument('--ocr', action='store_true', help='Usar OCR para PDFs escaneados')
    parser.add_argument('--extensions', nargs='+',
                        default=['.pdf', '.docx', '.pptx', '.doc', '.ppt'],
                        help='Extensiones de archivo a procesar (para conversión masiva)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Mostrar información detallada')

    args = parser.parse_args()

    # Configurar nivel de logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validar argumentos
    if not args.input and not args.directory:
        parser.error("Debe especificar un archivo de entrada o un directorio")

    if args.input and args.directory:
        parser.error("No puede especificar tanto un archivo como un directorio")

    try:
        # Inicializar conversor
        converter = DoclingConverter(use_ocr=args.ocr)

        if args.input:
            # Convertir archivo individual
            result = converter.convert_file(args.input, args.output)
            print(f"✅ Conversión completada: {result}")

        elif args.directory:
            # Convertir múltiples archivos
            results = converter.convert_multiple_files(
                args.directory,
                args.output_dir,
                args.extensions
            )
            print(f"✅ Conversión masiva completada: {len(results)} archivos convertidos")
            for result in results:
                print(f"  - {result}")

        # Mostrar formatos soportados
        if args.verbose:
            print(f"\nFormatos soportados: {', '.join(converter.get_supported_formats())}")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()