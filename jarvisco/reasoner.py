#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
JarvisCO Code Reasoner - Chain-of-Thought Code Generation & Transformation

The core Copilot-level reasoning engine that:
- Understands intent semantically
- Reasons about transformations step-by-step
- Validates generated code
- Iteratively improves solutions
- Maintains confidence scores

Author: JarvisCO
Date: 2025-12-30
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import ast
import subprocess

from jarvisco.analyzer import CodeAnalyzer, CodeIssue
from jarvisco.mistral_llm import MistralLLM

logger = logging.getLogger(__name__)


class TransformationType(Enum):
    """Types of code transformations."""
    REFACTOR = "refactor"
    GENERATE = "generate"
    OPTIMIZE = "optimize"
    FIX_BUG = "fix_bug"
    ADD_FEATURE = "add_feature"
    DOCUMENT = "document"
    TEST = "test"
    MIGRATE = "migrate"


@dataclass
class ReasoningStep:
    """One step in the reasoning chain."""
    step_num: int
    thought: str  # What the reasoner is thinking
    action: str   # What action to take
    code_snippet: Optional[str] = None
    confidence: float = 1.0
    rationale: str = ""


@dataclass
class TransformationResult:
    """Result of a code transformation."""
    success: bool
    original_code: str
    transformed_code: Optional[str] = None
    transformation_type: Optional[TransformationType] = None
    reasoning_steps: List[ReasoningStep] = field(default_factory=list)
    issues_found: List[CodeIssue] = field(default_factory=list)
    validation_errors: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    explanation: str = ""


