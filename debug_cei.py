#!/usr/bin/env python3

# Debug version to understand what's happening with CEI detection
import sys
import os
sys.path.insert(0, '/Users/wuyuze/anaconda3/lib/python3.11/site-packages')
from solidity_parser import parser

def debug_cei_analysis(file_path):
    print(f"Analyzing {file_path}")
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

                # Simulate the CEI analysis
                flags = {"check": False, "effects": False, "interaction": False}
                protected_vars = []

                if hasattr(function, '_node') and hasattr(function._node, 'body') and function._node.body:
                    statements = function._node.body.statements
                    print(f"    Statements: {len(statements) if statements else 0}")

                    for i, stmt in enumerate(statements):
                        if stmt is None:
                            continue
                        print(f"      {i}: {stmt.get('type', 'unknown')}", end="")

                        # Check for external calls
                        if stmt.get('type') == 'ExpressionStatement' and stmt.get('expression', {}).get('type') == 'FunctionCall':
                            expr = stmt['expression']
                            if (isinstance(expr.get('expression'), dict) and
                                expr['expression'].get('type') == 'MemberAccess' and
                                expr['expression'].get('memberName') in ['call', 'send', 'transfer', 'delegatecall']):
                                print(" → EXTERNAL CALL (interaction)")
                                flags["interaction"] = True
                            else:
                                print()

                        # Check for assignments (effects)
                        elif stmt.get('type') == 'ExpressionStatement' and stmt.get('expression', {}).get('type') in ['Assignment', 'UnaryOperation']:
                            print(" → STATE MODIFICATION (effects)")
                            flags["effects"] = True

                        # Check for if statements
                        elif stmt.get('type') == 'IfStatement':
                            print(" → IF STATEMENT (check)")
                            flags["check"] = True

                            # Analyze if body
                            if stmt.get('TrueBody') and stmt['TrueBody'].get('statements'):
                                for j, inner_stmt in enumerate(stmt['TrueBody']['statements']):
                                    if inner_stmt and inner_stmt.get('type') == 'ExpressionStatement':
                                        if inner_stmt.get('expression', {}).get('type') == 'FunctionCall':
                                            expr = inner_stmt['expression']
                                            if (isinstance(expr.get('expression'), dict) and
                                                expr['expression'].get('type') == 'MemberAccess' and
                                                expr['expression'].get('memberName') in ['call', 'send', 'transfer', 'delegatecall']):
                                                print(f"        └─ {j}: EXTERNAL CALL in IF body")
                                                flags["interaction"] = True
                                        elif inner_stmt['expression'].get('type') in ['Assignment', 'UnaryOperation']:
                                            print(f"        └─ {j}: STATE MODIFICATION in IF body")
                                            flags["effects"] = True
                        else:
                            print()

                print(f"    Final flags: {flags}")
                vulnerable = flags["interaction"] and flags["effects"] and not flags["check"]
                print(f"    Vulnerable: {vulnerable}")

    except Exception as e:
        print(f"Error parsing {file_path}: {e}")

if __name__ == "__main__":
    debug_cei_analysis("test_safe.sol")
    print("\n" + "="*50 + "\n")
    debug_cei_analysis("test_vulnerable.sol")
