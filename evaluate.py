"""
STAGE 6B: MODEL EVALUATION
===========================
Evaluates translation model using BLEU, accuracy, and error analysis.
Generates comprehensive evaluation reports and confidence scores.
"""

import torch
import pandas as pd
import numpy as np
from pathlib import Path
from transformers import AutoTokenizer, MarianMTModel
from sacrebleu import corpus_bleu, sentence_bleu
import json
from datetime import datetime
from collections import defaultdict


def normalize_translation_frame(data):
    """Return a DataFrame with english and luganda columns."""
    if isinstance(data, pd.DataFrame):
        if {'english', 'luganda'}.issubset(data.columns):
            return data[['english', 'luganda']].copy()
        if 'translation' in data.columns:
            english_values = []
            luganda_values = []
            for item in data['translation']:
                if isinstance(item, dict):
                    english_values.append(item.get('eng') or item.get('english') or item.get('src') or '')
                    luganda_values.append(item.get('lug') or item.get('luganda') or item.get('tgt') or '')
                else:
                    english_values.append('')
                    luganda_values.append('')
            return pd.DataFrame({'english': english_values, 'luganda': luganda_values})

    if hasattr(data, 'to_pandas'):
        return normalize_translation_frame(data.to_pandas())

    if hasattr(data, 'column_names') and 'translation' in getattr(data, 'column_names', []):
        rows = []
        for item in data['translation']:
            if isinstance(item, dict):
                rows.append({
                    'english': item.get('eng') or item.get('english') or item.get('src') or '',
                    'luganda': item.get('lug') or item.get('luganda') or item.get('tgt') or ''
                })
        return pd.DataFrame(rows)

    raise ValueError("Unsupported dataset format. Expected english/luganda columns or translation entries.")


