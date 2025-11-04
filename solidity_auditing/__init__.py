"""
Solidity Reentrancy Auditing Tool

A comprehensive tool for detecting reentrancy vulnerabilities in Solidity smart contracts
using advanced CEI (Checks-Effects-Interactions) pattern analysis.
"""

__version__ = "1.0.0"
__author__ = "Solidity Auditing Team"

from .core.detector import CEIVulnerabilityDetector
from .core.parser import SimpleSolidityParser

__all__ = [
    'CEIVulnerabilityDetector',
    'SimpleSolidityParser',
]
