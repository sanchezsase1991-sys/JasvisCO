#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
JarvisCO Code Reasoning Agent - Copilot-Level Orchestration

Orchestrates code analysis, reasoning, transformation, and validation.
Integrates CodeAnalyzer, CodeReasoner, and OutputFormatter.

Author: JarvisCO
Date: 2025-12-30
"""

import logging
import asyncio
import json
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from jarvisco.analyzer import CodeAnalyzer
from jarvisco.reasoner import CodeReasoner, TransformationType
from jarvisco.formatter import OutputFormatter
from jarvisco.mistral_llm import MistralLLM

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    ANALYZING = "analyzing"
    REASONING = "reasoning"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class CodeTask:
    """Copilot-level code task."""
    id: str
    description: str  # Natural language description
    code: str         # Code to analyze/transform
    transform_type: TransformationType = TransformationType.REFACTOR
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    
    # Results
    analysis_result: Optional[Dict] = None
    reasoning_result: Optional[Dict] = None
    formatted_output: Optional[str] = None
    
    # Tracking
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "transform_type": self.transform_type.value,
            "status": self.status.value,
            "analysis": self.analysis_result,
            "reasoning": self.reasoning_result,
            "output": self.formatted_output,
            "error": self.error
        }


class CodeReasoningAgent:
    """
    Copilot-level agent that orchestrates:
    1. Code analysis (CodeAnalyzer)
    2. Semantic reasoning (CodeReasoner)
    3. Output formatting (OutputFormatter)
    """
    
    def __init__(self, llm: Optional[MistralLLM] = None):
        """Initialize agent."""
        self.llm = llm or MistralLLM()
        self.analyzer = CodeAnalyzer()
        self.reasoner = CodeReasoner(self.llm)
        self.formatter = OutputFormatter()
        
        self.tasks: Dict[str, CodeTask] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.completed_tasks: List[CodeTask] = []
        self.failed_tasks: List[CodeTask] = []
        
        self.running = False
        
        logger.info("CodeReasoningAgent initialized")
    
    async def initialize(self) -> None:
        """Initialize agent resources."""
        logger.info("Initializing CodeReasoningAgent resources...")
        # LLM is already initialized in __init__
        logger.info("✓ Agent ready for code reasoning")
    
    def create_task(
        self,
        description: str,
        code: str,
        transform_type: TransformationType = TransformationType.REFACTOR,
        priority: TaskPriority = TaskPriority.NORMAL
    ) -> CodeTask:
        """Create a new code task."""
        task_id = f"task_{len(self.tasks)}_{int(datetime.now().timestamp() * 1000)}"
        task = CodeTask(
            id=task_id,
            description=description,
            code=code,
            transform_type=transform_type,
            priority=priority
        )
        self.tasks[task_id] = task
        logger.info(f"Created task: {task_id}")
        return task
    
    async def submit_task(self, task: CodeTask) -> None:
        """Submit task for execution."""
        await self.task_queue.put(task)
        logger.info(f"Submitted task: {task.id}")
    
    async def process_tasks(self) -> None:
        """Process task queue (main agent loop)."""
        self.running = True
        active_tasks = []
        
        logger.info("CodeReasoningAgent started processing tasks")
        
        while self.running:
            try:
                # Get task from queue (with timeout)
                try:
                    task = self.task_queue.get_nowait()
                except asyncio.QueueEmpty:
                    await asyncio.sleep(0.1)
                    continue
                
                # Execute task
                exec_task = asyncio.create_task(self._process_task(task))
                active_tasks.append(exec_task)
                
            except Exception as e:
                logger.error(f"Error in process_tasks: {e}")
                await asyncio.sleep(1)
    
    async def _process_task(self, task: CodeTask) -> None:
        """Process a single code task through the full pipeline."""
        try:
            task.started_at = datetime.now()
            task.status = TaskStatus.ANALYZING
            
            logger.info(f"Processing task {task.id}: {task.description}")
            
            # STEP 1: Analysis
            logger.info(f"[{task.id}] STEP 1: Analyzing code...")
            task.analysis_result = self.analyzer.analyze(task.code)
            
            if not task.analysis_result.get("success"):
                raise Exception(f"Code analysis failed: {task.analysis_result.get('error')}")
            
            # STEP 2: Reasoning (Core Copilot)
            logger.info(f"[{task.id}] STEP 2: Reasoning about transformation...")
            task.status = TaskStatus.REASONING
            
            reasoning_result = await self.reasoner.transform_code(
                code=task.code,
                intent=task.description,
                transform_type=task.transform_type,
                context=json.dumps(task.analysis_result.get("metrics", {}))
            )
            
            task.reasoning_result = {
                "success": reasoning_result.success,
                "confidence": reasoning_result.confidence_score,
                "transformed_code": reasoning_result.transformed_code,
                "reasoning_steps": [
                    {
                        "step": step.step_num,
                        "thought": step.thought,
                        "action": step.action,
                        "confidence": step.confidence
                    }
                    for step in reasoning_result.reasoning_steps
                ],
                "validation_errors": reasoning_result.validation_errors,
                "explanation": reasoning_result.explanation
            }
            
            # STEP 3: Formatting
            logger.info(f"[{task.id}] STEP 3: Formatting output...")
            task.status = TaskStatus.EXECUTING
            
            task.formatted_output = self.formatter.format_transformation_report(
                task.reasoning_result
            )
            
            # Completion
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            self.completed_tasks.append(task)
            
            logger.info(f"✓ Task completed: {task.id}")
            logger.info(f"  Confidence: {task.reasoning_result.get('confidence', 0):.0%}")
            
        except Exception as e:
            logger.error(f"Task failed: {task.id} - {e}")
            task.error = str(e)
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()
            self.failed_tasks.append(task)
    
    async def analyze_code(self, code: str) -> Dict:
        """Quick code analysis (without reasoning)."""
        return self.analyzer.analyze(code)
    
    async def reason_transformation(
        self,
        code: str,
        intent: str,
        transform_type: TransformationType = TransformationType.REFACTOR
    ) -> Dict:
        """Quick reasoning about transformation."""
        result = await self.reasoner.transform_code(
            code=code,
            intent=intent,
            transform_type=transform_type
        )
        return {
            "success": result.success,
            "code": result.transformed_code,
            "confidence": result.confidence_score,
            "explanation": result.explanation,
            "errors": result.validation_errors
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status."""
        return {
            "running": self.running,
            "total_tasks": len(self.tasks),
            "completed": len(self.completed_tasks),
            "failed": len(self.failed_tasks),
            "queue_size": self.task_queue.qsize()
        }
    
    def get_task_result(self, task_id: str) -> Optional[CodeTask]:
        """Get result of completed task."""
        return self.tasks.get(task_id)
    
    async def shutdown(self) -> None:
        """Shutdown agent."""
        logger.info("Shutting down CodeReasoningAgent...")
        self.running = False
        logger.info("Agent shutdown complete")


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="JarvisCO Code Reasoning Agent")
    parser.add_argument("--code", help="Code file to analyze")
    parser.add_argument("--intent", help="Transformation intent")
    parser.add_argument("--type", choices=["refactor", "generate", "optimize", "fix_bug", "add_feature", "document", "test", "migrate"],
                       default="refactor", help="Transformation type")
    args = parser.parse_args()
    
    agent = CodeReasoningAgent()
    await agent.initialize()
    
    if args.code and args.intent:
        # Single task mode
        code = open(args.code).read() if args.code else ""
        result = await agent.reason_transformation(
            code=code,
            intent=args.intent,
            transform_type=TransformationType[args.type.upper()]
        )
        print(json.dumps(result, indent=2))
    else:
        # Service mode
        logger.info("Agent ready. Waiting for tasks...")
        try:
            await agent.process_tasks()
        except KeyboardInterrupt:
            logger.info("Shutdown requested")
        finally:
            await agent.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
