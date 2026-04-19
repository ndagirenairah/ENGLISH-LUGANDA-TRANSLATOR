# ============================================================================
# STEP 7: EVALUATION WITH BLEU SCORE
# ============================================================================
# This script evaluates the translation model using BLEU score
# and other translation quality metrics
# ============================================================================

print("=" * 70)
print("ðŸš€ STEP 7: EVALUATION WITH BLEU SCORE")
print("=" * 70)

import pandas as pd
import numpy as np
from sacrebleu import corpus_bleu, sentence_bleu
import re

# ============================================================================
# PART 1: WHAT IS BLEU SCORE?
# ============================================================================
print("\\n" + "=" * 70)
print("ðŸ“š UNDERSTANDING BLEU SCORE")
print("=" * 70)

explanation = """
BLEU (Bilingual Evaluation Understudy) measures translation quality by:

  1. Comparing N-grams (word groups) between prediction and reference
  2. Calculating overlap percentages
  3. Applying brevity penalty (for very short predictions)

SCALE: 0 to 100
  - 0-30: Poor translation
  - 30-50: Acceptable (but needs improvement)
  - 50-70: Good translation
  - 70+: Excellent translation (near-human quality)

âš ï¸ NOTE: BLEU is useful but not perfect:
  âœ“ Good for comparing models
  âœ“ Fast to compute  
  âœ— Doesn't understand meaning
  âœ— One correct answer = one point (ignores synonyms)
  âœ— Works better with longer texts
"""

print(explanation)

# ============================================================================
# PART 2: LOAD TRANSLATION RESULTS
# ============================================================================
print("\\n" + "=" * 70)
print("ðŸ“¥ LOADING TRANSLATION RESULTS")
print("=" * 70)

try:
    results_df = pd.read_csv('outputs/translation_results.csv')
    print(f"\\nâœ… Translation results loaded: {len(results_df)} samples")
except Exception as e:
    print(f"\\nâŒ Error: Could not find translation results")
    print(f"   Please run Step 6 (Test Model) first")
    print(f"   Error: {e}")
    exit()

print(f"\\nDataFrame columns: {list(results_df.columns)}")
print(f"\\nSample of data:")
print(results_df.head(3))

# ============================================================================
# PART 3: DATA CLEANING FOR EVALUATION
# ============================================================================
print("\\n" + "=" * 70)
print("ðŸ§¹ PREPARING DATA FOR EVALUATION")
print("=" * 70)

def clean_for_evaluation(text):
    """Clean text for fair BLEU evaluation"""
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r'\\s+', ' ', text).strip()
    return text

# Clean the data
results_df['reference_clean'] = results_df['english_reference'].apply(clean_for_evaluation)
results_df['predicted_clean'] = results_df['english_predicted'].apply(clean_for_evaluation)

# Remove error entries
valid_indices = (results_df['predicted_clean'] != "[translation error]")
valid_results = results_df[valid_indices].copy()

print(f"\\nâœ“ Data cleaned")
print(f"  - Valid predictions: {len(valid_results)}/{len(results_df)}")
print(f"  - Translation errors: {len(results_df) - len(valid_results)}")

# ============================================================================
# PART 4: CALCULATE BLEU SCORES (Individual)
# ============================================================================
print("\\n" + "=" * 70)
print("ðŸ“Š CALCULATING INDIVIDUAL BLEU SCORES")
print("=" * 70)

print("\\nCalculating BLEU score for each translation...\\n")

bleu_scores = []

for idx, row in valid_results.iterrows():
    prediction = row['predicted_clean'].split()
    reference = row['reference_clean'].split()
    
    try:
        # Calculate BLEU for this sentence
        score = sentence_bleu(reference, prediction)
        bleu_scores.append(score.score)
    except:
        bleu_scores.append(0.0)

valid_results['bleu_score'] = bleu_scores

print(f"âœ… BLEU scores calculated for {len(bleu_scores)} sentences")

# ============================================================================
# PART 5: DISPLAY TOP AND BOTTOM TRANSLATIONS
# ============================================================================
print("\\n" + "=" * 70)
print("ðŸ† BEST TRANSLATIONS (Highest BLEU Scores)")
print("=" * 70)

top_5 = valid_results.nlargest(5, 'bleu_score')

