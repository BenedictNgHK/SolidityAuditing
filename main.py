from solidity_auditing.Reentrancy import AuditReentrancy
from solidity_auditing.Vulneralbilities import VulnerabilityLogger
import requests
import pprint
import sys
import os
import json

# Lazy import solidity_parser to avoid ANTLR issues
try:
    from solidity_parser import parser
    SOLIDITY_PARSER_AVAILABLE = True
except Exception as e:
    print(f"Warning: solidity_parser not available: {e}")
    SOLIDITY_PARSER_AVAILABLE = False

# Etherscan API Key Configuration
# The tool supports analyzing contracts from Etherscan by address
# API key can be configured in two ways:
# 1. Environment variable: export ETHERSCAN_API_KEY=your_key_here
# 2. Default key (built-in): QGPYMYKYX481IVTDDFTZZB14PK6REP28U4
ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY', 'QGPYMYKYX481IVTDDFTZZB14PK6REP28U4')


def get_contract_source_from_etherscan(contract_address, api_key):
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
        print("Usage: python main.py <file.sol>|<etherscan_address>")
        print("Examples:")
        print("  python main.py MyContract.sol")
        print("  python main.py 0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413")
        print("Note: Set ETHERSCAN_API_KEY environment variable for Etherscan analysis")
        exit()

    # Handle both local files and Etherscan addresses with advanced detector
    if len(sys.argv) > 1:
        file_path = None
        if sys.argv[1].endswith('.sol') and os.path.exists(sys.argv[1]):
            # Local file
            file_path = sys.argv[1]
        elif not sys.argv[1].endswith('.sol'):
            # Etherscan address - download source code
            try:
                source_code = get_source_code(sys.argv[1], api_key=ETHERSCAN_API_KEY)
                if source_code and "contracts" in source_code:
                    # Save to temporary file for analysis
                    import tempfile
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.sol', delete=False) as f:
                        f.write(source_code)
                        file_path = f.name
                else:
                    print("Could not retrieve source code from Etherscan")
                    sys.exit(1)
            except Exception as e:
                print(f"Failed to get source from Etherscan: {e}")
                sys.exit(1)

        if file_path:
            try:
                from advanced_cei_detector import CEIVulnerabilityDetector
                detector = CEIVulnerabilityDetector()
                analysis = detector.analyze_contract(file_path)

                logger = VulnerabilityLogger(sys.argv[1])
                if analysis['summary']['has_reentrancy_risk']:
                    for vuln in analysis['vulnerabilities']:
                        logger.logVulnerability(
                            contract_name=vuln.get('contract', 'Unknown'),
                            function_name=vuln['function'],
                            vulneralbility=f"Reentrancy: {vuln['description']}"
                        )
                logger.formattedPrint()

                # Clean up temporary file if created
                if file_path != sys.argv[1] and os.path.exists(file_path):
                    os.unlink(file_path)
                sys.exit(0)
            except Exception as e:
                print(f"Advanced detection failed: {e}")
                if not SOLIDITY_PARSER_AVAILABLE:
                    print("No parser available, skipping analysis")
                    sys.exit(1)

    # Original AST-based analysis for Etherscan addresses or fallback
    if sys.argv[1].endswith(".sol"):
        ast = parser.parse_file(sys.argv[1])
    else:
        sourceCode = get_source_code(sys.argv[1],api_key=ETHERSCAN_API_KEY)
        ast = parser.parse(sourceCode)
    objectified_source_unit = parser.objectify(ast)
    # pprint.pprint(ast)
    audit  = AuditReentrancy(objectified_source_unit)
    logger = VulnerabilityLogger(sys.argv[1])
    audit.checkReentrancy(logger)
    logger.formattedPrint()