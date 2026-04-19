# ============================================================================
# STEP 7 (BONUS): CULTURAL EVALUATION
# ============================================================================
# Evaluates model performance specifically on Baganda cultural translations
# ============================================================================

print("=" * 70)
print("🎭 CULTURAL TRANSLATION EVALUATION")
print("=" * 70)

import pandas as pd
import json
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline
import evaluate
from collections import defaultdict

# ============================================================================
# PART 1: LOAD MODEL AND DATA
# ============================================================================
print("\n📥 Loading model and cultural test data...\n")

# Load trained model
model_path = 'models/trained_model'
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSeq2SeqLM.from_pretrained(model_path)

print(f"✅ Model loaded from: {model_path}")

# Load cultural test set
cultural_test_df = pd.read_csv('data/cultural_test_set.csv', encoding='utf-8')
print(f"✅ Cultural test set loaded: {len(cultural_test_df)} examples")

# Load BLEU metric
bleu = evaluate.load('bleu')

# ============================================================================
# PART 2: SET UP TRANSLATION PIPELINE
# ============================================================================
print("\n🔄 Setting up translation pipeline...\n")

translator = pipeline(
    "translation_en_to_lg",
    model=model,
    tokenizer=tokenizer,
    device=0 if torch.cuda.is_available() else -1,
    max_length=512
)

# ============================================================================
# PART 3: EVALUATE BY CULTURAL CONTEXT
# ============================================================================
print("=" * 70)
print("🧪 EVALUATING BY CULTURAL CONTEXT")
print("=" * 70)

results_by_context = defaultdict(list)
all_predictions = []
all_references = []

