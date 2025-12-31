# Guía de Inicio Rápido - JarvisCO

## ¡Bienvenido a JarvisCO! 🚀

Esta guía te ayudará a ejecutar JarvisCO en menos de 5 minutos.

---

## Paso 1: Verificar Requisitos ✅

```bash
# Python 3.8+
python3 --version

# Debe mostrar: Python 3.8.0 o superior
```

---

## Paso 2: Instalación ⚙️

```bash
# Clonar el repositorio (si aún no lo has hecho)
git clone https://github.com/sanchezsase1991-sys/JasvisCO.git
cd JasvisCO

# Instalar dependencias
pip install -r requirements.txt

# Instalar JarvisCO
pip install -e .
```

---

## Paso 3: Verificar Instalación 🔍

```bash
# Opción 1: Verificación rápida
python3 quick_start.py --check-only

# Opción 2: Verificación completa
python3 verify_installation.py
```

---

## Paso 4: Primeros Pasos 🎯

### Crear un archivo de ejemplo

```bash
python3 quick_start.py --create-example
```

Esto crea `ejemplo_codigo.py` que puedes usar para probar JarvisCO.

### Probar los comandos

```bash
# Ver ayuda
jarvisco --help

# Analizar código
jarvisco analyze ejemplo_codigo.py

# Refactorizar código
jarvisco refactor ejemplo_codigo.py --aspect pythonic

# Generar documentación
jarvisco document ejemplo_codigo.py

# Iniciar servidor API
jarvisco-server --port 8000
```

---

## Documentación Completa 📚

- **[COMO_EJECUTAR.md](COMO_EJECUTAR.md)** - Guía completa con todos los detalles
- **[README.md](README.md)** - Documentación del proyecto
- **[RESUMEN_EJECUCION.txt](RESUMEN_EJECUCION.txt)** - Resumen técnico

---

## Scripts Útiles 🛠️

| Script | Descripción | Uso |
|--------|-------------|-----|
| `quick_start.py` | Inicio rápido e información | `python3 quick_start.py` |
| `verify_installation.py` | Verificar instalación completa | `python3 verify_installation.py` |

---

## Comandos Principales 💻

### CLI - Línea de Comandos

```bash
jarvisco analyze <archivo>              # Analizar código
jarvisco transform <archivo> "intent"   # Transformar con intención
jarvisco refactor <archivo> --aspect    # Refactorizar
jarvisco document <archivo>             # Generar documentación
jarvisco report <archivo>               # Generar reporte
jarvisco test <archivo>                 # Generar tests
```

### API REST - Servidor

```bash
# Iniciar servidor
jarvisco-server --port 8000

# Documentación automática en:
# http://localhost:8000/docs
# http://localhost:8000/redoc
```

### Biblioteca Python

```python
from jarvisco.analyzer import CodeAnalyzer
from jarvisco.reasoner import CodeReasoner

analyzer = CodeAnalyzer()
analysis = analyzer.analyze(your_code)
```

---

## Solución Rápida de Problemas 🔧

### Comando no encontrado

```bash
# Reinstalar
pip install -e .

# Agregar al PATH (si es necesario)
export PATH="$HOME/.local/bin:$PATH"
```

### Faltan dependencias

```bash
pip install -r requirements.txt
```

### Error de memoria

Para sistemas con poca RAM, edita tu código Python:

```python
from jarvisco.mistral_llm import MistralLLM

llm = MistralLLM(
    model_name="mistral-7b-instruct",
    device="cpu",
    load_in_4bit=True  # Activar cuantización
)
```

---

## ¿Necesitas Ayuda? 🆘

1. Revisa [COMO_EJECUTAR.md](COMO_EJECUTAR.md) para más detalles
2. Visita [Issues en GitHub](https://github.com/sanchezsase1991-sys/JasvisCO/issues)
3. Crea un nuevo issue si encuentras un problema

---

## Resumen de 3 Comandos ⚡

```bash
# 1. Instalar
pip install -r requirements.txt && pip install -e .

# 2. Verificar
python3 quick_start.py

# 3. ¡Usar!
jarvisco --help
```

---

**¡Listo! Ya puedes usar JarvisCO 🎉**

Para más información, consulta la [documentación completa](COMO_EJECUTAR.md).
