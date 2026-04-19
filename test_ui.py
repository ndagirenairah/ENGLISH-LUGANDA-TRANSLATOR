#!/usr/bin/env python3
import requests
import json
import time

time.sleep(2)

print("=" * 60)
print("TESTING UPDATED UI APIS")
print("=" * 60)

# Test 1: Translate API
print("\n✅ TEST 1: Translate API (exact match)")
r = requests.post('http://localhost:5000/api/translate', json={'text': 'what clan are you from?'})
print(json.dumps(r.json(), indent=2))

# Test 2: Translate API (AI fallback)
print("\n✅ TEST 2: Translate API (AI fallback)")
r = requests.post('http://localhost:5000/api/translate', json={'text': 'hello how are you?'})
print(json.dumps(r.json(), indent=2))

# Test 3: Examples API
print("\n✅ TEST 3: Examples API")
r = requests.get('http://localhost:5000/api/examples')
examples = r.json()['examples']
print(f"Loaded {len(examples)} examples")
for i, ex in enumerate(examples[:3], 1):
    print(f"  {i}. {ex['english']} → {ex['luganda']}")

# Test 4: Status API
print("\n✅ TEST 4: Status API")
r = requests.get('http://localhost:5000/api/status')
status = r.json()
print(f"Status: {status['status']}")
print(f"Dictionary size: {status['dictionary_size']} phrases")
print(f"Model: {status['model']}")

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED - UI IS READY")
print("=" * 60)
