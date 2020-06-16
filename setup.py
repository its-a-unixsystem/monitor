#!/usr/bin/python3

# from https://packaging.python.org/tutorials/packaging-projects/
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="monitor-pkg-thomas-uebermeier",
    version="0.9.3",
    author="Thomas Uebermeier",
    author_email="thomas@februus.net",
    description="Website monitor",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thomas-for-aiven/monitor",
    packages=setuptools.find_packages(),
    scripts=['monitor/consumtodb.py', 'monitor/checker.py'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
