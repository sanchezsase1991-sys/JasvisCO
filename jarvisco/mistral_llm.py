"""
Mistral 7B Language Model Integration for JarvisCO

This module provides a comprehensive integration with the Mistral 7B language model,
including model loading, text generation, streaming capabilities, intent understanding,
and parameter management with proper error handling and logging.

Author: JarvisCO
Date: 2025-12-30
"""

import os
import logging
import json
from typing import Optional, Generator, Dict, List, Any, Tuple
from dataclasses import dataclass, field, asdict
import warnings

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer
    from threading import Thread
    import torch
except ImportError as e:
    raise ImportError(
        f"Required dependencies not found: {e}. "
        "Please install: pip install transformers torch"
    )


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mistral_llm.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class GenerationParameters:
    """Data class for managing text generation parameters."""
    
    max_length: int = 512
    min_length: int = 1
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50
    repetition_penalty: float = 1.0
    num_beams: int = 1
    do_sample: bool = True
    early_stopping: bool = False
    length_penalty: float = 1.0
    no_repeat_ngram_size: int = 0
    pad_token_id: Optional[int] = None
    eos_token_id: Optional[int] = None
    
    def validate(self) -> bool:
        """Validate parameter ranges."""
        validations = [
            (0 < self.temperature <= 2.0, "temperature must be between 0 and 2.0"),
            (0 <= self.top_p <= 1.0, "top_p must be between 0 and 1.0"),
            (0 < self.top_k <= 100, "top_k must be between 0 and 100"),
            (0 < self.repetition_penalty <= 2.0, "repetition_penalty must be between 0 and 2.0"),
            (self.max_length > self.min_length, "max_length must be greater than min_length"),
            (self.num_beams >= 1, "num_beams must be at least 1"),
        ]
        
        for condition, message in validations:
            if not condition:
                logger.warning(f"Parameter validation warning: {message}")
                return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert parameters to dictionary."""
        return asdict(self)


@dataclass
class IntentAnalysis:
    """Data class for intent analysis results."""
    
    primary_intent: str
    confidence: float
    secondary_intents: List[Tuple[str, float]] = field(default_factory=list)
    entities: Dict[str, List[str]] = field(default_factory=dict)
    sentiment: str = "neutral"
    requires_action: bool = False
    action_type: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class MistralLLM:
    """
    Comprehensive Mistral 7B Language Model wrapper for JarvisCO.
    
    Features:
    - Model loading and caching
    - Text generation with customizable parameters
    - Streaming text generation
    - Intent understanding and analysis
    - Parameter management and validation
    - Comprehensive error handling and logging
    """
    
    # Supported model variants
    SUPPORTED_MODELS = {
        "mistral-7b": "mistralai/Mistral-7B-v0.1",
        "mistral-7b-instruct": "mistralai/Mistral-7B-Instruct-v0.1",
        "mistral-7b-instruct-v2": "mistralai/Mistral-7B-Instruct-v0.2",
    }
    
    def __init__(
        self,
        model_name: str = "mistral-7b-instruct",
        device: str = "auto",
        dtype: str = "float16",
        cache_dir: Optional[str] = None,
        load_in_8bit: bool = False,
        load_in_4bit: bool = False,
    ):
        """
        Initialize Mistral 7B model.
        
        Args:
            model_name: Name or path of the model variant
            device: Device to load model on ('cuda', 'cpu', 'auto')
            dtype: Data type for model ('float16', 'float32', 'bfloat16')
            cache_dir: Directory to cache downloaded models
            load_in_8bit: Enable 8-bit quantization
            load_in_4bit: Enable 4-bit quantization
        
        Raises:
            ValueError: If model name is not supported
            RuntimeError: If model loading fails
        """
        logger.info(f"Initializing Mistral 7B model: {model_name}")
        
        self.model_name = model_name
        self.device = self._resolve_device(device)
        self.dtype = self._resolve_dtype(dtype)
        self.cache_dir = cache_dir
        self.load_in_8bit = load_in_8bit
        self.load_in_4bit = load_in_4bit
        
        # Validate model name
        if model_name not in self.SUPPORTED_MODELS and not os.path.exists(model_name):
            raise ValueError(
                f"Model '{model_name}' not supported. "
                f"Supported models: {list(self.SUPPORTED_MODELS.keys())}"
            )
        
        # Resolve model path
        self.model_path = self.SUPPORTED_MODELS.get(model_name, model_name)
        
        # Initialize model and tokenizer
        self.tokenizer: Optional[AutoTokenizer] = None
        self.model: Optional[AutoModelForCausalLM] = None
        self.generation_params = GenerationParameters()
        
        try:
            self._load_model()
            logger.info(f"Successfully loaded model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise RuntimeError(f"Model loading failed: {str(e)}") from e
    
    def _resolve_device(self, device: str) -> str:
        """Resolve device selection."""
        if device == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        if device not in ["cuda", "cpu", "mps"]:
            logger.warning(f"Unknown device '{device}', defaulting to 'cpu'")
            return "cpu"
        return device
    
    def _resolve_dtype(self, dtype: str) -> torch.dtype:
        """Resolve data type."""
        dtype_map = {
            "float16": torch.float16,
            "float32": torch.float32,
            "bfloat16": torch.bfloat16,
        }
        return dtype_map.get(dtype, torch.float16)
    
    def _load_model(self) -> None:
        """Load tokenizer and model."""
        # Load tokenizer
        logger.info(f"Loading tokenizer from {self.model_path}")
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_path,
            cache_dir=self.cache_dir,
            trust_remote_code=True,
        )
        
        # Set padding token if not already set
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load model
        logger.info(f"Loading model from {self.model_path}")
        
        model_kwargs = {
            "cache_dir": self.cache_dir,
            "trust_remote_code": True,
            "device_map": self.device,
        }
        
        if self.dtype == torch.float16:
            model_kwargs["torch_dtype"] = torch.float16
        elif self.dtype == torch.bfloat16:
            model_kwargs["torch_dtype"] = torch.bfloat16
        
        if self.load_in_8bit or self.load_in_4bit:
            try:
                from transformers import BitsAndBytesConfig
                
                if self.load_in_4bit:
                    model_kwargs["quantization_config"] = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_compute_dtype=torch.float16,
                        bnb_4bit_use_double_quant=True,
                        bnb_4bit_quant_type="nf4",
                    )
                else:
                    model_kwargs["load_in_8bit"] = True
            except ImportError:
                logger.warning("bitsandbytes not available, loading without quantization")
        
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            **model_kwargs
        )
        
        self.model.eval()
    
    def update_generation_params(self, **kwargs) -> None:
        """
        Update generation parameters.
        
        Args:
            **kwargs: Parameter names and values to update
        
        Raises:
            ValueError: If invalid parameter name
        """
        for key, value in kwargs.items():
            if not hasattr(self.generation_params, key):
                raise ValueError(f"Unknown parameter: {key}")
            setattr(self.generation_params, key, value)
            logger.debug(f"Updated parameter {key} to {value}")
        
        if not self.generation_params.validate():
            logger.warning("Some parameters are outside recommended ranges")
    
    def get_generation_params(self) -> Dict[str, Any]:
        """Get current generation parameters."""
        return self.generation_params.to_dict()
    
    def generate(
        self,
        prompt: str,
        max_length: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate text from prompt.
        
        Args:
            prompt: Input text prompt
            max_length: Maximum length of generated text (overrides default)
            temperature: Sampling temperature (overrides default)
            top_p: Nucleus sampling parameter (overrides default)
            top_k: Top-k sampling parameter (overrides default)
            **kwargs: Additional generation parameters
        
        Returns:
            Generated text
        
        Raises:
            ValueError: If prompt is empty or invalid
            RuntimeError: If generation fails
        """
        if not prompt or not isinstance(prompt, str):
            raise ValueError("Prompt must be a non-empty string")
        
        logger.info(f"Generating text for prompt: {prompt[:100]}...")
        
        try:
            # Prepare generation parameters
            gen_params = self.generation_params.to_dict()
            
            if max_length is not None:
                gen_params["max_length"] = max_length
            if temperature is not None:
                gen_params["temperature"] = temperature
            if top_p is not None:
                gen_params["top_p"] = top_p
            if top_k is not None:
                gen_params["top_k"] = top_k
            
            gen_params.update(kwargs)
            
            # Tokenize input
            inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    **gen_params
                )
            
            # Decode output
            generated_text = self.tokenizer.decode(
                outputs[0],
                skip_special_tokens=True
            )
            
            logger.debug(f"Generation successful")
            return generated_text
        
        except Exception as e:
            logger.error(f"Text generation failed: {str(e)}")
            raise RuntimeError(f"Generation failed: {str(e)}") from e
    
    def generate_streaming(
        self,
        prompt: str,
        max_length: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        """
        Generate text with streaming output.
        
        Args:
            prompt: Input text prompt
            max_length: Maximum length of generated text
            temperature: Sampling temperature
            **kwargs: Additional generation parameters
        
        Yields:
            Text tokens as they are generated
        
        Raises:
            ValueError: If prompt is invalid
            RuntimeError: If streaming generation fails
        """
        if not prompt or not isinstance(prompt, str):
            raise ValueError("Prompt must be a non-empty string")
        
        logger.info(f"Starting streaming generation for prompt: {prompt[:100]}...")
        
        try:
            # Prepare generation parameters
            gen_params = self.generation_params.to_dict()
            gen_params["do_sample"] = True
            
            if max_length is not None:
                gen_params["max_length"] = max_length
            if temperature is not None:
                gen_params["temperature"] = temperature
            
            gen_params.update(kwargs)
            
            # Setup streamer
            streamer = TextIteratorStreamer(
                self.tokenizer,
                skip_special_tokens=True
            )
            
            # Tokenize input
            inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
            
            # Run generation in separate thread
            generation_kwargs = {
                **gen_params,
                "inputs": inputs,
                "streamer": streamer,
            }
            
            thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
            thread.start()
            
            # Yield tokens as they stream in
            for token in streamer:
                yield token
            
            thread.join()
            logger.debug("Streaming generation completed")
        
        except Exception as e:
            logger.error(f"Streaming generation failed: {str(e)}")
            raise RuntimeError(f"Streaming generation failed: {str(e)}") from e
    
    def analyze_intent(self, text: str) -> IntentAnalysis:
        """
        Analyze user intent from input text.
        
        Args:
            text: Input text to analyze
        
        Returns:
            IntentAnalysis object with detected intents and entities
        
        Raises:
            ValueError: If text is invalid
            RuntimeError: If analysis fails
        """
        if not text or not isinstance(text, str):
            raise ValueError("Text must be a non-empty string")
        
        logger.info(f"Analyzing intent for text: {text[:100]}...")
        
        try:
            # Create intent analysis prompt
            intent_prompt = f"""Analyze the following user text and provide:
1. Primary intent (single word or short phrase)
2. Confidence level (0-1)
3. Any secondary intents
4. Key entities mentioned
5. Sentiment (positive/negative/neutral)
6. Whether action is required

Text: "{text}"

Respond in JSON format."""
            
            # Generate analysis
            analysis_text = self.generate(
                intent_prompt,
                max_length=256,
                temperature=0.3,
            )
            
            # Parse response
            intent_result = self._parse_intent_response(analysis_text, text)
            logger.debug(f"Intent analysis complete: {intent_result.primary_intent}")
            
            return intent_result
        
        except Exception as e:
            logger.error(f"Intent analysis failed: {str(e)}")
            raise RuntimeError(f"Intent analysis failed: {str(e)}") from e
    
    def _parse_intent_response(self, response: str, original_text: str) -> IntentAnalysis:
        """
        Parse intent analysis response from model.
        
        Args:
            response: Model response text
            original_text: Original user text
        
        Returns:
            IntentAnalysis object
        """
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
            else:
                # Fallback parsing
                data = self._fallback_intent_parsing(original_text)
            
            return IntentAnalysis(
                primary_intent=data.get("primary_intent", "query"),
                confidence=float(data.get("confidence", 0.5)),
                secondary_intents=data.get("secondary_intents", []),
                entities=data.get("entities", {}),
                sentiment=data.get("sentiment", "neutral"),
                requires_action=data.get("requires_action", False),
                action_type=data.get("action_type", None),
            )
        
        except Exception as e:
            logger.warning(f"Failed to parse intent response: {str(e)}")
            return IntentAnalysis(
                primary_intent="unknown",
                confidence=0.0,
                sentiment="neutral",
                requires_action=False,
            )
    
    def _fallback_intent_parsing(self, text: str) -> Dict[str, Any]:
        """Fallback intent parsing without JSON."""
        text_lower = text.lower()
        
        # Simple keyword-based intent detection
        intents = {
            "help": ["help", "assist", "support"],
            "generate": ["generate", "create", "write", "produce"],
            "analyze": ["analyze", "analyze", "examine", "review"],
            "summarize": ["summarize", "summary", "brief"],
            "translate": ["translate", "translation"],
            "explain": ["explain", "clarify", "elaborate"],
        }
        
        detected_intent = "query"
        for intent, keywords in intents.items():
            if any(kw in text_lower for kw in keywords):
                detected_intent = intent
                break
        
        return {
            "primary_intent": detected_intent,
            "confidence": 0.6,
            "secondary_intents": [],
            "entities": {},
            "sentiment": "neutral",
            "requires_action": False,
            "action_type": None,
        }
    
    def batch_generate(
        self,
        prompts: List[str],
        **kwargs
    ) -> List[str]:
        """
        Generate text for multiple prompts.
        
        Args:
            prompts: List of input prompts
            **kwargs: Generation parameters
        
        Returns:
            List of generated texts
        
        Raises:
            ValueError: If prompts list is empty
        """
        if not prompts or not isinstance(prompts, list):
            raise ValueError("Prompts must be a non-empty list")
        
        logger.info(f"Batch generating text for {len(prompts)} prompts")
        
        results = []
        for i, prompt in enumerate(prompts):
            try:
                result = self.generate(prompt, **kwargs)
                results.append(result)
                logger.debug(f"Batch generation {i+1}/{len(prompts)} complete")
            except Exception as e:
                logger.error(f"Failed to generate for prompt {i+1}: {str(e)}")
                results.append(f"[Error: {str(e)}]")
        
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded model."""
        return {
            "model_name": self.model_name,
            "model_path": self.model_path,
            "device": self.device,
            "dtype": str(self.dtype),
            "quantization": {
                "int8": self.load_in_8bit,
                "int4": self.load_in_4bit,
            },
            "total_parameters": sum(p.numel() for p in self.model.parameters()),
            "trainable_parameters": sum(
                p.numel() for p in self.model.parameters() if p.requires_grad
            ),
        }
    
    def __del__(self) -> None:
        """Cleanup on deletion."""
        try:
            if self.model is not None:
                del self.model
            if self.tokenizer is not None:
                del self.tokenizer
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            logger.info("Model cleanup completed")
        except Exception as e:
            logger.warning(f"Error during cleanup: {str(e)}")


# ============================================================================
# Example Usage
# ============================================================================

def example_basic_generation():
    """Example: Basic text generation."""
    print("\n" + "="*60)
    print("Example 1: Basic Text Generation")
    print("="*60)
    
    try:
        # Initialize model
        model = MistralLLM(
            model_name="mistral-7b-instruct",
            device="auto",
            dtype="float16",
        )
        
        # Generate text
        prompt = "The future of artificial intelligence is"
        generated = model.generate(
            prompt,
            max_length=200,
            temperature=0.7,
        )
        
        print(f"Prompt: {prompt}")
        print(f"\nGenerated:\n{generated}")
        
    except Exception as e:
        print(f"Error: {str(e)}")


def example_streaming_generation():
    """Example: Streaming text generation."""
    print("\n" + "="*60)
    print("Example 2: Streaming Text Generation")
    print("="*60)
    
    try:
        model = MistralLLM(model_name="mistral-7b-instruct")
        
        prompt = "Write a short poem about technology:"
        print(f"Prompt: {prompt}\n")
        
        print("Streaming output:")
        for token in model.generate_streaming(prompt, max_length=150):
            print(token, end="", flush=True)
        print("\n")
        
    except Exception as e:
        print(f"Error: {str(e)}")


def example_intent_analysis():
    """Example: Intent analysis."""
    print("\n" + "="*60)
    print("Example 3: Intent Analysis")
    print("="*60)
    
    try:
        model = MistralLLM(model_name="mistral-7b-instruct")
        
        test_texts = [
            "Can you help me write a Python script?",
            "What is machine learning?",
            "Generate a creative story about space exploration",
        ]
        
        for text in test_texts:
            intent = model.analyze_intent(text)
            print(f"\nText: {text}")
            print(f"Primary Intent: {intent.primary_intent}")
            print(f"Confidence: {intent.confidence}")
            print(f"Sentiment: {intent.sentiment}")
        
    except Exception as e:
        print(f"Error: {str(e)}")


def example_batch_generation():
    """Example: Batch text generation."""
    print("\n" + "="*60)
    print("Example 4: Batch Generation")
    print("="*60)
    
    try:
        model = MistralLLM(model_name="mistral-7b-instruct")
        
        prompts = [
            "Explain quantum computing in simple terms:",
            "What are the benefits of renewable energy?",
            "Describe a perfect day:",
        ]
        
        results = model.batch_generate(prompts, max_length=150)
        
        for prompt, result in zip(prompts, results):
            print(f"\nPrompt: {prompt}")
            print(f"Result: {result[:200]}...")
        
    except Exception as e:
        print(f"Error: {str(e)}")


def example_parameter_management():
    """Example: Parameter management."""
    print("\n" + "="*60)
    print("Example 5: Parameter Management")
    print("="*60)
    
    try:
        model = MistralLLM(model_name="mistral-7b-instruct")
        
        # Get current parameters
        print("Current parameters:")
        params = model.get_generation_params()
        for key, value in params.items():
            print(f"  {key}: {value}")
        
        # Update parameters
        print("\nUpdating parameters...")
        model.update_generation_params(
            temperature=0.5,
            top_p=0.85,
            max_length=300,
        )
        
        print("Updated parameters:")
        params = model.get_generation_params()
        for key, value in params.items():
            print(f"  {key}: {value}")
        
        # Get model info
        print("\nModel Information:")
        info = model.get_model_info()
        for key, value in info.items():
            print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    """
    Run examples with proper error handling.
    
    Note: These examples require a GPU with sufficient VRAM.
    For CPU-only environments, use smaller model variants or
    enable quantization (load_in_8bit=True or load_in_4bit=True).
    """
    
    print("JarvisCO Mistral 7B Integration Examples")
    print("=" * 60)
    
    # Uncomment examples to run
    # example_basic_generation()
    # example_streaming_generation()
    # example_intent_analysis()
    # example_batch_generation()
    # example_parameter_management()
    
    print("\nTo run examples, uncomment them in the __main__ block")
