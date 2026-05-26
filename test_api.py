"""
Test script for English-Luganda Translator API
=============================================

Run this after starting the Flask server to test all endpoints.
"""

import requests
import json
import sys

BASE_URL = "http://localhost:5000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_result(endpoint, status, response, expected_status=200):
    """Print test result."""
    status_text = f"{Colors.GREEN}PASS{Colors.END}" if status == expected_status else f"{Colors.RED}FAIL{Colors.END}"
    print(f"  [{status_text}] {endpoint}")
    if status != expected_status:
        print(f"      Expected: {expected_status}, Got: {status}")
        print(f"      Response: {response}")
    print()

def test_health():
    """Test health check endpoint."""
    print(f"\n{Colors.BLUE}Testing Health Check{Colors.END}")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print_result("GET /api/health", response.status_code, response.json())
    except Exception as e:
        print(f"  {Colors.RED}ERROR{Colors.END}: {str(e)}\n")

def test_status():
    """Test status endpoint."""
    print(f"{Colors.BLUE}Testing Status Endpoint{Colors.END}")
    try:
        response = requests.get(f"{BASE_URL}/api/status")
        print_result("GET /api/status", response.status_code, response.json())
    except Exception as e:
        print(f"  {Colors.RED}ERROR{Colors.END}: {str(e)}\n")

def test_docs():
    """Test documentation endpoint."""
    print(f"{Colors.BLUE}Testing API Documentation{Colors.END}")
    try:
        response = requests.get(f"{BASE_URL}/api/docs")
        print_result("GET /api/docs", response.status_code, response.json())
    except Exception as e:
        print(f"  {Colors.RED}ERROR{Colors.END}: {str(e)}\n")

def test_single_translation():
    """Test single text translation."""
    print(f"{Colors.BLUE}Testing Single Translation{Colors.END}")
    
    test_cases = [
        ("Hello", "Valid text"),
        ("", "Empty text (should fail)"),
        ("The quick brown fox jumps over the lazy dog", "Long text"),
    ]
    
    for text, description in test_cases:
        try:
            payload = {'text': text}
            response = requests.post(
                f"{BASE_URL}/api/translate",
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            expected = 200 if text else 400
            print_result(f"POST /api/translate ({description})", response.status_code, response.json(), expected)
        except Exception as e:
            print(f"  {Colors.RED}ERROR{Colors.END}: {str(e)}\n")

def test_batch_translation():
    """Test batch translation."""
    print(f"{Colors.BLUE}Testing Batch Translation{Colors.END}")
    
    test_cases = [
        (["Hello", "Good morning"], "Normal batch"),
        ([], "Empty list (should fail)"),
        (["Text " + str(i) for i in range(51)], "Batch too large (should fail)"),
    ]
    
    for texts, description in test_cases:
        try:
            payload = {'texts': texts}
            response = requests.post(
                f"{BASE_URL}/api/translate-batch",
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            expected = 200 if texts and len(texts) <= 50 else 400
            print_result(f"POST /api/translate-batch ({description})", response.status_code, response.json(), expected)
        except Exception as e:
            print(f"  {Colors.RED}ERROR{Colors.END}: {str(e)}\n")

def test_invalid_endpoint():
    """Test invalid endpoint."""
    print(f"{Colors.BLUE}Testing Invalid Endpoint{Colors.END}")
    try:
        response = requests.get(f"{BASE_URL}/api/invalid")
        print_result("GET /api/invalid", response.status_code, response.json(), 404)
    except Exception as e:
        print(f"  {Colors.RED}ERROR{Colors.END}: {str(e)}\n")

def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("English-Luganda Translator - API Test Suite")
    print("="*80)
    
    # Check server connectivity
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=2)
    except requests.exceptions.ConnectionError:
        print(f"\n{Colors.RED}ERROR: Cannot connect to server at {BASE_URL}{Colors.END}")
        print("Please start the Flask server first: python web_server_flask.py\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}ERROR: {str(e)}{Colors.END}\n")
        sys.exit(1)
    
    # Run tests
    test_health()
    test_status()
    test_docs()
    test_single_translation()
    test_batch_translation()
    test_invalid_endpoint()
    
    print("="*80)
    print(f"Test suite completed.\n")

if __name__ == '__main__':
    main()
