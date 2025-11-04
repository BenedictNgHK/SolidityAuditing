#!/usr/bin/env python3
"""
Advanced CEI (Checks-Effects-Interactions) Pattern Detector
This module provides sophisticated reentrancy detection that analyzes
the order of operations within Solidity functions.
"""

import re
import ast
from typing import List, Dict, Tuple, Set
from simple_solidity_parser import SimpleSolidityParser


class CEIVulnerabilityDetector:
    """
    Advanced detector for CEI pattern violations in Solidity contracts.
    Analyzes the sequence of operations to identify reentrancy vulnerabilities.
    """

    def __init__(self):
        # External call patterns - more comprehensive
        self.external_call_patterns = [
            r'\.call\s*\.\s*value\s*\(',  # msg.sender.call.value(amount)()
            r'\.call\s*\(',               # addr.call(data)
            r'\.call\s*\{',               # addr.call{value: amount}(data) - new syntax
            r'\.send\s*\(',               # addr.send(amount)
            r'\.transfer\s*\(',           # addr.transfer(amount)
            r'\.delegatecall\s*\(',       # addr.delegatecall(data)
            r'\.delegatecall\s*\{',       # addr.delegatecall{}(data) - new syntax
            r'\.staticcall\s*\(',         # addr.staticcall(data)
        ]

        # State modification patterns (assignments to storage variables)
        self.state_modification_patterns = [
            r'\w+(\[[^\]]*\])*\s*[-+]?=\s*[^=]',  # variable[index] = value, variable = value
            r'\w+(\[[^\]]*\])*\s*\+\+',            # variable++ or variable[index]++
            r'\w+(\[[^\]]*\])*\s*--',              # variable-- or variable[index]--
            r'\w+(\[[^\]]*\])*\s*[-+]?=\s*\w+',    # assignments with variables
        ]

        # Guard patterns (checks that protect operations)
        self.guard_patterns = [
            r'\b(require|assert)\s*\(',
            r'\bif\s*\(',
            r'\bmodifier\s+\w+\s*\([^)]*\)\s*{',
            r'\bfunction\s+\w+\s*\([^)]*\)\s*[^}]*noReentrancy',
            r'\bfunction\s+\w+\s*\([^)]*\)\s*[^}]*simpleGuard',
        ]

        # Safe external call patterns (don't create reentrancy risks)
        self.safe_call_patterns = [
            r'\.staticcall\s*\(',
            r'\baddress\s*\(\s*0\s*\)\s*\.',
            r'\.transfer\s*\(\s*\d+',  # transfer with small gas
        ]

    def analyze_contract(self, file_path: str) -> Dict:
        """
        Analyze a Solidity contract for CEI violations.
        Returns detailed analysis of vulnerabilities found.
        """
        # Use simple parser to extract functions
        parser = SimpleSolidityParser()
        parsed_data = parser.parse_file(file_path)

        vulnerabilities = []
        safe_patterns = []
        total_functions = 0

        # Analyze all functions in all contracts
        for contract_name, functions in parsed_data['contracts'].items():
            for func_name, func_body in functions.items():
                total_functions += 1
                analysis = self._analyze_function_with_parser(func_name, func_body, parser, parsed_data.get('source'))

                if analysis['vulnerable']:
                    # Add contract name to vulnerabilities
                    for vuln in analysis['issues']:
                        vuln['contract'] = contract_name
                    vulnerabilities.extend(analysis['issues'])
                else:
                    safe_patterns.append({
                        'function': f"{contract_name}.{func_name}",
                        'reason': analysis.get('safe_reason', 'CEI compliant')
                    })

        return {
            'vulnerabilities': vulnerabilities,
            'safe_patterns': safe_patterns,
            'summary': {
                'total_functions': total_functions,
                'vulnerable_functions': len(set(v['function'] for v in vulnerabilities)),
                'safe_functions': len(safe_patterns),
                'has_reentrancy_risk': len(vulnerabilities) > 0
            }
        }

    def _extract_functions(self, content: str) -> Dict[str, str]:
        """Extract function bodies from Solidity contract."""
        functions = {}

        # Remove comments
        content = re.sub(r'//.*', '', content)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

        # Find function definitions
        func_pattern = r'function\s+(\w+)\s*\([^)]*\)(?:\s*[^{]*?)?{([^}]*)}'
        matches = re.findall(func_pattern, content, re.DOTALL)

        for func_name, func_body in matches:
            functions[func_name] = func_body.strip()

        return functions

    def _analyze_function(self, func_name: str, func_body: str) -> Dict:
        """
        Analyze a single function for CEI violations.
        Returns detailed analysis of the function.
        """
        # Extract operation sequence
        operations = self._extract_operation_sequence(func_body)

        # Check for reentrancy guards
        has_guard = self._has_reentrancy_guard(func_body)

        # Analyze for dangerous patterns
        issues = []

        if not has_guard:
            # Check for external calls before state modifications
            external_call_positions = []
            state_mod_positions = []

            for i, op in enumerate(operations):
                if op['type'] == 'external_call' and not self._is_safe_call(op['content']):
                    external_call_positions.append(i)
                elif op['type'] == 'state_modification':
                    state_mod_positions.append(i)

            # Check for dangerous sequences
            for call_pos in external_call_positions:
                # Find if there are state modifications after this call
                subsequent_mods = [pos for pos in state_mod_positions if pos > call_pos]
                if subsequent_mods:
                    issues.append({
                        'function': func_name,
                        'type': 'CEI_VIOLATION',
                        'description': 'External call before state modification completion',
                        'severity': 'HIGH',
                        'line': operations[call_pos].get('line', 'unknown'),
                        'pattern': 'Interaction before Effects complete'
                    })

            # Check for multiple external calls with state mods in between
            if len(external_call_positions) > 1:
                for i in range(len(external_call_positions) - 1):
                    start_pos = external_call_positions[i]
                    end_pos = external_call_positions[i + 1]

                    # Check for state modifications between calls
                    mods_between = [pos for pos in state_mod_positions
                                  if start_pos < pos < end_pos]

                    if mods_between:
                        issues.append({
                            'function': func_name,
                            'type': 'MULTIPLE_CALLS_VIOLATION',
                            'description': 'Multiple external calls with state modifications between them',
                            'severity': 'HIGH',
                            'pattern': 'Unsafe multiple interactions'
                        })

        # Check for delegatecall without validation
        if self._has_delegatecall(func_body) and not self._has_delegatecall_validation(func_body):
            issues.append({
                'function': func_name,
                'type': 'UNSAFE_DELEGATECALL',
                'description': 'Delegatecall without proper input validation',
                'severity': 'CRITICAL',
                'pattern': 'Unsafe delegatecall usage'
            })

        return {
            'vulnerable': len(issues) > 0,
            'issues': issues,
            'safe_reason': 'Has reentrancy guard' if has_guard else ('CEI compliant' if not issues else None),
            'has_guard': has_guard
        }

    def _extract_operation_sequence(self, func_body: str) -> List[Dict]:
        """Extract sequence of operations from function body."""
        operations = []
        lines = func_body.split('\n')

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('//') or line.startswith('/*'):
                continue

            # Check for external calls
            for pattern in self.external_call_patterns:
                if re.search(pattern, line):
                    operations.append({
                        'type': 'external_call',
                        'content': line,
                        'line': line_num
                    })
                    break

            # Check for state modifications
            for pattern in self.state_modification_patterns:
                if re.search(pattern, line) and not self._is_declaration(line):
                    operations.append({
                        'type': 'state_modification',
                        'content': line,
                        'line': line_num
                    })
                    break

        return operations

    def _analyze_function_with_parser(self, func_name: str, func_body: str, parser: SimpleSolidityParser, source_code: str = None) -> Dict:
        """
        Analyze a single function for CEI violations using the simple parser.
        """
        # Extract operation sequence using parser
        operations = parser.extract_operations(func_body)

        # Check for reentrancy guards
        has_guard = parser.has_reentrancy_guard(func_body, source_code)

        # Analyze for dangerous patterns
        issues = []

        if not has_guard:
            # Check for external calls followed by state modifications
            external_call_positions = []
            state_mod_positions = []

            for i, op in enumerate(operations):
                if op['type'] == 'external_call':
                    external_call_positions.append(i)
                elif op['type'] == 'state_modification':
                    state_mod_positions.append(i)

            # Check for dangerous sequences
            for call_pos in external_call_positions:
                # Find if there are state modifications after this call
                subsequent_mods = [pos for pos in state_mod_positions if pos > call_pos]
                if subsequent_mods:
                    issues.append({
                        'function': func_name,
                        'type': 'CEI_VIOLATION',
                        'description': 'External call before state modification completion',
                        'severity': 'HIGH',
                        'line': operations[call_pos].get('line', 'unknown'),
                        'pattern': 'Interaction before Effects complete'
                    })

        # Check for delegatecall without validation
        if '.delegatecall' in func_body and not parser.has_delegatecall_validation(func_body):
            issues.append({
                'function': func_name,
                'type': 'UNSAFE_DELEGATECALL',
                'description': 'Delegatecall without proper input validation',
                'severity': 'CRITICAL',
                'pattern': 'Unsafe delegatecall usage'
            })

        return {
            'vulnerable': len(issues) > 0,
            'issues': issues,
            'safe_reason': 'Has reentrancy guard' if has_guard else ('CEI compliant' if not issues else None),
            'has_guard': has_guard
        }

    def _has_reentrancy_guard(self, func_body: str) -> bool:
        """Check if function has reentrancy guard."""
        patterns = [
            r'noReentrancy',
            r'nonReentrant',
            r'reentrancy.*guard',
            r'mutex',
            r'lock',
        ]

        return any(re.search(pattern, func_body, re.IGNORECASE) for pattern in patterns)

    def _has_delegatecall(self, func_body: str) -> bool:
        """Check if function contains delegatecall."""
        return '.delegatecall' in func_body

    def _has_delegatecall_validation(self, func_body: str) -> bool:
        """Check if delegatecall has proper validation."""
        validation_patterns = [
            r'require.*==.*owner',
            r'if.*==.*owner',
            r'onlyOwner',
            r'address.*!=.*0',
        ]

        return any(re.search(pattern, func_body) for pattern in validation_patterns)

    def _is_safe_call(self, call_content: str) -> bool:
        """Check if external call is safe (doesn't create reentrancy risk)."""
        return any(re.search(pattern, call_content) for pattern in self.safe_call_patterns)

    def _is_declaration(self, line: str) -> bool:
        """Check if line is a variable declaration rather than modification."""
        # Simple heuristic: declarations often have types
        type_keywords = ['uint', 'address', 'bool', 'string', 'bytes', 'mapping']
        return any(keyword in line and '=' in line for keyword in type_keywords)


