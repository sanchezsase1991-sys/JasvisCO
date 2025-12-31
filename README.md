# JarvisCO - Copilot-Level Code Analysis & Transformation Engine

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Quality](https://img.shields.io/badge/code%20quality-production%20ready-brightgreen.svg)]()

**An intelligent code analysis, reasoning, and transformation system powered by Mistral 7B.**

JarvisCO provides semantic code understanding through AST analysis, chain-of-thought reasoning, and safe code generation with professional output formatting.

## 🎯 Features

### 🧠 Semantic Code Understanding
- **AST Parsing** - Deep code structure analysis
- **Type Analysis** - mypy integration for type safety
- **Complexity Metrics** - Cyclomatic complexity measurement
- **Issue Detection** - Code quality and pattern identification
- **Metric Extraction** - Comprehensive code metrics

### 🤔 Chain-of-Thought Reasoning
- **Intent Understanding** - Semantic natural language parsing
- **Multi-Step Planning** - Structured transformation planning
- **Constraint Validation** - Safety and compatibility checks
- **Risk Assessment** - Breaking change detection
- **Confidence Scoring** - Quality and reliability assessment

### 💻 Safe Code Generation
- **Intent-Driven** - Generate from natural language
- **7 Transformation Types** - Refactor, Optimize, Fix, Feature, Document, Test, Migrate
- **Self-Validation** - Syntax and type checking
- **Iterative Improvement** - Quality enhancement

### 📄 Professional Output
- **RosaENLG Integration** - Structured document generation
- **Documentation** - Automatic code documentation
- **Reports** - Analysis and transformation reports
- **Multi-Format** - Markdown, HTML, JSON output

## 🚀 Quick Start

### Installation

```bash
pip install jarvisco
```

### CLI Usage

```bash
# Analyze code
jarvisco analyze code.py

# Transform with intent
jarvisco transform code.py "Refactor to use async/await"

# Refactor with predefined aspects
jarvisco refactor code.py --aspect pythonic
jarvisco refactor code.py --aspect performance

# Generate documentation
jarvisco document code.py

# Generate analysis report
jarvisco report code.py

# Generate tests
jarvisco test code.py
```

### REST API

```bash
# Start server
jarvisco-server --port 8000

# Analyze code
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"code": "def foo(): pass"}'

# Transform code
curl -X POST http://localhost:8000/transform \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def foo(): pass",
    "intent": "Add type hints",
    "transform_type": "refactor"
  }'
```

### Python Library

```python
from jarvisco import CodeAnalyzer, CodeReasoner, OutputFormatter, MistralLLM

# Initialize
llm = MistralLLM()
analyzer = CodeAnalyzer()
reasoner = CodeReasoner(llm)
formatter = OutputFormatter()

# Analyze code
analysis = analyzer.analyze(code)

# Reason about transformation
result = await reasoner.transform_code(
    code=code,
    intent="Optimize for performance",
    transform_type=TransformationType.OPTIMIZE
)

# Format output
report = formatter.format_transformation_report(result)
print(report)
```

## 📊 What Makes It Copilot-Level

**Traditional AI Assistants:**
```
Input → LLM → Output
```

**JarvisCO (Copilot-Level):**
```
Input
  ↓
Semantic Intent Understanding
  ↓
Code Structure Analysis (AST)
  ↓
Chain-of-Thought Reasoning
  ↓
Multi-Step Code Generation
  ↓
Self-Validation & Testing
  ↓
Confidence Scoring
  ↓
Professional Output Formatting
  ↓
Result
```

## 🏗️ Architecture

```
┌────────────────────────────────────────┐
│         USER INTERFACE                 │
│      CLI / API / Python Library        │
└──────────────┬─────────────────────────┘
               │
┌──────────────▼─────────────────────────┐
│    ORCHESTRATION LAYER                 │
│  CodeReasoningAgent + REST Server      │
└──────────────┬─────────────────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼─┐  ┌─────▼────┐  ┌─▼──────┐
│ANALYZER│ │REASONER│ │FORMATTER│
└───┬──┘  └─────┬────┘  └─┬──────┘
    │          │          │
    └──────────┼──────────┘
               │
┌──────────────▼──────────────────────┐
│   LANGUAGE MODEL LAYER              │
│  Mistral 7B (Quantized Q4_K_M)     │
└───────────────────────────────────┘
```

## 📈 Capabilities

### Code Analysis
- AST parsing and structure extraction
- Type hint analysis
- Cyclomatic complexity calculation
- Code quality issue detection
- Comprehensive metrics

### Code Reasoning
- Semantic intent understanding
- Step-by-step reasoning explanation
- Constraint and compatibility validation
- Risk assessment
- Confidence scoring

### Code Transformation
- 7 transformation types (refactor, optimize, fix, feature, document, test, migrate)
- Safe generation with validation
- Syntax and type checking
- Quality assurance

### Output Formatting
- RosaENLG professional formatting
- Multiple output styles (markdown, HTML, JSON)
- Documentation generation
- Report generation
- Template support

## 💾 Platform Support

- ✅ **Linux** - Full support
- ✅ **macOS** - Full support
- ✅ **Windows** - Full support (via WSL recommended)
- ✅ **Termux (Android)** - Optimized for mobile with quantization

## 📋 Requirements

- Python 3.8+
- 4GB RAM (8GB+ recommended)
- 4GB disk space for Mistral 7B model
- CUDA 11.8+ (optional, for GPU acceleration)

## �� Configuration

### Desktop (Full Features)
```python
llm = MistralLLM(
    model_name="mistral-7b-instruct",
    device="auto",  # Auto GPU/CPU selection
    load_in_4bit=False
)
```

### Mobile/Termux (Optimized)
```python
llm = MistralLLM(
    model_name="mistral-7b-instruct",
    device="cpu",
    load_in_4bit=True  # Q4 quantization for low memory
)
```

## 📚 Documentation

- [Architecture Documentation](COPILOT_LEVEL_ARCHITECTURE.md)
- [Completion Status](COPILOT_COMPLETE.md)
- [API Reference](docs/api.md) (coming soon)
- [Examples](docs/examples.md) (coming soon)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**sanchezsase1991-sys**
- GitHub: [@sanchezsase1991-sys](https://github.com/sanchezsase1991-sys)
- Email: dev@jarvisco.local

## 🙏 Acknowledgments

- Powered by [Mistral 7B](https://mistral.ai/)
- Uses [RosaENLG](https://github.com/sflanagan87/rosaenlg) for professional output formatting
- Built with [FastAPI](https://fastapi.tiangolo.com/) and [asyncio](https://docs.python.org/3/library/asyncio.html)

## 📞 Support

For issues, questions, or suggestions:
1. Check [existing issues](https://github.com/sanchezsase1991-sys/JasvisCO/issues)
2. Create a [new issue](https://github.com/sanchezsase1991-sys/JasvisCO/issues/new)
3. Start a [discussion](https://github.com/sanchezsase1991-sys/JasvisCO/discussions)

---

## 🇪🇸 Guía en Español / Spanish Guide

**¿Cómo ejecuto JarvisCO?** / **How do I run JarvisCO?**

📖 **[INICIO_RAPIDO.md](INICIO_RAPIDO.md)** - Guía de inicio en 5 minutos (español)

📖 **[COMO_EJECUTAR.md](COMO_EJECUTAR.md)** - Guía completa de instalación y ejecución (español)

### Inicio Rápido / Quick Start (ES)

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Instalar JarvisCO
pip install -e .

# 3. Verificar instalación / Verify installation
python3 quick_start.py

# 4. Ejecutar / Run
jarvisco --help                    # Ver ayuda
jarvisco analyze archivo.py        # Analizar código
jarvisco-server                    # Iniciar servidor API
```

---

**Made with ❤️ for developers who want intelligent code assistance.**
