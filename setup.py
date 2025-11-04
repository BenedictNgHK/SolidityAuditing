#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Setup script for Solidity Auditing Tool
"""

import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


version = "1.0.0"
name = "solidity-auditing"

setup(
    name=name,
    version=version,
    packages=find_packages(exclude=['tests', 'examples', 'docs', 'scripts']),
    author="Solidity Auditing Team",
    author_email="",
    description=(
        "Advanced Solidity smart contract reentrancy vulnerability detection "
        "using CEI (Checks-Effects-Interactions) pattern analysis"),
    license="MIT",
    keywords=["solidity", "auditing", "security", "reentrancy", "blockchain", "ethereum"],
    url="https://github.com/BenedictNgHK/SolidityAuditing",
    long_description=read("README.md") if os.path.isfile("README.md") else "",
    long_description_content_type='text/markdown',
    install_requires=[
        "requests",
        "antlr4-python3-runtime>=4.9.3",
    ],
    extras_require={
        'dev': [
            'pytest',
            'pytest-cov',
            'black',
            'flake8',
        ],
    },
    entry_points={
        'console_scripts': [
            'solidity-audit=solidity_auditing.cli.commands:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Security',
        'Topic :: Software Development :: Quality Assurance',
    ],
    python_requires='>=3.8',
)
