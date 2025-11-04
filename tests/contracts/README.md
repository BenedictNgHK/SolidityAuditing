# Solidity Reentrancy Test Contracts

This directory contains comprehensive test contracts for validating reentrancy vulnerability detection tools.

## Directory Structure

```
TestContracts/
├── Safe/           # Contracts that should NOT be flagged as vulnerable
├── Unsafe/         # Contracts that SHOULD be flagged as vulnerable
└── README.md       # This file
```

## Safe Contracts (Should Pass - No False Positives)

### CEIGuard.sol
- **Pattern**: Proper Checks-Effects-Interactions with reentrancy guard
- **Protection**: Modifier-based reentrancy guard + CEI pattern
- **Safe Features**:
  - `noReentrancy()` modifier
  - Checks before effects
  - Effects before interactions
  - Uses `transfer()` instead of `call.value()`

### SafeDelegateCall.sol
- **Pattern**: Secure delegatecall usage
- **Protection**: Input validation + reentrancy guards + safe call patterns
- **Safe Features**:
  - Contract address validation
  - No self-calls
  - Staticcall for view functions
  - Controlled upgrade pattern

### CEI_require.sol
- **Pattern**: Basic CEI compliance with require statements
- **Protection**: Input validation before state changes

### CEI_revert.sol
- **Pattern**: CEI with conditional reverts
- **Protection**: Guard conditions that revert on invalid states

### OppenzepplinGuard.sol
- **Pattern**: OpenZeppelin-style reentrancy guard
- **Protection**: NonReentrant modifier

### SafeMultipleCall.sol
- **Pattern**: Multiple external calls following CEI
- **Protection**: All state changes before any external calls

### SimpleGuard.sol
- **Pattern**: Basic reentrancy guard
- **Protection**: Boolean lock pattern

### FalsePositive.sol
- **Pattern**: Edge cases that should NOT be flagged
- **Safe Features**:
  - External calls without state modifications
  - Staticcall usage
  - Pure/view functions
  - CEI-compliant patterns

## Unsafe Contracts (Should Fail - True Positives)

### ReentrancyAttack.sol
- **Vulnerability**: Classic reentrancy attack
- **Pattern**: External call before state update
- **Exploit**: `withdraw()` function allows reentrancy

### ComplexReentrancy.sol
- **Vulnerabilities**: Multiple reentrancy patterns
- **Patterns**:
  - State updates between external calls
  - Cross-function reentrancy
  - Bonus claiming with external calls

### DelegateCallReentrancy.sol
- **Vulnerabilities**: Unsafe delegatecall usage
- **Patterns**:
  - Delegatecall without validation
  - Storage modification through delegatecall
  - Unprotected upgrade mechanism

### CEI_violated.sol
- **Vulnerability**: Violates CEI pattern
- **Pattern**: State changes after external calls

### DAO.sol
- **Vulnerability**: Original DAO exploit
- **Pattern**: `executeProposal()` with external call before state validation

### DumbDao.sol
- **Vulnerability**: Simplified DAO-like reentrancy
- **Pattern**: Unprotected proposal execution

### StorageVariable.sol
- **Vulnerability**: Storage manipulation through reentrancy

### UnSafeMultipleCall.sol
- **Vulnerability**: Multiple unprotected external calls

### UpdateAfterCEI.sol
- **Vulnerability**: State updates after external interactions

### UpdateAfterGuard.sol
- **Vulnerability**: Bypasses reentrancy guard through indirect calls

### IndirectReentrancy.sol
- **Vulnerability**: Reentrancy through helper contracts
- **Pattern**: Cross-contract reentrancy attacks

## Running Tests

Use the comprehensive test script:

```bash
cd /path/to/SolidityAuditing
python3 test_all_samples.py
```

This will:
1. Test all safe contracts (should report no vulnerabilities)
2. Test all unsafe contracts (should report vulnerabilities)
3. Test real Etherscan contracts
4. Generate a detailed report

## Expected Results

### Safe Contracts
- Should report: "contains no Reentrancy vulnerability"
- False Positive Rate: 0%

### Unsafe Contracts
- Should report: "Vulnerability: Reentrancy" with specific functions
- True Positive Rate: 100%

### Etherscan Contracts
- DAO Contract (0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413): Should detect multiple vulnerabilities

## Adding New Test Contracts

### For Safe Contracts:
1. Ensure CEI pattern compliance
2. Include proper reentrancy guards
3. Use safe external call patterns (`transfer()`, `staticcall()`)
4. Add comprehensive comments explaining safety features

### For Unsafe Contracts:
1. Include clear reentrancy vulnerabilities
2. Document the specific vulnerable pattern
3. Add comments explaining the exploit
4. Keep contracts focused on specific vulnerability types

## Test Metrics

The test suite tracks:
- **True Positives**: Correctly identified vulnerabilities
- **True Negatives**: Correctly identified safe contracts
- **False Positives**: Incorrectly flagged safe contracts
- **False Negatives**: Missed vulnerabilities
- **Accuracy**: Overall correctness percentage

## Etherscan Test Addresses

- **0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413**: The DAO contract (vulnerable)
- Additional addresses can be added to the test script

## Contributing

When adding new test contracts:
1. Follow naming conventions
2. Include comprehensive documentation
3. Ensure contracts compile
4. Test with the full test suite
5. Update this README
