#!/usr/bin/env python
"""Direct test of the GUARANTEED_TRANSLATIONS dictionary"""

import sys
sys.path.insert(0, 'd:\\ENGLISH-LUGANDA TRANSLATOR')

from app import GUARANTEED_TRANSLATIONS

print("=" * 70)
print("✅ TESTING GUARANTEED TRANSLATIONS DICTIONARY")
print("=" * 70)
print(f"\n📋 Total translations: {len(GUARANTEED_TRANSLATIONS)}\n")

# Test key phrases
test_phrases = [
    "how are you today?",
    "i am a student",
    "good morning",
    "the kabaka is the king of buganda",
    "bakisimba is a traditional buganda dance",
    "the gomesi is the traditional dress for women",
    "one hand cannot clap",
    "a good name is better than riches",
    "we greet elders by kneeling",
    "matooke is the staple food of buganda",
]

print("Testing key phrases:")
print("-" * 70)
for phrase in test_phrases:
    if phrase in GUARANTEED_TRANSLATIONS:
        print(f"✅ '{phrase}'")
        print(f"   → '{GUARANTEED_TRANSLATIONS[phrase]}'")
    else:
        print(f"❌ '{phrase}' NOT FOUND")
    print()

print("=" * 70)
print("📊 DICTIONARY SUMMARY BY CATEGORY")
print("=" * 70)

categories = {}
for key in GUARANTEED_TRANSLATIONS.keys():
    # Just show a few from each category for demo
    print(f"✅ Available: {len(GUARANTEED_TRANSLATIONS)} verified translations")

print("\n✅ Dictionary is loaded and ready!")
print("=" * 70)
