#!/usr/bin/env python3
"""
Script de verificación de instalación de JarvisCO
Verification script for JarvisCO installation

Este script verifica que JarvisCO esté correctamente instalado.
This script verifies that JarvisCO is correctly installed.
"""

import sys
import subprocess
from pathlib import Path

def print_header(text):
    """Imprime un encabezado formateado."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")

def check_python_version():
    """Verifica la versión de Python."""
    print_header("1. Verificando versión de Python / Checking Python version")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("✓ Python 3.8+ detectado")
        return True
    else:
        print("✗ Se requiere Python 3.8 o superior")
        return False

def check_package_installed():
    """Verifica que el paquete JarvisCO esté instalado."""
    print_header("2. Verificando instalación del paquete / Checking package installation")
    
    try:
        import jarvisco
        print(f"✓ JarvisCO instalado - Versión: {jarvisco.__version__}")
        return True
    except ImportError as e:
        print(f"✗ JarvisCO no está instalado: {e}")
        print("\nPara instalar, ejecuta / To install, run:")
        print("  pip install -e .")
        return False

def check_commands():
    """Verifica que los comandos estén disponibles."""
    print_header("3. Verificando comandos disponibles / Checking available commands")
    
    commands = ["jarvisco", "jarvisco-server", "jarvisco-agent"]
    all_found = True
    
    for cmd in commands:
        result = subprocess.run(["which", cmd], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ {cmd}: {result.stdout.strip()}")
        else:
            print(f"✗ {cmd}: No encontrado / Not found")
            all_found = False
    
    return all_found

def check_dependencies():
    """Verifica las dependencias principales."""
    print_header("4. Verificando dependencias principales / Checking main dependencies")
    
    dependencies = [
        ("transformers", "Transformers (Hugging Face)"),
        ("torch", "PyTorch"),
        ("fastapi", "FastAPI"),
        ("flask", "Flask"),
        ("numpy", "NumPy"),
        ("pandas", "Pandas"),
    ]
    
    missing = []
    
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"✓ {name}")
        except ImportError:
            print(f"✗ {name} - No instalado / Not installed")
            missing.append(module)
    
    if missing:
        print("\nPara instalar las dependencias faltantes / To install missing dependencies:")
        print("  pip install -r requirements.txt")
    
    return len(missing) == 0

def check_project_structure():
    """Verifica la estructura del proyecto."""
    print_header("5. Verificando estructura del proyecto / Checking project structure")
    
    required_files = [
        "setup.py",
        "requirements.txt",
        "README.md",
        "COMO_EJECUTAR.md",
        "jarvisco/__init__.py",
        "jarvisco/cli.py",
        "jarvisco/server.py",
        "jarvisco/agent.py",
    ]
    
    all_present = True
    base_path = Path(__file__).parent
    
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - No encontrado / Not found")
            all_present = False
    
    return all_present

def print_summary(checks):
    """Imprime un resumen de las verificaciones."""
    print_header("Resumen / Summary")
    
    total = len(checks)
    passed = sum(checks.values())
    
    print(f"Verificaciones completadas: {passed}/{total}")
    print(f"Checks completed: {passed}/{total}\n")
    
    for check_name, result in checks.items():
        status = "✓" if result else "✗"
        print(f"{status} {check_name}")
    
    if passed == total:
        print("\n🎉 ¡JarvisCO está completamente instalado y listo para usar!")
        print("🎉 JarvisCO is fully installed and ready to use!\n")
        print("Para comenzar / To get started:")
        print("  jarvisco --help")
        print("  jarvisco-server --port 8000")
        print("\nConsulta COMO_EJECUTAR.md para más información.")
        print("See COMO_EJECUTAR.md for more information.")
    elif checks["package_installed"] and checks["commands_available"]:
        print("\n⚠️  JarvisCO está instalado pero faltan algunas dependencias.")
        print("⚠️  JarvisCO is installed but some dependencies are missing.\n")
        print("Para completar la instalación / To complete installation:")
        print("  pip install -r requirements.txt")
    else:
        print("\n⚠️  JarvisCO no está completamente instalado.")
        print("⚠️  JarvisCO is not fully installed.\n")
        print("Para instalar / To install:")
        print("  pip install -r requirements.txt")
        print("  pip install -e .")

def main():
    """Función principal."""
    print("\n" + "=" * 70)
    print("  VERIFICACIÓN DE INSTALACIÓN DE JARVISCO")
    print("  JARVISCO INSTALLATION VERIFICATION")
    print("=" * 70)
    
    checks = {
        "python_version": check_python_version(),
        "package_installed": check_package_installed(),
        "commands_available": check_commands(),
        "dependencies": check_dependencies(),
        "project_structure": check_project_structure(),
    }
    
    print_summary(checks)
    
    return 0 if all(checks.values()) else 1

if __name__ == "__main__":
    sys.exit(main())
