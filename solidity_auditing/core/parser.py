#!/usr/bin/env python3
"""
Simple Solidity Parser for CEI Detection
Bypasses ANTLR compatibility issues by using regex-based parsing
"""

import re
from typing import List, Dict, Tuple, Set


class SimpleSolidityParser:
    """
    Lightweight Solidity parser focused on extracting function bodies
    and operation sequences for CEI analysis.
    """

    def __init__(self):
        # Simple patterns for extracting functions
        pass

    def parse_file(self, file_path: str) -> Dict:
        """Parse a Solidity file and extract contract/function information."""
        with open(file_path, 'r') as f:
            content = f.read()

        # Remove comments
        content = self._remove_comments(content)

        # Extract functions from the entire file
        functions = self._extract_functions(content)

        # Try to determine contract name
        contract_match = re.search(r'contract\s+(\w+)', content)
        contract_name = contract_match.group(1) if contract_match else 'Main'

        return {
            'contracts': {contract_name: functions},
            'source': content
        }

    def _remove_comments(self, content: str) -> str:
        """Remove comments from Solidity code."""
        # Remove single-line comments
        content = re.sub(r'//.*', '', content)
        # Remove multi-line comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        return content

    def _extract_functions(self, content: str) -> Dict[str, str]:
        """Extract all functions from content using brace matching."""
        functions = {}

        # Find function declarations
        func_starts = []
        for match in re.finditer(r'function\s+(\w+)\s*\([^)]*\)\s*(?:[^{]*)\{', content):
            func_name = match.group(1)
            func_start_pos = match.start()  # Start of function declaration
            brace_pos = match.end() - 1     # Position of the opening brace
            func_starts.append((func_name, func_start_pos, brace_pos))

        # Extract function bodies by matching braces
        for func_name, func_start_pos, start_pos in func_starts:
            brace_count = 0
            end_pos = start_pos

            for i in range(start_pos, len(content)):
                if content[i] == '{':
                    brace_count += 1
                elif content[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_pos = i
                        break

            if end_pos > start_pos:
                # Include the function signature and modifiers in the body
                full_func = content[func_start_pos:end_pos + 1]
                functions[func_name] = full_func

        return functions

    def extract_operations(self, function_body: str) -> List[Dict]:
        """Extract operation sequence from function body (inside braces only)."""
        operations = []

        # Find the opening brace and only process content after it
        brace_pos = function_body.find('{')
        if brace_pos == -1:
            return operations

        body_content = function_body[brace_pos + 1:]  # Content after opening brace
        lines = body_content.split('\n')

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('//') or line.startswith('/*') or line == '}':
                continue

            # Check for external calls
            if self._is_external_call(line):
                operations.append({
                    'type': 'external_call',
                    'content': line,
                    'line': line_num
                })

            # Check for state modifications
            elif self._is_state_modification(line):
                operations.append({
                    'type': 'state_modification',
                    'content': line,
                    'line': line_num
                })

        return operations

    def _is_external_call(self, line: str) -> bool:
        """Check if line contains external call."""
        external_call_patterns = [
            r'\.call\s*\.\s*value\s*\(',
            r'\.call\s*\(',
            r'\.call\s*\{',               # addr.call{value: amount}(data) - new syntax
            r'\.send\s*\(',
            r'\.transfer\s*\(',
            r'\.delegatecall\s*\(',
            r'\.delegatecall\s*\{',       # addr.delegatecall{}(data) - new syntax
        ]

        return any(re.search(pattern, line) for pattern in external_call_patterns)

    def _is_state_modification(self, line: str) -> bool:
        """Check if line modifies state variables."""
        # Skip if it's a declaration
        if re.match(r'(uint|address|bool|string|bytes|mapping)\s+\w+', line):
            return False

        # Skip if it's a local variable
        if re.match(r'\w+\s+\w+\s*=', line):
            return False

        # Check for assignments to variables (including array/map access)
        state_mod_patterns = [
            r'\w+(\[[^\]]*\])*\s*[-+]?=\s*[^=]',
            r'\w+(\[[^\]]*\])*\s*\+\+',
            r'\w+(\[[^\]]*\])*\s*--',
        ]

        return any(re.search(pattern, line) for pattern in state_mod_patterns)

    def has_reentrancy_guard(self, function_body: str, source_code: str = None) -> bool:
        """Check if function has reentrancy guard."""
        guard_patterns = [
            r'noReentrancy',
            r'nonReentrant',
            r'reentrancy.*guard',
            r'mutex',
            r'lock',
            r'simpleGuard',
        ]

        has_guard = any(re.search(pattern, function_body, re.IGNORECASE) for pattern in guard_patterns)

        # Special check for simpleGuard: check if the modifier definition has state modifications after _;
        if has_guard and 'simpleGuard' in function_body and source_code:
            # Find the simpleGuard modifier definition
            modifier_match = re.search(r'modifier\s+simpleGuard\s*\([^}]*\{([^}]*)\}', source_code, re.DOTALL)
            if modifier_match:
                modifier_body = modifier_match.group(1)
                # Check if there are state modifications after _;
                if '_;' in modifier_body:
                    after_placeholder = modifier_body.split('_;')[1]
                    if self._has_state_modifications_in_text(after_placeholder):
                        return False  # Flawed guard - has state mods after function body

        return has_guard

    def _has_state_modifications_in_text(self, text: str) -> bool:
        """Check if text contains state modifications (excluding lock variables)."""
        state_mod_patterns = [
            r'\w+(\[[^\]]*\])*\s*[-+]?=\s*[^=]',
            r'\w+(\[[^\]]*\])*\s*\+\+',
            r'\w+(\[[^\]]*\])*\s*--',
        ]

        # Find all assignments
        for pattern in state_mod_patterns:
            for match in re.finditer(pattern, text):
                # Extract the variable name being modified
                var_match = re.match(r'(\w+)', match.group())
                if var_match:
                    var_name = var_match.group(1)
                    # Exclude common lock variable names
                    if var_name not in ['j', 'lock', 'mutex', 'locked', 'reentrancyLock']:
                        return True  # Found modification of non-lock variable

        return False

    def has_delegatecall_validation(self, function_body: str) -> bool:
        """Check if delegatecall has proper validation."""
        validation_patterns = [
            r'require.*==.*owner',
            r'if.*==.*owner',
            r'onlyOwner',
            r'address.*!=.*0',
        ]

        return any(re.search(pattern, function_body) for pattern in validation_patterns)
