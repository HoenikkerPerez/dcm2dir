"""
Setup script for the dcm2dir package.

This script is used to package and distribute the dcm2dir tool.

To install the package locally, run:
    pip install .

To publish the package to PyPI, use:
    python setup.py sdist bdist_wheel
    twine upload dist/*
"""

from setuptools import setup, find_packages

setup(
    name="dcm2dir",
    version="0.1.0",
    author="Luca Peretti",
    author_email="luca_peretti@hotmail.com",
    description="Dicom Organizer: Organize DICOM files into a structured output folder.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/HoenikkerPerez/dcm2dir",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pydicom",
        "tqdm",
    ],
    entry_points={
        "console_scripts": [
            "dcm2dir=dcm2dir.dcm2dir:main",
        ],
    },
)
