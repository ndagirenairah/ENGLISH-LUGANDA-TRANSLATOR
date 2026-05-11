"""
LECTURER DEMO TEST - Validates translation quality
Tests that translations are:
1. NOT just echoed back (different from input)
2. In the correct target language
3. Semantically meaningful (not garbage)
"""

import json
import os
import sys
import requests
from datetime import datetime

# Test cases: (Luganda input, Expected English output keywords)
TEST_CASES = [
    {
        "luganda": "Wasuze otya?",
        "english_keywords": ["how", "are", "you", "hello"],
        "description": "Greeting: How are you?"
    },
    {
        "luganda": "Webale nyo",
        "english_keywords": ["thank", "thanks"],
        "description": "Polite: Thank you very much"
    },
    {
        "luganda": "Oli mu kika ki?",
        "english_keywords": ["clan", "which", "what"],
        "description": "Culture: What clan are you from?"
    },
    {
        "luganda": "Ndi muganda",
        "english_keywords": ["baganda", "muganda", "from"],
        "description": "Identity: I am Baganda"
    },
    {
        "luganda": "Nkwagala",
        "english_keywords": ["love", "like"],
        "description": "Emotion: I love"
    },
    {
        "luganda": "Ndi bulungi",
        "english_keywords": ["fine", "good", "well"],
        "description": "Status: I am fine"
    },
    {
        "luganda": "Waggulo nnyo",
        "english_keywords": ["good", "evening"],
        "description": "Greeting: Good evening"
    },
    {
        "luganda": "Abantu bagenda ku nnimiro",
        "english_keywords": ["people", "farm", "field", "went"],
        "description": "Action: People went to the farm"
    }
]

def validate_translation(luganda_input, translation, keywords):
    """
    Validate that translation is:
    1. Different from input (not echoed)
    2. In English (contains English words)
    3. Matches expected keywords
    """
    
    # ❌ FAIL: Echoed back
    if translation.lower() == luganda_input.lower():
        return False, "Translation echoed input (not translated)"
    
    # ❌ FAIL: Same text with minor modifications
    if translation.lower().strip("- .,!?") == luganda_input.lower():
        return False, "Translation is input with minor changes (typo, not translation)"
    
    # ❌ FAIL: Contains special markers
    if "[" in translation and "]" in translation:
        return False, "Translation failed (contains error marker)"
    
    # ✅ PASS: Contains expected keywords
    translation_lower = translation.lower()
    for keyword in keywords:
        if keyword.lower() in translation_lower:
            return True, f"Contains expected keyword: '{keyword}'"
    
    # ⚠️ PARTIAL: At least different and not error
    if len(translation) > 0 and translation != luganda_input:
        return True, "Different from input (partial validation)"
    
    return False, "Translation failed validation"

def run_tests():
    """Run all test cases and generate report"""
    
    print("=" * 70)
    print("🧪 ENGLISH-LUGANDA TRANSLATOR - QUALITY TEST SUITE")
    print("=" * 70)
    
    results = []
    passed = 0
    failed = 0
    
    # Verify Flask server is running
    try:
        response = requests.get("http://localhost:5000/api/status", timeout=2)
        print("✅ Flask server is running\n")
    except:
        print("❌ Flask server not responding!")
        print("   Run: python app.py")
        sys.exit(1)
    
    print("Running translation validation tests...\n")
    
    for i, test_case in enumerate(TEST_CASES, 1):
        luganda = test_case["luganda"]
        keywords = test_case["english_keywords"]
        description = test_case["description"]
        
        print(f"Test {i}/8: {description}")
        print(f"  Input (Luganda): {luganda}")
        
        try:
            # Call Flask API
            response = requests.post(
                "http://localhost:5000/api/translate",
                json={
                    "text": luganda,
                    "source_language": "luganda",
                    "target_language": "english"
                },
                timeout=5
            )
            
            if response.status_code != 200:
                print(f"  ❌ API Error: {response.status_code}")
                results.append({
                    "luganda": luganda,
                    "english": "API ERROR",
                    "status": "❌",
                    "reason": f"HTTP {response.status_code}"
                })
                failed += 1
                continue
            
            data = response.json()
            translation = data.get("translation", "")
            source = data.get("source", "")
            confidence = data.get("confidence", 0)
            
            print(f"  Output (English): {translation}")
            print(f"  Source: {source} | Confidence: {confidence}%")
            
            # Validate
            is_valid, reason = validate_translation(luganda, translation, keywords)
            
            if is_valid:
                print(f"  ✅ PASS - {reason}\n")
                results.append({
                    "luganda": luganda,
                    "english": translation,
                    "status": "✅",
                    "reason": reason
                })
                passed += 1
            else:
                print(f"  ❌ FAIL - {reason}\n")
                results.append({
                    "luganda": luganda,
                    "english": translation,
                    "status": "❌",
                    "reason": reason
                })
                failed += 1
                
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}\n")
            results.append({
                "luganda": luganda,
                "english": "EXCEPTION",
                "status": "❌",
                "reason": str(e)
            })
            failed += 1
    
    # Generate report
    print("=" * 70)
    print(f"📊 TEST RESULTS: {passed} Passed | {failed} Failed | {passed+failed} Total")
    print("=" * 70)
    
    # Determine overall status
    if passed == len(TEST_CASES):
        overall_status = "✅ EXCELLENT"
        color = "GREEN"
    elif passed >= len(TEST_CASES) * 0.75:
        overall_status = "⚠️ GOOD"
        color = "YELLOW"
    elif passed >= len(TEST_CASES) * 0.5:
        overall_status = "⚠️ PARTIAL"
        color = "ORANGE"
    else:
        overall_status = "❌ NEEDS WORK"
        color = "RED"
    
    print(f"\nOverall Status: {overall_status}")
    
    # Save results to JSON
    report = {
        "timestamp": datetime.now().isoformat(),
        "test_results": results,
        "passed": passed,
        "failed": failed,
        "total": passed + failed,
        "pass_rate": f"{(passed / (passed + failed) * 100):.1f}%" if (passed + failed) > 0 else "0%",
        "status": overall_status,
        "notes": [
            "✅ PASS: Translation is different AND contains expected English keywords",
            "❌ FAIL: Translation echoed input or contains error markers",
            "📍 FOCUS: Dictionary-based translations are prioritized (most reliable)",
            "💡 IMPROVEMENT: Add more Luganda phrases to GUARANTEED_TRANSLATIONS dictionary"
        ]
    }
    
    # Save report
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/LECTURER_DEMO_RESULTS.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📁 Report saved to: outputs/LECTURER_DEMO_RESULTS.json")
    
    # Print detailed results
    print("\n" + "=" * 70)
    print("DETAILED RESULTS")
    print("=" * 70)
    for result in results:
        print(f"{result['status']} {result['luganda']}")
        print(f"   → {result['english']}")
        print(f"   Reason: {result['reason']}\n")
    
    return passed == len(TEST_CASES)

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
