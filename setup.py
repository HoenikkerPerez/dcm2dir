from setuptools import setup, find_packages

setup(
    name="dcm2dir",
    version="0.1.0",
    author="Luca Peretti",
    author_email="luca_peretti@hotmail.com",
    description="Dicom Organizer: Organize DICOM files into a structured output folder.",
    long_description=open("README.md").read(),
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