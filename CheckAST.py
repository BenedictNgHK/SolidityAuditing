from solidity_auditing.Reentrancy import AuditReentrancy
from solidity_auditing.Vulneralbilities import VulnerabilityLogger
from solidity_parser import parser
import requests
import pprint
import sys
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python Reentrancy.py <file.sol>|<contract_address>")
        exit()
    if sys.argv[1].endswith(".sol"):
        ast = parser.parse_file(sys.argv[1])
    
    objectified_source_unit = parser.objectify(ast)
    pprint.pprint(ast)