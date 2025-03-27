from solidity_parser.parser import parse
import sys
class CEIPatternChecker:
    def __init__(self, solidity_code):
        self.ast = parse(solidity_code)
        self.violations = []

    def check_cei_pattern(self):
        self._traverse_ast(self.ast)
        return self.violations

    def _traverse_ast(self, node):
        if isinstance(node, dict):
            # Check if the node is a function definition
            if node.get('type') == 'FunctionDefinition':
                self._check_function_cei(node)

            # Recursively traverse child nodes
            for key, value in node.items():
                if isinstance(value, (dict, list)):
                    self._traverse_ast(value)
        elif isinstance(node, list):
            for item in node:
                self._traverse_ast(item)

    def _check_function_cei(self, function_node):
        # Extract the function body
        body = function_node.get('body', {}).get('statements', [])
        if not body:
            return

        # Track the order of checks, effects, and interactions
        checks = []
        effects = []
        interactions = []

        for statement in body:
            if self._is_check(statement):
                checks.append(statement)
            elif self._is_effect(statement):
                effects.append(statement)
            elif self._is_interaction(statement):
                interactions.append(statement)

        # Check if interactions occur before effects
        if interactions and effects:
            first_interaction_index = body.index(interactions[0])
            first_effect_index = body.index(effects[0])

            if first_interaction_index < first_effect_index:
                self.violations.append({
                    'function': function_node.get('name'),
                    'line': function_node.get('loc', {}).get('start', {}).get('line'),
                    'message': 'Interaction before effect detected. Violates CEI pattern.'
                })

    def _is_check(self, node):
        # Check if the node is a require or assert statement
        if isinstance(node, dict):
            return node.get('type') in ['RequireStatement', 'AssertStatement']
        return False

    def _is_effect(self, node):
        # Check if the node modifies the contract state
        if isinstance(node, dict):
            return node.get('type') in ['Assignment', 'VariableDeclaration']
        return False

    def _is_interaction(self, node):
        # Check if the node is an external call (e.g., call, send, transfer)
        if isinstance(node, dict):
            if node.get('type') == 'FunctionCall':
                expression = node.get('expression', {})
                if expression.get('type') == 'MemberAccess':
                    return expression.get('memberName') in ['call', 'send', 'transfer']
        return False

def main():
    # Load Solidity code from a file or string
    with open(sys.argv[1], 'r') as file:
        solidity_code = file.read()

    # Check for CEI pattern violations
    checker = CEIPatternChecker(solidity_code)
    violations = checker.check_cei_pattern()

    # Output results
    if violations:
        print("CEI pattern violations detected:")
        for violation in violations:
            print(f"Function: {violation['function']}, Line: {violation['line']}, Message: {violation['message']}")
    else:
        print("No CEI pattern violations detected.")

if __name__ == "__main__":
    main()