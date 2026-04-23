#!/usr/bin/env python3
"""
POST-TRAINING VALIDATION & COMPREHENSIVE PERFORMANCE TEST
Runs after training to evaluate, optimize, and report improvements
"""

import os
import json
import pandas as pd
import numpy as np
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch
import time
from pathlib import Path

print("=" * 120)
print("✅ POST-TRAINING VALIDATION & PERFORMANCE ANALYSIS")
print("=" * 120)

# Check if training is complete
TRAINED_MODEL_PATH = "models/trained_model"
pytorch_bin = os.path.join(TRAINED_MODEL_PATH, "pytorch_model.bin")

if not os.path.exists(pytorch_bin):
    print("\n❌ ERROR: No trained model found!")
    print(f"   Expected: {pytorch_bin}")
    print("\n   Possible solutions:")
    print("   1. Run: python TRAIN_PRODUCTION_MODEL.py")
    print("   2. Check if training is still running")
    print("   3. Verify disk space for model weights")
    exit(1)

print("\n✅ TRAINED MODEL FOUND - Starting validation...\n")

# ============================================================================
# STEP 1: LOAD TRAINED MODEL
# ============================================================================
print("[STEP 1] Loading Trained Model")
print("-" * 120)

model = AutoModelForSeq2SeqLM.from_pretrained(TRAINED_MODEL_PATH)
tokenizer = AutoTokenizer.from_pretrained(TRAINED_MODEL_PATH)

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

print(f"\n✅ Trained model loaded")
print(f"   Device: {device.upper()}")
print(f"   Parameters: {model.num_parameters():,.0f}")

# ============================================================================
# STEP 2: COMPREHENSIVE TEST ON LARGE DATASET
# ============================================================================
print("\n[STEP 2] Comprehensive Performance Test")
print("-" * 120)

# Load test data
test_data = pd.read_csv("data/test_data.csv") if os.path.exists("data/test_data.csv") else pd.read_csv("luganda_training_data.csv").head(100)

test_data.columns = test_data.columns.str.strip().str.lower()
lug_col = [c for c in test_data.columns if 'luganda' in c or 'lug' in c or 'source' in c][0]
eng_col = [c for c in test_data.columns if 'english' in c or 'eng' in c or 'target' in c][0]

sample_size = min(200, len(test_data))  # Test on up to 200 samples
test_sample = test_data.head(sample_size)

print(f"\n🔄 Testing on {sample_size} samples...")

predictions = []
references = []
times = []
errors = 0

progress_bar_len = 50
for idx, (_, row) in enumerate(test_sample.iterrows()):
    try:
        lug_text = str(row[lug_col]).strip()
        eng_text = str(row[eng_col]).strip()
        
        t0 = time.time()
        input_ids = tokenizer.encode(lug_text, return_tensors="pt").to(device)
        outputs = model.generate(input_ids, max_length=128, num_beams=4)
        prediction = tokenizer.decode(outputs[0], skip_special_tokens=True)
        t_elapsed = time.time() - t0
        
        predictions.append(prediction)
        references.append(eng_text)
        times.append(t_elapsed)
        
        # Progress
        progress = (idx + 1) / sample_size
        filled = int(progress_bar_len * progress)
        bar = "█" * filled + "░" * (progress_bar_len - filled)
        print(f"\r   [{bar}] {idx + 1:3d}/{sample_size}", end="", flush=True)
        
    except Exception as e:
        predictions.append("[ERROR]")
        references.append(eng_text)
        errors += 1

print(f"\n   ✅ Completed {len(predictions)} translations\n")

# ============================================================================
# STEP 3: CALCULATE METRICS
# ============================================================================
print("[STEP 3] Calculate Quality Metrics")
print("-" * 120)

results_df = pd.DataFrame({
    'luganda': test_sample[lug_col].values[:len(predictions)],
    'english_ref': references,
    'english_pred': predictions
})

