# ============================================================================
# STEP 1: ENVIRONMENT SETUP FOR LUGANDA-ENGLISH TRANSLATOR
# ============================================================================
# This script sets up Google Colab and installs all required libraries
# ============================================================================

print("=" * 70)
print("🚀 STEP 1: SETTING UP ENVIRONMENT")
print("=" * 70)

# ============================================================================
# PART 1: INSTALL REQUIRED LIBRARIES
# ============================================================================
print("\n📦 Installing required libraries...\n")

import subprocess
import sys

# List of libraries we need
required_libraries = [
    'transformers',      # For MarianMT model
    'datasets',          # For loading Sunbird SALT dataset
    'sentencepiece',     # For tokenization
    'torch',            # PyTorch (deep learning framework)
    'sacrebleu',        # For BLEU score calculation
    'pandas',           # For data manipulation
    'numpy',            # For numerical operations
]

print("Installing packages:")
for lib in required_libraries:
    print(f"  ✓ {lib}")

# Uncomment this line if running on Google Colab
subprocess.check_call([sys.executable, "-m", "pip", "install"] + required_libraries)

# ============================================================================
# PART 2: IMPORT ALL LIBRARIES
# ============================================================================
print("\n✅ Importing libraries...\n")

try:
    # NLP & Model libraries
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
    print("✓ Transformers imported successfully")
    
    # Dataset library
    from datasets import load_dataset, Dataset
    print("✓ Datasets imported successfully")
    
    # Deep Learning
    import torch
    print(f"✓ PyTorch imported successfully")
    print(f"  - GPU Available: {torch.cuda.is_available()}")
    
    # Data processing
    import pandas as pd
    import numpy as np
    print("✓ Pandas & NumPy imported successfully")
    
    # Evaluation
    import sacrebleu
    print("✓ SacreBLEU imported successfully")
    
except ImportError as e:
    print(f"❌ Error importing library: {e}")
    print("Make sure to run: pip install -r requirements.txt")

# ============================================================================
# PART 3: VERIFY GPU ACCESS (Important for Training)
# ============================================================================
print("\n" + "=" * 70)
print("🔋 GPU STATUS")
print("=" * 70)

if torch.cuda.is_available():
    print(f"✅ GPU is AVAILABLE!")
    print(f"   - GPU Name: {torch.cuda.get_device_name(0)}")
    print(f"   - CUDA Version: {torch.version.cuda}")
else:
    print("⚠️  GPU not available (CPU will be used - slower training)")

# ============================================================================
# PART 4: DISPLAY SYSTEM INFO
# ============================================================================
print("\n" + "=" * 70)
print("📊 SYSTEM INFORMATION")
print("=" * 70)

print(f"Python Version: {sys.version.split()[0]}")
print(f"PyTorch Version: {torch.__version__}")

# ============================================================================
# PART 5: CREATE DIRECTORIES FOR PROJECT
# ============================================================================
print("\n" + "=" * 70)
print("📁 CREATING PROJECT DIRECTORIES")
print("=" * 70)

import os

directories = [
    'data',
    'models',
    'outputs',
    'checkpoints',
]

for directory in directories:
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"✓ Created directory: {directory}/")
    else:
        print(f"✓ Directory already exists: {directory}/")

# ============================================================================
# PART 6: SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print("✅ SETUP COMPLETE!")
print("=" * 70)
print("\n🎯 You are ready for STEP 2: Load Sunbird SALT Dataset\n")
print("Next: Run Step2_Load_Dataset.py\n")