class CodeReasoner:
    """
    Copilot-level code reasoning engine.
    
    Uses chain-of-thought prompting to:
    1. Understand intent semantically
    2. Analyze current code
    3. Reason about transformation
    4. Generate improved code
    5. Validate against constraints
    """
    
    def __init__(self, llm: MistralLLM):
        """Initialize reasoner."""
        self.llm = llm
        self.analyzer = CodeAnalyzer()
        self.reasoning_history: List[ReasoningStep] = []
        
    async def transform_code(
        self,
        code: str,
        intent: str,
        transform_type: TransformationType = TransformationType.REFACTOR,
        context: Optional[str] = None
    ) -> TransformationResult:
        """
        Transform code based on intent using chain-of-thought reasoning.
        
        Args:
            code: Source code to transform
            intent: Natural language description of desired transformation
            transform_type: Type of transformation
            context: Additional context (dependencies, requirements, etc)
            
        Returns:
            TransformationResult with reasoning and transformed code
        """
        
        result = TransformationResult(
            success=False,
            original_code=code,
            transformation_type=transform_type
        )
        
        # STEP 1: Analyze current code
        logger.info("Step 1: Analyzing code structure...")
        analysis = self.analyzer.analyze(code)
        result.issues_found = [
            CodeIssue(**issue) for issue in analysis.get('issues', [])
        ]
        
        # STEP 2: Semantic understanding of intent
        logger.info("Step 2: Understanding intent semantically...")
        intent_understanding = await self._understand_intent(intent, code, context)
        
        # STEP 3: Chain-of-thought reasoning
        logger.info("Step 3: Reasoning about transformation...")
        reasoning_steps = await self._reason_transformation(
            code=code,
            intent=intent,
            analysis=analysis,
            intent_understanding=intent_understanding,
            transform_type=transform_type
        )
        result.reasoning_steps = reasoning_steps
        
        # STEP 4: Generate transformation
        logger.info("Step 4: Generating transformed code...")
        transformed_code = await self._generate_transformation(
            code=code,
            reasoning_steps=reasoning_steps,
            transform_type=transform_type
        )
        result.transformed_code = transformed_code
        
        # STEP 5: Validate transformation
        logger.info("Step 5: Validating generated code...")
        validation_errors = await self._validate_code(transformed_code)
        result.validation_errors = validation_errors
        
        # STEP 6: Calculate confidence
        logger.info("Step 6: Calculating confidence score...")
        confidence = self._calculate_confidence(
            reasoning_steps=reasoning_steps,
            validation_errors=validation_errors,
            analysis=analysis
        )
        result.confidence_score = confidence
        
        # STEP 7: Generate explanation
        result.explanation = await self._generate_explanation(
            reasoning_steps=reasoning_steps,
            transform_type=transform_type
        )
        
        result.success = len(validation_errors) == 0 and confidence > 0.7
        
        return result
    
    async def _understand_intent(
        self,
        intent: str,
        code: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Understand intent semantically (not just keywords).
        
        Returns: Intent understanding with semantic analysis
        """
        
        semantic_analysis_prompt = f"""
Analyze this code transformation intent semantically:

Intent: "{intent}"

Code to transform:
```python
{code}
```

{f"Context: {context}" if context else ""}

Identify:
1. What is the PRIMARY goal? (refactor, optimize, fix, feature, etc)
2. What CONSTRAINTS must be maintained? (API compatibility, performance, etc)
3. What PATTERNS are involved? (design patterns, idioms, etc)
4. What RISKS exist? (breaking changes, performance, security, etc)
5. What DEPENDENCIES are relevant? (external libs, internal modules, etc)

Provide semantic understanding, not just surface-level interpretation.
"""
        
        response = self.llm.generate(semantic_analysis_prompt)
        
        # Parse response into structured understanding
        return {
            "raw_understanding": response,
            "primary_goal": self._extract_from_response(response, "PRIMARY goal"),
            "constraints": self._extract_from_response(response, "CONSTRAINTS"),
            "patterns": self._extract_from_response(response, "PATTERNS"),
            "risks": self._extract_from_response(response, "RISKS"),
            "dependencies": self._extract_from_response(response, "DEPENDENCIES")
        }
    
    async def _reason_transformation(
        self,
        code: str,
        intent: str,
        analysis: Dict,
        intent_understanding: Dict,
        transform_type: TransformationType
    ) -> List[ReasoningStep]:
        """
        Chain-of-thought reasoning about the transformation.
        
        Breaks down the transformation into logical steps.
        """
        
        reasoning_prompt = f"""
You are a code reasoning engine. Think step-by-step about transforming this code.

INTENT: {intent}
TRANSFORMATION TYPE: {transform_type.value}

CURRENT CODE ANALYSIS:
- Complexity: {analysis.get('complexity', '?')}
- Functions: {len(analysis.get('entities', {}).get('function', []))}
- Issues: {len(analysis.get('issues', []))}

SEMANTIC UNDERSTANDING:
- Goal: {intent_understanding.get('primary_goal')}
- Constraints: {intent_understanding.get('constraints')}
- Risks: {intent_understanding.get('risks')}

CODE:
```python
{code}
```

Now reason step-by-step (use numbered steps):
1. First, identify what SPECIFICALLY needs to change
2. Then, list the SEQUENCE of transformations
3. For each step, explain the RATIONALE
4. Consider EDGE CASES and RISKS
5. Validate that CONSTRAINTS are maintained

Be specific and actionable.
"""
        
        response = self.llm.generate(reasoning_prompt)
        
        # Parse reasoning steps from response
        steps = self._parse_reasoning_steps(response)
        return steps
    
    async def _generate_transformation(
        self,
        code: str,
        reasoning_steps: List[ReasoningStep],
        transform_type: TransformationType
    ) -> str:
        """
        Generate the actual transformed code.
        
        Uses the reasoning steps as guidance for generation.
        """
        
        steps_text = "\n".join([
            f"Step {step.step_num}: {step.thought}\nAction: {step.action}"
            for step in reasoning_steps
        ])
        
        generation_prompt = f"""
Based on this reasoning, generate the transformed code:

{steps_text}

ORIGINAL CODE:
```python
{code}
```

Generate the COMPLETE transformed code that follows all the reasoning steps.
Ensure:
1. Code is syntactically correct Python
2. All steps are implemented
3. No breaking changes to interfaces (unless intentional)
4. Code is well-structured and readable
5. Comments explain non-obvious transformations

Return ONLY the code, wrapped in ```python blocks.
"""
        
        response = self.llm.generate(generation_prompt)
        
        # Extract code block from response
        transformed = self._extract_code_block(response)
        return transformed if transformed else code
    
    async def _validate_code(self, code: str) -> List[str]:
        """
        Validate generated code.
        
        Returns list of validation errors (empty if valid).
        """
        errors = []
        
        # Syntax validation
        try:
            ast.parse(code)
        except SyntaxError as e:
            errors.append(f"Syntax error at line {e.lineno}: {e.msg}")
        
        # Type checking
        type_errors = self._check_types(code)
        errors.extend(type_errors)
        
        # Code quality checks
        quality_issues = self.analyzer.analyze(code).get('issues', [])
        critical_issues = [
            issue for issue in quality_issues
            if isinstance(issue, dict) and issue.get('severity') == 'error'
        ]
        errors.extend([issue['message'] for issue in critical_issues])
        
        return errors
    
    def _check_types(self, code: str) -> List[str]:
        """Type check code using mypy."""
        try:
            result = subprocess.run(
                ['python', '-m', 'mypy', '-'],
                input=code,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            errors = []
            for line in result.stdout.split('\n'):
                if 'error' in line.lower():
                    errors.append(line)
            return errors
        
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return []
    
    def _calculate_confidence(
        self,
        reasoning_steps: List[ReasoningStep],
        validation_errors: List[str],
        analysis: Dict
    ) -> float:
        """Calculate confidence score for the transformation."""
        
        # Base confidence from reasoning quality
        reasoning_confidence = sum(
            step.confidence for step in reasoning_steps
        ) / len(reasoning_steps) if reasoning_steps else 0.5
        
        # Reduce for validation errors
        validation_penalty = min(0.2 * len(validation_errors), 0.5)
        
        # Reduce for existing issues
        existing_issues = len(analysis.get('issues', []))
        issue_penalty = min(0.1 * existing_issues, 0.3)
        
        final_confidence = max(
            reasoning_confidence - validation_penalty - issue_penalty,
            0.0
        )
        
        return min(final_confidence, 1.0)
    
    async def _generate_explanation(
        self,
        reasoning_steps: List[ReasoningStep],
        transform_type: TransformationType
    ) -> str:
        """Generate human-readable explanation of the transformation."""
        
        summary_prompt = f"""
Summarize this code transformation in 2-3 sentences:

Transformation Type: {transform_type.value}

Reasoning:
{chr(10).join([f"- {step.thought}" for step in reasoning_steps[:3]])}

Be clear and concise.
"""
        
        explanation = self.llm.generate(summary_prompt)
        return explanation
    
    # Helper methods
    
    def _extract_from_response(self, response: str, key: str) -> str:
        """Extract a specific section from LLM response."""
        lines = response.split('\n')
        result = []
        capturing = False
        
        for line in lines:
            if key.upper() in line.upper():
                capturing = True
                continue
            if capturing:
                if line.strip().startswith('-') or line.strip().startswith('•'):
                    result.append(line.strip())
                elif line.strip() and not line[0].isdigit():
                    break
        
        return '\n'.join(result) or "Not found"
    
    def _parse_reasoning_steps(self, response: str) -> List[ReasoningStep]:
        """Parse numbered reasoning steps from LLM response."""
        steps = []
        current_step = None
        
        for line in response.split('\n'):
            # Match numbered steps
            if line.strip() and line[0].isdigit():
                if current_step:
                    steps.append(current_step)
                
                step_num = int(line[0])
                thought = line.split('.', 1)[1].strip() if '.' in line else line
                current_step = ReasoningStep(
                    step_num=step_num,
                    thought=thought,
                    action=""
                )
            elif current_step and line.strip().startswith('Action:'):
                current_step.action = line.split(':', 1)[1].strip()
        
        if current_step:
            steps.append(current_step)
        
        return steps
    
    def _extract_code_block(self, response: str) -> Optional[str]:
        """Extract Python code block from LLM response."""
        lines = response.split('\n')
        in_block = False
        code_lines = []
        
        for line in lines:
            if '```python' in line or '```' in line:
                in_block = not in_block
                continue
            if in_block:
                code_lines.append(line)
        
        return '\n'.join(code_lines) if code_lines else None
