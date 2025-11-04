#!/usr/bin/env python3
"""
Comprehensive test script for Solidity Reentrancy Auditing Tool
Tests all sample contracts and Etherscan addresses
"""

import os
import sys
import glob
import subprocess
import json
from pathlib import Path

class ReentrancyTestSuite:
    def __init__(self):
        self.project_root = Path("/Users/wuyuze/Desktop/FYP/SolidityAuditing")
        self.test_results = {
            "safe_contracts": [],
            "unsafe_contracts": [],
            "etherscan_addresses": [],
            "summary": {}
        }

    def get_test_files(self):
        """Get all test contract files"""
        safe_files = glob.glob(str(self.project_root / "TestContracts" / "Safe" / "*.sol"))
        unsafe_files = glob.glob(str(self.project_root / "TestContracts" / "Unsafe" / "*.sol"))
        return safe_files, unsafe_files

    def get_etherscan_addresses(self):
        """Get list of known vulnerable Etherscan addresses"""
        return [
            {
                "address": "0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413",
                "name": "The DAO Contract",
                "expected_vulnerabilities": True,
                "description": "Original DAO contract exploited in 2016"
            },
            {
                "address": "0x0c6C80D2061afA35E160F3799411d83BDEEA0a5A",
                "name": "Test Address",
                "expected_vulnerabilities": True,
                "description": "Test address - should have vulnerabilities"
            }
        ]

    def run_tool_on_file(self, file_path):
        """Run the reentrancy tool on a file"""
        try:
            cmd = [sys.executable, str(self.project_root / "main.py"), file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Timeout"
        except Exception as e:
            return -1, "", str(e)

    def run_tool_on_address(self, address):
        """Run the reentrancy tool on an Etherscan address"""
        try:
            cmd = [sys.executable, str(self.project_root / "main.py"), address]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Timeout"
        except Exception as e:
            return -1, "", str(e)

    def parse_tool_output(self, output):
        """Parse the tool output to determine if vulnerabilities were found"""
        # Remove warning messages and clean up output
        lines = output.split('\n')
        clean_lines = [line for line in lines if not line.startswith('Warning:') and line.strip()]

        clean_output = '\n'.join(clean_lines)

        if "no reentrancy vulnerability" in clean_output.lower():
            return False, []  # No vulnerabilities
        elif "vulnerability: reentrancy" in clean_output.lower() or "reentrancy:" in clean_output.lower():
            return True, self.extract_vulnerabilities(clean_output)  # Vulnerabilities found
        else:
            return None, []  # Unable to determine

    def extract_vulnerabilities(self, output):
        """Extract vulnerability details from output"""
        vulnerabilities = []
        lines = output.split('\n')
        current_contract = None

        for line in lines:
            if "In contract" in line:
                current_contract = line.split("In contract")[1].strip()
            elif "In function" in line and "Vulnerability: Reentrancy" in line:
                func_name = line.split("In function")[1].split(":")[0].strip()
                vulnerabilities.append({
                    "contract": current_contract,
                    "function": func_name,
                    "type": "Reentrancy"
                })

        return vulnerabilities

    def test_contract_file(self, file_path, expected_vulnerable):
        """Test a single contract file"""
        file_name = Path(file_path).name

        print(f"\n🧪 Testing {file_name}...")
        print(f"   Expected: {'VULNERABLE' if expected_vulnerable else 'SAFE'}")

        returncode, stdout, stderr = self.run_tool_on_file(file_path)

        if returncode != 0:
            print(f"   ❌ Tool execution failed: {stderr}")
            return {
                "file": file_name,
                "expected": expected_vulnerable,
                "success": False,
                "error": stderr,
                "actual": None,
                "vulnerabilities": []
            }

        has_vulns, vulnerabilities = self.parse_tool_output(stdout)

        if has_vulns is None:
            print(f"   ⚠️  Could not parse tool output")
            return {
                "file": file_name,
                "expected": expected_vulnerable,
                "success": False,
                "error": "Parse error",
                "actual": None,
                "vulnerabilities": []
            }

        result_correct = (has_vulns == expected_vulnerable)
        status = "✅" if result_correct else "❌"

        print(f"   {status} Actual: {'VULNERABLE' if has_vulns else 'SAFE'}")
        if vulnerabilities:
            print(f"   📋 Found {len(vulnerabilities)} vulnerabilities:")
            for vuln in vulnerabilities:
                print(f"      - {vuln['contract']}.{vuln['function']}")

        return {
            "file": file_name,
            "expected": expected_vulnerable,
            "success": True,
            "actual": has_vulns,
            "correct": result_correct,
            "vulnerabilities": vulnerabilities
        }

    def test_etherscan_address(self, addr_info):
        """Test an Etherscan address"""
        address = addr_info["address"]
        name = addr_info["name"]
        expected = addr_info["expected_vulnerabilities"]

        print(f"\n🌐 Testing Etherscan: {name}")
        print(f"   Address: {address}")
        print(f"   Expected: {'VULNERABLE' if expected else 'SAFE'}")

        returncode, stdout, stderr = self.run_tool_on_address(address)

        if returncode != 0:
            # For Etherscan addresses, API failures are expected in test environments
            error_output = stderr + stdout
            if "Could not retrieve source code" in error_output or "Failed to get source" in error_output:
                print(f"   ⚠️  Etherscan API unavailable (expected in test environment)")
                return {
                    "address": address,
                    "name": name,
                    "expected": expected,
                    "success": True,  # Don't count API failures as test failures
                    "error": "Etherscan API unavailable",
                    "actual": None,
                    "correct": None,  # Unknown result due to API
                    "vulnerabilities": []
                }
            else:
                print(f"   ❌ Tool execution failed: {stderr}")
                return {
                    "address": address,
                    "name": name,
                    "expected": expected,
                    "success": False,
                    "error": stderr,
                    "actual": None,
                    "vulnerabilities": []
                }

        has_vulns, vulnerabilities = self.parse_tool_output(stdout)

        if has_vulns is None:
            print(f"   ⚠️  Could not parse tool output")
            return {
                "address": address,
                "name": name,
                "expected": expected,
                "success": False,
                "error": "Parse error",
                "actual": None,
                "vulnerabilities": []
            }

        result_correct = (has_vulns == expected)
        status = "✅" if result_correct else "❌"

        print(f"   {status} Actual: {'VULNERABLE' if has_vulns else 'SAFE'}")
        if vulnerabilities:
            print(f"   📋 Found {len(vulnerabilities)} vulnerabilities:")
            for vuln in vulnerabilities:
                print(f"      - {vuln['contract']}.{vuln['function']}")

        return {
            "address": address,
            "name": name,
            "expected": expected,
            "success": True,
            "actual": has_vulns,
            "correct": result_correct,
            "vulnerabilities": vulnerabilities
        }

    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Comprehensive Reentrancy Tool Test Suite")
        print("=" * 60)

        # Test safe contracts
        print("\n🛡️  Testing SAFE Contracts (should report NO vulnerabilities)")
        print("-" * 50)

        safe_files, unsafe_files = self.get_test_files()

        for file_path in safe_files:
            result = self.test_contract_file(file_path, expected_vulnerable=False)
            self.test_results["safe_contracts"].append(result)

        # Test unsafe contracts
        print("\n⚠️  Testing UNSAFE Contracts (should report vulnerabilities)")
        print("-" * 50)

        for file_path in unsafe_files:
            result = self.test_contract_file(file_path, expected_vulnerable=True)
            self.test_results["unsafe_contracts"].append(result)

        # Test Etherscan addresses
        print("\n🌐 Testing Etherscan Addresses")
        print("-" * 50)

        etherscan_addresses = self.get_etherscan_addresses()
        for addr_info in etherscan_addresses:
            result = self.test_etherscan_address(addr_info)
            self.test_results["etherscan_addresses"].append(result)

        self.generate_report()

    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)

        # Calculate statistics
        safe_results = self.test_results["safe_contracts"]
        unsafe_results = self.test_results["unsafe_contracts"]
        etherscan_results = self.test_results["etherscan_addresses"]

        def calc_stats(results):
            total = len(results)
            successful = sum(1 for r in results if r["success"])
            # Only count results that have a definitive correct/incorrect outcome
            correct = sum(1 for r in results if r.get("correct") is True)
            return total, successful, correct

        # Safe contracts stats
        safe_total, safe_successful, safe_correct = calc_stats(safe_results)
        safe_accuracy = (safe_correct / safe_successful * 100) if safe_successful > 0 else 0

        # Unsafe contracts stats
        unsafe_total, unsafe_successful, unsafe_correct = calc_stats(unsafe_results)
        unsafe_accuracy = (unsafe_correct / unsafe_successful * 100) if unsafe_successful > 0 else 0

        # Etherscan stats
        eth_total, eth_successful, eth_correct = calc_stats(etherscan_results)
        eth_accuracy = (eth_correct / eth_successful * 100) if eth_successful > 0 else 0

        print(f"\n🛡️  SAFE Contracts:")
        print(f"   Total: {safe_total}")
        print(f"   Successful: {safe_successful}")
        print(f"   Accuracy: {safe_accuracy:.1f}%")
        print(f"   True Negatives: {safe_correct}")

        print(f"\n⚠️  UNSAFE Contracts:")
        print(f"   Total: {unsafe_total}")
        print(f"   Successful: {unsafe_successful}")
        print(f"   Accuracy: {unsafe_accuracy:.1f}%")
        print(f"   True Positives: {unsafe_correct}")

        print(f"\n🌐 Etherscan Addresses:")
        print(f"   Total: {eth_total}")
        print(f"   Successful: {eth_successful}")
        print(f"   Accuracy: {eth_accuracy:.1f}%")
        print(f"   Correct Results: {eth_correct}")

        # Overall statistics
        total_tests = safe_total + unsafe_total + eth_total
        total_successful = safe_successful + unsafe_successful + eth_successful
        total_correct = safe_correct + unsafe_correct + eth_correct

        print(f"\n🎯 OVERALL PERFORMANCE:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Successful: {total_successful}")
        if total_successful > 0:
            overall_accuracy = (total_correct / total_successful * 100)
            print(f"   Overall Accuracy: {overall_accuracy:.1f}%")
        else:
            print(f"   Overall Accuracy: N/A")

        # List failures
        print(f"\n❌ FAILED TESTS:")
        all_results = safe_results + unsafe_results + etherscan_results
        failures = [r for r in all_results if not r.get("success", True) or not r.get("correct", True)]

        if not failures:
            print("   ✅ All tests passed!")
        else:
            for failure in failures:
                test_type = "Contract" if "file" in failure else "Etherscan"
                name = failure.get("file", failure.get("name", "Unknown"))
                reason = failure.get("error", "Incorrect result")
                print(f"   - {test_type}: {name} - {reason}")

        # Save detailed results
        with open(self.project_root / "test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)

        print(f"\n💾 Detailed results saved to: test_results.json")

if __name__ == "__main__":
    tester = ReentrancyTestSuite()
    tester.run_all_tests()
