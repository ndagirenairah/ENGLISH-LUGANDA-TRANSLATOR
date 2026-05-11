"""
STAGE 1: PROBLEM DEFINITION
============================
Defines the problem statement, objectives, and constraints for the 
English-Luganda Neural Machine Translation system.
"""

import json
import os

class ProblemDefinition:
    """
    Encapsulates the problem definition for English-Luganda translation.
    """
    
    def __init__(self):
        self.project_name = "English-Luganda Neural Machine Translator"
        self.problem_statement = """
        Low-resource language translation is challenging due to:
        - Limited parallel corpora (100k-500k vs 5M+ for high-resource pairs)
        - Vocabulary sparsity and word inflections
        - Complex morphology in Luganda
        - Limited pre-trained models for African languages
        """
        
        self.objective = """
        Build a bidirectional English ↔ Luganda translation system that:
        1. Achieves reasonable translation quality (BLEU > 0.25)
        2. Provides confidence scores for reliability assessment
        3. Supports both text and voice input/output
        4. Explains translation choices
        5. Maintains translation history for user feedback
        """
        
        self.expected_inputs = {
            "text": "English or Luganda sentence (max 512 tokens)",
            "language": "Source language (english/luganda)",
            "voice": "Audio file (WAV/MP3) - optional"
        }
        
        self.expected_outputs = {
            "translation": "Translated text",
            "confidence": "0.0-1.0 confidence score",
            "explanation": "Why this translation was chosen",
            "audio": "Speech synthesis of translation",
            "metadata": {"source_language": "str", "target_language": "str"}
        }
        
        self.use_cases = [
            "Real-time communication between English and Luganda speakers",
            "Document translation for educational materials",
            "Customer support in multiple languages",
            "Language learning assistance",
            "Cultural preservation and communication"
        ]
        
        self.constraints = [
            "Limited training data (100k parallel sentences)",
            "Computational constraints (must run on CPU)",
            "Low-resource language (sparse embeddings)",
            "Real-time latency requirements (< 2 seconds)",
            "Accuracy vs speed tradeoff"
        ]
        
        self.success_metrics = {
            "BLEU_Score": ">= 0.30",
            "Translation_Accuracy": ">= 70%",
            "Confidence_Calibration": "95% confidence = 95% accuracy",
            "Inference_Time": "< 2 seconds",
            "User_Satisfaction": ">= 4/5 stars"
        }
        
        self.model_approach = {
            "architecture": "Transformer Seq2Seq (MarianMT)",
            "pre_training": "Helsinki-NLP/opus-mt-en-mul",
            "fine_tuning": "English-Luganda parallel corpus",
            "inference": "Beam search (k=4)",
            "features": "Bidirectional, confidence scoring, voice I/O"
        }
    
    def display(self):
        """Display the problem definition."""
        print("=" * 80)
        print("PROBLEM DEFINITION: English-Luganda Translation System")
        print("=" * 80)
        
        print("\nPROJECT OBJECTIVE:")
        print(self.objective)
        
        print("\nPROBLEM STATEMENT:")
        print(self.problem_statement)
        
        print("\nUSE CASES:")
        for i, use_case in enumerate(self.use_cases, 1):
            print(f"  {i}. {use_case}")
        
        print("\nCONSTRAINTS:")
        for i, constraint in enumerate(self.constraints, 1):
            print(f"  {i}. {constraint}")
        
        print("\nEXPECTED INPUTS:")
        for key, value in self.expected_inputs.items():
            print(f"  - {key}: {value}")
        
        print("\nEXPECTED OUTPUTS:")
        for key, value in self.expected_outputs.items():
            print(f"  - {key}: {value}")
        
        print("\nSUCCESS METRICS:")
        for metric, target in self.success_metrics.items():
            print(f"  - {metric}: {target}")
        
        print("\nMODEL APPROACH:")
        for key, value in self.model_approach.items():
            print(f"  - {key}: {value}")
        
        print("\n" + "=" * 80)
    
    def save_report(self, filepath="reports/problem_definition.json"):
        """Save problem definition as JSON report."""
        report = {
            "project_name": self.project_name,
            "problem_statement": self.problem_statement.strip(),
            "objective": self.objective.strip(),
            "use_cases": self.use_cases,
            "constraints": self.constraints,
            "expected_inputs": self.expected_inputs,
            "expected_outputs": self.expected_outputs,
            "success_metrics": self.success_metrics,
            "model_approach": self.model_approach
        }

        report_dir = os.path.dirname(filepath)
        if report_dir:
            os.makedirs(report_dir, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Problem definition saved to: {filepath}")


if __name__ == "__main__":
    problem = ProblemDefinition()
    problem.display()
    problem.save_report()
