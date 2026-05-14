#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QUICK START - AUTOMATIC SETUP & EXECUTION
===========================================
Run this script to automatically:
1. Install dependencies
2. Prepare data
3. Train model
4. Evaluate
5. Launch app

Usage:
    python QUICKSTART.py
"""

import os
import sys
import subprocess
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def run_command(cmd, description):
    """Run shell command with error handling."""
    logger.info(f"\n{'='*80}")
    logger.info(f"[STEP] {description}")
    logger.info(f"{'='*80}")
    logger.info(f"[CMD] {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=False)
        if result.returncode != 0:
            logger.error(f"[ERROR] Command failed with return code {result.returncode}")
            return False
        logger.info(f"[SUCCESS] {description} complete")
        return True
    except Exception as e:
        logger.error(f"[ERROR] {e}")
        return False


def main():
    """Main execution."""
    
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "NLLB-200 ENGLISH-LUGANDA TRANSLATOR - QUICK START".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    # Check dataset exists
    if not Path('data/raw/luganda_dataset.csv').exists():
        logger.error("[ERROR] Dataset not found: data/raw/luganda_dataset.csv")
        logger.info("[INFO] Please ensure dataset is in data/raw/luganda_dataset.csv")
        sys.exit(1)
    
    logger.info("\n[CHECK] Dataset found: data/raw/luganda_dataset.csv")
    
    # ====================================================================
    # STEP 1: Install Dependencies
    # ====================================================================
    logger.info("\n" + "="*80)
    logger.info("[PHASE 1] Installing Dependencies")
    logger.info("="*80)
    
    response = input("\n[PROMPT] Install pip dependencies? (y/n): ").lower()
    if response == 'y':
        if not run_command("pip install -r requirements_nllb.txt", "Installing dependencies"):
            logger.error("[ERROR] Dependency installation failed")
            sys.exit(1)
    
    # ====================================================================
    # STEP 2: Clean Data
    # ====================================================================
    logger.info("\n" + "="*80)
    logger.info("[PHASE 2] Data Preparation & Cleaning")
    logger.info("="*80)
    
    response = input("\n[PROMPT] Clean and prepare dataset? (y/n): ").lower()
    if response == 'y':
        if not run_command("python data_quality.py", "Cleaning dataset"):
            logger.error("[ERROR] Data cleaning failed")
            sys.exit(1)
    
    # ====================================================================
    # STEP 3: Train Model
    # ====================================================================
    logger.info("\n" + "="*80)
    logger.info("[PHASE 3] Model Training")
    logger.info("="*80)
    
    logger.info("""
[INFO] Training will:
  - Load cleaned dataset
  - Train NLLB-200 with professional techniques
  - Implement early stopping based on validation BLEU
  - Save best model to models/nllb_trained/

Expected time:
  - GPU (NVIDIA T4):    6-10 hours
  - GPU (RTX 3090):     2-4 hours
  - CPU:                48-72 hours (not recommended)
    """)
    
    response = input("\n[PROMPT] Train model? (y/n): ").lower()
    if response == 'y':
        if not run_command("python train_nllb_professional.py", "Training model"):
            logger.error("[ERROR] Training failed")
            logger.info("[INFO] You can resume training by running train_nllb_professional.py again")
            sys.exit(1)
    
    # ====================================================================
    # STEP 4: Evaluate Model
    # ====================================================================
    logger.info("\n" + "="*80)
    logger.info("[PHASE 4] Model Evaluation")
    logger.info("="*80)
    
    response = input("\n[PROMPT] Evaluate model? (y/n): ").lower()
    if response == 'y':
        eval_code = """
from pathlib import Path
import pandas as pd
from evaluation_comprehensive import evaluate_model

if Path('models/nllb_trained').exists():
    test_df = pd.read_csv('data/processed/cleaned_dataset.csv')
    test_df = test_df.sample(n=min(1000, len(test_df)), random_state=42)
    evaluate_model('models/nllb_trained', test_df)
else:
    print('[ERROR] Model not found. Please train first.')
"""
        
        if not run_command(f'python -c "{eval_code}"', "Evaluating model"):
            logger.error("[ERROR] Evaluation failed")
    
    # ====================================================================
    # STEP 5: Launch App
    # ====================================================================
    logger.info("\n" + "="*80)
    logger.info("[PHASE 5] Launch Web Application")
    logger.info("="*80)
    
    response = input("\n[PROMPT] Launch Streamlit web app? (y/n): ").lower()
    if response == 'y':
        logger.info("\n[INFO] Starting Streamlit...")
        logger.info("[URL] Access at: http://localhost:8501")
        logger.info("[NOTE] Press Ctrl+C to stop")
        
        os.system("streamlit run app_streamlit_professional.py")
    
    logger.info("\n" + "="*80)
    logger.info("[SUCCESS] QUICK START COMPLETE!")
    logger.info("="*80)
    logger.info("""
Next steps:
1. Run: python EXECUTION_GUIDE.py  (for detailed instructions)
2. Run: streamlit run app_streamlit_professional.py  (web interface)
3. Run: python app.py  (Flask API server)
4. Check README_REBUILD.md  (comprehensive documentation)
    """)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n[INFO] Cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"[ERROR] {e}")
        sys.exit(1)
