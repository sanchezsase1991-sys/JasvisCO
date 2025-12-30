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
    from jarvisco.config import Config
    from jarvisco.mistral_llm import MistralLLM
    from jarvisco.rosa_enlg import RosaENLG
    from jarvisco.fusion_engine import FusionEngine
    from jarvisco.prompt_manager import PromptManager
    from jarvisco.system_tools import SystemTools
    from jarvisco.code_analyzer import CodeAnalyzer
    from jarvisco.project_setup import ProjectSetup
    
    logger.info(f"JarvisCO v{__version__} initialized successfully")
except ImportError as e:
    logger.warning(f"Failed to import some core modules: {e}")

# Define public API
__all__: List[str] = [
    "Config",
    "MistralLLM",
    "RosaENLG",
    "FusionEngine",
    "PromptManager",
    "SystemTools",
    "CodeAnalyzer",
    "ProjectSetup",
    "__version__",
]
