"""
STEP 4: Evaluate Model - Week 6 (Evaluation Metrics)
=====================================================
Evaluate trained model on test set using BLEU score and other metrics.

Week 6 concepts:
  - Cross-validation: Test on unseen data
  - Performance metrics: BLEU, accuracy, loss
  - Evaluation protocols: Proper test set isolation
"""

from pathlib import Path
import sys
import json
import pandas as pd
import torch
from datasets import Dataset
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from sacrebleu import corpus_bleu
import numpy as np

try:
    from config import PROCESSED_DATA_DIR, TRAIN_OUTPUT_DIR, OUTPUTS_DIR, EVAL_OUTPUT_FILE, DEVICE
    from utils import print_section
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from config import PROCESSED_DATA_DIR, TRAIN_OUTPUT_DIR, OUTPUTS_DIR, EVAL_OUTPUT_FILE, DEVICE
    from utils import print_section


def load_test_data():
    """Load test set."""
    test_path = PROCESSED_DATA_DIR / "test.csv"
    
    if not test_path.exists():
        raise FileNotFoundError(
            f"❌ Test data not found at {test_path}\n"
            f"   Run: python src/2_preprocess.py first"
        )
    
    test_df = pd.read_csv(test_path)
    return test_df


def load_trained_model():
    """Load the trained model and tokenizer."""
    if not TRAIN_OUTPUT_DIR.exists():
        raise FileNotFoundError(
            f"❌ Trained model not found at {TRAIN_OUTPUT_DIR}\n"
            f"   Run: python src/3_train.py first"
        )
    
    print(f"📂 Loading model from {TRAIN_OUTPUT_DIR}")
    tokenizer = AutoTokenizer.from_pretrained(TRAIN_OUTPUT_DIR)
    model = AutoModelForSeq2SeqLM.from_pretrained(TRAIN_OUTPUT_DIR)
    model = model.to(DEVICE)
    
    return model, tokenizer


def generate_translations(model, tokenizer, texts, max_length=128):
    """Generate translations for a batch of texts."""
    inputs = tokenizer(
        texts,
        max_length=128,
        truncation=True,
        padding="max_length",
        return_tensors="pt"
    )
    
    # Move to device
    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}
    
    # Generate
    with torch.no_grad():
        output_ids = model.generate(
            inputs['input_ids'],
            attention_mask=inputs['attention_mask'],
            max_length=max_length,
            num_beams=4,
            early_stopping=True,
        )
    
    # Decode
    translations = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
    return translations


def evaluate_on_test_set(model, tokenizer, test_df):
    """
    Evaluate model on test set.
    Calculate BLEU score and other metrics.
    """
    print("\n📊 Evaluating on test set...")
    
    # Prepare data
    english_texts = test_df['english'].tolist()
    luganda_references = test_df['luganda'].tolist()
    
    print(f"   Test samples: {len(english_texts)}")
    
    # Generate predictions in batches
    batch_size = 32
    predictions = []
    
    print("   Generating translations...")
    for i in range(0, len(english_texts), batch_size):
        batch = english_texts[i:i+batch_size]
        batch_predictions = generate_translations(model, tokenizer, batch)
        predictions.extend(batch_predictions)
        
        # Progress
        progress = min(i + batch_size, len(english_texts))
        print(f"      [{progress}/{len(english_texts)}]", end='\r')
    
    print()
    
    # Calculate BLEU score
    print("   Calculating BLEU score...")
    bleu = corpus_bleu(predictions, [luganda_references])
    bleu_score = bleu.score
    
    print(f"\n   ✅ BLEU Score: {bleu_score:.2f}")
    
    # Calculate other metrics
    print("\n   📈 Additional Metrics:")
    
    # Average translation length
    avg_pred_length = np.mean([len(p.split()) for p in predictions])
    avg_ref_length = np.mean([len(r.split()) for r in luganda_references])
    print(f"      Average prediction length: {avg_pred_length:.1f} tokens")
    print(f"      Average reference length: {avg_ref_length:.1f} tokens")
    
    return {
        "bleu_score": bleu_score,
        "num_test_samples": len(english_texts),
        "avg_prediction_length": avg_pred_length,
        "avg_reference_length": avg_ref_length,
        "predictions": predictions,
        "references": luganda_references,
    }


def show_sample_translations(predictions, references, num_samples=5):
    """Display sample translations."""
    print("\n" + "="*80)
    print("SAMPLE PREDICTIONS")
    print("="*80)
    
    for i in range(min(num_samples, len(predictions))):
        print(f"\nSample {i+1}:")
        print(f"  Reference: {references[i]}")
        print(f"  Predicted: {predictions[i]}")


def save_results(eval_results):
    """Save evaluation results to JSON."""
    print("\n💾 Saving results...")
    
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save results (without full predictions for file size)
    results_to_save = {
        "bleu_score": eval_results["bleu_score"],
        "num_test_samples": eval_results["num_test_samples"],
        "avg_prediction_length": eval_results["avg_prediction_length"],
        "avg_reference_length": eval_results["avg_reference_length"],
    }
    
    with open(EVAL_OUTPUT_FILE, 'w') as f:
        json.dump(results_to_save, f, indent=2)
    
    print(f"   ✅ Saved to {EVAL_OUTPUT_FILE}")
    
    # Save predictions and references as CSV
    predictions_df = pd.DataFrame({
        'reference': eval_results['references'],
        'predicted': eval_results['predictions'],
    })
    
    predictions_file = OUTPUTS_DIR / "predictions.csv"
    predictions_df.to_csv(predictions_file, index=False)
    print(f"   ✅ Predictions saved to {predictions_file}")


def main():
    """Evaluate the trained model."""
    print_section("STEP 4: EVALUATING MODEL", width=80)
    
    # Load test data
    print("\n📁 Loading test data...")
    test_df = load_test_data()
    print(f"   Test samples: {len(test_df)}")
    
    # Load trained model
    print("\n🤖 Loading trained model...")
    model, tokenizer = load_trained_model()
    
    # Evaluate
    eval_results = evaluate_on_test_set(model, tokenizer, test_df)
    
    # Show samples
    show_sample_translations(
        eval_results['predictions'],
        eval_results['references'],
        num_samples=5
    )
    
    # Save results
    save_results(eval_results)
    
    print_section("EVALUATION COMPLETE", width=80)
    print(f"\n✅ Model evaluation complete!")
    print(f"   BLEU Score: {eval_results['bleu_score']:.2f}")
    print(f"\n   Results saved to {OUTPUTS_DIR}/")


if __name__ == "__main__":
    main()
