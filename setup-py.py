"""
Setup script for 3D Pipe Routing
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pipe-routing-3d",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="3D Pipe Routing with Priority-Based Search",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pipe-routing",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        'numpy>=1.21.0',
        'scipy>=1.7.0',
        'pandas>=1.3.0',
        'matplotlib>=3.4.0',
        'seaborn>=0.11.0',
        'plotly>=5.0.0',
        'ortools>=9.0',
        'tqdm>=4.62.0',
        'pytest>=6.2.0',
    ],
)
