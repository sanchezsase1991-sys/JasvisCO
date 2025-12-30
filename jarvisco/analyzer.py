#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
JarvisCO Code Analyzer - AST Parsing & Semantic Analysis

Provides deep code understanding through:
- AST parsing and analysis
- Type checking integration (mypy)
- Code pattern detection
- Dependency mapping
- Semantic structure extraction

Author: JarvisCO
Date: 2025-12-30
"""

import ast
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import subprocess
import json

logger = logging.getLogger(__name__)


@dataclass
class CodeEntity:
    """Represents a code entity (function, class, variable)."""
    name: str
    entity_type: str  # 'function', 'class', 'variable', 'import'
    line_start: int
    line_end: int
    docstring: Optional[str] = None
    parameters: List[str] = field(default_factory=list)
    return_type: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    is_public: bool = True
    complexity: int = 1  # Cyclomatic complexity
    references: List[str] = field(default_factory=list)
    

@dataclass
class CodeIssue:
    """Represents a code issue or pattern."""
    severity: str  # 'error', 'warning', 'info'
    category: str  # 'style', 'performance', 'security', 'maintainability'
    message: str
    line: int
    suggestion: Optional[str] = None
    

@dataclass
class TypeInfo:
    """Type information extracted from code."""
    name: str
    type_hint: str
    inferred_type: Optional[str] = None
    is_optional: bool = False
    confidence: float = 1.0


class CodeAnalyzer:
    """Deep code analysis using AST and type checking."""
    
    def __init__(self):
        """Initialize analyzer."""
        self.entities: Dict[str, List[CodeEntity]] = {}
        self.issues: List[CodeIssue] = []
        self.types: Dict[str, TypeInfo] = {}
        self.imports: List[Tuple[str, str]] = []
        self.dependencies: Dict[str, List[str]] = {}
        
    def analyze(self, code: str, filename: str = "<stdin>") -> Dict[str, Any]:
        """
        Analyze code comprehensively.
        
        Args:
            code: Source code to analyze
            filename: Filename for context
            
        Returns:
            Dictionary with analysis results
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            logger.error(f"Syntax error in {filename}: {e}")
            return {
                "success": False,
                "error": str(e),
                "line": e.lineno
            }
        
        # Extract entities
        self._extract_entities(tree)
        
        # Extract imports
        self._extract_imports(tree)
        
        # Analyze complexity
        self._analyze_complexity(tree)
        
        # Type inference
        self._infer_types(tree)
        
        # Style and quality checks
        self._check_code_quality(tree, code)
        
        # Type checking with mypy (if available)
        self._run_mypy_check(code, filename)
        
        return {
            "success": True,
            "entities": self._serialize_entities(),
            "issues": self._serialize_issues(),
            "types": self._serialize_types(),
            "imports": self.imports,
            "dependencies": self.dependencies,
            "metrics": self._calculate_metrics(),
            "complexity": self._get_overall_complexity()
        }
    
    def _extract_entities(self, tree: ast.AST) -> None:
        """Extract functions, classes, and variables."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self._extract_function(node)
            elif isinstance(node, ast.ClassDef):
                self._extract_class(node)
            elif isinstance(node, ast.Assign):
                self._extract_variable(node)
    
    def _extract_function(self, node: ast.FunctionDef) -> None:
        """Extract function information."""
        entity = CodeEntity(
            name=node.name,
            entity_type='function',
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            docstring=ast.get_docstring(node),
            parameters=[arg.arg for arg in node.args.args],
            is_public=not node.name.startswith('_'),
            decorators=[
                d.id if isinstance(d, ast.Name) else ast.unparse(d)
                for d in node.decorator_list
            ]
        )
        
        # Extract return type annotation
        if node.returns:
            entity.return_type = ast.unparse(node.returns)
        
        if 'function' not in self.entities:
            self.entities['function'] = []
        self.entities['function'].append(entity)
    
    def _extract_class(self, node: ast.ClassDef) -> None:
        """Extract class information."""
        entity = CodeEntity(
            name=node.name,
            entity_type='class',
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            docstring=ast.get_docstring(node),
            is_public=not node.name.startswith('_')
        )
        
        if 'class' not in self.entities:
            self.entities['class'] = []
        self.entities['class'].append(entity)
    
    def _extract_variable(self, node: ast.Assign) -> None:
        """Extract variable assignments."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                entity = CodeEntity(
                    name=target.id,
                    entity_type='variable',
                    line_start=node.lineno,
                    line_end=node.end_lineno or node.lineno,
                    is_public=not target.id.startswith('_')
                )
                
                if 'variable' not in self.entities:
                    self.entities['variable'] = []
                self.entities['variable'].append(entity)
    
    def _extract_imports(self, tree: ast.AST) -> None:
        """Extract import statements."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.imports.append(('import', alias.name))
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    self.imports.append(('from', f"{node.module}.{alias.name}"))
    
    def _analyze_complexity(self, tree: ast.AST) -> None:
        """Analyze cyclomatic complexity."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_function_complexity(node)
                for entity in self.entities.get('function', []):
                    if entity.name == node.name:
                        entity.complexity = complexity
                        break
    
    def _calculate_function_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity
    
    def _infer_types(self, tree: ast.AST) -> None:
        """Infer types from annotations and usage."""
        # Extract type annotations
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for arg in node.args.args:
                    if arg.annotation:
                        type_str = ast.unparse(arg.annotation)
                        self.types[arg.arg] = TypeInfo(
                            name=arg.arg,
                            type_hint=type_str
                        )
    
    def _check_code_quality(self, tree: ast.AST, code: str) -> None:
        """Check code quality issues."""
        lines = code.split('\n')
        
        # Check for long functions
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_length = (node.end_lineno or node.lineno) - node.lineno
                if func_length > 50:
                    self.issues.append(CodeIssue(
                        severity='warning',
                        category='maintainability',
                        message=f"Function '{node.name}' is {func_length} lines long",
                        line=node.lineno,
                        suggestion="Consider breaking into smaller functions"
                    ))
        
        # Check for missing docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node) and node.name.startswith('_') is False:
                    self.issues.append(CodeIssue(
                        severity='info',
                        category='maintainability',
                        message=f"Missing docstring for {node.__class__.__name__} '{node.name}'",
                        line=node.lineno,
                        suggestion="Add docstring documentation"
                    ))
    
    def _run_mypy_check(self, code: str, filename: str) -> None:
        """Run mypy type checking."""
        try:
            # Write code to temp file
            temp_file = Path(f"/tmp/{filename}")
            temp_file.write_text(code)
            
            # Run mypy
            result = subprocess.run(
                ['mypy', str(temp_file), '--ignore-missing-imports'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Parse mypy output
            for line in result.stdout.split('\n'):
                if ':' in line and 'error' in line.lower():
                    parts = line.split(':')
                    if len(parts) >= 3:
                        try:
                            line_num = int(parts[1])
                            message = ':'.join(parts[3:]).strip()
                            self.issues.append(CodeIssue(
                                severity='error',
                                category='type',
                                message=message,
                                line=line_num
                            ))
                        except (ValueError, IndexError):
                            pass
        
        except (FileNotFoundError, subprocess.TimeoutExpired):
            logger.debug("mypy not available or timed out")
    
    def _calculate_metrics(self) -> Dict[str, Any]:
        """Calculate code metrics."""
        total_lines = sum(
            e.line_end - e.line_start
            for entities in self.entities.values()
            for e in entities
        )
        
        return {
            "total_entities": sum(len(e) for e in self.entities.values()),
            "functions": len(self.entities.get('function', [])),
            "classes": len(self.entities.get('class', [])),
            "variables": len(self.entities.get('variable', [])),
            "imports": len(self.imports),
            "total_lines": total_lines,
            "issues_count": len(self.issues),
            "issues_by_severity": self._count_issues_by_severity()
        }
    
    def _count_issues_by_severity(self) -> Dict[str, int]:
        """Count issues by severity."""
        counts = {'error': 0, 'warning': 0, 'info': 0}
        for issue in self.issues:
            counts[issue.severity] = counts.get(issue.severity, 0) + 1
        return counts
    
    def _get_overall_complexity(self) -> int:
        """Get overall code complexity score."""
        if not self.entities.get('function'):
            return 1
        
        avg_complexity = sum(
            f.complexity for f in self.entities['function']
        ) / len(self.entities['function'])
        
        return int(avg_complexity)
    
    def _serialize_entities(self) -> Dict[str, List[Dict]]:
        """Serialize entities to dictionary."""
        result = {}
        for entity_type, entities in self.entities.items():
            result[entity_type] = [
                {
                    "name": e.name,
                    "line_start": e.line_start,
                    "line_end": e.line_end,
                    "docstring": e.docstring,
                    "parameters": e.parameters,
                    "return_type": e.return_type,
                    "decorators": e.decorators,
                    "is_public": e.is_public,
                    "complexity": e.complexity
                }
                for e in entities
            ]
        return result
    
    def _serialize_issues(self) -> List[Dict]:
        """Serialize issues to dictionary."""
        return [
            {
                "severity": i.severity,
                "category": i.category,
                "message": i.message,
                "line": i.line,
                "suggestion": i.suggestion
            }
            for i in self.issues
        ]
    
    def _serialize_types(self) -> Dict[str, Dict]:
        """Serialize types to dictionary."""
        return {
            name: {
                "type_hint": t.type_hint,
                "inferred_type": t.inferred_type,
                "is_optional": t.is_optional,
                "confidence": t.confidence
            }
            for name, t in self.types.items()
        }
    
    def suggest_refactoring(self, code: str) -> List[str]:
        """
        Suggest refactoring improvements.
        
        Returns:
            List of refactoring suggestions
        """
        suggestions = []
        
        analysis = self.analyze(code)
        
        # Suggest based on complexity
        if analysis['complexity'] > 5:
            suggestions.append("Consider reducing complexity by breaking into smaller functions")
        
        # Suggest based on issues
        for issue in self.issues:
            if issue.suggestion:
                suggestions.append(issue.suggestion)
        
        # Suggest based on metrics
        metrics = analysis['metrics']
        if metrics['total_lines'] > 500:
            suggestions.append("File is large. Consider splitting into modules")
        
        if metrics['functions'] > 30:
            suggestions.append("Too many functions in one module. Consider better organization")
        
        return suggestions
