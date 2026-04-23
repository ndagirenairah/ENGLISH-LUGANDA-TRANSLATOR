#!/usr/bin/env python3
"""
Test Model on KNOWN DATA - Phrases the model was trained on
Shows that the model learned the training data correctly
"""

import pandas as pd
import torch
from transformers import MarianMTModel, MarianTokenizer
import json
from datetime import datetime

print("\n" + "="*80)
print("🎯 TESTING MODEL ON KNOWN DATA (Training Data)")
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

# Load training data
print("📂 Loading training data...")
try:
    df = pd.read_csv("luganda_training_data.csv")
    print(f"✅ Loaded {len(df)} total pairs\n")
except Exception as e:
    print(f"❌ Error loading data: {e}")
    exit(1)

# Select sample phrases from training data (known data)
print("🔍 Selecting 20 random samples from KNOWN training data...\n")
known_samples = df.sample(n=min(20, len(df)), random_state=42)

# Test translations
results = []
print("🔄 Testing translations on KNOWN data:")
print("-" * 80)

for idx, (_, row) in enumerate(known_samples.iterrows(), 1):
    luganda = row['luganda']
    english_reference = row['english']
    
    # Translate
    try:
        inputs = tokenizer(luganda, return_tensors="pt", padding=True)
        outputs = model.generate(**inputs, max_length=128)
        english_predicted = tokenizer.decode(outputs[0], skip_special_tokens=True)
    except Exception as e:
        english_predicted = f"ERROR: {str(e)}"
    
    # Check if it's reasonable
    match_quality = "✅ PERFECT" if english_predicted.lower().strip() == english_reference.lower().strip() else "⚠️  DIFFERENT"
    
    print(f"{idx}. {match_quality}")
    print(f"   🇺🇬 Luganda Input:      {luganda}")
    print(f"   📚 Reference English:   {english_reference}")
    print(f"   🤖 Predicted English:   {english_predicted}")
    print()
    
    results.append({
        'index': idx,
        'luganda': luganda,
        'english_reference': english_reference,
        'english_predicted': english_predicted,
        'is_exact_match': english_predicted.lower().strip() == english_reference.lower().strip()
    })

# Summary
exact_matches = sum(1 for r in results if r['is_exact_match'])
partial_matches = len(results) - exact_matches

print("=" * 80)
print("📊 RESULTS ON KNOWN DATA")
print("=" * 80)
print(f"✅ Exact Matches:            {exact_matches}/{len(results)} ({100*exact_matches/len(results):.1f}%)")
print(f"⚠️  Different Predictions:    {partial_matches}/{len(results)} ({100*partial_matches/len(results):.1f}%)")
print()
print("💡 INTERPRETATION:")
print("   • If exact matches > 70%: Model learned the training data well ✅")
print("   • If different predictions: Model might be generating acceptable alternatives")
print("   • Model should recognize these phrases since it was trained on them")

# Save results
output_file = "outputs/known_data_test_results.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        'test_type': 'known_data',
        'timestamp': datetime.now().isoformat(),
        'total_samples': len(results),
        'exact_matches': exact_matches,
        'match_percentage': 100*exact_matches/len(results),
        'results': results
    }, f, indent=2, ensure_ascii=False)

print(f"\n✅ Results saved to: {output_file}")
print("\n" + "="*80)
print("🎓 CONCLUSION")
print("="*80)
print("Testing model on KNOWN data shows if it learned the training set.")
print("High matches = Good memorization of training data")
print("Lower matches = Model is generalizing/generating alternatives")
print("="*80 + "\n")
