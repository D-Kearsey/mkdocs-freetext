#!/usr/bin/env python3
"""
Consolidated Test Runner for MkDocs Free-Text Plugin

This test runner replaces multiple scattered test runners and provides:
- Unified test execution
- Clear test categorization
- Comprehensive reporting
- Easy CI/CD integration

Replaces: run_all_tests.py, run_enhanced_tests.py, simple_test_runner.py
"""

import pytest
import os
import sys
from pathlib import Path


def main():
    """Main test runner function."""
    print("=" * 80)
    print("🧪 MkDocs Free-Text Plugin - Comprehensive Test Suite")
    print("=" * 80)
    
    # Get the test directory
    test_dir = Path(__file__).parent
    
    # Define test categories
    test_categories = {
        'JavaScript Integration': [
            'test_javascript_integration.py',
        ],
        'HTML Generation': [
            'test_html_generation.py',
        ],
        'Core Plugin Functionality': [
            'test_plugin.py',
            'test_config.py',
            'test_content_processing.py',
        ],
        'Error Handling': [
            'test_error_handling.py',
        ],
        'Performance': [
            'test_performance.py',
        ]
    }
    
    # Check which test files actually exist
    existing_tests = []
    missing_tests = []
    
    for category, test_files in test_categories.items():
        print(f"\n📂 {category}:")
        for test_file in test_files:
            test_path = test_dir / test_file
            if test_path.exists():
                print(f"  ✅ {test_file}")
                existing_tests.append(str(test_path))
            else:
                print(f"  ❌ {test_file} (missing)")
                missing_tests.append(test_file)
    
    if missing_tests:
        print(f"\n⚠️  Warning: {len(missing_tests)} test files are missing")
    
    print(f"\n🚀 Running {len(existing_tests)} test files...")
    print("=" * 80)
    
    # Run pytest with comprehensive options
    pytest_args = [
        '-v',  # Verbose output
        '--tb=short',  # Short traceback format
        '--strict-markers',  # Strict marker handling
        '--disable-warnings',  # Disable warnings for cleaner output
        '-x',  # Stop on first failure (optional)
    ] + existing_tests
    
    # Run the tests
    exit_code = pytest.main(pytest_args)
    
    print("\n" + "=" * 80)
    if exit_code == 0:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED!")
    print("=" * 80)
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
