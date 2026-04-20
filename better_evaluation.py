#!/usr/bin/env python3
"""
Better Evaluation Metrics for Low-Resource Language Translation
Implements chrF++, similarity metrics, and human evaluation framework
"""

import numpy as np
from typing import List, Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TranslationEvaluator:
    """Comprehensive evaluation metrics for translation"""
    
    @staticmethod
    def chrf_score(references: List[str], hypotheses: List[str], 
                   n: int = 6, beta: float = 3.0) -> float:
        """
        Compute chrF++ score (character n-gram F-score)
        Better than BLEU for morphologically rich languages like Luganda
        
        Args:
            references: Reference translations
            hypotheses: Generated translations
            n: n-gram size (default 6)
            beta: weight for recall (default 3.0, emphasize recall)
        
        Returns:
            chrF++ score (0-1)
        """
        chrf_scores = []
        
        for ref, hyp in zip(references, hypotheses):
            # Get character n-grams
            ref_ngrams = TranslationEvaluator._get_char_ngrams(ref, n)
            hyp_ngrams = TranslationEvaluator._get_char_ngrams(hyp, n)
            
            # Compute precision and recall
            if len(hyp_ngrams) == 0:
                precision = 0
            else:
                matches = sum((hyp_ngrams & ref_ngrams).values())
                precision = matches / sum(hyp_ngrams.values())
            
            if len(ref_ngrams) == 0:
                recall = 0
            else:
                matches = sum((hyp_ngrams & ref_ngrams).values())
                recall = matches / sum(ref_ngrams.values())
            
            # F-score with beta
            if precision + recall == 0:
                f_score = 0
            else:
                f_score = (1 + beta**2) * (precision * recall) / ((beta**2 * precision) + recall)
            
            chrf_scores.append(f_score)
        
        return np.mean(chrf_scores) if chrf_scores else 0
    
    @staticmethod
    def _get_char_ngrams(text: str, n: int) -> Dict[str, int]:
        """Extract character n-grams from text"""
        ngrams = {}
        text = text.lower()
        
        for i in range(len(text) - n + 1):
            ngram = text[i:i+n]
            ngrams[ngram] = ngrams.get(ngram, 0) + 1
        
        return ngrams
    
    @staticmethod
    def similarity_score(reference: str, hypothesis: str) -> Dict[str, float]:
        """
        Compute multiple similarity metrics
        """
        ref_words = reference.lower().split()
        hyp_words = hypothesis.lower().split()
        
        # Word overlap
        ref_set = set(ref_words)
        hyp_set = set(hyp_words)
        
        if len(ref_set | hyp_set) == 0:
            jaccard = 0
        else:
            jaccard = len(ref_set & hyp_set) / len(ref_set | hyp_set)
        
        # Length ratio
        if len(ref_words) == 0:
            length_ratio = 0
        else:
            length_ratio = len(hyp_words) / len(ref_words)
        
        # Exact match
        exact_match = 1.0 if reference.lower() == hypothesis.lower() else 0.0
        
        return {
            "jaccard_similarity": jaccard,
            "length_ratio": length_ratio,
            "exact_match": exact_match,
            "ref_length": len(ref_words),
            "hyp_length": len(hyp_words)
        }
    
    @staticmethod
    def evaluate_batch(references: List[str], hypotheses: List[str]) -> Dict:
        """
        Comprehensive evaluation on multiple metrics
        """
        if len(references) != len(hypotheses):
            raise ValueError("References and hypotheses must have same length")
        
        results = {
            "total_samples": len(references),
            "chrf_score": TranslationEvaluator.chrf_score(references, hypotheses),
            "per_sample": [],
            "summary": {}
        }
        
        jaccard_scores = []
        length_ratios = []
        exact_matches = 0
        
        for ref, hyp in zip(references, hypotheses):
            similarity = TranslationEvaluator.similarity_score(ref, hyp)
            results["per_sample"].append({
                "reference": ref,
                "hypothesis": hyp,
                **similarity
            })
            
            jaccard_scores.append(similarity["jaccard_similarity"])
            length_ratios.append(similarity["length_ratio"])
            if similarity["exact_match"] == 1.0:
                exact_matches += 1
        
        results["summary"] = {
            "avg_jaccard": np.mean(jaccard_scores),
            "avg_length_ratio": np.mean(length_ratios),
            "exact_matches": exact_matches,
            "exact_match_rate": exact_matches / len(references)
        }
        
        return results

