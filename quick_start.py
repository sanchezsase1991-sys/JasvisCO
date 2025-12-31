#!/usr/bin/env python3
"""
Script de inicio rápido para JarvisCO (sin dependencias pesadas)
Quick start script for JarvisCO (without heavy dependencies)

Este script demuestra el uso básico de JarvisCO sin necesidad de instalar
todas las dependencias pesadas como PyTorch o Transformers.

This script demonstrates basic JarvisCO usage without needing to install
all heavy dependencies like PyTorch or Transformers.
"""

import sys
import argparse
import shutil
from pathlib import Path

def print_banner():
    """Imprime el banner de JarvisCO."""
    banner = """
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║              🤖 JARVISCO - INICIO RÁPIDO 🤖                   ║
    ║              🤖 JARVISCO - QUICK START 🤖                     ║
    ║                                                                ║
    ║        Copilot-Level Code Analysis & Transformation            ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def show_installation_status():
    """Muestra el estado de la instalación."""
    print("\n📊 ESTADO DE INSTALACIÓN / INSTALLATION STATUS")
    print("=" * 70)
    
    try:
        import jarvisco
        print(f"✓ Paquete JarvisCO: Versión {jarvisco.__version__}")
        package_ok = True
    except ImportError:
        print("✗ Paquete JarvisCO: No instalado")
        print("  Ejecuta: pip install -e .")
        package_ok = False
    
    # Check for commands
    commands = ["jarvisco", "jarvisco-server", "jarvisco-agent"]
    commands_ok = True
    
    for cmd in commands:
        cmd_path = shutil.which(cmd)
        if cmd_path:
            print(f"✓ Comando {cmd}: Disponible")
        else:
            print(f"✗ Comando {cmd}: No disponible")
            commands_ok = False
    
    # Check for key dependencies (optional)
    optional_deps = ["transformers", "torch", "fastapi"]
    deps_installed = []
    deps_missing = []
    
    for dep in optional_deps:
        try:
            __import__(dep)
            deps_installed.append(dep)
        except ImportError:
            deps_missing.append(dep)
    
    if deps_installed:
        print(f"\n✓ Dependencias instaladas: {', '.join(deps_installed)}")
    if deps_missing:
        print(f"⚠️  Dependencias pendientes: {', '.join(deps_missing)}")
        print("   Para instalar: pip install -r requirements.txt")
    
    return package_ok and commands_ok

def show_quick_examples():
    """Muestra ejemplos rápidos de uso."""
    print("\n🚀 EJEMPLOS DE USO / USAGE EXAMPLES")
    print("=" * 70)
    
    examples = [
        ("Analizar código", "Analyze code", "jarvisco analyze archivo.py"),
        ("Refactorizar código", "Refactor code", "jarvisco refactor archivo.py --aspect pythonic"),
        ("Transformar con intención", "Transform with intent", 'jarvisco transform archivo.py "Add type hints"'),
        ("Generar documentación", "Generate docs", "jarvisco document archivo.py"),
        ("Iniciar servidor API", "Start API server", "jarvisco-server --port 8000"),
        ("Ver documentación API", "View API docs", "http://localhost:8000/docs"),
    ]
    
    for i, (desc_es, desc_en, cmd) in enumerate(examples, 1):
        print(f"\n{i}. {desc_es} / {desc_en}:")
        print(f"   {cmd}")

def show_documentation():
    """Muestra enlaces a la documentación."""
    print("\n📚 DOCUMENTACIÓN / DOCUMENTATION")
    print("=" * 70)
    
    docs = [
        ("COMO_EJECUTAR.md", "Guía completa en español / Complete Spanish guide"),
        ("README.md", "Documentación general / General documentation"),
        ("RESUMEN_EJECUCION.txt", "Resumen técnico / Technical summary"),
        ("verify_installation.py", "Script de verificación / Verification script"),
    ]
    
    for file, desc in docs:
        status = "✓" if Path(file).exists() else "✗"
        print(f"{status} {file:30s} - {desc}")

def create_example_file():
    """Crea un archivo de ejemplo para probar."""
    print("\n📝 CREANDO ARCHIVO DE EJEMPLO / CREATING EXAMPLE FILE")
    print("=" * 70)
    
    example_code = '''def calcular_suma(a, b):
    """Calcula la suma de dos números."""
    return a + b

def calcular_factorial(n):
    """Calcula el factorial de un número."""
    if n <= 1:
        return 1
    return n * calcular_factorial(n - 1)

if __name__ == "__main__":
    print(f"Suma: {calcular_suma(5, 3)}")
    print(f"Factorial: {calcular_factorial(5)}")
'''
    
    example_file = Path("ejemplo_codigo.py")
    example_file.write_text(example_code)
    
    print(f"✓ Archivo de ejemplo creado: {example_file}")
    print(f"\nContenido:")
    print("-" * 70)
    print(example_code)
    print("-" * 70)
    
    print(f"\nAhora puedes probar:")
    print(f"  jarvisco analyze {example_file}")
    print(f"  jarvisco refactor {example_file} --aspect pythonic")
    print(f"  jarvisco document {example_file}")

def show_next_steps():
    """Muestra los próximos pasos."""
    print("\n🎯 PRÓXIMOS PASOS / NEXT STEPS")
    print("=" * 70)
    
    steps = [
        "1. Si aún no has instalado: pip install -r requirements.txt",
        "2. Verificar instalación: python3 verify_installation.py",
        "3. Crear archivo de prueba: python3 quick_start.py --create-example",
        "4. Probar comandos básicos: jarvisco --help",
        "5. Iniciar servidor API: jarvisco-server --port 8000",
        "6. Explorar documentación API: http://localhost:8000/docs",
        "7. Leer la guía completa: COMO_EJECUTAR.md",
    ]
    
    for step in steps:
        print(f"  {step}")

def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description="Script de inicio rápido para JarvisCO / Quick start script for JarvisCO"
    )
    parser.add_argument(
        "--create-example",
        action="store_true",
        help="Crear un archivo de ejemplo para probar / Create an example file to test"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Solo verificar instalación / Only check installation"
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    if args.check_only:
        status_ok = show_installation_status()
        return 0 if status_ok else 1
    
    show_installation_status()
    
    if args.create_example:
        create_example_file()
    else:
        show_quick_examples()
        show_documentation()
        show_next_steps()
        
        print("\n" + "=" * 70)
        print("Para crear un archivo de ejemplo, ejecuta:")
        print("To create an example file, run:")
        print("  python3 quick_start.py --create-example")
        print("=" * 70 + "\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
