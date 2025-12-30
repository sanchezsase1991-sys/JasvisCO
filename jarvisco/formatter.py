#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
JarvisCO Formatter - RosaENLG Integration & Output Formatting

Handles structured output generation using RosaENLG templates:
- Documentation generation
- Report formatting
- Code analysis output
- Test documentation

Author: JarvisCO
Date: 2025-12-30
"""

import logging
import json
from typing import Dict, List, Any, Optional
from dataclasses import asdict
from pathlib import Path
import jinja2

try:
    from rosaenlg import RosaENLG
    ROSAENLG_AVAILABLE = True
except ImportError:
    ROSAENLG_AVAILABLE = False
    logging.warning("RosaENLG not available, using Jinja2 fallback")

logger = logging.getLogger(__name__)


class OutputFormatter:
    """
    Formats code analysis and generation output using RosaENLG.
    
    Features:
    - Professional documentation generation
    - Structured report formatting
    - Code analysis visualization
    - Test documentation
    """
    
    def __init__(self):
        """Initialize formatter with templates."""
        self.rosaenlg_available = ROSAENLG_AVAILABLE
        self.jinja_env = jinja2.Environment(
            loader=jinja2.DictLoader(self._get_templates()),
            autoescape=True
        )
        self.template_cache = {}
    
    def format_code_documentation(
        self,
        code_analysis: Dict[str, Any],
        title: str = "Code Documentation",
        style: str = "markdown"
    ) -> str:
        """
        Generate formatted documentation for code.
        
        Args:
            code_analysis: Analysis result from CodeAnalyzer
            title: Documentation title
            style: Output format ('markdown', 'html', 'text')
            
        Returns:
            Formatted documentation string
        """
        
        template_name = f"code_documentation_{style}"
        template_data = {
            "title": title,
            "entities": code_analysis.get("entities", {}),
            "metrics": code_analysis.get("metrics", {}),
            "issues": code_analysis.get("issues", []),
            "types": code_analysis.get("types", {}),
            "complexity": code_analysis.get("complexity", 1)
        }
        
        return self._render_template(template_name, template_data)
    
    def format_analysis_report(
        self,
        analysis_data: Dict[str, Any],
        include_issues: bool = True,
        include_metrics: bool = True,
        style: str = "markdown"
    ) -> str:
        """
        Generate professional analysis report.
        
        Args:
            analysis_data: Code analysis data
            include_issues: Include code issues in report
            include_metrics: Include metrics in report
            style: Output format
            
        Returns:
            Formatted report
        """
        
        template_name = f"analysis_report_{style}"
        template_data = {
            "analysis": analysis_data,
            "include_issues": include_issues,
            "include_metrics": include_metrics,
            "timestamp": self._get_timestamp()
        }
        
        if include_issues:
            template_data["critical_issues"] = [
                i for i in analysis_data.get("issues", [])
                if isinstance(i, dict) and i.get("severity") == "error"
            ]
            template_data["warnings"] = [
                i for i in analysis_data.get("issues", [])
                if isinstance(i, dict) and i.get("severity") == "warning"
            ]
        
        if include_metrics:
            template_data["metrics"] = analysis_data.get("metrics", {})
        
        return self._render_template(template_name, template_data)
    
    def format_transformation_report(
        self,
        transformation_result: Dict[str, Any],
        style: str = "markdown"
    ) -> str:
        """
        Format code transformation results.
        
        Args:
            transformation_result: Result from CodeReasoner
            style: Output format
            
        Returns:
            Formatted report
        """
        
        template_name = f"transformation_report_{style}"
        template_data = {
            "success": transformation_result.get("success"),
            "confidence": transformation_result.get("confidence_score"),
            "explanation": transformation_result.get("explanation", ""),
            "reasoning_steps": transformation_result.get("reasoning_steps", []),
            "validation_errors": transformation_result.get("validation_errors", []),
            "timestamp": self._get_timestamp()
        }
        
        return self._render_template(template_name, template_data)
    
    def format_test_documentation(
        self,
        code: str,
        test_cases: List[Dict[str, Any]],
        style: str = "markdown"
    ) -> str:
        """
        Generate formatted test documentation.
        
        Args:
            code: Code being tested
            test_cases: List of test cases
            style: Output format
            
        Returns:
            Formatted test documentation
        """
        
        template_name = f"test_documentation_{style}"
        template_data = {
            "code": code,
            "test_cases": test_cases,
            "total_tests": len(test_cases),
            "timestamp": self._get_timestamp()
        }
        
        return self._render_template(template_name, template_data)
    
    def _render_template(self, template_name: str, data: Dict[str, Any]) -> str:
        """Render a template with data."""
        try:
            if self.rosaenlg_available and "rosaenlg" in template_name.lower():
                return self._render_with_rosaenlg(template_name, data)
            else:
                return self._render_with_jinja2(template_name, data)
        except Exception as e:
            logger.error(f"Template rendering error: {e}")
            return json.dumps(data, indent=2)
    
    def _render_with_jinja2(self, template_name: str, data: Dict) -> str:
        """Render template using Jinja2 (fallback)."""
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**data)
        except jinja2.TemplateNotFound:
            logger.warning(f"Template not found: {template_name}")
            return self._fallback_format(template_name, data)
    
    def _render_with_rosaenlg(self, template_name: str, data: Dict) -> str:
        """Render template using RosaENLG."""
        try:
            engine = RosaENLG()
            # RosaENLG rendering logic
            # (Would depend on RosaENLG API)
            return engine.render(template_name, data)
        except Exception as e:
            logger.warning(f"RosaENLG rendering failed: {e}, falling back to Jinja2")
            return self._render_with_jinja2(template_name, data)
    
    def _get_templates(self) -> Dict[str, str]:
        """Get built-in Jinja2 templates."""
        return {
            "code_documentation_markdown": """# {{ title }}

