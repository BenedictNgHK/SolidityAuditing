"""
External integrations for Solidity auditing.
"""

from .etherscan import (
    get_contract_source_from_etherscan,
    get_source_code,
    get_source_code_from_github,
    ETHERSCAN_API_KEY
)

__all__ = [
    'get_contract_source_from_etherscan',
    'get_source_code',
    'get_source_code_from_github',
    'ETHERSCAN_API_KEY',
]
