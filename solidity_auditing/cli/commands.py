"""
CLI commands for Solidity auditing tool.
"""

import sys
import os
import tempfile
import json
from pathlib import Path

from ..core import CEIVulnerabilityDetector
from ..integrations import get_source_code
from solidity_auditing.Vulneralbilities import VulnerabilityLogger

# Lazy import solidity_parser to avoid ANTLR issues
try:
    from solidity_parser import parser
    SOLIDITY_PARSER_AVAILABLE = True
except Exception as e:
    print(f"Warning: solidity_parser not available: {e}")
    SOLIDITY_PARSER_AVAILABLE = False


def save_results_to_json(analysis_results, input_path):
    """
    Save analysis results to a JSON file.

    Args:
        analysis_results (dict): Results from detector.analyze_contract()
        input_path (str): Input file path or address
    """
    # Create output filename based on input
    if input_path.endswith('.sol'):
        base_name = Path(input_path).stem
        output_file = f"{base_name}_analysis.json"
    else:
        # For addresses, use a generic name
        output_file = "contract_analysis.json"

    # Format results for JSON output
    json_results = {
        "input": input_path,
        "timestamp": str(Path(output_file).stat().st_mtime) if Path(output_file).exists() else None,
        "analysis": {
            "summary": analysis_results["summary"],
            "vulnerabilities": analysis_results["vulnerabilities"],
            "safe_patterns": analysis_results["safe_patterns"]
        }
    }

    # Save to JSON file
    with open(output_file, 'w') as f:
        json.dump(json_results, f, indent=2)

    print(f"\n💾 Analysis results saved to: {output_file}")


def analyze_file(file_path):
    """
    Analyze a Solidity file for reentrancy vulnerabilities.

    Args:
        file_path (str): Path to the Solidity file
    """
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist")
        return 1

    try:
        detector = CEIVulnerabilityDetector()
        analysis = detector.analyze_contract(file_path)

        # Save results to JSON
        save_results_to_json(analysis, file_path)

        logger = VulnerabilityLogger(file_path)
        if analysis['summary']['has_reentrancy_risk']:
            for vuln in analysis['vulnerabilities']:
                logger.logVulnerability(
                    contract_name=vuln.get('contract', 'Unknown'),
                    function_name=vuln['function'],
                    vulneralbility=f"Reentrancy: {vuln['description']}"
                )
        logger.formattedPrint()
        return 0
    except Exception as e:
        print(f"Error analyzing file: {e}")
        return 1


def analyze_address(contract_address):
    """
    Analyze a contract from Etherscan by address.

    Args:
        contract_address (str): Ethereum contract address
    """
    try:
        source_code = get_source_code(contract_address)
        if source_code.startswith("Error"):
            print(f"Error: {source_code}")
            return 1

        # Save to temporary file for analysis
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sol', delete=False) as f:
            f.write(source_code)
            temp_file = f.name

        try:
            detector = CEIVulnerabilityDetector()
            analysis = detector.analyze_contract(temp_file)

            # Save results to JSON
            save_results_to_json(analysis, contract_address)

            logger = VulnerabilityLogger(contract_address)
            if analysis['summary']['has_reentrancy_risk']:
                for vuln in analysis['vulnerabilities']:
                    logger.logVulnerability(
                        contract_name=vuln.get('contract', 'Unknown'),
                        function_name=vuln['function'],
                        vulneralbility=f"Reentrancy: {vuln['description']}"
                    )
            logger.formattedPrint()
            return 0
        finally:
            # Clean up temporary file
            os.unlink(temp_file)

    except Exception as e:
        print(f"Error analyzing address: {e}")
        return 1


def main():
    """Main CLI entry point."""
    if len(sys.argv) != 2:
        print("Usage: python -m solidity_auditing <file.sol>|<etherscan_address>")
        print("Examples:")
        print("  python -m solidity_auditing MyContract.sol")
        print("  python -m solidity_auditing 0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413")
        print("Note: Set ETHERSCAN_API_KEY environment variable for Etherscan analysis")
        return 1

    input_path = sys.argv[1]

    if input_path.endswith('.sol'):
        # Analyze local file
        return analyze_file(input_path)
    else:
        # Analyze Etherscan address
        return analyze_address(input_path)


if __name__ == "__main__":
    sys.exit(main())