class TranslationEvaluator:
    """
    Evaluates translation model on test set.
    """
    
    def __init__(self, model_path='models/trained_model_cpu'):
        """
        Initialize evaluator with trained model.
        
        Args:
            model_path (str): Path to trained model
        """
        print(f"\n[EVALUATION] Loading model from {model_path}")
        
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = MarianMTModel.from_pretrained(model_path)
        self.model.to(self.device)
        self.model.eval()
        
        print(f"  ✓ Model loaded on {self.device.upper()}")
    
    def translate_batch(self, texts, max_length=128, batch_size=8):
        """
        Translate batch of texts.
        
        Args:
            texts (list): List of texts to translate
            max_length (int): Maximum output length
            batch_size (int): Batch size for translation
            
        Returns:
            list: Translated texts
        """
        translations = []
        
        with torch.no_grad():
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i+batch_size]
                
                inputs = self.tokenizer(
                    batch,
                    max_length=max_length,
                    truncation=True,
                    padding=True,
                    return_tensors='pt'
                ).to(self.device)
                
                output_ids = self.model.generate(
                    **inputs,
                    max_length=max_length,
                    num_beams=4,
                    early_stopping=True
                )
                
                batch_translations = self.tokenizer.batch_decode(
                    output_ids,
                    skip_special_tokens=True
                )
                
                translations.extend(batch_translations)
        
        return translations
    
    def compute_bleu_score(self, predictions, references):
        """
        Compute BLEU score for translations.
        
        Args:
            predictions (list): Predicted translations
            references (list): Reference translations
            
        Returns:
            float: BLEU score (0-100)
        """
        refs = [[ref] for ref in references]
        bleu = corpus_bleu(predictions, refs)
        return bleu.score
    
    def compute_sentence_bleu_scores(self, predictions, references):
        """
        Compute sentence-level BLEU scores.
        
        Args:
            predictions (list): Predicted translations
            references (list): Reference translations
            
        Returns:
            np.array: Array of sentence-level BLEU scores
        """
        scores = []
        for pred, ref in zip(predictions, references):
            bleu = sentence_bleu(pred, [ref])
            scores.append(bleu.score)
        
        return np.array(scores)
    
    def compute_exact_match(self, predictions, references):
        """
        Compute exact match accuracy.
        
        Args:
            predictions (list): Predicted translations
            references (list): Reference translations
            
        Returns:
            float: Exact match percentage
        """
        matches = sum(1 for p, r in zip(predictions, references) if p.strip() == r.strip())
        return (matches / len(predictions)) * 100
    
    def estimate_confidence_scores(self, texts, translations):
        """
        Estimate confidence scores for translations.
        
        Args:
            texts (list): Input texts
            translations (list): Translated texts
            
        Returns:
            np.array: Confidence scores (0-100)
        """
        scores = []
        
        with torch.no_grad():
            for text, translation in zip(texts, translations):
                inputs = self.tokenizer(
                    text,
                    return_tensors='pt',
                    truncation=True,
                    max_length=128
                ).to(self.device)
                
                outputs = self.model(**inputs, labels=inputs['input_ids'])
                logits = outputs.logits
                
                # Average log probability as confidence
                log_probs = torch.log_softmax(logits, dim=-1)
                avg_log_prob = log_probs.max(dim=-1)[0].mean().item()
                
                # Convert to 0-100 scale
                confidence = max(0, min(100, (avg_log_prob + 10) * 10))
                scores.append(confidence)
        
        return np.array(scores)
    
    def analyze_errors(self, predictions, references, texts):
        """
        Analyze translation errors.
        
        Args:
            predictions (list): Predicted translations
            references (list): Reference translations
            texts (list): Input texts
            
        Returns:
            dict: Error analysis report
        """
        errors = {
            'total': len(predictions),
            'exact_matches': 0,
            'partial_matches': 0,
            'empty_predictions': 0,
            'too_short': 0,
            'too_long': 0,
            'examples': []
        }
        
        for text, pred, ref in zip(texts, predictions, references):
            if pred.strip() == ref.strip():
                errors['exact_matches'] += 1
            elif pred.strip() == '':
                errors['empty_predictions'] += 1
            elif len(pred.split()) < len(ref.split()) * 0.5:
                errors['too_short'] += 1
            elif len(pred.split()) > len(ref.split()) * 1.5:
                errors['too_long'] += 1
            else:
                errors['partial_matches'] += 1
            
            # Store first 5 errors
            if pred.strip() != ref.strip() and len(errors['examples']) < 5:
                errors['examples'].append({
                    'input': text[:100],
                    'predicted': pred[:100],
                    'reference': ref[:100]
                })
        
        return errors
    
    def evaluate_dataset(self, test_df, output_dir='outputs'):
        """
        Evaluate on test dataset.
        
        Args:
            test_df (pd.DataFrame): Test data with 'english' and 'luganda' columns
            output_dir (str): Output directory for results
            
        Returns:
            dict: Evaluation results
        """
        print(f"\n[EVALUATION] Running on {len(test_df):,} test samples")
        
        test_df = normalize_translation_frame(test_df)
        texts = test_df['english'].tolist()
        references = test_df['luganda'].tolist()
        
        # Translate
        print("  • Generating predictions...")
        predictions = self.translate_batch(texts)
        
        # Compute metrics
        print("  • Computing BLEU score...")
        bleu_score = self.compute_bleu_score(predictions, references)
        
        print("  • Computing sentence-level BLEU scores...")
        sentence_bleu_scores = self.compute_sentence_bleu_scores(predictions, references)
        
        print("  • Computing exact match accuracy...")
        exact_match = self.compute_exact_match(predictions, references)
        
        print("  • Estimating confidence scores...")
        confidence_scores = self.estimate_confidence_scores(texts, predictions)
        
        print("  • Analyzing errors...")
        error_analysis = self.analyze_errors(predictions, references, texts)
        
        # Compile results
        results = {
            'timestamp': datetime.now().isoformat(),
            'num_samples': len(test_df),
            'bleu_score': float(bleu_score),
            'exact_match_accuracy': float(exact_match),
            'sentence_bleu_scores': {
                'mean': float(sentence_bleu_scores.mean()),
                'std': float(sentence_bleu_scores.std()),
                'min': float(sentence_bleu_scores.min()),
                'max': float(sentence_bleu_scores.max())
            },
            'confidence_scores': {
                'mean': float(confidence_scores.mean()),
                'std': float(confidence_scores.std()),
                'min': float(confidence_scores.min()),
                'max': float(confidence_scores.max())
            },
            'error_analysis': error_analysis
        }
        
        # Save results
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        print(f"\n[SAVING RESULTS] to {output_dir}/")
        
        # Save as JSON
        results_path = Path(output_dir) / 'evaluation_results.json'
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"  ✓ evaluation_results.json")
        
        # Save predictions as CSV
        results_df = pd.DataFrame({
            'english': texts,
            'luganda_reference': references,
            'luganda_predicted': predictions,
            'bleu_score': sentence_bleu_scores,
            'confidence_score': confidence_scores
        })
        
        csv_path = Path(output_dir) / 'evaluation_results.csv'
        results_df.to_csv(csv_path, index=False)
        print(f"  ✓ evaluation_results.csv ({len(results_df):,} rows)")
        
        # Generate report
        self._generate_report(results, output_dir)
        
        return results
    
    def _generate_report(self, results, output_dir='outputs'):
        """
        Generate evaluation report.
        
        Args:
            results (dict): Evaluation results
            output_dir (str): Output directory
        """
        report = f"""# Model Evaluation Report
Generated: {results['timestamp']}

## Test Set Performance
- **Samples Evaluated**: {results['num_samples']:,}
- **BLEU Score**: {results['bleu_score']:.2f}
- **Exact Match Accuracy**: {results['exact_match_accuracy']:.2f}%

## Sentence-Level BLEU Scores
- Mean: {results['sentence_bleu_scores']['mean']:.2f}
- Std Dev: {results['sentence_bleu_scores']['std']:.2f}
- Min: {results['sentence_bleu_scores']['min']:.2f}
- Max: {results['sentence_bleu_scores']['max']:.2f}

## Confidence Scores
- Mean: {results['confidence_scores']['mean']:.2f}
- Std Dev: {results['confidence_scores']['std']:.2f}
- Min: {results['confidence_scores']['min']:.2f}
- Max: {results['confidence_scores']['max']:.2f}

## Error Analysis
- **Total Errors**: {results['num_samples'] - results['error_analysis']['exact_matches']}
- **Exact Matches**: {results['error_analysis']['exact_matches']}
- **Partial Matches**: {results['error_analysis']['partial_matches']}
- **Empty Predictions**: {results['error_analysis']['empty_predictions']}
- **Too Short**: {results['error_analysis']['too_short']}
- **Too Long**: {results['error_analysis']['too_long']}

## Example Errors
"""
        
        for i, example in enumerate(results['error_analysis']['examples'], 1):
            report += f"\n### Error {i}\n"
            report += f"- Input: {example['input']}\n"
            report += f"- Predicted: {example['predicted']}\n"
            report += f"- Reference: {example['reference']}\n"
        
        report_path = Path(output_dir) / 'evaluation_report.md'
        with open(report_path, 'w') as f:
            f.write(report)
        
        print(f"  ✓ evaluation_report.md")


