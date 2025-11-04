#!/usr/bin/env python3

# Inspect the AST structure of our test contracts
import sys
import os
sys.path.insert(0, '/Users/wuyuze/anaconda3/lib/python3.11/site-packages')
from solidity_parser import parser
import json

def inspect_ast(file_path):
    print(f"Inspecting AST for {file_path}")
    print("=" * 50)

    try:
        ast = parser.parse_file(file_path)
        objectified_source_unit = parser.objectify(ast)

        for contract_name in objectified_source_unit.contracts:
            contract = objectified_source_unit.contracts[contract_name]
            print(f"\nContract: {contract_name}")

            for function_name in contract.functions:
                function = contract.functions[function_name]
                print(f"\n  Function: {function_name}")

                if hasattr(function, '_node') and hasattr(function._node, 'body') and function._node.body:
                    statements = function._node.body.statements
                    print(f"    Statements: {len(statements) if statements else 0}")

                    for i, stmt in enumerate(statements):
                        print(f"      Statement {i}: {json.dumps(stmt, indent=2) if stmt else 'None'}")
                        if stmt and stmt.get('type') == 'IfStatement' and stmt.get('TrueBody'):
                            print(f"        If Body Statements:")
                            for j, inner_stmt in enumerate(stmt['TrueBody'].get('statements', [])):
                                print(f"          Inner Statement {j}: {json.dumps(inner_stmt, indent=4) if inner_stmt else 'None'}")

    except Exception as e:
        print(f"Error parsing {file_path}: {e}")

if __name__ == "__main__":
    inspect_ast("test_vulnerable.sol")
    print("\n" + "="*50 + "\n")
    inspect_ast("test_safe.sol")
