#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
JarvisCO Copilot-Level CLI

Interactive command-line interface for:
- Code analysis
- Semantic code transformation
- Reasoning and planning
- Output formatting

Author: JarvisCO
Date: 2025-12-30
"""

import sys
import argparse
import logging
import asyncio
import json
from pathlib import Path
from typing import Optional

from jarvisco.analyzer import CodeAnalyzer
from jarvisco.reasoner import CodeReasoner, TransformationType
from jarvisco.formatter import OutputFormatter
from jarvisco.mistral_llm import MistralLLM
from jarvisco import __version__

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JarvisoCLI:
    """Copilot-level CLI interface."""
    
    def __init__(self):
        """Initialize CLI."""
        self.llm = MistralLLM()
        self.analyzer = CodeAnalyzer()
        self.reasoner = CodeReasoner(self.llm)
        self.formatter = OutputFormatter()
    
    def load_code(self, path: str) -> str:
        """Load code from file."""
        try:
            return Path(path).read_text()
        except FileNotFoundError:
            logger.error(f"File not found: {path}")
            sys.exit(1)
    
    async def analyze(self, code_path: str, output_format: str = "markdown"):
        """Analyze code."""
        print(f"📊 Analyzing {code_path}...")
        
        code = self.load_code(code_path)
        analysis = self.analyzer.analyze(code)
        
        if not analysis.get("success"):
            print(f"❌ Analysis failed: {analysis.get('error')}")
            return
        
        # Format output
        formatted = self.formatter.format_code_documentation(
            analysis,
            style=output_format
        )
        
        print(formatted)
        
        # Optionally save
        if output_format == "markdown":
            output_file = Path(code_path).stem + "_analysis.md"
            Path(output_file).write_text(formatted)
            print(f"\n✓ Analysis saved to {output_file}")
    
    async def transform(
        self,
        code_path: str,
        intent: str,
        transform_type: str = "refactor",
        output_file: Optional[str] = None
    ):
        """Transform code."""
        print(f"🔄 Transforming code: {intent}")
        print(f"   Type: {transform_type}")
        
        code = self.load_code(code_path)
        transform_enum = TransformationType[transform_type.upper()]
        
        result = await self.reasoner.transform_code(
            code=code,
            intent=intent,
            transform_type=transform_enum
        )
        
        print(f"\n✓ Transformation confidence: {result.confidence_score:.0%}")
        
        if result.success:
            print(f"✓ Transformation successful")
            print(f"\n## Reasoning:")
            for step in result.reasoning_steps:
                print(f"  Step {step.step_num}: {step.thought}")
            
            print(f"\n## Transformed Code:")
            print("```python")
            print(result.transformed_code)
            print("```")
            
            if output_file:
                Path(output_file).write_text(result.transformed_code)
                print(f"\n✓ Saved to {output_file}")
            
            if result.validation_errors:
                print(f"\n⚠️ Validation warnings:")
                for error in result.validation_errors:
                    print(f"  - {error}")
        else:
            print(f"❌ Transformation failed")
            for error in result.validation_errors:
                print(f"  - {error}")
    
    async def refactor(
        self,
        code_path: str,
        aspect: str = "general",
        output_file: Optional[str] = None
    ):
        """Refactor code."""
        intents = {
            "general": "Refactor this code for better readability and maintainability",
            "performance": "Optimize this code for performance",
            "async": "Refactor this code to use async/await",
            "pythonic": "Make this code more Pythonic",
            "testing": "Refactor this code to be more testable",
        }
        
        intent = intents.get(aspect, intents["general"])
        await self.transform(code_path, intent, "refactor", output_file)
    
    async def document(self, code_path: str):
        """Generate documentation."""
        print(f"📚 Generating documentation for {code_path}...")
        
        code = self.load_code(code_path)
        analysis = self.analyzer.analyze(code)
        
        if not analysis.get("success"):
            print(f"❌ Analysis failed")
            return
        
        # Generate documentation
        doc = self.formatter.format_code_documentation(
            analysis,
            title=f"Documentation for {Path(code_path).name}",
            style="markdown"
        )
        
        # Save
        output_file = Path(code_path).stem + "_docs.md"
        Path(output_file).write_text(doc)
        
        print(f"✓ Documentation saved to {output_file}")
    
    async def report(self, code_path: str):
        """Generate analysis report."""
        print(f"📋 Generating report for {code_path}...")
        
        code = self.load_code(code_path)
        analysis = self.analyzer.analyze(code)
        
        if not analysis.get("success"):
            print(f"❌ Analysis failed")
            return
        
        report = self.formatter.format_analysis_report(
            analysis,
            include_issues=True,
            include_metrics=True,
            style="markdown"
        )
        
        # Save
        output_file = Path(code_path).stem + "_report.md"
        Path(output_file).write_text(report)
        
        print(f"✓ Report saved to {output_file}")
        
        # Print summary
        metrics = analysis.get("metrics", {})
        print(f"\n## Summary:")
        print(f"  Functions: {metrics.get('functions', 0)}")
        print(f"  Classes: {metrics.get('classes', 0)}")
        print(f"  Complexity: {analysis.get('complexity', 1)}/10")
        print(f"  Issues: {len(analysis.get('issues', []))}")
    
    async def test(self, code_path: str):
        """Generate test cases."""
        print(f"🧪 Generating tests for {code_path}...")
        
        code = self.load_code(code_path)
        
        # Use reasoner to generate tests
        result = await self.reasoner.transform_code(
            code=code,
            intent="Create comprehensive test cases for this code",
            transform_type=TransformationType.TEST
        )
        
        if result.success:
            # Save tests
            output_file = Path(code_path).stem + "_test.py"
            Path(output_file).write_text(result.transformed_code)
            print(f"✓ Tests generated and saved to {output_file}")
        else:
            print(f"❌ Test generation failed")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="JarvisCO - Copilot-Level Code Analysis & Transformation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  jarvisco analyze code.py
  jarvisco transform code.py "Refactor to use async/await"
  jarvisco refactor code.py --aspect performance
  jarvisco document code.py
  jarvisco report code.py
  jarvisco test code.py
        """
    )
    
    parser.add_argument("--version", action="version", version=f"JarvisCO {__version__}")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze code")
    analyze_parser.add_argument("code", help="Code file to analyze")
    analyze_parser.add_argument("--format", choices=["markdown", "html", "json"], default="markdown")
    
    # Transform command
    transform_parser = subparsers.add_parser("transform", help="Transform code")
    transform_parser.add_argument("code", help="Code file to transform")
    transform_parser.add_argument("intent", help="Transformation intent (natural language)")
    transform_parser.add_argument("--type", choices=[
        "refactor", "generate", "optimize", "fix_bug", "add_feature", "document", "test", "migrate"
    ], default="refactor")
    transform_parser.add_argument("--output", "-o", help="Output file")
    
    # Refactor command
    refactor_parser = subparsers.add_parser("refactor", help="Refactor code")
    refactor_parser.add_argument("code", help="Code file to refactor")
    refactor_parser.add_argument("--aspect", choices=[
        "general", "performance", "async", "pythonic", "testing"
    ], default="general")
    refactor_parser.add_argument("--output", "-o", help="Output file")
    
    # Document command
    subparsers.add_parser("document", help="Generate documentation").add_argument("code")
    
    # Report command
    subparsers.add_parser("report", help="Generate analysis report").add_argument("code")
    
    # Test command
    subparsers.add_parser("test", help="Generate test cases").add_argument("code")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    cli = JarvisoCLI()
    
    # Execute command
    if args.command == "analyze":
        asyncio.run(cli.analyze(args.code, args.format))
    elif args.command == "transform":
        asyncio.run(cli.transform(args.code, args.intent, args.type, args.output))
    elif args.command == "refactor":
        asyncio.run(cli.refactor(args.code, args.aspect, args.output))
    elif args.command == "document":
        asyncio.run(cli.document(args.code))
    elif args.command == "report":
        asyncio.run(cli.report(args.code))
    elif args.command == "test":
        asyncio.run(cli.test(args.code))


if __name__ == "__main__":
    main()
