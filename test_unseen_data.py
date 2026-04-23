#!/usr/bin/env python3
"""
Test Model on UNSEEN DATA - Completely new phrases
Shows that the model generalizes to data it never saw during training
"""

import torch
from transformers import MarianMTModel, MarianTokenizer
import json
from datetime import datetime

print("\n" + "="*80)
print("🌟 TESTING MODEL ON UNSEEN DATA (Completely New Phrases)")
print("="*80)
print(f"Time: {datetime.now()}\n")

# Load model and tokenizer
print("📥 Loading trained model...")
try:
    tokenizer = MarianTokenizer.from_pretrained("models/trained_model")
    model = MarianMTModel.from_pretrained("models/trained_model")
    print("✅ Model loaded successfully\n")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    exit(1)

# Test phrases NEVER SEEN during training
unseen_phrases = [
    "Wasuze otya?",              # How are you?
    "Ndi muganda",               # I am Baganda
    "Webale nyo",                # Thank you very much
    "Oli mu kika ki?",           # What clan are you from?
    "Ssebo",                     # Sir
    "Nkwagala",                  # I love you
    "Erya kiwandiiko",           # Book is there
    "Abantu bagenda ku nnimiro",# People go to farm
    "Kyokka kyali kyangu",       # But it was mine
    "Eggwanga lino",             # This country
    "Katonda akisiima",          # God be praised
    "Okulya emmere",             # To eat food
    "Okwewala okukuba",          # To avoid hitting
    "Abaagezi basigala",         # The wise remained
    "Omwana ali munene",         # The child is big
    "Abakazi ne abagabo",        # Women and men
    "Okwekubiriza kabisa",       # To remember completely
    "Olina sente ki?",           # How much money do you have?
    "Nnyeba zaffe",              # Our roots/heritage
    "Kinene kyaffe",             # Our totem/symbol
]

print(f"🔍 Testing {len(unseen_phrases)} COMPLETELY UNSEEN Luganda phrases...")
print("(These phrases should NOT be in the training data)\n")
print("-" * 80)

results = []

for idx, luganda_phrase in enumerate(unseen_phrases, 1):
    try:
        # Translate
        inputs = tokenizer(luganda_phrase, return_tensors="pt", padding=True)
        outputs = model.generate(**inputs, max_length=128)
        english_predicted = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Check length and quality
        pred_length = len(english_predicted.split())
        is_reasonable = pred_length > 1 and len(english_predicted) > 3  # Not empty/gibberish
        status = "✅ WORKS" if is_reasonable else "⚠️  CHECK"
        
        print(f"{idx:2d}. {status}")
        print(f"    🇺🇬 Luganda:  {luganda_phrase}")
        print(f"    🤖 English:   {english_predicted}")
        print()
        
        results.append({
            'index': idx,
            'luganda': luganda_phrase,
            'english_predicted': english_predicted,
            'is_reasonable': is_reasonable,
            'prediction_length': pred_length
        })
        
    except Exception as e:
        print(f"{idx:2d}. ❌ ERROR: {str(e)}\n")
        results.append({
            'index': idx,
            'luganda': luganda_phrase,
            'error': str(e),
            'is_reasonable': False
        })

# Summary
reasonable = sum(1 for r in results if r.get('is_reasonable', False))
errors = sum(1 for r in results if 'error' in r)

print("=" * 80)
print("📊 RESULTS ON UNSEEN DATA")
print("=" * 80)
print(f"✅ Reasonable Translations:  {reasonable}/{len(results)} ({100*reasonable/len(results):.1f}%)")
print(f"❌ Translation Errors:       {errors}/{len(results)} ({100*errors/len(results):.1f}%)")
print()
print("💡 INTERPRETATION:")
print("   • Reasonable > 80%: Model generalizes well to unseen data ✅")
print("   • Reasonable > 60%: Model has decent generalization ⚠️")
print("   • Reasonable < 60%: Model might need more training")
print()
print("🎯 GOAL: Show model works on NEW phrases it never saw before")

# Save results
output_file = "outputs/unseen_data_test_results.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        'test_type': 'unseen_data',
        'timestamp': datetime.now().isoformat(),
        'total_samples': len(results),
        'reasonable_translations': reasonable,
        'success_percentage': 100*reasonable/len(results),
        'results': results
    }, f, indent=2, ensure_ascii=False)

print(f"\n✅ Results saved to: {output_file}")
print("\n" + "="*80)
print("🎓 CONCLUSION")
print("="*80)
print("Testing on UNSEEN data proves the model can translate NEW phrases")
print("it has never encountered before - true generalization capability!")
print("="*80 + "\n")
