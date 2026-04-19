#!/usr/bin/env python3
"""
Test translator with UNSEEN data (not in the dictionary)
These will use the AI model fallback
"""
import requests
import json
import time

time.sleep(2)

# Test data organized by category
test_cases = {
    "GREETINGS (NOT IN DICT)": [
        "How do you do?",
        "Nice to see you again",
        "Welcome to my home",
    ],
    "FAMILY RELATIONS (NOT IN DICT)": [
        "My son is very smart",
        "The daughter is studying",
        "Cousins are coming to visit",
    ],
    "DAILY ACTIVITIES (NOT IN DICT)": [
        "I eat rice and beans",
        "We go to the market every day",
        "She is cooking dinner",
    ],
    "CULTURE & TRADITIONS (NOT IN DICT)": [
        "The traditional ceremony is important",
        "We celebrate our heritage",
        "The elders share their wisdom",
    ],
    "EMOTIONS & FEELINGS (NOT IN DICT)": [
        "I am very happy today",
        "He feels sad about leaving",
        "We are excited for tomorrow",
    ],
    "QUESTIONS (NOT IN DICT)": [
        "Where do you live?",
        "What is your favorite food?",
        "Why do you love your culture?",
        "When will you visit home?",
    ],
    "DIASPORA & IDENTITY (NOT IN DICT)": [
        "Living abroad makes me miss home",
        "My children ask about their grandparents",
        "I teach them songs from Uganda",
        "We gather with other Baganda families",
    ],
    "NATURE & ENVIRONMENT (NOT IN DICT)": [
        "The rain is falling",
        "Beautiful flowers grow in the garden",
        "The sun is setting",
    ],
}

print("=" * 70)
print("🧪 TESTING UNSEEN DATA WITH AI MODEL FALLBACK")
print("=" * 70)
print("\n📊 These phrases are NOT in the dictionary")
print("✨ The AI Model (Helsinki-NLP/opus-mt-en-mul) will translate them\n")

results = []

for category, phrases in test_cases.items():
    print(f"\n📂 {category}")
    print("-" * 70)
    
    for phrase in phrases:
        try:
            r = requests.post('http://localhost:5000/api/translate', 
                            json={'text': phrase})
            data = r.json()
            
            in_dict = data['in_dictionary']
            translation = data['translation']
            
            # Show result
            status = "📚 DICT" if in_dict else "🤖 AI"
            print(f"{status} | {phrase}")
            print(f"     → {translation}")
            
            results.append({
                'phrase': phrase,
                'translation': translation,
                'in_dict': in_dict,
                'category': category
            })
            
        except Exception as e:
            print(f"❌ Error: {e}")

print("\n" + "=" * 70)
print("📈 SUMMARY")
print("=" * 70)

dict_count = sum(1 for r in results if r['in_dict'])
ai_count = sum(1 for r in results if not r['in_dict'])

print(f"✅ Total phrases tested: {len(results)}")
print(f"📚 Dictionary matches: {dict_count}")
print(f"🤖 AI Model translations: {ai_count}")
print(f"📊 AI fallback rate: {(ai_count/len(results)*100):.1f}%")

print("\n" + "=" * 70)
print("💡 TRY MORE IN THE WEB UI AT http://localhost:5000")
print("=" * 70)
print("\nType any English text to see how the translator handles it!")
print("Dictionary phrases appear INSTANTLY (verified)")
print("Unknown phrases use AI translation (may vary in quality)")
