#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
JarvisCO API Server - Copilot-Level REST API

FastAPI server exposing:
- Code analysis endpoints
- Semantic reasoning endpoints
- Output formatting endpoints
- Task management endpoints

Author: JarvisCO
Date: 2025-12-30
"""

import logging
from contextlib import asynccontextmanager
from typing import Optional
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from jarvisco.analyzer import CodeAnalyzer
from jarvisco.reasoner import CodeReasoner, TransformationType
from jarvisco.formatter import OutputFormatter
from jarvisco.mistral_llm import MistralLLM
from jarvisco.agent import CodeReasoningAgent
from jarvisco import __version__

logger = logging.getLogger(__name__)

# Global instances
llm_instance: Optional[MistralLLM] = None
agent_instance: Optional[CodeReasoningAgent] = None
analyzer = CodeAnalyzer()
formatter = OutputFormatter()


# Pydantic models

class CodeAnalysisRequest(BaseModel):
    """Request for code analysis."""
    code: str = Field(..., description="Code to analyze")


class CodeAnalysisResponse(BaseModel):
    """Response from code analysis."""
    success: bool
    entities: dict
    issues: list
    metrics: dict
    complexity: int


class TransformationRequest(BaseModel):
    """Request for code transformation."""
    code: str = Field(..., description="Code to transform")
    intent: str = Field(..., description="Transformation intent")
    transform_type: str = Field("refactor", description="Type of transformation")
    context: Optional[str] = Field(None, description="Additional context")


class TransformationResponse(BaseModel):
    """Response from code transformation."""
    success: bool
    transformed_code: Optional[str]
    confidence: float
    explanation: str
    reasoning_steps: list
    validation_errors: list


class FormattingRequest(BaseModel):
    """Request for output formatting."""
    data: dict = Field(..., description="Data to format")
    format_type: str = Field("documentation", description="Format type")
    style: str = Field("markdown", description="Output style")


# Lifespan events

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan."""
    global llm_instance, agent_instance
    
    logger.info("Starting JarvisCO API Server (Copilot-Level)...")
    try:
        llm_instance = MistralLLM(model_name="mistral-7b-instruct", device="auto")
        agent_instance = CodeReasoningAgent(llm_instance)
        await agent_instance.initialize()
        logger.info("✓ Server initialized - Copilot-level services ready")
    except Exception as e:
        logger.error(f"Failed to initialize: {e}")
        raise
    
    yield
    
    logger.info("Shutting down JarvisCO API Server...")
    if agent_instance:
        await agent_instance.shutdown()


# Create FastAPI app

app = FastAPI(
    title="JarvisCO Copilot-Level API",
    description="Intelligent code analysis, reasoning, and transformation",
    version=__version__,
    lifespan=lifespan
)


# Health & Info endpoints

@app.get("/health")
async def health():
    """Health check."""
    return {
        "status": "healthy",
        "version": __version__,
        "services": {
            "analyzer": "ready",
            "reasoner": llm_instance is not None,
            "formatter": True
        }
    }


@app.get("/info")
async def info():
    """API information."""
    return {
        "name": "JarvisCO",
        "version": __version__,
        "level": "Copilot",
        "description": "Code analysis, reasoning, and transformation engine",
        "endpoints": {
            "analysis": "/analyze",
            "transformation": "/transform",
            "formatting": "/format",
            "tasks": "/tasks"
        }
    }


# Analysis endpoints

@app.post("/analyze", response_model=CodeAnalysisResponse)
async def analyze(request: CodeAnalysisRequest):
    """Analyze code structure and quality."""
    if not llm_instance:
        raise HTTPException(status_code=503, detail="Analyzer not loaded")
    
    try:
        result = analyzer.analyze(request.code)
        return CodeAnalysisResponse(
            success=result["success"],
            entities=result.get("entities", {}),
            issues=result.get("issues", []),
            metrics=result.get("metrics", {}),
            complexity=result.get("complexity", 1)
        )
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Reasoning endpoints

@app.post("/transform", response_model=TransformationResponse)
async def transform(request: TransformationRequest):
    """Transform code using semantic reasoning."""
    if not agent_instance:
        raise HTTPException(status_code=503, detail="Agent not loaded")
    
    try:
        transform_type = TransformationType[request.transform_type.upper()]
        result = await agent_instance.reason_transformation(
            code=request.code,
            intent=request.intent,
            transform_type=transform_type
        )
        
        return TransformationResponse(
            success=result["success"],
            transformed_code=result.get("code"),
            confidence=result.get("confidence", 0),
            explanation=result.get("explanation", ""),
            reasoning_steps=result.get("reasoning_steps", []),
            validation_errors=result.get("errors", [])
        )
    except Exception as e:
        logger.error(f"Transformation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Formatting endpoints

@app.post("/format")
async def format_output(request: FormattingRequest):
    """Format analysis/transformation output."""
    try:
        if request.format_type == "documentation":
            output = formatter.format_code_documentation(request.data, style=request.style)
        elif request.format_type == "report":
            output = formatter.format_analysis_report(request.data, style=request.style)
        elif request.format_type == "transformation":
            output = formatter.format_transformation_report(request.data, style=request.style)
        else:
            raise ValueError(f"Unknown format type: {request.format_type}")
        
        return {"formatted_output": output}
    except Exception as e:
        logger.error(f"Formatting error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# Task management endpoints

@app.post("/tasks/create")
async def create_task(request: TransformationRequest):
    """Create a new code reasoning task."""
    if not agent_instance:
        raise HTTPException(status_code=503, detail="Agent not loaded")
    
    try:
        transform_type = TransformationType[request.transform_type.upper()]
        task = agent_instance.create_task(
            description=request.intent,
            code=request.code,
            transform_type=transform_type
        )
        return {"task_id": task.id, "status": task.status.value}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/tasks/{task_id}/submit")
async def submit_task(task_id: str, background_tasks: BackgroundTasks):
    """Submit task for processing."""
    if not agent_instance:
        raise HTTPException(status_code=503, detail="Agent not loaded")
    
    task = agent_instance.tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    try:
        background_tasks.add_task(agent_instance.submit_task, task)
        return {"task_id": task_id, "message": "Task submitted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """Get task status and results."""
    if not agent_instance:
        raise HTTPException(status_code=503, detail="Agent not loaded")
    
    task = agent_instance.get_task_result(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task.to_dict()


@app.get("/tasks/status")
async def get_agent_status():
    """Get agent status."""
    if not agent_instance:
        raise HTTPException(status_code=503, detail="Agent not loaded")
    
    return agent_instance.get_status()


# Error handlers

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return {"error": exc.detail, "status_code": exc.status_code}


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return {"error": "Internal server error", "status_code": 500}


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="JarvisCO Copilot-Level API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--workers", type=int, default=1, help="Number of workers")
    
    args = parser.parse_args()
    
    logger.info(f"Starting server on {args.host}:{args.port}")
    logger.info(f"API Docs: http://{args.host}:{args.port}/docs")
    
    uvicorn.run(
        "jarvisco.server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers
    )


if __name__ == "__main__":
    main()
