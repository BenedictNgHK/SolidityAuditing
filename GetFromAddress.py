import requests

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
    # Your contract address
    contract_address = "0x526af336D614adE5cc252A407062B8861aF998F5"
    #contract_address = "@openzeppelin/contracts/token/ERC20/ERC20.sol"
    # Your Etherscan API key
    api_key = "QGPYMYKYX481IVTDDFTZZB14PK6REP28U4"

    # OpenZeppelin GitHub URL for ReentrancyGuard.sol
    openzeppelin_url = "@openzeppelin/contracts/utils/ReentrancyGuard.sol"
    
    # Fetch the source code
    
    source_code = get_source_code(openzeppelin_url, api_key)
    print(source_code)