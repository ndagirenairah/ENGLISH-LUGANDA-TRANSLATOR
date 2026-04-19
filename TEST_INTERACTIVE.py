#!/usr/bin/env python3
# ============================================================================
# 🎯 INTERACTIVE MODEL TESTER
# ============================================================================
# Test how the model would translate your own Luganda sentences
# This is like a practice tool before running the real model
# ============================================================================

print("\n" + "=" * 70)
print("🎯 INTERACTIVE LUGANDA TRANSLATION TESTER")
print("=" * 70)
print()

import csv

# ============================================================================
# LOAD TRAINING DATA (To see what model learned)
# ============================================================================
print("📖 Loading training data...")

try:
    pairs = {}  # Dictionary to store Luganda → English mappings
    
    with open('data/luganda_english_dataset_combined.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            luganda = row['luganda'].lower().strip()
            english = row['english'].lower().strip()
            pairs[luganda] = english
    
    print(f"✅ Loaded {len(pairs)} translations")
    print()
    
except FileNotFoundError:
    print("❌ Training data not found!")
    exit()

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def find_best_match(input_text):
    """Find the closest matching training example"""
    input_lower = input_text.lower().strip()
    
    # Exact match
    if input_lower in pairs:
        return pairs[input_lower], "EXACT MATCH ✅"
    
    # Partial match (substring)
    for luganda, english in pairs.items():
        if input_lower in luganda or luganda in input_lower:
            return english, "PARTIAL MATCH 🟡"
    
    # Word match
    input_words = set(input_lower.split())
    best_match = None
    best_score = 0
    
    for luganda, english in pairs.items():
        luganda_words = set(luganda.split())
        overlap = len(input_words & luganda_words)
        if overlap > 0 and overlap > best_score:
            best_score = overlap
            best_match = (english, f"WORD MATCH ({overlap} words)")
    
    if best_match:
        return best_match
    
    return None, "NO MATCH ❌"

def explain_translation(luganda_input, english_output, match_type):
    """Explain how the translation works"""
    
    print()
    print("📊 ANALYSIS:")
    print(f"   Match Type:     {match_type}")
    
    # Show pattern
    luganda_words = luganda_input.lower().split()
    english_words = english_output.lower().split()
    
    print(f"   Input words:    {len(luganda_words)} ({', '.join(luganda_words[:5])}{'...' if len(luganda_words) > 5 else ''})")
    print(f"   Output words:   {len(english_words)} ({', '.join(english_words[:5])}{'...' if len(english_words) > 5 else ''})")
    print()

# ============================================================================
# INTERACTIVE LOOP
# ============================================================================
print("=" * 70)
print("🎤 TESTING LUGANDA TRANSLATIONS")
print("=" * 70)
print()
print("How it works:")
print("   1. You type a Luganda sentence")
print("   2. The model finds similar training examples")
print("   3. It suggests the best translation")
print()
print("Commands:")
print("   - Type 'quit' to exit")
print("   - Type 'show' to see first 20 training pairs")
print("   - Type 'random' to see random example")
print()

import random

while True:
    print()
    luganda_input = input("🇺🇬 Enter Luganda text (or command): ").strip()
    
    if not luganda_input:
        print("   (Empty input - try again)")
        continue
    
    if luganda_input.lower() == 'quit':
        print("   ✅ Thank you for testing!")
        break
    
    if luganda_input.lower() == 'show':
        print()
        print("📋 FIRST 20 TRAINING PAIRS:")
        print()
        for i, (lug, eng) in enumerate(list(pairs.items())[:20], 1):
            print(f"   {i:2}. 🇺🇬 {lug:40} → 🇬🇧 {eng}")
        continue
    
    if luganda_input.lower() == 'random':
        lug, eng = random.choice(list(pairs.items()))
        print()
        print("📚 RANDOM TRAINING EXAMPLE:")
        print(f"   🇺🇬 Luganda: {lug}")
        print(f"   🇬🇧 English: {eng}")
        continue
    
    # Find translation
    translation, match_type = find_best_match(luganda_input)
    
    if translation:
        print()
        print(f"🇬🇧 Suggested English: {translation}")
        explain_translation(luganda_input, translation, match_type)
        
        if "EXACT" in match_type:
            print("   💯 The model learned this exact phrase!")
        elif "PARTIAL" in match_type:
            print("   🎯 The model found a similar phrase!")
        elif "WORD" in match_type:
            print("   🔍 The model matched some words!")
    else:
        print()
        print("   ❌ No matching translation found")
        print("   💡 Tip: Try a shorter phrase or words from the training data")
        print()
        print("   Here are some phrases the model DOES know:")
        samples = random.sample(list(pairs.keys()), 3)
        for i, phrase in enumerate(samples, 1):
            print(f"      {i}. {phrase}")

print()
print("=" * 70)
print("Thank you for testing! 🎉")
print("=" * 70)
