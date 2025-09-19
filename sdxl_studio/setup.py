#!/usr/bin/env python3
"""
Setup script for SDXL Studio
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text() if readme_path.exists() else ""

setup(
    name="sdxl-studio",
    version="1.0.0",
    description="Fast, focused Stable Diffusion interface - like A1111 but modern",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Bibin Abraham",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.105.0",
        "uvicorn[standard]>=0.24.0",
        "websockets>=12.0",
        "python-multipart>=0.0.6",
        "pillow>=11.3.0",
        "torch>=2.3.0",
        "torchvision>=0.18.0",
        "diffusers>=0.35.0",
        "transformers>=4.56.0",
        "accelerate>=1.10.0",
        "safetensors>=0.6.0",
        "rich>=13.7.0",
        "pydantic>=2.5.0",
    ],
    extras_require={
        "mlx": ["mlx>=0.29.0", "mlx-lm>=0.27.0"],
        "dev": ["pytest>=7.4.0", "black>=23.12.0", "isort>=5.13.0"],
    },
    entry_points={
        "console_scripts": [
            "sdxl-studio=sdxl_studio.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Graphics :: Editors",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="stable-diffusion ai image-generation sdxl art",
)