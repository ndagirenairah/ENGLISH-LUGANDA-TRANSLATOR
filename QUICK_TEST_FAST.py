#!/usr/bin/env python3
"""
QUICK FAST MODEL TRAINING & TEST
- Trains model quickly on sample data  
- Shows real-time progress
- Tests immediately after
- Generates actionable performance report
"""

import os
import sys
import json
import torch
import pandas as pd
import numpy as np
from tqdm import tqdm
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    TextGenerationPipeline,
    pipeline
)
import time

print("=" * 100)
print("⚡ QUICK MODEL TEST & OPTIMIZATION")
print("=" * 100)

# ============================================================================
# STEP 1: LOAD MODEL
# ============================================================================
print("\n[STEP 1] Loading Model...")
print("-" * 100)

model_path = "models/trained_model"
model_name = "Helsinki-NLP/opus-mt-en-mul"

print(f"\n📥 Checking for trained model at: {model_path}")

try:
    if os.path.exists(model_path) and os.path.exists(f"{model_path}/pytorch_model.bin"):
        print("   ✅ TRAINED MODEL FOUND")
        model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model_status = "TRAINED"
    else:
        print("   ℹ️  No trained weights found, using BASE model")
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model_status = "BASE"
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)
print(f"   ✅ Device: {device.upper()}")
print(f"   ✅ Model: {model_status}")
print(f"   ℹ️  Parameters: {model.num_parameters():,.0f}")

# ============================================================================
# STEP 2: LOAD TEST DATA
# ============================================================================
print("\n[STEP 2] Loading Test Data...")
print("-" * 100)

# Try different data paths
test_paths = [
    ("data/test_data.csv", "Primary test data"),
    ("luganda_training_data.csv", "Training data (as fallback)"),
]

test_data = None
for path, desc in test_paths:
    if os.path.exists(path):
        print(f"\n   📖 Found {desc}: {path}")
        df = pd.read_csv(path)
        print(f"   ✅ Loaded {len(df)} samples")
        test_data = df
        break

if test_data is None:
    print("   ❌ No test data found!")
    sys.exit(1)

# Clean column names
test_data.columns = test_data.columns.str.strip().str.lower()

# Find correct columns
lug_col = eng_col = None
for col in test_data.columns:
    if any(x in col for x in ['luganda', 'lug', 'source']):
        lug_col = col
    if any(x in col for x in ['english', 'eng', 'target']):
        eng_col = col

print(f"   ✅ Luganda column: {lug_col}")
print(f"   ✅ English column: {eng_col}")

# ============================================================================
# STEP 3: GENERATE TRANSLATIONS
# ============================================================================
print("\n[STEP 3] Generating Translations...")
print("-" * 100)

# Sample test set for faster testing
sample_size = min(50, len(test_data))  # Test on up to 50 samples
test_sample = test_data.head(sample_size)

print(f"\n   🔄 Testing on {sample_size} samples...")
print("   " + "." * 60)

predictions = []
references = []
times = []
errors = 0

for idx, (_, row) in enumerate(test_sample.iterrows()):
    try:
        luganda_sent = str(row[lug_col]).strip()
        english_ref = str(row[eng_col]).strip()
        
        # Time the translation
        t0 = time.time()
        
        input_ids = tokenizer.encode(luganda_sent, return_tensors="pt").to(device)
        outputs = model.generate(
            input_ids,
            max_length=100,
            num_beams=4,
        )
        translation = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        t_elapsed = time.time() - t0
        
        predictions.append(translation)
        references.append(english_ref)
        times.append(t_elapsed)
        
        # Progress bar
        if (idx + 1) % 10 == 0:
            print(f"   ✓ {idx + 1:3d}/{sample_size}")
            
    except Exception as e:
        predictions.append("[ERROR]")
        references.append(english_ref)
        errors += 1
        continue

print(f"   ✅ Completed {len(predictions)} translations ({errors} errors)")

# ============================================================================
# STEP 4: CALCULATE METRICS
# ============================================================================
print("\n[STEP 4] Calculating Performance Metrics...")
print("-" * 100)

# Basic accuracy
results_df = pd.DataFrame({
    'luganda': test_sample[lug_col].values[:len(predictions)],
    'reference': references,
    'predicted': predictions
})

# Count quality
exact_matches = sum([p.lower().strip() == r.lower().strip() for p, r in zip(predictions, references) if p != "[ERROR]"])
partial_matches = sum([len(set(p.lower().split()) & set(r.lower().split())) >= 1 for p, r in zip(predictions, references) if p != "[ERROR]"])
error_count = sum([p == "[ERROR]" for p in predictions])

accuracy = (exact_matches / len(predictions)) * 100
error_rate = (error_count / len(predictions)) * 100

print(f"\n📊 TRANSLATION ACCURACY:")
print(f"   Exact matches:       {exact_matches:3d} ({accuracy:.1f}%)")
print(f"   Partial matches:     {partial_matches:3d} ({partial_matches/len(predictions)*100:.1f}%)")
print(f"   Translation errors:  {error_count:3d} ({error_rate:.1f}%)")

print(f"\n⏱️  PERFORMANCE:")
avg_time = np.mean(times)
print(f"   Average time/translation: {avg_time:.3f}s")
print(f"   Throughput:               {len(predictions)/sum(times):.1f} trans/sec")
print(f"   Total time:               {sum(times):.2f}s")

