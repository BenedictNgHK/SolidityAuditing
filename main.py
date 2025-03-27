from solidity_auditing.Reentrancy import AuditReentrancy
from solidity_auditing.Vulneralbilities import VulnerabilityLogger
from solidity_parser import parser
import requests
import pprint
import sys


def get_contract_source_from_etherscan(contract_address, api_key):
    # Etherscan API endpoint
    url = "https://api.etherscan.io/api"
    
    # Parameters for the API request
    params = {
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
            source_code = data["result"][0]
            return source_code["SourceCode"]
        else:
            return f"Error: {data['message']}"
        
    except Exception as e:
        return f"Error fetching source code: {str(e)}"
def get_source_code_from_github(import_path):
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

def get_source_code(contract_address_or_import, api_key):
    # Check if the input is an import directive
    if contract_address_or_import.startswith("@"):
        return get_source_code_from_github(contract_address_or_import)
    else:
        return get_contract_source_from_etherscan(contract_address_or_import, api_key)
# Example usage
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python Reentrancy.py <file.sol>|<contract_address>")
        exit()
    if sys.argv[1].endswith(".sol"):
        ast = parser.parse_file(sys.argv[1])
    else:
        
        sourceCode = get_source_code(sys.argv[1],api_key="QGPYMYKYX481IVTDDFTZZB14PK6REP28U4")
        ast = parser.parse(sourceCode)
    objectified_source_unit = parser.objectify(ast)
   
    audit  = AuditReentrancy(objectified_source_unit)
    logger = VulnerabilityLogger(sys.argv[1])
    audit.checkReentrancy(logger)
    logger.formattedPrint()