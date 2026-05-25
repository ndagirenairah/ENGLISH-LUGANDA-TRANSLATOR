"""
English-Luganda Translator - ML Pipeline
=========================================

Complete machine learning workflow following Week 2 concepts:
  1. Load Data: Combine all 5 datasets
  2. Preprocess: Clean & create train/val/test splits
  3. Train: Fine-tune transformer model
  4. Evaluate: Calculate BLEU score on test set

Run this script to execute the complete pipeline:
  python scripts/run_pipeline.py
"""

import sys
import os
from pathlib import Path

# Add src to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from utils import print_section


def run_step(step_num: int, step_name: str, step_module):
    """Run a pipeline step with error handling."""
    print_section(f"RUNNING STEP {step_num}: {step_name}", width=80)
    
    try:
        step_module.main()
        return True
    except Exception as e:
        print(f"\n❌ Error in Step {step_num}: {e}")
        print(f"   Traceback:")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Execute the complete ML pipeline."""
    
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║     ENGLISH-LUGANDA TRANSLATOR - ML PIPELINE                              ║
║                                                                            ║
║  Following course curriculum:                                             ║
║    Week 2: ML Workflow (Data → Train/Test Split → Training → Evaluation)  ║
║    Week 3: Regularization (Dropout, L2 regularization)                    ║
║    Week 6: Evaluation Metrics (BLEU, cross-validation)                    ║
║    Week 9: Transformers (OPUS-MT sequence-to-sequence model)              ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
""")
    
    # Import pipeline steps
    import sys
    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    
    from load_data import main as step1_load
    from preprocess import main as step2_preprocess
    from train import main as step3_train
    from evaluate import main as step4_evaluate
    
    # Step 1: Load Data
    if not run_step(1, "Load Data (Week 2)", load_data := type('module', (), {'main': step1_load})):
        print("\n❌ Pipeline stopped at Step 1")
        return False
    
    # Step 2: Preprocess
    if not run_step(2, "Preprocess Data (Week 2)", preprocess := type('module', (), {'main': step2_preprocess})):
        print("\n❌ Pipeline stopped at Step 2")
        return False
    
    # Step 3: Train
    if not run_step(3, "Train Model (Week 9)", train := type('module', (), {'main': step3_train})):
        print("\n❌ Pipeline stopped at Step 3")
        return False
    
    # Step 4: Evaluate
    if not run_step(4, "Evaluate Model (Week 6)", evaluate := type('module', (), {'main': step4_evaluate})):
        print("\n❌ Pipeline stopped at Step 4")
        return False
    
    # Pipeline complete
    print_section("PIPELINE COMPLETE", width=80)
    print("""
✅ ALL STEPS COMPLETE!

Summary:
  ✓ Step 1: Loaded all 5 datasets from data/raw/
  ✓ Step 2: Created train/val/test splits
  ✓ Step 3: Trained transformer model
  ✓ Step 4: Evaluated on test set (BLEU score)

Results saved to:
  - models/trained_model/          (trained model & tokenizer)
  - outputs/evaluation_results.json (BLEU score & metrics)
  - outputs/predictions.csv        (sample predictions)

Next steps:
  - Review results in outputs/
  - Fine-tune hyperparameters and retrain
  - Deploy model for inference
""")


if __name__ == "__main__":
    main()
