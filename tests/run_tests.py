#!/usr/bin/env python
"""
Test runner for Kavak AI Sales Agent
Provides a convenient way to run different test suites
"""

import argparse
import os
import subprocess
import sys
from typing import List, Optional


def run_command(command: List[str], cwd: Optional[str] = None) -> int:
    """Run a command and return the exit code"""
    print(f"Running: {' '.join(command)}")
    result = subprocess.run(command, cwd=cwd)
    return result.returncode


def run_unit_tests(verbose: bool = False, coverage: bool = False) -> int:
    """Run unit tests"""
    print("\n=== Running Unit Tests ===\n")

    cmd = ["pytest", "tests/unit/"]
    if verbose:
        cmd.append("-v")
    if coverage:
        cmd = [
            "pytest",
            "--cov=src",
            "--cov-report=term",
            "--cov-report=html:coverage_reports/unit",
            "tests/unit/",
        ]

    return run_command(cmd)


def run_integration_tests(verbose: bool = False, coverage: bool = False) -> int:
    """Run integration tests"""
    print("\n=== Running Integration Tests ===\n")

    cmd = ["pytest", "tests/integration/"]
    if verbose:
        cmd.append("-v")
    if coverage:
        cmd = [
            "pytest",
            "--cov=src",
            "--cov-report=term",
            "--cov-report=html:coverage_reports/integration",
            "tests/integration/",
        ]

    return run_command(cmd)


def run_e2e_tests(verbose: bool = False, coverage: bool = False) -> int:
    """Run end-to-end tests"""
    print("\n=== Running End-to-End Tests ===\n")

    cmd = ["pytest", "tests/e2e/"]
    if verbose:
        cmd.append("-v")
    if coverage:
        cmd = [
            "pytest",
            "--cov=src",
            "--cov-report=term",
            "--cov-report=html:coverage_reports/e2e",
            "tests/e2e/",
        ]

    return run_command(cmd)


def run_all_tests(verbose: bool = False, coverage: bool = False) -> int:
    """Run all tests"""
    print("\n=== Running All Tests ===\n")

    cmd = ["pytest", "tests/"]
    if verbose:
        cmd.append("-v")
    if coverage:
        cmd = [
            "pytest",
            "--cov=src",
            "--cov-report=term",
            "--cov-report=html:coverage_reports/all",
            "tests/",
        ]

    return run_command(cmd)


def run_specific_test(test_path: str, verbose: bool = False) -> int:
    """Run a specific test file or directory"""
    print(f"\n=== Running Test: {test_path} ===\n")

    cmd = ["pytest", test_path]
    if verbose:
        cmd.append("-v")

    return run_command(cmd)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run tests for Kavak AI Sales Agent")

    # Test type arguments
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--unit", action="store_true", help="Run unit tests")
    group.add_argument(
        "--integration", action="store_true", help="Run integration tests"
    )
    group.add_argument("--e2e", action="store_true", help="Run end-to-end tests")
    group.add_argument("--all", action="store_true", help="Run all tests")
    group.add_argument("--test", type=str, help="Run a specific test file or directory")

    # Optional arguments
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--coverage", "-c", action="store_true", help="Generate coverage report"
    )

    args = parser.parse_args()

    # Create coverage directory if needed
    if args.coverage:
        os.makedirs("coverage_reports", exist_ok=True)

    # Run the appropriate tests
    if args.unit:
        exit_code = run_unit_tests(args.verbose, args.coverage)
    elif args.integration:
        exit_code = run_integration_tests(args.verbose, args.coverage)
    elif args.e2e:
        exit_code = run_e2e_tests(args.verbose, args.coverage)
    elif args.all:
        exit_code = run_all_tests(args.verbose, args.coverage)
    elif args.test:
        exit_code = run_specific_test(args.test, args.verbose)
    else:
        parser.print_help()
        exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
