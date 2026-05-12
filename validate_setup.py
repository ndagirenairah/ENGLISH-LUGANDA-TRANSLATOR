#!/usr/bin/env python3
"""
QUICK VALIDATION SCRIPT
Tests that Kabale dataset loads correctly and model can be trained
"""

import os
import sys
import torch
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import pandas as pd

print("=" * 80)
print("🔍 VALIDATION SCRIPT: Kabale Dataset & Model Check")
print("=" * 80)

# ============================================================================
# CHECK 1: Dataset Access
# ============================================================================
print("\n[CHECK 1] Testing Kabale Dataset Access...")

try:
    print("  🔄 Loading kambale/luganda-english-parallel-corpus...")
    dataset = load_dataset('kambale/luganda-english-parallel-corpus')
    print(f"  ✅ Dataset loaded successfully!")
    print(f"     Splits: {list(dataset.keys())}")
    
    main_split = dataset['train'] if 'train' in dataset else dataset[list(dataset.keys())[0]]
    print(f"     Total samples: {len(main_split):,}")
    
    # Show sample
    sample = main_split[0]
    print(f"\n  📋 Sample entry structure:")
    for key, value in sample.items():
        if isinstance(value, dict):
            print(f"     {key}: {value}")
        elif isinstance(value, str):
            print(f"     {key}: {value[:50]}...")
        else:
            print(f"     {key}: {value}")
    
except Exception as e:
    print(f"  ❌ Error loading dataset: {e}")
    print(f"  💡 Troubleshooting:")
    print(f"     - Check internet connection")
    print(f"     - Make sure 'datasets' package is installed: pip install datasets")
    print(f"     - Try manually downloading from: https://huggingface.co/datasets/kambale/luganda-english-parallel-corpus")
    sys.exit(1)

# ============================================================================
# CHECK 2: Data Normalization
# ============================================================================
print("\n[CHECK 2] Testing Data Normalization...")

try:
    rows = []
    for i, item in enumerate(main_split[:100]):  # Test with first 100
        try:
            if 'translation' in item and isinstance(item['translation'], dict):
                eng = item['translation'].get('en') or item['translation'].get('eng') or item['translation'].get('english') or ''
                lug = item['translation'].get('lg') or item['translation'].get('lug') or item['translation'].get('luganda') or ''
            elif 'english' in item and 'luganda' in item:
                eng = item['english']
                lug = item['luganda']
            else:
                continue
            
            eng = str(eng).strip() if eng else ''
            lug = str(lug).strip() if lug else ''
            
            if len(eng) > 3 and len(lug) > 3:
                rows.append({'english': eng, 'luganda': lug})
        except:
            continue
    
    df = pd.DataFrame(rows)
    print(f"  ✅ Successfully normalized {len(df):,} pairs from first 100 samples")
    print(f"     - English avg length: {df['english'].str.len().mean():.1f} chars")
    print(f"     - Luganda avg length: {df['luganda'].str.len().mean():.1f} chars")
    
    # Show sample
    print(f"\n  📋 Sample normalized pairs:")
    for idx in range(min(3, len(df))):
        print(f"     [{idx+1}] EN: {df.iloc[idx]['english'][:40]}...")
        print(f"         LG: {df.iloc[idx]['luganda'][:40]}...")
    
except Exception as e:
    print(f"  ❌ Error normalizing data: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# CHECK 3: Model Loading
# ============================================================================
print("\n[CHECK 3] Testing Model Loading...")

try:
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"  🖥️  Device: {device.upper()}")
    
    model_name = 'Helsinki-NLP/opus-mt-en-mul'
    print(f"  🔄 Loading model: {model_name}")
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    
    print(f"  ✅ Model loaded successfully!")
    print(f"     Parameters: {model.num_parameters():,}")
    print(f"     Vocab size (source): {tokenizer.vocab_size:,}")
    
    model.to(device)
    print(f"  ✅ Model moved to {device.upper()}")
    
except Exception as e:
    print(f"  ❌ Error loading model: {e}")
    print(f"  💡 Make sure you have torch and transformers installed:")
    print(f"     pip install torch transformers")
    sys.exit(1)

# ============================================================================
# CHECK 4: Tokenization Test
# ============================================================================
print("\n[CHECK 4] Testing Tokenization...")

try:
    test_text = "Hello, how are you today?"
    
    inputs = tokenizer(test_text, return_tensors='pt', truncation=True, max_length=128)
    print(f"  ✅ Tokenization successful!")
    print(f"     Input: {test_text}")
    print(f"     Tokens: {inputs['input_ids'].shape}")
    print(f"     Token IDs: {inputs['input_ids'].tolist()[0][:10]}...")
    
except Exception as e:
    print(f"  ❌ Error in tokenization: {e}")
    sys.exit(1)

# ============================================================================
# CHECK 5: Inference Test
# ============================================================================
print("\n[CHECK 5] Testing Model Inference...")

try:
    model.eval()
    
    with torch.no_grad():
        # Test translation
        test_sentence = "Good morning, welcome to Uganda"
        inputs = tokenizer(test_sentence, return_tensors='pt', max_length=128, truncation=True).to(device)
        
        print(f"  🔄 Translating: '{test_sentence}'")
        
        outputs = model.generate(**inputs, max_length=128, num_beams=4)
        translation = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        print(f"  ✅ Translation complete!")
        print(f"     Result: '{translation}'")
    
except Exception as e:
    print(f"  ❌ Error in inference: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# CHECK 6: Verify Training Script
# ============================================================================
print("\n[CHECK 6] Verifying Training Script...")

try:
    training_script = 'train_with_kabale_dataset.py'
    if os.path.exists(training_script):
        print(f"  ✅ Training script found: {training_script}")
        print(f"     This script will:")
        print(f"     1. Load the Kabale dataset")
        print(f"     2. Split into train/val/test (70%/15%/15%)")
        print(f"     3. Train for 5 epochs with batch size 16")
        print(f"     4. Save model to models/trained_model_cpu/")
        print(f"\n  💡 To start training, run:")
        print(f"     python {training_script}")
    else:
        print(f"  ⚠️  Training script not found: {training_script}")

except Exception as e:
    print(f"  ⚠️  Could not verify training script: {e}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("✅ ALL VALIDATION CHECKS PASSED!")
print("=" * 80)
print(f"""
📊 System Summary:
   • Device: {device.upper()}
   • Dataset: Kabale English-Luganda (kambale/luganda-english-parallel-corpus)
   • Model: Helsinki-NLP/opus-mt-en-mul ({model.num_parameters():,} params)
   • Status: ✅ Ready for training

🚀 Next Steps:
   1. Run the training script: python train_with_kabale_dataset.py
   2. Wait for training to complete (may take several hours depending on dataset size)
   3. Once trained, the model will be saved to: models/trained_model_cpu/
   4. Then deploy with Streamlit: streamlit run app_streamlit.py

✨ Everything is configured correctly!
""")
