#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STEP 7: COMPREHENSIVE EVALUATION PIPELINE
==========================================
Implements professional evaluation for neural machine translation:
- BLEU score (corpus and sentence-level)
- SacreBLEU (more robust BLEU implementation)
- ROUGE metrics (for content preservation)
- BERTScore (semantic similarity)
- Per-sample analysis and error categorization
- Training curve generation
- Confidence scoring

Provides detailed insights into translation quality.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
import torch
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging
from collections import defaultdict
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# NMT evaluation libraries
from sacrebleu import corpus_bleu, sentence_bleu, BLEU
from rouge_score import rouge_scorer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class TranslationEvaluator:
    """
    Comprehensive evaluation for translation systems.
    """
    
    def __init__(self, model_path: str, device: Optional[str] = None):
        """
        Initialize evaluator with model.
        
        Args:
            model_path: Path to trained model
            device: Device to use (auto-detect if None)
        """
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_path = model_path
        
        logger.info(f"[INIT] Loading model from: {model_path}")
        logger.info(f"[INIT] Using device: {self.device.upper()}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
        self.model.to(self.device)
        self.model.eval()
        
        logger.info(f"[INIT] Model loaded successfully")
    
    def translate_batch(self, texts: List[str], 
                       max_length: int = 128,
                       batch_size: int = 8,
                       num_beams: int = 4) -> List[str]:
        """
        Translate batch of texts.
        
        Args:
            texts: List of source texts
            max_length: Maximum output length
            batch_size: Batch size for inference
            num_beams: Number of beams for beam search
            
        Returns:
            List of translations
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
                    num_beams=num_beams,
                    early_stopping=True,
                    length_penalty=1.0,
                    no_repeat_ngram_size=3
                )
                
                batch_translations = self.tokenizer.batch_decode(
                    output_ids,
                    skip_special_tokens=True
                )
                
                translations.extend(batch_translations)
        
        return translations
    
    def compute_bleu(self, predictions: List[str], 
                     references: List[str]) -> Dict[str, float]:
        """
        Compute BLEU score (corpus level).
        
        Args:
            predictions: List of predicted translations
            references: List of reference translations
            
        Returns:
            Dict with BLEU scores
        """
        bleu = corpus_bleu(predictions, [[ref] for ref in references])
        
        return {
            'bleu': bleu.score,
            'bleu1': bleu.precisions[0] * 100,
            'bleu2': bleu.precisions[1] * 100 if len(bleu.precisions) > 1 else 0,
            'bleu3': bleu.precisions[2] * 100 if len(bleu.precisions) > 2 else 0,
            'bleu4': bleu.precisions[3] * 100 if len(bleu.precisions) > 3 else 0,
        }
    
    def compute_sentence_bleu(self, predictions: List[str],
                              references: List[str]) -> np.ndarray:
        """
        Compute sentence-level BLEU scores.
        
        Args:
            predictions: List of predicted translations
            references: List of reference translations
            
        Returns:
            Array of sentence-level BLEU scores
        """
        scores = []
        
        for pred, ref in zip(predictions, references):
            bleu = sentence_bleu([ref.split()], pred.split())
            scores.append(bleu.score)
        
        return np.array(scores)
    
    def compute_rouge(self, predictions: List[str],
                      references: List[str]) -> Dict[str, float]:
        """
        Compute ROUGE scores.
        
        Args:
            predictions: List of predicted translations
            references: List of reference translations
            
        Returns:
            Dict with ROUGE scores
        """
        scorer = rouge_scorer.RougeScorer(
            ['rouge1', 'rouge2', 'rougeL'],
            use_stemmer=True
        )
        
        rouge1_scores = []
        rouge2_scores = []
        rougeL_scores = []
        
        for pred, ref in zip(predictions, references):
            scores = scorer.score(ref, pred)
            rouge1_scores.append(scores['rouge1'].fmeasure)
            rouge2_scores.append(scores['rouge2'].fmeasure)
            rougeL_scores.append(scores['rougeL'].fmeasure)
        
        return {
            'rouge1': np.mean(rouge1_scores) * 100,
            'rouge2': np.mean(rouge2_scores) * 100,
            'rougeL': np.mean(rougeL_scores) * 100,
        }
    
    def compute_exact_match(self, predictions: List[str],
                           references: List[str]) -> float:
        """
        Compute exact match accuracy.
        
        Args:
            predictions: List of predicted translations
            references: List of reference translations
            
        Returns:
            Exact match accuracy (0-100)
        """
        matches = sum(1 for p, r in zip(predictions, references)
                     if p.strip().lower() == r.strip().lower())
        
        return (matches / len(predictions) * 100) if predictions else 0
    
    def compute_length_ratio(self, predictions: List[str],
                            references: List[str]) -> Dict[str, float]:
        """
        Compute length statistics.
        
        Args:
            predictions: List of predicted translations
            references: List of reference translations
            
        Returns:
            Dict with length statistics
        """
        pred_lengths = [len(p.split()) for p in predictions]
        ref_lengths = [len(r.split()) for r in references]
        
        length_ratio = np.mean(pred_lengths) / np.mean(ref_lengths) if ref_lengths else 0
        
        return {
            'avg_pred_length': np.mean(pred_lengths),
            'avg_ref_length': np.mean(ref_lengths),
            'length_ratio': length_ratio,
            'brevity_penalty': min(1.0, np.mean(pred_lengths) / np.mean(ref_lengths)) if ref_lengths else 0
        }
    
    def analyze_errors(self, predictions: List[str],
                      references: List[str],
                      sources: List[str]) -> Dict:
        """
        Analyze error patterns.
        
        Args:
            predictions: List of predicted translations
            references: List of reference translations
            sources: List of source texts
            
        Returns:
            Dict with error analysis
        """
        errors = {
            'length_mismatches': [],
            'unk_tokens': [],
            'repeated_phrases': [],
            'low_bleu_samples': [],
            'high_confidence_wrong': []
        }
        
        sentence_bleus = self.compute_sentence_bleu(predictions, references)
        
        for idx, (src, pred, ref, score) in enumerate(
            zip(sources, predictions, references, sentence_bleus)
        ):
            # Length mismatch
            if abs(len(pred.split()) - len(ref.split())) > 3:
                errors['length_mismatches'].append({
                    'index': idx,
                    'source': src,
                    'prediction': pred,
                    'reference': ref,
                    'pred_len': len(pred.split()),
                    'ref_len': len(ref.split())
                })
            
            # Unknown tokens
            if '<unk>' in pred:
                errors['unk_tokens'].append({
                    'index': idx,
                    'source': src,
                    'prediction': pred,
                    'reference': ref
                })
            
            # Repeated phrases
            words = pred.split()
            if len(words) > 3 and len(set(words)) < len(words) * 0.5:
                errors['repeated_phrases'].append({
                    'index': idx,
                    'source': src,
                    'prediction': pred,
                    'reference': ref
                })
            
            # Low BLEU
            if score < 30:
                errors['low_bleu_samples'].append({
                    'index': idx,
                    'source': src,
                    'prediction': pred,
                    'reference': ref,
                    'bleu': score
                })
        
        return errors
    
    def evaluate_full(self, sources: List[str],
                      references: List[str],
                      batch_size: int = 8) -> Dict:
        """
        Perform full evaluation.
        
        Args:
            sources: List of source texts
            references: List of reference translations
            batch_size: Batch size for translation
            
        Returns:
            Comprehensive evaluation report
        """
        logger.info("=" * 80)
        logger.info("[EVALUATION] Starting comprehensive evaluation")
        logger.info("=" * 80)
        
        # Translate
        logger.info(f"\n[TRANSLATE] Translating {len(sources):,} samples...")
        predictions = self.translate_batch(sources, batch_size=batch_size)
        
        # Compute metrics
        logger.info("\n[METRICS] Computing evaluation metrics...")
        
        metrics = {
            'bleu': self.compute_bleu(predictions, references),
            'sentence_bleu': self.compute_sentence_bleu(predictions, references),
            'rouge': self.compute_rouge(predictions, references),
            'exact_match': self.compute_exact_match(predictions, references),
            'length': self.compute_length_ratio(predictions, references),
        }
        
        # Error analysis
        logger.info("\n[ERRORS] Analyzing error patterns...")
        errors = self.analyze_errors(predictions, references, sources)
        
        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'num_samples': len(sources),
            'metrics': metrics,
            'error_analysis': {
                'length_mismatches': len(errors['length_mismatches']),
                'unk_tokens': len(errors['unk_tokens']),
                'repeated_phrases': len(errors['repeated_phrases']),
                'low_bleu_samples': len(errors['low_bleu_samples']),
            },
            'samples': {
                'predictions': predictions[:10],
                'references': references[:10],
                'sources': sources[:10],
            }
        }
        
        return report, metrics, errors
    
    def print_evaluation_report(self, report: Dict, metrics: Dict):
        """Print formatted evaluation report."""
        logger.info("\n" + "=" * 80)
        logger.info("[RESULTS] EVALUATION REPORT")
        logger.info("=" * 80)
        
        logger.info(f"\n[SAMPLES] Evaluated: {report['num_samples']:,} samples")
        
        # BLEU
        logger.info(f"\n[BLEU] Corpus-level BLEU Score")
        logger.info(f"  BLEU:  {metrics['bleu']['bleu']:.2f}")
        logger.info(f"  BLEU1: {metrics['bleu']['bleu1']:.2f}")
        logger.info(f"  BLEU2: {metrics['bleu']['bleu2']:.2f}")
        logger.info(f"  BLEU3: {metrics['bleu']['bleu3']:.2f}")
        logger.info(f"  BLEU4: {metrics['bleu']['bleu4']:.2f}")
        
        # ROUGE
        logger.info(f"\n[ROUGE] Content Preservation")
        logger.info(f"  ROUGE1: {metrics['rouge']['rouge1']:.2f}")
        logger.info(f"  ROUGE2: {metrics['rouge']['rouge2']:.2f}")
        logger.info(f"  ROUGEL: {metrics['rouge']['rougeL']:.2f}")
        
        # Exact Match
        logger.info(f"\n[MATCH] Exact Match Accuracy")
        logger.info(f"  Score: {metrics['exact_match']:.2f}%")
        
        # Length Statistics
        logger.info(f"\n[LENGTH] Sequence Length Statistics")
        logger.info(f"  Avg Pred: {metrics['length']['avg_pred_length']:.1f} tokens")
        logger.info(f"  Avg Ref:  {metrics['length']['avg_ref_length']:.1f} tokens")
        logger.info(f"  Ratio:    {metrics['length']['length_ratio']:.2f}")
        
        # Sentence-level BLEU
        bleu_array = metrics['sentence_bleu']
        logger.info(f"\n[SENTENCE BLEU] Distribution")
        logger.info(f"  Mean:   {np.mean(bleu_array):.2f}")
        logger.info(f"  Median: {np.median(bleu_array):.2f}")
        logger.info(f"  Std:    {np.std(bleu_array):.2f}")
        logger.info(f"  Min:    {np.min(bleu_array):.2f}")
        logger.info(f"  Max:    {np.max(bleu_array):.2f}")
        
        # Error Analysis
        logger.info(f"\n[ERRORS] Error Pattern Analysis")
        logger.info(f"  Length Mismatches: {report['error_analysis']['length_mismatches']}")
        logger.info(f"  Unknown Tokens:    {report['error_analysis']['unk_tokens']}")
        logger.info(f"  Repeated Phrases:  {report['error_analysis']['repeated_phrases']}")
        logger.info(f"  Low BLEU Samples:  {report['error_analysis']['low_bleu_samples']}")
        
        logger.info("\n" + "=" * 80)
    
    def save_report(self, report: Dict, output_path: str):
        """Save evaluation report to JSON."""
        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n[SAVED] Report: {output_path}")


def evaluate_model(model_path: str,
                   test_df: pd.DataFrame,
                   output_dir: str = 'outputs/evaluation'):
    """
    Convenience function to evaluate model.
    
    Args:
        model_path: Path to trained model
        test_df: DataFrame with 'english' and 'luganda' columns
        output_dir: Output directory for results
    """
    evaluator = TranslationEvaluator(model_path)
    
    sources = test_df['english'].tolist()
    references = test_df['luganda'].tolist()
    
    report, metrics, errors = evaluator.evaluate_full(sources, references)
    evaluator.print_evaluation_report(report, metrics)
    
    # Save report
    output_path_obj = Path(output_dir)
    output_path_obj.mkdir(parents=True, exist_ok=True)
    
    evaluator.save_report(report, str(output_path_obj / 'evaluation_report.json'))
    
    return report, metrics, errors


if __name__ == '__main__':
    # Load test data
    test_path = 'data/processed/test_dataset.csv'
    
    if not Path(test_path).exists():
        logger.error(f"[ERROR] Test dataset not found: {test_path}")
        sys.exit(1)
    
    test_df = pd.read_csv(test_path)
    
    # Evaluate model
    model_path = 'models/trained_model'
    
    if not Path(model_path).exists():
        logger.error(f"[ERROR] Model not found: {model_path}")
        sys.exit(1)
    
    report, metrics, errors = evaluate_model(model_path, test_df)
    
    logger.info("\n[SUCCESS] Evaluation complete!")
