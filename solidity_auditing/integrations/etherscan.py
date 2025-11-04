"""
Etherscan API integration for fetching contract source code.
"""

import requests
import json
import os

# Etherscan API Key Configuration
# The tool supports analyzing contracts from Etherscan by address
# API key can be configured in two ways:
# 1. Environment variable: export ETHERSCAN_API_KEY=your_key_here
# 2. Default key (built-in): QGPYMYKYX481IVTDDFTZZB14PK6REP28U4
ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY', 'QGPYMYKYX481IVTDDFTZZB14PK6REP28U4')


def get_contract_source_from_etherscan(contract_address, api_key=None):
    """
    Fetch contract source code from Etherscan API.

    Args:
        contract_address (str): Ethereum contract address
        api_key (str, optional): Etherscan API key

    Returns:
        str: Contract source code or error message
    """
    if api_key is None:
        api_key = ETHERSCAN_API_KEY

    # Etherscan API V2 endpoint
    url = "https://api.etherscan.io/v2/api"

    # Parameters for the V2 API request
    params = {
        "chainid": "1",  # Ethereum mainnet
        "module": "contract",
        "action": "getsourcecode",
        "address": contract_address,
        "apikey": api_key
    }

    try:
        # Make the request
        response = requests.get(url, params=params)
        data = response.json()

        if data["status"] == "1" and data["message"] == "OK":
            # Get the first result
            contract_data = data["result"][0]
            source_code = contract_data["SourceCode"]

            # Handle multi-file contracts (JSON format)
            if source_code.startswith('{{') or source_code.startswith('{'):
                try:
                    # Clean up the JSON string and parse it
                    cleaned_code = source_code.replace('{{', '{').replace('}}', '}')
                    parsed = json.loads(cleaned_code)

                    if "sources" in parsed:
                        # Multi-file contract - combine all source files
                        combined_code = ""
                        for file_path, file_data in parsed["sources"].items():
                            if isinstance(file_data, dict) and "content" in file_data:
                                combined_code += f"\n// ===== File: {file_path} =====\n"
                                combined_code += file_data["content"]
                            else:
                                combined_code += f"\n// ===== File: {file_path} =====\n"
                                combined_code += str(file_data)
                        return combined_code
                    else:
                        return source_code
                except (json.JSONDecodeError, KeyError):
                    # If JSON parsing fails, return as-is
                    return source_code
            else:
                # Single file contract
                return source_code
        else:
            return f"Error: {data['message']}"

    except Exception as e:
        return f"Error fetching source code: {str(e)}"


def get_source_code(contract_address_or_import, api_key=None):
    """
    Get source code from either Etherscan address or GitHub import.

    Args:
        contract_address_or_import (str): Contract address or import path
        api_key (str, optional): Etherscan API key

    Returns:
        str: Source code or error message
    """
    # Check if the input is an import directive
    if contract_address_or_import.startswith("@"):
        return get_source_code_from_github(contract_address_or_import)
    else:
        return get_contract_source_from_etherscan(contract_address_or_import, api_key)


def get_source_code_from_github(import_path):
    """
    Fetch source code from GitHub for @openzeppelin imports.

    Args:
        import_path (str): Import path (e.g., "@openzeppelin/contracts/utils/Address.sol")

    Returns:
        str: Source code or error message
    """
    # Convert OpenZeppelin import path to GitHub raw URL
    if import_path.startswith("@openzeppelin/"):
        github_url = f"https://raw.githubusercontent.com/OpenZeppelin/openzeppelin-contracts/refs/heads/master/{import_path[len('@openzeppelin/'):]}"
    else:
        return f"Unsupported import path: {import_path}"

    try:
        response = requests.get(github_url)
        if response.status_code == 200:
            return response.text
        else:
            return f"Error fetching source code from GitHub: {response.status_code}"
    except Exception as e:
        return f"Error fetching source code from GitHub: {str(e)}"