# Quality metrics
exact = sum([p.lower().strip() == r.lower().strip() for p, r in zip(predictions, references) if p != "[ERROR]"])
partial = sum([len(set(p.lower().split()) & set(r.lower().split())) >= 2 for p, r in zip(predictions, references) if p != "[ERROR]"])
error_count = sum([p == "[ERROR]" for p in predictions])

accuracy = (exact / len(predictions)) * 100 if predictions else 0
error_rate = (error_count / len(predictions)) * 100 if predictions else 0

print(f"\n📊 ACCURACY METRICS:")
print(f"   Exact matches:        {exact:4d} ({(exact/len(predictions)*100):5.1f}%)")
print(f"   Partial matches:      {partial:4d} ({(partial/len(predictions)*100):5.1f}%)")
print(f"   Translation errors:   {error_count:4d} ({error_rate:5.1f}%)")
print(f"   {'─' * 40}")
print(f"   Overall accuracy:     {exact + partial:4d} ({((exact + partial)/len(predictions)*100):5.1f}%)")

print(f"\n⏱️  PERFORMANCE METRICS:")
avg_time = np.mean(times)
min_time = np.min(times)
max_time = np.max(times)
total_time = sum(times)
throughput = len(predictions) / total_time

print(f"   Average time/translation: {avg_time:6.3f} sec")
print(f"   Min/Max:                  {min_time:6.3f} / {max_time:6.3f} sec")
print(f"   Total test time:          {total_time:6.2f} sec")
print(f"   Throughput:               {throughput:6.2f} translations/sec")

print(f"\n📏 TEXT LENGTH METRICS:")
print(f"   Luganda input:        {results_df['luganda'].str.len().mean():6.0f} chars avg")
print(f"   English predicted:    {results_df['english_pred'].str.len().mean():6.0f} chars avg")
print(f"   English reference:    {results_df['english_ref'].str.len().mean():6.0f} chars avg")

# ============================================================================
# STEP 4: ADVANCED METRICS
# ============================================================================
print("\n[STEP 4] Advanced Quality Metrics")
print("-" * 120)

try:
    from sacrebleu import corpus_chrf, corpus_bleu
    
    chrf = corpus_chrf(predictions, [references])
    bleu = corpus_bleu(predictions, [references])
    
    print(f"\n📈 TRANSLATION QUALITY SCORES:")
    print(f"   chrF++ Score:  {chrf.score:7.2f}/100  (Best for morphologically rich languages)")
    print(f"   BLEU Score:    {bleu.score:7.2f}/100  (Standard metric)")
    
    # Quality rating
    if chrf.score >= 70:
        rating = "🟢 EXCELLENT - Production-ready"
    elif chrf.score >= 50:
        rating = "🟡 GOOD - Acceptable with minor improvements needed"
    elif chrf.score >= 30:
        rating = "🟠 FAIR - Needs improvement before production"
    else:
        rating = "🔴 POOR - Requires significant retraining"
    
    print(f"\n🎯 QUALITY RATING: {rating}")
    
except ImportError:
    print("\n⚠️  sacrebleu not available for advanced metrics")

# ============================================================================
# STEP 5: SAMPLE RESULTS
# ============================================================================
print("\n[STEP 5] Sample Translations (First 10)")
print("-" * 120)

for idx in range(min(10, len(results_df))):
    row = results_df.iloc[idx]
    is_exact = row['english_pred'].lower().strip() == row['english_ref'].lower().strip()
    status = "✅ EXACT" if is_exact else "⚠️  DIFFERENT"
    
    print(f"\n{idx+1}. {status}")
    print(f"   🇺🇬 Luganda Input:    {row['luganda'][:60]}")
    print(f"   📖 Reference English: {row['english_ref'][:60]}")
    print(f"   🤖 Predicted English: {row['english_pred'][:60]}")

# ============================================================================
# STEP 6: GENERATE COMPREHENSIVE REPORT
# ============================================================================
print("\n[STEP 6] Generate Report")
print("-" * 120)