# Group by cultural context
for context in cultural_test_df['cultural_context'].unique():
    context_df = cultural_test_df[cultural_test_df['cultural_context'] == context]
    
    print(f"\n📊 Evaluating {context} ({len(context_df)} samples):")
    print("-" * 70)
    
    context_bleu_scores = []
    
    for idx, row in context_df.iterrows():
        english = row['english']
        reference = row['luganda']
        
        # Translate
        try:
            result = translator(english, max_length=512)
            prediction = result[0]['translation_text']
        except Exception as e:
            print(f"   ⚠️  Error translating: {e}")
            prediction = ""
        
        # Calculate BLEU for this example
        try:
            bleu_score = bleu.compute(
                predictions=[prediction.split()],
                references=[[reference.split()]]
            )['bleu']
        except:
            bleu_score = 0.0
        
        context_bleu_scores.append(bleu_score)
        results_by_context[context].append({
            'english': english,
            'reference': reference,
            'prediction': prediction,
            'bleu': bleu_score
        })
        
        all_predictions.append(prediction)
        all_references.append(reference)
        
        # Print sample
        if idx % max(1, len(context_df) // 3) == 0:  # Show 3 samples per context
            print(f"\n   📝 Example {idx + 1}:")
            print(f"      EN: {english}")
            print(f"      Reference: {reference}")
            print(f"      Prediction: {prediction}")
            print(f"      BLEU: {bleu_score:.3f}")
    
    avg_bleu = sum(context_bleu_scores) / len(context_bleu_scores)
    print(f"\n   ✅ {context} - Average BLEU: {avg_bleu:.3f}")

# ============================================================================
# PART 4: OVERALL EVALUATION
# ============================================================================
print("\n" + "=" * 70)
print("📈 OVERALL CULTURAL EVALUATION")
print("=" * 70)

# Calculate overall BLEU score
overall_bleu_result = bleu.compute(
    predictions=[p.split() for p in all_predictions],
    references=[[r.split()] for r in all_references]
)

print(f"\n✅ Overall BLEU Score: {overall_bleu_result['bleu']:.3f}")

# Statistics by context
print(f"\n📊 Performance by Cultural Context:")
print("-" * 70)

context_stats = []
for context in sorted(results_by_context.keys()):
    scores = [r['bleu'] for r in results_by_context[context]]
    avg_score = sum(scores) / len(scores)
    max_score = max(scores)
    min_score = min(scores)
    
    context_stats.append({
        'context': context,
        'samples': len(scores),
        'avg_bleu': avg_score,
        'max_bleu': max_score,
        'min_bleu': min_score
    })
    
    print(f"   {context:15} | Avg BLEU: {avg_score:.3f} | Samples: {len(scores)}")

context_stats_df = pd.DataFrame(context_stats)

# ============================================================================
# PART 5: QUALITATIVE ANALYSIS
# ============================================================================
print("\n" + "=" * 70)
print("🔍 QUALITATIVE ANALYSIS")
print("=" * 70)

# Find best and worst examples
print(f"\n✨ Top 5 Best Translations (Highest BLEU):")
print("-" * 70)

best_examples = sorted(
    [r for results in results_by_context.values() for r in results],
    key=lambda x: x['bleu'],
    reverse=True
)[:5]

for i, ex in enumerate(best_examples, 1):
    print(f"\n{i}. BLEU: {ex['bleu']:.3f}")
    print(f"   EN: {ex['english']}")
    print(f"   Ref: {ex['reference']}")
    print(f"   Pred: {ex['prediction']}")

print(f"\n\n❌ Top 5 Worst Translations (Lowest BLEU):")
print("-" * 70)

worst_examples = sorted(
    [r for results in results_by_context.values() for r in results],
    key=lambda x: x['bleu']
)[:5]

for i, ex in enumerate(worst_examples, 1):
    print(f"\n{i}. BLEU: {ex['bleu']:.3f}")
    print(f"   EN: {ex['english']}")
    print(f"   Ref: {ex['reference']}")
    print(f"   Pred: {ex['prediction']}")

# ============================================================================
# PART 6: SAVE RESULTS
# ============================================================================
print("\n" + "=" * 70)
print("💾 SAVING RESULTS")
print("=" * 70)

# Save context statistics
context_stats_df.to_csv('outputs/cultural_evaluation_by_context.csv', index=False)
print(f"\n✅ Saved: outputs/cultural_evaluation_by_context.csv")

# Save all results detailed
all_results = []
for context, examples in results_by_context.items():
    for ex in examples:
        ex['cultural_context'] = context
        all_results.append(ex)

all_results_df = pd.DataFrame(all_results)
all_results_df.to_csv('outputs/cultural_evaluation_detailed.csv', index=False)
print(f"✅ Saved: outputs/cultural_evaluation_detailed.csv")

# Create summary report
summary_report = {
    'overall_bleu': float(overall_bleu_result['bleu']),
    'total_examples': len(cultural_test_df),
    'evaluation_date': pd.Timestamp.now().isoformat(),
    'performance_by_context': {
        row['context']: {
            'avg_bleu': float(row['avg_bleu']),
            'max_bleu': float(row['max_bleu']),
            'min_bleu': float(row['min_bleu']),
            'samples': int(row['samples'])
        }
        for _, row in context_stats_df.iterrows()
    }
}

with open('outputs/cultural_evaluation_summary.json', 'w', encoding='utf-8') as f:
    json.dump(summary_report, f, indent=2, ensure_ascii=False)

print(f"✅ Saved: outputs/cultural_evaluation_summary.json")

# ============================================================================
# PART 7: CONCLUSIONS
# ============================================================================
print("\n" + "=" * 70)
print("🏆 EVALUATION SUMMARY")
print("=" * 70)

print(f"\n📊 Key Metrics:")
print(f"   - Overall BLEU Score: {overall_bleu_result['bleu']:.3f}")
print(f"   - Total Examples: {len(cultural_test_df)}")
print(f"   - Cultural Contexts: {len(results_by_context)}")

best_context = context_stats_df.loc[context_stats_df['avg_bleu'].idxmax()]
worst_context = context_stats_df.loc[context_stats_df['avg_bleu'].idxmin()]

print(f"\n✅ Best Performing Context: {best_context['context']} ({best_context['avg_bleu']:.3f})")
print(f"⚠️  Needs Improvement: {worst_context['context']} ({worst_context['avg_bleu']:.3f})")

print(f"\n💡 Recommendations:")
print(f"   1. Model performs well on {best_context['context']} translations")
print(f"   2. Focus training data expansion on {worst_context['context']}")
print(f"   3. Consider fine-tuning specifically on weak contexts")
print(f"   4. Apply post-processing rules for cultural accuracy")

print("\n" + "=" * 70)
print("✨ Cultural Evaluation Complete!")
print("=" * 70 + "\n")