class HumanEvaluationFramework:
    """
    Framework for human evaluation of translations
    Structured scoring system for translation quality
    """
    
    # Scoring rubric
    RUBRIC = {
        2: "✅ Correct - Translation is accurate and natural",
        1: "🟡 Acceptable - Understandable but may have minor issues",
        0: "❌ Incorrect - Translation has errors or is nonsensical"
    }
    
    # Task categories for evaluation
    CATEGORIES = {
        "greetings": ["good morning", "hello", "how are you?"],
        "clan_system": ["what clan are you from?", "i am from the monkey clan"],
        "education": ["education is important", "learning helps us grow"],
        "family": ["how is your family?", "respect your elders"],
        "cultural": ["we are baganda and proud", "luganda is beautiful"],
        "common": ["thank you", "please", "yes", "no"]
    }
    
    def __init__(self):
        self.evaluations = []
        self.scores = {}
    
    def evaluate_phrase(self, english: str, luganda: str, 
                       score: int, category: str, notes: str = "") -> Dict:
        """
        Record human evaluation of a translation
        
        score: 0 (incorrect), 1 (acceptable), 2 (correct)
        """
        if score not in [0, 1, 2]:
            raise ValueError("Score must be 0, 1, or 2")
        
        evaluation = {
            "english": english,
            "luganda": luganda,
            "score": score,
            "category": category,
            "rating": self.RUBRIC[score],
            "notes": notes
        }
        
        self.evaluations.append(evaluation)
        
        if category not in self.scores:
            self.scores[category] = []
        self.scores[category].append(score)
        
        return evaluation
    
    def get_summary(self) -> Dict:
        """Get evaluation summary"""
        if not self.evaluations:
            return {"status": "No evaluations yet"}
        
        all_scores = []
        for scores in self.scores.values():
            all_scores.extend(scores)
        
        summary = {
            "total_evaluated": len(self.evaluations),
            "overall_score": np.mean(all_scores),
            "perfect_translations": sum(1 for s in all_scores if s == 2),
            "acceptable_translations": sum(1 for s in all_scores if s == 1),
            "incorrect_translations": sum(1 for s in all_scores if s == 0),
            "by_category": {}
        }
        
        for category, scores in self.scores.items():
            summary["by_category"][category] = {
                "count": len(scores),
                "average_score": np.mean(scores),
                "perfect": sum(1 for s in scores if s == 2),
                "acceptable": sum(1 for s in scores if s == 1),
                "incorrect": sum(1 for s in scores if s == 0)
            }
        
        return summary
    
    def generate_report(self) -> str:
        """Generate human evaluation report"""
        summary = self.get_summary()
        
        report = []
        report.append("=" * 80)
        report.append("👤 HUMAN EVALUATION REPORT")
        report.append("=" * 80)
        report.append("")
        
        if "status" in summary:
            report.append(f"ℹ️  {summary['status']}")
            return "\n".join(report)
        
        report.append(f"📊 OVERALL SUMMARY")
        report.append(f"  Total Evaluated: {summary['total_evaluated']}")
        report.append(f"  Overall Score: {summary['overall_score']:.2f}/2.0")
        report.append(f"  ✅ Perfect: {summary['perfect_translations']}")
        report.append(f"  🟡 Acceptable: {summary['acceptable_translations']}")
        report.append(f"  ❌ Incorrect: {summary['incorrect_translations']}")
        report.append("")
        
        if summary["by_category"]:
            report.append("📈 BY CATEGORY")
            report.append("-" * 80)
            for category, stats in summary["by_category"].items():
                report.append(f"\n  {category.upper()}")
                report.append(f"    Count: {stats['count']}")
                report.append(f"    Average Score: {stats['average_score']:.2f}/2.0")
                report.append(f"    ✅ Perfect: {stats['perfect']}")
                report.append(f"    🟡 Acceptable: {stats['acceptable']}")
                report.append(f"    ❌ Incorrect: {stats['incorrect']}")
        
        report.append("\n" + "=" * 80)
        report.append("✅ EVALUATION COMPLETE")
        report.append("=" * 80)
        
        return "\n".join(report)

if __name__ == "__main__":
    # Test evaluation
    logger.info("🧪 Testing Translation Evaluator\n")
    
    # Test data
    references = [
        "Ndi mu kika kya Ngo",
        "Oli otya?",
        "Webale nnyo"
    ]
    
    hypotheses = [
        "Ndi mu kika kya Ngoo",  # Slight variation
        "Oli otya?",  # Perfect match
        "Webale"  # Correct but shorter
    ]
    
    evaluator = TranslationEvaluator()
    results = evaluator.evaluate_batch(references, hypotheses)
    
    logger.info("📊 EVALUATION RESULTS")
    logger.info(f"  chrF++ Score: {results['chrf_score']:.3f}")
    logger.info(f"  Avg Jaccard: {results['summary']['avg_jaccard']:.3f}")
    logger.info(f"  Exact Matches: {results['summary']['exact_matches']}/{results['total_samples']}")
    logger.info("")
    
    # Test human evaluation
    logger.info("👤 Testing Human Evaluation Framework\n")
    
    human_eval = HumanEvaluationFramework()
    
    # Simulate human scores
    human_eval.evaluate_phrase("What clan are you from?", "Oli mu kika ki?", 2, "clan_system")
    human_eval.evaluate_phrase("Good morning", "Wasuze otya?", 2, "greetings")
    human_eval.evaluate_phrase("Good morning", "Wasuubire nnyo", 0, "greetings")
    human_eval.evaluate_phrase("Thank you", "Webale", 2, "common")
    
    print(human_eval.generate_report())