def evaluate_model(test_path='data/processed/test_dataset.pkl',
                   model_path='models/trained_model_cpu',
                   output_dir='outputs'):
    """
    Main evaluation pipeline.
    
    Args:
        test_path (str): Path to test data
        model_path (str): Path to trained model
        output_dir (str): Output directory
    """
    print("\n" + "=" * 80)
    print("STAGE 6B: MODEL EVALUATION")
    print("=" * 80)
    
    # Load test data
    print(f"\n[LOADING] Reading from: {test_path}")
    test_df = pd.read_pickle(test_path)
    print(f"  ✓ Loaded {len(test_df):,} test samples")
    
    # Initialize evaluator
    evaluator = TranslationEvaluator(model_path=model_path)
    
    # Evaluate
    results = evaluator.evaluate_dataset(test_df, output_dir)
    
    print("\n" + "=" * 80)
    print("EVALUATION COMPLETE")
    print("=" * 80)
    print(f"\n📊 RESULTS SUMMARY:")
    print(f"  • BLEU Score: {results['bleu_score']:.2f}")
    print(f"  • Exact Match: {results['exact_match_accuracy']:.2f}%")
    print(f"  • Avg Confidence: {results['confidence_scores']['mean']:.2f}%")
    
    return results


if __name__ == "__main__":
    try:
        evaluate_model()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Run data_collection.py, preprocessing.py, and train.py first.")
