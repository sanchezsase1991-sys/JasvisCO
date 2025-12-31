# Cómo Ejecutar JarvisCO

## 🎯 Inicio Rápido

**¿Primera vez usando JarvisCO?** Ejecuta:

```bash
python3 quick_start.py
```

Este script te mostrará:
- ✓ Estado de instalación
- ✓ Comandos disponibles  
- ✓ Ejemplos de uso
- ✓ Próximos pasos

Para crear un archivo de ejemplo y probarlo:
```bash
python3 quick_start.py --create-example
```

---

## 📋 Tabla de Contenidos
1. [Requisitos Previos](#requisitos-previos)
2. [Instalación](#instalación)
3. [Formas de Ejecutar JarvisCO](#formas-de-ejecutar-jarvisco)
4. [Ejemplos de Uso](#ejemplos-de-uso)
5. [Solución de Problemas](#solución-de-problemas)

---

## 🔧 Requisitos Previos

Antes de ejecutar JarvisCO, asegúrate de tener instalado:

- **Python 3.8+** (Python 3.10 o superior recomendado)
- **4GB RAM** (8GB+ recomendado)
- **4GB de espacio en disco** para los modelos de Mistral 7B
- **pip** (gestor de paquetes de Python)

### Verificar Python

```bash
python3 --version
# Debe mostrar: Python 3.8.0 o superior
```

---

## 📦 Instalación

### Opción 1: Instalación desde el Código Fuente (Recomendado)

```bash
# 1. Clonar el repositorio (si aún no lo has hecho)
git clone https://github.com/sanchezsase1991-sys/JasvisCO.git
cd JasvisCO

# 2. Instalar las dependencias
pip install -r requirements.txt

# 3. Instalar JarvisCO en modo de desarrollo
pip install -e .
```

### Opción 2: Instalación con pip (cuando esté disponible en PyPI)

```bash
pip install JarvisCO
```

### Verificar la Instalación

Después de instalar, verifica que los comandos estén disponibles:

```bash
# Verificar versión
jarvisco --version

# Ver ayuda de los comandos
jarvisco-server --help
jarvisco-agent --help

# Ejecutar script de verificación completo
python3 verify_installation.py
```

El script `verify_installation.py` verificará:
- ✓ Versión de Python (3.8+)
- ✓ Paquete JarvisCO instalado
- ✓ Comandos disponibles (jarvisco, jarvisco-server, jarvisco-agent)
- ✓ Dependencias instaladas
- ✓ Estructura del proyecto

---

## 🚀 Formas de Ejecutar JarvisCO

JarvisCO ofrece **tres formas principales** de ejecución:

### 1️⃣ Interfaz de Línea de Comandos (CLI)

La forma más común y directa de usar JarvisCO.

#### Comandos Disponibles:

```bash
# Ver ayuda general
jarvisco --help

# Analizar código
jarvisco analyze archivo.py

# Transformar código con intención natural
jarvisco transform archivo.py "Refactorizar para usar async/await"

# Refactorizar con aspectos predefinidos
jarvisco refactor archivo.py --aspect pythonic
jarvisco refactor archivo.py --aspect performance

# Generar documentación
jarvisco document archivo.py

# Generar reporte de análisis
jarvisco report archivo.py

# Generar casos de prueba
jarvisco test archivo.py
```

### 2️⃣ Servidor API REST

Para integrar JarvisCO con otras aplicaciones o usarlo como servicio.

#### Iniciar el Servidor:

```bash
# Iniciar en puerto por defecto (8000)
jarvisco-server

# Iniciar en puerto personalizado
jarvisco-server --port 8080

# Iniciar con host personalizado
jarvisco-server --host 0.0.0.0 --port 8000
```

#### Documentación Automática:

Una vez iniciado el servidor, accede a:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

#### Ejemplos de Uso con curl:

```bash
# Verificar estado del servidor
curl http://localhost:8000/health

# Analizar código
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"code": "def foo(): pass"}'

# Transformar código
curl -X POST http://localhost:8000/transform \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def foo(): pass",
    "intent": "Agregar type hints",
    "transform_type": "refactor"
  }'
```

### 3️⃣ Biblioteca de Python

Usar JarvisCO directamente en tus scripts de Python.

```python
import asyncio
from jarvisco.analyzer import CodeAnalyzer
from jarvisco.reasoner import CodeReasoner, TransformationType
from jarvisco.formatter import OutputFormatter
from jarvisco.mistral_llm import MistralLLM

async def main():
    # Inicializar componentes
    llm = MistralLLM()
    analyzer = CodeAnalyzer()
    reasoner = CodeReasoner(llm)
    formatter = OutputFormatter()
    
    # Tu código a analizar
    code = """
    def calcular_suma(a, b):
        return a + b
    """
    
    # Analizar código
    analysis = analyzer.analyze(code)
    print("Análisis:", analysis)
    
    # Transformar código
    result = await reasoner.transform_code(
        code=code,
        intent="Optimizar para rendimiento",
        transform_type=TransformationType.OPTIMIZE
    )
    
    # Formatear salida
    report = formatter.format_transformation_report(result)
    print(report)

# Ejecutar
asyncio.run(main())
```

---

## 💡 Ejemplos de Uso

### Ejemplo 1: Analizar un Archivo Python

```bash
# Crear archivo de ejemplo
echo 'def suma(a, b): return a + b' > ejemplo.py

# Analizar el archivo
jarvisco analyze ejemplo.py
```

**Salida esperada**: Análisis detallado con métricas, complejidad, tipos, etc.

### Ejemplo 2: Refactorizar Código

```bash
# Refactorizar para hacerlo más "pythonic"
jarvisco refactor ejemplo.py --aspect pythonic -o ejemplo_refactorizado.py
```

### Ejemplo 3: Generar Documentación

```bash
# Generar documentación automática
jarvisco document ejemplo.py
```

### Ejemplo 4: Transformación con Intención Natural

```bash
# Usar lenguaje natural para especificar la transformación
jarvisco transform ejemplo.py "Convertir a función async y agregar manejo de errores"
```

### Ejemplo 5: Usar el Servidor API

```bash
# Terminal 1: Iniciar servidor
jarvisco-server --port 8000

# Terminal 2: Hacer peticiones
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explica qué hace este código: def factorial(n): return 1 if n <= 1 else n * factorial(n-1)", "temperature": 0.7}'
```

---

## 🛠️ Solución de Problemas

### Script de Verificación Rápida

Ejecuta el script de verificación para diagnosticar problemas de instalación:

```bash
python3 verify_installation.py
```

Este script te mostrará exactamente qué está instalado y qué falta.

### Problema: Comando `jarvisco` no encontrado

**Solución**:

```bash
# Reinstalar el paquete
pip install -e .

# O agregar el directorio de scripts de Python al PATH
export PATH="$HOME/.local/bin:$PATH"  # Linux/Mac
# O en Windows: agregar Python\Scripts al PATH del sistema
```

### Problema: Error al importar módulos

**Solución**:

```bash
# Verificar que todas las dependencias estén instaladas
pip install -r requirements.txt

# Reinstalar JarvisCO
pip install -e . --force-reinstall
```

### Problema: Modelo Mistral 7B no encontrado

**Solución**:

El modelo se descarga automáticamente en el primer uso. Si hay problemas:

```bash
# Verificar conexión a internet
# Asegurarse de tener suficiente espacio en disco (4GB+)
# El modelo se descarga en: ~/.cache/huggingface/
```

### Problema: Errores de memoria al ejecutar

**Solución**:

```python
# En mobile/Termux o sistemas con poca RAM, usar cuantización:
from jarvisco.mistral_llm import MistralLLM

llm = MistralLLM(
    model_name="mistral-7b-instruct",
    device="cpu",
    load_in_4bit=True  # Activar cuantización Q4
)
```

### Problema: Puerto 8000 ya en uso

**Solución**:

```bash
# Usar un puerto diferente
jarvisco-server --port 8080

# O detener el proceso que usa el puerto 8000
lsof -ti:8000 | xargs kill -9  # Linux/Mac
```

---

## 📚 Recursos Adicionales

- **README.md**: Documentación general en inglés
- **RESUMEN_EJECUCION.txt**: Resumen técnico de implementación
- **IMPLEMENTATION_COMPLETE.md**: Documentación técnica completa
- **GitHub**: https://github.com/sanchezsase1991-sys/JasvisCO

---

## 🆘 Soporte

Si tienes problemas o preguntas:

1. Revisa la [documentación completa](README.md)
2. Busca en [issues existentes](https://github.com/sanchezsase1991-sys/JasvisCO/issues)
3. Crea un [nuevo issue](https://github.com/sanchezsase1991-sys/JasvisCO/issues/new)

---

## ✅ Checklist de Verificación

Antes de reportar un problema, verifica que:

- [ ] Python 3.8+ está instalado
- [ ] Todas las dependencias están instaladas (`pip install -r requirements.txt`)
- [ ] El paquete JarvisCO está instalado (`pip install -e .`)
- [ ] Los comandos están disponibles (`jarvisco --version`)
- [ ] Tienes suficiente memoria RAM (4GB mínimo)
- [ ] Tienes suficiente espacio en disco (4GB+ para modelos)

---

**¡Disfruta usando JarvisCO! 🚀**
