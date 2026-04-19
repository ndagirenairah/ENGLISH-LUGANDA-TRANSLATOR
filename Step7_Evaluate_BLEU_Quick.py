# ============================================================================
# STEP 7: QUICK EVALUATION WITH BLEU SCORE
# ============================================================================

print("=" * 70)
print("🚀 STEP 7: EVALUATION WITH BLEU SCORE")
print("=" * 70)

import json
import pandas as pd
import numpy as np
import os

os.makedirs('outputs', exist_ok=True)

# ============================================================================
# LOAD RESULTS
# ============================================================================
print("\n📥 Loading translation results...")

df = pd.read_csv('outputs/translation_results.csv')
print(f"✅ Loaded {len(df)} translations")

# ============================================================================
# SIMPLE BLEU CALCULATION
# ============================================================================
def simple_bleu(reference, prediction):
    """Calculate simple BLEU score"""
    ref_words = set(reference.lower().split())
    pred_words = set(prediction.lower().split())
    
    if not ref_words or not pred_words:
        return 0
    
    matches = len(ref_words & pred_words)
    total = len(pred_words)
    
    return (matches / total * 100) if total > 0 else 0

# ============================================================================
# CALCULATE METRICS
# ============================================================================
print("\n" + "=" * 70)
print("📊 CALCULATING BLEU SCORES")
print("=" * 70)

df['bleu_score'] = df.apply(
    lambda row: simple_bleu(row['reference'], row['predicted']),
    axis=1
)

avg_bleu = df['bleu_score'].mean()
print(f"\n✅ Average BLEU Score: {avg_bleu:.2f}")

# Word-level metrics
def word_overlap(ref, pred):
    ref_words = set(ref.lower().split())
    pred_words = set(pred.lower().split())
    if not ref_words:
        return 0
    return len(ref_words & pred_words) / len(ref_words) * 100

df['word_overlap%'] = df.apply(
    lambda row: word_overlap(row['reference'], row['predicted']),
    axis=1
)

# Exact match
df['exact_match'] = (df['reference'].str.lower() == df['predicted'].str.lower())
exact_pct = df['exact_match'].sum() / len(df) * 100

# ============================================================================
# DISPLAY RESULTS
# ============================================================================
print("\n" + "=" * 70)
print("✅ EVALUATION RESULTS")
print("=" * 70)

metrics = {
    "BLEU Score (Average)": avg_bleu,
    "Word Overlap (Average %)": df['word_overlap%'].mean(),
    "Exact Match %": exact_pct,
    "Min BLEU": df['bleu_score'].min(),
    "Max BLEU": df['bleu_score'].max(),
    "Std Dev": df['bleu_score'].std()
}

print("\nMetrics:")
for metric, value in metrics.items():
    if '%' in metric or 'Average' in metric:
        print(f"  • {metric}: {value:.2f}%")
    else:
        print(f"  • {metric}: {value:.2f}")

# ============================================================================
# QUALITY DISTRIBUTION
# ============================================================================
print("\n" + "=" * 70)
print("📈 QUALITY DISTRIBUTION")
print("=" * 70)

print("\nBLEU Score Distribution:")
print(f"  • Excellent (80+): {(df['bleu_score'] >= 80).sum()}")
print(f"  • Good (60-80): {((df['bleu_score'] >= 60) & (df['bleu_score'] < 80)).sum()}")
print(f"  • Fair (40-60): {((df['bleu_score'] >= 40) & (df['bleu_score'] < 60)).sum()}")
print(f"  • Poor (0-40): {(df['bleu_score'] < 40).sum()}")

# ============================================================================
# SAVE RESULTS
# ============================================================================
print("\n" + "=" * 70)
print("💾 SAVING RESULTS")
print("=" * 70)

# Save with metrics
df.to_csv('outputs/evaluation_results.csv', index=False)
print("✅ Saved: outputs/evaluation_results.csv")

# Save summary
summary = {
    "average_bleu": float(avg_bleu),
    "word_overlap_percent": float(df['word_overlap%'].mean()),
    "exact_match_percent": float(exact_pct),
    "total_samples": len(df),
    "metrics": {k: float(v) if isinstance(v, (int, float, np.number)) else v 
                for k, v in metrics.items()}
}

with open('outputs/evaluation_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
print("✅ Saved: outputs/evaluation_summary.json")

# ============================================================================
# SAMPLE ANALYSIS
# ============================================================================
print("\n" + "=" * 70)
print("🔍 SAMPLE TRANSLATIONS")
print("=" * 70)

print("\nBest Translations (by BLEU):")
best_idx = df['bleu_score'].nlargest(3).index
for i, idx in enumerate(best_idx, 1):
    row = df.iloc[idx]
    print(f"\n{i}. BLEU: {row['bleu_score']:.1f}")
    print(f"   Luganda: {row['luganda']}")
    print(f"   Reference: {row['reference']}")
    print(f"   Predicted: {row['predicted']}")

# ============================================================================
# INTERPRETATION
# ============================================================================
print("\n" + "=" * 70)
print("📝 INTERPRETATION")
print("=" * 70)

interpretation = f"""
BLEU Score: {avg_bleu:.2f}/100
  - Under 30: Poor (typical for very low-resource)
  - 30-50: Fair to good
  - 50+: Strong performance

Your Score ({avg_bleu:.1f}):
  ✓ Demonstrates basic translation capability
  ✓ With more training data, expect score to increase
  ✓ Cultural nuances require human evaluation

Next Steps:
  → Increase training data
  → Use larger pre-trained models
  → Add domain-specific fine-tuning
  → Collect human feedback
"""

print(interpretation)

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print("✅ STEP 7 COMPLETE!")
print("=" * 70)

print(f"\n📊 FINAL SUMMARY:")
print(f"   • Average BLEU: {avg_bleu:.2f}")
print(f"   • Exact Match: {exact_pct:.1f}%")
print(f"   • Samples: {len(df)}")

print(f"\n📁 OUTPUT FILES:")
print(f"   ✓ outputs/evaluation_results.csv")
print(f"   ✓ outputs/evaluation_summary.json")

print(f"\n🎯 NEXT: STEP 8 - Deploy Web App")
print(f"   Run: python Step8_Build_WebApp.py")

print("\n" + "=" * 70)
