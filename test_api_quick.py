#!/usr/bin/env python
import requests
import json

url = "http://localhost:5000/api/translate"
headers = {"Content-Type": "application/json"}

test_sentences = [
    "How are you today?",
    "I am a student",
    "Good morning",
    "Welcome to Uganda"
]

print("=" * 70)
print("🧪 TESTING WEB APP API")
print("=" * 70)
print()

for sentence in test_sentences:
    try:
        data = {"text": sentence}
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        print(f"📝 English:  {sentence}")
        print(f"🇺🇬 Luganda:  {result.get('translation', 'ERROR')}")
        print(f"   Status:   {result.get('status', 'unknown')}")
        print()
    except Exception as e:
        print(f"❌ Error testing '{sentence}': {e}")
        print()

print("=" * 70)