for i, (idx, row) in enumerate(top_5.iterrows(), 1):
    print(f"\\n{i}. BLEU Score: {row['bleu_score']:.1f}/100 {'â­' * (int(row['bleu_score']//20)+1)}")
    print(f"   Luganda:     {row['luganda']}")
    print(f"   Reference:   {row['english_reference']}")
    print(f"   Predicted:   {row['english_predicted']}")

print("\\n" + "=" * 70)
print("ðŸ”§ WORST TRANSLATIONS (Lowest BLEU Scores)")
print("=" * 70)

bottom_5 = valid_results.nsmallest(5, 'bleu_score')

for i, (idx, row) in enumerate(bottom_5.iterrows(), 1):
    print(f"\\n{i}. BLEU Score: {row['bleu_score']:.1f}/100")
    print(f"   Luganda:     {row['luganda']}")
    print(f"   Reference:   {row['english_reference']}")
    print(f"   Predicted:   {row['english_predicted']}")

# ============================================================================
# PART 6: CALCULATE CORPUS-LEVEL BLEU
# ============================================================================
print("\\n" + "=" * 70)
print("ðŸ“ˆ CORPUS-LEVEL BLEU SCORE")
print("=" * 70)

# Prepare data for corpus BLEU
references = [[ref.split()] for ref in valid_results['reference_clean']]
predictions = [pred.split() for pred in valid_results['predicted_clean']]

try:
    corpus_score = corpus_bleu(predictions, references)
    print(f"\\nâœ… Corpus BLEU Score: {corpus_score.score:.2f}/100")
    print(f"\\n   Translation Quality: ", end="")
    
    score = corpus_score.score
    if score < 30:
        print("POOR âš ï¸ (Model needs more training)")
    elif score < 50:
        print("ACCEPTABLE âœ“ (Can be improved)")
    elif score < 70:
        print("GOOD âœ“âœ“ (Solid performance)")
    else:
        print("EXCELLENT â­ (Near-human quality)")
        
except Exception as e:
    print(f"\\nâš ï¸ Could not calculate corpus BLEU: {e}")

# ============================================================================
# PART 7: STATISTICS AND BREAKDOWN
# ============================================================================
print("\\n" + "=" * 70)
print("ðŸ“Š DETAILED STATISTICS")
print("=" * 70)

if len(bleu_scores) > 0:
    print(f"\\nBLEU Score Statistics:")
    print(f"  - Mean:   {np.mean(bleu_scores):.2f}/100")
    print(f"  - Median: {np.median(bleu_scores):.2f}/100")
    print(f"  - Min:    {np.min(bleu_scores):.2f}/100")
    print(f"  - Max:    {np.max(bleu_scores):.2f}/100")
    print(f"  - Std:    {np.std(bleu_scores):.2f}")
    
    # Distribution
    perfect = sum(1 for s in bleu_scores if s >= 90)
    excellent = sum(1 for s in bleu_scores if 70 <= s < 90)
    good = sum(1 for s in bleu_scores if 50 <= s < 70)
    acceptable = sum(1 for s in bleu_scores if 30 <= s < 50)
    poor = sum(1 for s in bleu_scores if s < 30)
    
    print(f"\\nTranslation Quality Distribution:")
    print(f"  - Perfect (90-100):   {perfect:4d} ({perfect/len(bleu_scores)*100:5.1f}%) â­â­â­")
    print(f"  - Excellent (70-89):  {excellent:4d} ({excellent/len(bleu_scores)*100:5.1f}%) â­â­")
    print(f"  - Good (50-69):       {good:4d} ({good/len(bleu_scores)*100:5.1f}%) â­")
    print(f"  - Acceptable (30-49): {acceptable:4d} ({acceptable/len(bleu_scores)*100:5.1f}%) âœ“")
    print(f"  - Poor (0-29):        {poor:4d} ({poor/len(bleu_scores)*100:5.1f}%) âš ï¸")

# ============================================================================
# PART 8: OTHER EVALUATION METRICS
# ============================================================================
print("\\n" + "=" * 70)
print("ðŸ“ ADDITIONAL METRICS")
print("=" * 70)

print(f"\\nText Length Comparison:")
print(f"  - Avg Reference length: {valid_results['reference_clean'].str.len().mean():.0f} chars")
print(f"  - Avg Predicted length: {valid_results['predicted_clean'].str.len().mean():.0f} chars")
print(f"  - Length ratio: {valid_results['predicted_clean'].str.len().mean() / valid_results['reference_clean'].str.len().mean():.2f}")