## Overview
Generated on {{ timestamp }}

## Entities

{% for entity_type, entities in entities.items() %}
### {{ entity_type|title }}s
{% for entity in entities %}
- **{{ entity.name }}** (line {{ entity.line_start }}-{{ entity.line_end }})
  {% if entity.docstring %}
  > {{ entity.docstring }}
  {% endif %}
  {% if entity.parameters %}
  - Parameters: {{ entity.parameters|join(', ') }}
  {% endif %}
  {% if entity.complexity and entity.complexity > 1 %}
  - Complexity: {{ entity.complexity }}
  {% endif %}
{% endfor %}
{% endfor %}

## Metrics
- Total Entities: {{ metrics.total_entities }}
- Functions: {{ metrics.functions }}
- Classes: {{ metrics.classes }}
- Imports: {{ metrics.imports }}
- Overall Complexity: {{ complexity }}/10

## Code Quality
{% if issues %}
Found {{ issues|length }} issue(s):
{% for issue in issues %}
- **{{ issue.severity|upper }}** ({{ issue.category }}): {{ issue.message }} (line {{ issue.line }})
  {% if issue.suggestion %}
  → {{ issue.suggestion }}
  {% endif %}
{% endfor %}
{% else %}
✓ No major issues found
{% endif %}
""",

            "analysis_report_markdown": """# Code Analysis Report

Generated: {{ timestamp }}

## Summary
- **Files Analyzed**: 1
- **Total Issues**: {{ analysis.issues|length if analysis.issues else 0 }}
- **Complexity**: {{ analysis.complexity or 'N/A' }}

## Issues
{% if include_issues and critical_issues %}
### Critical Issues ({{ critical_issues|length }})
{% for issue in critical_issues %}
- [{{ issue.line }}] {{ issue.message }}
{% endfor %}
{% endif %}

{% if include_issues and warnings %}
### Warnings ({{ warnings|length }})
{% for issue in warnings %}
- [{{ issue.line }}] {{ issue.message }}
{% endfor %}
{% endif %}

## Metrics
{% if include_metrics and metrics %}
{% for key, value in metrics.items() %}
- **{{ key }}**: {{ value }}
{% endfor %}
{% endif %}

## Recommendations
Based on the analysis, consider:
1. Addressing critical issues first
2. Refactoring high-complexity functions
3. Adding documentation for public APIs
4. Improving code organization
""",

            "transformation_report_markdown": """# Code Transformation Report

Generated: {{ timestamp }}
Status: {% if success %}✓ Success{% else %}✗ Failed{% endif %}
Confidence: {{ confidence * 100|int }}%

## Transformation Process

{% for step in reasoning_steps %}
### Step {{ step.step_num }}: {{ step.thought }}
**Action**: {{ step.action }}
{% if step.code_snippet %}
```python
{{ step.code_snippet }}
```
{% endif %}
{% endfor %}

## Result
{{ explanation }}

{% if validation_errors %}
## Validation Issues
{% for error in validation_errors %}
- ⚠️ {{ error }}
{% endfor %}
{% else %}
## Validation
✓ Code passed all validation checks
{% endif %}
""",

            "test_documentation_markdown": """# Test Documentation

Total Tests: {{ total_tests }}
Generated: {{ timestamp }}

## Test Cases

{% for test_case in test_cases %}
### {{ test_case.name }}
**Description**: {{ test_case.description or 'No description' }}

{% if test_case.inputs %}
**Inputs**:
{% for input in test_case.inputs %}
- `{{ input.name }}`: {{ input.type }}
{% endfor %}
{% endif %}

**Expected Result**: {{ test_case.expected_result or 'N/A' }}

{% if test_case.edge_cases %}
**Edge Cases**:
{% for edge_case in test_case.edge_cases %}
- {{ edge_case }}
{% endfor %}
{% endif %}
---
{% endfor %}
"""
        }
    
    def _fallback_format(self, template_name: str, data: Dict) -> str:
        """Fallback formatting when templates not found."""
        if "markdown" in template_name:
            return f"# Output\n\n```json\n{json.dumps(data, indent=2)}\n```"
        else:
            return json.dumps(data, indent=2)
    
    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Convenience functions

def format_code_analysis(analysis: Dict[str, Any]) -> str:
    """Quick function to format code analysis."""
    formatter = OutputFormatter()
    return formatter.format_code_documentation(analysis)


def format_report(analysis: Dict[str, Any]) -> str:
    """Quick function to generate analysis report."""
    formatter = OutputFormatter()
    return formatter.format_analysis_report(analysis)
