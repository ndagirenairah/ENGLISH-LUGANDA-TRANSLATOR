#!/usr/bin/env python3
"""
QUICK MODEL PERFORMANCE TEST
Tests current model with real translations and generates performance report
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from transformers import MarianMTModel, MarianTokenizer, AutoModelForSeq2SeqLM, AutoTokenizer
import time
import traceback

print("=" * 80)
print("🚀 QUICK MODEL PERFORMANCE TEST")
print("=" * 80)

# ============================================================================
# PART 1: LOAD MODEL (TRY TRAINED FIRST, FALLBACK TO BASE)
# ============================================================================
print("\n📦 LOADING MODEL...")

model = None
tokenizer = None
model_type = "UNKNOWN"

# Try 1: Load trained model
try:
    print("   ├─ Trying to load TRAINED model from models/trained_model...")
    trained_path = "models/trained_model"
    if os.path.exists(trained_path) and os.path.exists(f"{trained_path}/pytorch_model.bin"):
        try:
            model = AutoModelForSeq2SeqLM.from_pretrained(trained_path)
            tokenizer = AutoTokenizer.from_pretrained(trained_path)
            model_type = "TRAINED"
            print("   ✅ TRAINED MODEL LOADED")
        except Exception as e:
            print(f"   ⚠️  Trained model load failed: {str(e)[:60]}")
except Exception as e:
    print(f"   ⚠️  Error: {str(e)[:60]}")

# Try 2: Load base model from HuggingFace (CORRECT: Tatoeba for Luganda→English)
if model is None:
    try:
        print("   ├─ Loading BASE model (Helsinki-NLP/Tatoeba-MT-mul+eng-eng)...")
        model_name = "Helsinki-NLP/Tatoeba-MT-mul+eng-eng"  # CORRECT: Multi→English
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        model_type = "BASE (Tatoeba)"
        print("   ✅ BASE MODEL LOADED")
    except Exception as e:
        print(f"   ⚠️  Tatoeba model load failed: {e}")
        print("   ├─ Trying fallback: Helsinki-NLP/opus-mt-en-mul...")
        try:
            model_name = "Helsinki-NLP/opus-mt-en-mul"
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            model_type = "FALLBACK (Opus)"
            print("   ⚠️  FALLBACK MODEL LOADED (Wrong direction - English→Luganda)")
        except Exception as e2:
            print(f"   ❌ Both models failed: {e2}")
            sys.exit(1)

print(f"\n✅ Model: {model_type}")

# Move to GPU if available
device = "cuda" if os.environ.get('CUDA_VISIBLE_DEVICES') else "cpu"
model.to(device)
print(f"✅ Device: {device.upper()}")

# ============================================================================
# PART 2: LOAD TEST DATA
# ============================================================================
print("\n📊 LOADING TEST DATA...")

test_data_path = "data/test_data.csv"
if not os.path.exists(test_data_path):
    print(f"   ⚠️  Test data not found at {test_data_path}")
    print("   Creating sample test data instead...")
    # Use dictionary for quick testing
    sample_data = {
        "luganda_clean": [
            "Wasuze otya?",
            "Ndi muganda",
            "Webale",
            "Oli mu kika ki?",
            "Ssebo"
        ],
        "english_clean": [
            "How are you?",
            "I am Ugandan",
            "Thank you",
            "What clan are you from?",
            "Sir"
        ]
    }
    test_df = pd.DataFrame(sample_data)
else:
    test_df = pd.read_csv(test_data_path)

print(f"✅ Loaded {len(test_df)} test samples")

# ============================================================================
# PART 3: TEST TRANSLATIONS
# ============================================================================
print("\n🔄 GENERATING TRANSLATIONS...")
print(f"   Testing {len(test_df)} Luganda sentences...\n")

predictions = []
reference = []
translation_times = []
errors = []

start_time = time.time()

for idx, row in test_df.iterrows():
    luganda_sent = row['luganda_clean']
    english_ref = row['english_clean']
    
    try:
        # Time the translation
        t0 = time.time()
        
        # Prepare input with language tag
        # Tatoeba model translates FROM any language TO English
        # No language tag needed for target (English), just input the source text
        input_text = luganda_sent
        input_ids = tokenizer.encode(input_text, return_tensors="pt").to(device)
        
        # Generate translation
        outputs = model.generate(
            input_ids,
            max_length=100,
            num_beams=4,
            early_stopping=True
        )
        
        translation = tokenizer.decode(outputs[0], skip_special_tokens=True)
        t_elapsed = time.time() - t0
        
        predictions.append(translation)
        reference.append(english_ref)
        translation_times.append(t_elapsed)
        
        status = "✅" if translation else "⚠️"
        print(f"   {status} [{idx+1:3d}] {luganda_sent[:40]:40s} → {translation[:50]}")
        
    except Exception as e:
        predictions.append("[ERROR]")
        reference.append(english_ref)
        errors.append(str(e))
        print(f"   ❌ [{idx+1:3d}] {luganda_sent[:40]:40s} → [Translation Error]")

total_time = time.time() - start_time

# ============================================================================
# PART 4: CALCULATE METRICS
# ============================================================================
print("\n" + "=" * 80)
print("📊 PERFORMANCE METRICS")
print("=" * 80)

results_df = pd.DataFrame({
    'luganda': test_df['luganda_clean'].values[:len(predictions)],
    'english_reference': reference,
    'english_predicted': predictions
})

# Basic accuracy
exact_matches = sum([p.lower().strip() == r.lower().strip() for p, r in zip(predictions, reference)])
partial_matches = sum([any(word in r.lower() for word in p.lower().split()) for p, r in zip(predictions, reference) if p != "[ERROR]"])
error_count = sum([p == "[ERROR]" for p in predictions])

accuracy = (exact_matches / len(predictions)) * 100 if predictions else 0
error_rate = (error_count / len(predictions)) * 100 if predictions else 0

print(f"\n✅ Total Translations: {len(predictions)}")
print(f"✅ Exact Matches: {exact_matches} ({(exact_matches/len(predictions)*100):.1f}%)")
print(f"⚠️  Partial Matches: {partial_matches} ({(partial_matches/len(predictions)*100):.1f}%)")
print(f"❌ Translation Errors: {error_count} ({error_rate:.1f}%)")

print(f"\n⏱️  TIMING METRICS:")
print(f"   Total Time: {total_time:.2f}s")
print(f"   Avg per Translation: {np.mean(translation_times):.3f}s")
print(f"   Min: {np.min(translation_times):.3f}s | Max: {np.max(translation_times):.3f}s")
print(f"   Throughput: {len(predictions)/total_time:.1f} translations/sec")

print(f"\n📏 LENGTH METRICS:")
print(f"   Avg Luganda length: {results_df['luganda'].str.len().mean():.0f} chars")
print(f"   Avg Predicted length: {results_df['english_predicted'].str.len().mean():.0f} chars")
print(f"   Avg Reference length: {results_df['english_reference'].str.len().mean():.0f} chars")

# ============================================================================
# PART 5: CHRف++ SCORE (BETTER THAN BLEU FOR LOW-RESOURCE LANGUAGES)
# ============================================================================
print("\n" + "=" * 80)
print("📈 QUALITY METRICS")
print("=" * 80)

try:
    from sacrebleu import corpus_chrf, corpus_bleu
    
    # Calculate chrF++ (better for morphologically rich languages like Luganda)
    chrf_score = corpus_chrf(predictions, [reference])
    print(f"\n✅ chrF++ Score: {chrf_score.score:.1f} (0-100 scale)")
    
    # Calculate BLEU score
    bleu_score = corpus_bleu(predictions, [reference])
    print(f"\n✅ BLEU Score: {bleu_score.score:.1f} (0-100 scale)")
    
    quality_tier = "EXCELLENT" if chrf_score.score >= 70 else "GOOD" if chrf_score.score >= 50 else "FAIR" if chrf_score.score >= 30 else "POOR"
    print(f"\n🎯 Quality Rating: {quality_tier}")
    
except ImportError:
    print("   ⚠️  sacrebleu not available (can be installed with: pip install sacrebleu)")

# ============================================================================
# PART 6: SAMPLE RESULTS
# ============================================================================
print("\n" + "=" * 80)
print("📋 SAMPLE TRANSLATIONS")
print("=" * 80)

for idx in range(min(5, len(results_df))):
    row = results_df.iloc[idx]
    match_status = "✅ MATCH" if row['english_predicted'].lower()[:15] == row['english_reference'].lower()[:15] else "⚠️  DIFFERENT"
    
    print(f"\n{idx+1}. {match_status}")
    print(f"   🇺🇬 Input (Luganda):     {row['luganda']}")
    print(f"   📖 Reference (English): {row['english_reference']}")
    print(f"   🤖 Predicted (English): {row['english_predicted']}")

# ============================================================================
# PART 7: SAVE RESULTS
# ============================================================================
print("\n" + "=" * 80)
print("💾 SAVING RESULTS")
print("=" * 80)

# Save detailed results
results_df.to_csv('outputs/quick_test_results.csv', index=False)
print("\n✅ Saved to: outputs/quick_test_results.csv")

# Save metrics summary
metrics = {
    "model_type": model_type,
    "device": device.upper(),
    "total_translations": len(predictions),
    "exact_matches": int(exact_matches),
    "partial_matches": int(partial_matches),
    "errors": int(error_count),
    "accuracy_percent": float(accuracy),
    "error_rate_percent": float(error_rate),
    "avg_time_per_translation": float(np.mean(translation_times)),
    "throughput_per_second": float(len(predictions)/total_time)
}

with open('outputs/quick_test_metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)
print("✅ Saved to: outputs/quick_test_metrics.json")

# ============================================================================
# PART 8: SUMMARY & RECOMMENDATIONS
# ============================================================================
print("\n" + "=" * 80)
print("🎯 SUMMARY & NEXT STEPS")
print("=" * 80)

print(f"\n✅ Model Type: {model_type}")
print(f"   - If BASE: Run training (Step5_Train_Model.py) to improve")
print(f"   - If TRAINED: Model is using your fine-tuned weights")

if error_rate > 10:
    print(f"\n⚠️  High error rate ({error_rate:.1f}%)")
    print("   - Check data quality")
    print("   - Verify model architecture")
    print("   - Consider retraining")

if accuracy < 30:
    print(f"\n⚠️  Low accuracy ({accuracy:.1f}%)")
    print("   - Consider fine-tuning on more diverse data")
    print("   - Try data augmentation")

print(f"\n✅ TEST COMPLETE - Review outputs/quick_test_results.csv for details\n")