# Word error rate (basic)
def calculate_wer(reference, hypothesis):
    """Calculate Word Error Rate"""
    ref_words = reference.split()
    hyp_words = hypothesis.split()
    
    if len(ref_words) == 0:
        return 100.0
    
    # Simple edit distance approximation
    matches = sum(1 for r, h in zip(ref_words, hyp_words) if r == h)
    return (1 - matches / max(len(ref_words), len(hyp_words))) * 100

# This is a simplified version - real WER needs edit distance
print(f"\\n(Approximate) Word Matching:")
matches = 0
total = 0
for _, row in valid_results.iterrows():
    ref_words = set(row['reference_clean'].split())
    pred_words = set(row['predicted_clean'].split())
    matches += len(ref_words & pred_words)
    total += len(ref_words | pred_words)

if total > 0:
    overlap = (matches / total) * 100
    print(f"  - Word overlap: {overlap:.1f}%")

# ============================================================================
# PART 9: SAVE DETAILED EVALUATION REPORT
# ============================================================================
print("\\n" + "=" * 70)
print("ðŸ’¾ SAVING EVALUATION REPORT")
print("=" * 70)

# Save results with BLEU scores
output_csv = 'outputs/translation_results_with_bleu.csv'
valid_results.to_csv(output_csv, index=False)
print(f"\\nâœ… Results with BLEU scores saved to: {output_csv}")

# Create a detailed text report
with open('outputs/evaluation_report.txt', 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\\n")
    f.write("LUGANDA-ENGLISH TRANSLATOR - EVALUATION REPORT\\n")
    f.write("=" * 80 + "\\n\\n")
    
    f.write("SUMMARY STATISTICS\\n")
    f.write("-" * 80 + "\\n")
    f.write(f"Total translations evaluated: {len(valid_results)}\\n")
    f.write(f"Mean BLEU Score: {np.mean(bleu_scores):.2f}/100\\n")
    f.write(f"Median BLEU Score: {np.median(bleu_scores):.2f}/100\\n")
    f.write(f"Min BLEU Score: {np.min(bleu_scores):.2f}/100\\n")
    f.write(f"Max BLEU Score: {np.max(bleu_scores):.2f}/100\\n\\n")
    
    f.write("QUALITY DISTRIBUTION\\n")
    f.write("-" * 80 + "\\n")
    f.write(f"Perfect (90-100):   {perfect:4d} translations\\n")
    f.write(f"Excellent (70-89):  {excellent:4d} translations\\n")
    f.write(f"Good (50-69):       {good:4d} translations\\n")
    f.write(f"Acceptable (30-49): {acceptable:4d} translations\\n")
    f.write(f"Poor (0-29):        {poor:4d} translations\\n\\n")
    
    f.write("SAMPLE TRANSLATIONS\\n")
    f.write("-" * 80 + "\\n")
    for i, (idx, row) in enumerate(valid_results.head(20).iterrows(), 1):
        f.write(f"\\n{i}. [BLEU: {row['bleu_score']:.1f}/100]\\n")
        f.write(f"   Luganda: {row['luganda']}\\n")
        f.write(f"   Reference: {row['english_reference']}\\n")
        f.write(f"   Predicted: {row['english_predicted']}\\n")

print(f"âœ… Detailed report saved to: outputs/evaluation_report.txt")

# ============================================================================
# PART 10: SUMMARY
# ============================================================================
print("\\n" + "=" * 70)
print("âœ… STEP 7 COMPLETE!")
print("=" * 70)

print(f"\\nâœ“ Calculated BLEU scores for all translations")
print(f"âœ“ Generated detailed evaluation metrics")
print(f"\\nðŸ“Š Final Metrics:")
print(f"   - Mean BLEU: {np.mean(bleu_scores):.2f}/100")
print(f"   - Total translations: {len(valid_results)}")
print(f"\\nðŸ“„ Results saved:")
print(f"   - CSV: outputs/translation_results_with_bleu.csv")
print(f"   - REPORT: outputs/evaluation_report.txt")
print(f"\\nðŸŽ¯ Next: STEP 8 - Build Gradio Web App")
print(f"   Run: Step8_Build_WebApp.py\\n")

