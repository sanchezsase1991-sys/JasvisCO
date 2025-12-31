#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Setup configuration for JarvisCO package.

JarvisCO is an intelligent automation and orchestration platform
designed to streamline workflow management and intelligent task execution.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="JarvisCO",
    version="1.0.0",
    author="sanchezsase1991-sys",
    author_email="dev@jarvisco.local",
    description="Copilot-Level Code Analysis, Reasoning & Transformation Engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sanchezsase1991-sys/JasvisCO",
    project_urls={
        "Bug Tracker": "https://github.com/sanchezsase1991-sys/JasvisCO/issues",
        "Documentation": "https://github.com/sanchezsase1991-sys/JasvisCO/wiki",
        "Source Code": "https://github.com/sanchezsase1991-sys/JasvisCO",
    },
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
        "Topic :: Office/Business",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=22.0",
            "flake8>=4.0",
            "isort>=5.0",
            "mypy>=0.990",
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
            "sphinx-autodoc-typehints>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "jarvisco=jarvisco.cli:main",
            "jarvisco-server=jarvisco.server:main",
            "jarvisco-agent=jarvisco.agent:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="automation orchestration workflow intelligence task-management",
    license="MIT",
    platforms=["any"],
)
