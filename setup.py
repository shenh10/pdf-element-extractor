#!/usr/bin/env python3
"""
Setup script for PDF Element Extractor package.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "PDF Element Extractor - A Python package for automatically identifying and extracting Figure and Table elements from PDF documents."

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return [
        'PyMuPDF>=1.23.0',
        'Pillow>=9.0.0',
        'numpy>=1.21.0'
    ]

setup(
    name="pdf-element-extractor",
    version="1.0.0",
    author="PDF Element Extractor Team",
    author_email="support@pdf-element-extractor.com",
    description="A Python package for automatically identifying and extracting Figure and Table elements from PDF documents",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/pdf-element-extractor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "pdf-element-extractor=pdf_element_extractor.core.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "pdf_element_extractor": ["*.md", "*.txt"],
    },
    keywords="pdf, extraction, figure, table, document processing, computer vision",
    project_urls={
        "Bug Reports": "https://github.com/your-username/pdf-element-extractor/issues",
        "Source": "https://github.com/your-username/pdf-element-extractor",
        "Documentation": "https://github.com/your-username/pdf-element-extractor#readme",
    },
) 