report = {
    "test_timestamp": pd.Timestamp.now().isoformat(),
    "model_status": "TRAINED",
    "test_samples": len(predictions),
    "accuracy_metrics": {
        "exact_matches": int(exact),
        "exact_percentage": float((exact/len(predictions)*100)),
        "partial_matches": int(partial),
        "partial_percentage": float((partial/len(predictions)*100)),
        "translation_errors": int(error_count),
        "error_rate_percentage": float(error_rate)
    },
    "performance_metrics": {
        "average_time_sec": float(avg_time),
        "min_time_sec": float(min_time),
        "max_time_sec": float(max_time),
        "total_time_sec": float(total_time),
        "throughput_per_sec": float(throughput)
    },
    "text_metrics": {
        "avg_luganda_chars": float(results_df['luganda'].str.len().mean()),
        "avg_predicted_chars": float(results_df['english_pred'].str.len().mean()),
        "avg_reference_chars": float(results_df['english_ref'].str.len().mean())
    }
}

# Add sacrebleu scores if available
try:
    from sacrebleu import corpus_chrf, corpus_bleu
    chrf = corpus_chrf(predictions, [references])
    bleu = corpus_bleu(predictions, [references])
    report["quality_scores"] = {
        "chrf_score": float(chrf.score),
        "bleu_score": float(bleu.score)
    }
except:
    pass

# Save report
os.makedirs("outputs", exist_ok=True)
with open("outputs/post_training_report.json", "w") as f:
    json.dump(report, f, indent=2)

# Save detailed results
results_df.to_csv("outputs/post_training_test_results.csv", index=False)

print(f"\n💾 Reports saved:")
print(f"   - outputs/post_training_report.json")
print(f"   - outputs/post_training_test_results.csv")

# ============================================================================
# STEP 7: FINAL RECOMMENDATIONS
# ============================================================================
print("\n[STEP 7] Recommendations & Next Steps")
print("-" * 120)

recommendations = []

if error_rate > 5:
    recommendations.append(f"⚠️  Error rate ({error_rate:.1f}%) is high - Check data quality")

if accuracy < 10:
    recommendations.append("🔴 Accuracy very low (<10%) - Model may need more training epochs")
    recommendations.append("   Recommended: Increase EPOCHS to 5 in TRAIN_PRODUCTION_MODEL.py and retrain")

elif accuracy < 30:
    recommendations.append("🟠 Accuracy low (<30%) - Model needs improvement")
    recommendations.append("   Options:")
    recommendations.append("   - Increase training epochs")
    recommendations.append("   - Use data augmentation") 
    recommendations.append("   - Fine-tune hyperparameters")

elif accuracy < 50:
    recommendations.append("🟡 Accuracy moderate - Can be deployed with monitoring")
    recommendations.append("   Consider retraining with augmented data for production")

else:
    recommendations.append("🟢 Model is performing well!")
    recommendations.append("   Ready for deployment")

if not recommendations:
    recommendations.append("✅ No critical issues found")

print("\n🎯 RECOMMENDATIONS:")
for rec in recommendations:
    print(f"   {rec}")

# ============================================================================
# FINAL STATUS
# ============================================================================
print("\n" + "=" * 120)
print("✅ VALIDATION COMPLETE")
print("=" * 120)

print(f"""
📊 FINAL STATUS:
   Model Type:     TRAINED
   Device:         {device.upper()}
   Test Samples:   {len(predictions)}
   Accuracy:       {accuracy:.1f}%
   Error Rate:     {error_rate:.1f}%
   Throughput:     {throughput:.1f} trans/sec

📁 Output Files:
   - outputs/post_training_report.json
   - outputs/post_training_test_results.csv

🚀 DEPLOYMENT OPTIONS:
   1. If accuracy is good (>30%):
      python app.py
   
   2. Monitor performance in production
   
   3. If accuracy is low (<30%):
      python TRAIN_PRODUCTION_MODEL.py  (with more epochs)

💡 REMEMBER:
   - Model performance improves with more data and epochs
   - Monitor real-world translations for continuous improvement
   - Collect user feedback for future retraining

""")

print("=" * 120)
