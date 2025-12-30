"""
JarvisCO - An intelligent code orchestration and analysis framework.

This package provides a comprehensive suite of tools for code analysis,
project setup, prompt management, and AI-powered code generation.
"""

import logging
from typing import List

# Version
__version__ = "0.1.0"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Import core modules
try:
    from jarvisco.mistral_llm import MistralLLM, GenerationParameters, IntentAnalysis
    from jarvisco.analyzer import CodeAnalyzer, CodeEntity, CodeIssue
    from jarvisco.reasoner import CodeReasoner, TransformationType, TransformationResult
    from jarvisco.formatter import OutputFormatter, format_code_analysis, format_report
    from jarvisco.cli import JarvisConsole
    from jarvisco.server import app as server_app
    from jarvisco.agent import JarvisAgent, Task, TaskStatus, TaskPriority, WorkflowStep
    
    logger.info(f"JarvisCO v{__version__} (Copilot-Level) initialized successfully")
except ImportError as e:
    logger.warning(f"Failed to import some modules: {e}")

# Define public API
__all__: List[str] = [
    "MistralLLM",
    "GenerationParameters",
    "IntentAnalysis",
    "CodeAnalyzer",
    "CodeEntity",
    "CodeIssue",
    "CodeReasoner",
    "TransformationType",
    "TransformationResult",
    "OutputFormatter",
    "format_code_analysis",
    "format_report",
    "JarvisConsole",
    "server_app",
    "JarvisAgent",
    "Task",
    "TaskStatus",
    "TaskPriority",
    "WorkflowStep",
    "__version__",
]