def analyze_file(file_path: str) -> Dict:
    """
    Convenience function to analyze a single file.
    Returns True if vulnerable, False if safe.
    """
    detector = CEIVulnerabilityDetector()
    result = detector.analyze_contract(file_path)
    return result['summary']['has_reentrancy_risk']


if __name__ == "__main__":
    # Test the detector
    detector = CEIVulnerabilityDetector()

    # Test on sample files
    test_files = [
        ("TestContracts/Safe/CEIGuard.sol", False),
        ("TestContracts/Unsafe/ReentrancyAttack.sol", True),
        ("TestContracts/Unsafe/DAO.sol", True),
    ]

    print("🧪 Testing Advanced CEI Detector")
    print("=" * 40)

    for file_path, expected in test_files:
        try:
            result = detector.analyze_contract(file_path)
            is_vulnerable = result['summary']['has_reentrancy_risk']
            status = "✅" if is_vulnerable == expected else "❌"

            print(f"{status} {file_path}")
            print(f"   Expected: {'VULNERABLE' if expected else 'SAFE'}")
            print(f"   Detected: {'VULNERABLE' if is_vulnerable else 'SAFE'}")

            if result['vulnerabilities']:
                print(f"   Issues found: {len(result['vulnerabilities'])}")
                for vuln in result['vulnerabilities'][:2]:  # Show first 2
                    print(f"     - {vuln['type']}: {vuln['description']}")

        except Exception as e:
            print(f"❌ {file_path} - Error: {e}")