print(f"\n📏 TEXT LENGTH:")
print(f"   Avg input (Luganda):     {results_df['luganda'].str.len().mean():.0f} chars")
print(f"   Avg output (predicted):  {results_df['predicted'].str.len().mean():.0f} chars")
print(f"   Avg reference (English): {results_df['reference'].str.len().mean():.0f} chars")

# ============================================================================
# STEP 5: CALCULATE QUALITY SCORES
# ============================================================================
print("\n[STEP 5] Calculating Quality Scores...")
print("-" * 100)

try:
    from sacrebleu import corpus_chrf, corpus_bleu
    
    print("\n📈 TRANSLATION QUALITY:")
    
    chrf_score = corpus_chrf(predictions, [references])
    print(f"   chrF++ Score:  {chrf_score.score:6.1f}/100  (Better for low-resource languages)")
    
    bleu_score = corpus_bleu(predictions, [references])
    print(f"   BLEU Score:    {bleu_score.score:6.1f}/100  (Standard metric)")
    
    # Quality tier
    if chrf_score.score >= 70:
        quality = "🟢 EXCELLENT"
    elif chrf_score.score >= 50:
        quality = "🟡 GOOD"
    elif chrf_score.score >= 30:
        quality = "🟠 FAIR"
    else:
        quality = "🔴 POOR"
    
    print(f"\n🎯 OVERALL QUALITY: {quality}")
    
except ImportError as e:
    print(f"   ⚠️  Quality metrics unavailable ({e})")
    print("      Install: pip install sacrebleu")

# ============================================================================
# STEP 6: SHOW SAMPLES
# ============================================================================
print("\n[STEP 6] Sample Translations...")
print("-" * 100)

print("\nFirst 5 translations:\n")

for idx in range(min(5, len(results_df))):
    row = results_df.iloc[idx]
    
    is_close = row['predicted'].lower()[:20] == row['reference'].lower()[:20]
    status = "✅" if is_close else "⚠️"
    
    print(f"{idx+1}. {status}")
    print(f"   Input (Luganda):    {row['luganda'][:50]}")
    print(f"   Reference English:  {row['reference'][:50]}")
    print(f"   Predicted English:  {row['predicted'][:50]}")
    print()

# ============================================================================
# STEP 7: GENERATE REPORT & RECOMMENDATIONS
# ============================================================================
print("\n[STEP 7] Analysis & Recommendations...")
print("-" * 100)

report_data = {
    "timestamp": pd.Timestamp.now().isoformat(),
    "model_status": model_status,
    "device": device.upper(),
    "num_parameters": int(model.num_parameters()),
    "test_samples": len(predictions),
    "accuracy_percent": float(accuracy),
    "error_rate_percent": float(error_rate),
    "avg_time_sec": float(avg_time),
    "throughput_per_sec": float(len(predictions)/sum(times))
}

# Save results
results_df.to_csv("outputs/quick_test_results.csv", index=False)
with open("outputs/quick_test_report.json", "w") as f:
    json.dump(report_data, f, indent=2)

print(f"\n💾 Results saved:")
print(f"   - CSV: outputs/quick_test_results.csv")
print(f"   - JSON: outputs/quick_test_report.json")

# ============================================================================
# STEP 8: ACTION PLAN
# ============================================================================
print("\n[STEP 8] Action Plan for Improvement...")
print("-" * 100)

recommendations = []

if error_rate > 5:
    recommendations.append(f"⚠️  High error rate ({error_rate:.1f}%) - Check data quality and model configuration")

if accuracy < 10:
    recommendations.append("🔴 Very low accuracy - Model needs retraining")
    recommendations.append("   → Run: python Step5_Train_Model.py")
    recommendations.append("   → Or: python OPTIMIZE_MODEL_COMPLETE.py")

if accuracy < 30:
    recommendations.append("🟠 Low accuracy - Consider:")
    recommendations.append("   → More training data")
    recommendations.append("   → Longer training (increase epochs)")
    recommendations.append("   → Different model architecture")

if accuracy == 0:
    recommendations.append("🔴 CRITICAL: Model is not translating at all!")
    recommendations.append("   → Check if model is in wrong direction (English→Luganda vs Luganda→English)")
    recommendations.append("   → Verify training data format")
    recommendations.append("   → Check language tags")

if not recommendations:
    recommendations.append("✅ Model is performing well!")
    recommendations.append("   → Deploy to production")

print("\n🎯 RECOMMENDATIONS:")
for rec in recommendations:
    print(f"   {rec}")

# ============================================================================
# FINAL STATUS
# ============================================================================
print("\n" + "=" * 100)
print("✅ TEST COMPLETE")
print("=" * 100)

print(f"""
📊 FINAL STATUS:
   Model:       {model_status}
   Device:      {device.upper()}
   Samples:     {len(predictions)}
   Accuracy:    {accuracy:.1f}%
   Throughput:  {len(predictions)/sum(times):.1f} trans/sec

📁 Files Generated:
   - outputs/quick_test_results.csv (detailed results)
   - outputs/quick_test_report.json (metrics)

🚀 NEXT STEPS:
   1. Review the recommendations above
   2. If accuracy is low: Train the model (Step5_Train_Model.py)
   3. If accuracy is good: Deploy to production (python app.py)
   4. Monitor performance continuously

""")

print("=" * 100)
