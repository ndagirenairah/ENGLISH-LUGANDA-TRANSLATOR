#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QUICK REFERENCE: LUGANDA-ENGLISH DATASETS
Lists available datasets and how to access them
"""

import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("""
================================================================================
LUGANDA-ENGLISH TRANSLATION DATASETS - COMPREHENSIVE GUIDE
================================================================================

1. PRIMARY OPTION - KABALE DATASET (Recommended)
   ┌─────────────────────────────────────────────────────────────────────────┐
   │ Name: kambale/luganda-english-parallel-corpus                           │
   │ URL: https://huggingface.co/datasets/kambale/luganda-english-parallel  │
   │ Size: ~100k+ pairs (highest quality)                                    │
   │ Access: GATED - Requires manual approval                                │
   │ Load Command: load_dataset('kambale/luganda-english-parallel-corpus')  │
   │ Status: [GATED] - Request access first                                  │
   └─────────────────────────────────────────────────────────────────────────┘

2. PUBLIC OPTION - SUNBIRD AI SALT
   ┌─────────────────────────────────────────────────────────────────────────┐
   │ Name: Sunbird/salt                                                       │
   │ URL: https://huggingface.co/datasets/Sunbird/salt                       │
   │ Split: "lug-eng"                                                         │
   │ Size: ~10k pairs (lower quality)                                         │
   │ Access: GATED - Requires approval                                        │
   │ Load Command: load_dataset("Sunbird/salt", "lug-eng", split="train")   │
   │ Status: [GATED] - Request access first                                  │
   └─────────────────────────────────────────────────────────────────────────┘

3. PUBLIC OPTION - OPUS_100 (JW300 based)
   ┌─────────────────────────────────────────────────────────────────────────┐
   │ Name: opus_100                                                           │
   │ URL: https://opus.nlp.eu/                                               │
   │ Language Pair: en-lg                                                     │
   │ Size: Variable (~50k pairs)                                              │
   │ Access: Public but may have data availability issues                     │
   │ Status: [UNRELIABLE] - May not be available on HF                        │
   └─────────────────────────────────────────────────────────────────────────┘

4. LOCAL OPTION - CULTURAL TRAINING DATA
   ┌─────────────────────────────────────────────────────────────────────────┐
   │ Location: data/raw/cultural_training.csv                                │
   │ Format: CSV with 'english' and 'luganda' columns                         │
   │ Size: Local samples (variable)                                           │
   │ Access: Immediate                                                        │
   │ Load Command: pd.read_csv('data/raw/cultural_training.csv')             │
   │ Status: [AVAILABLE] - Use if other sources fail                          │
   └─────────────────────────────────────────────────────────────────────────┘

================================================================================
RECOMMENDED WORKFLOW
================================================================================

BEST CASE (Highest Quality):
1. Request access to Kabale dataset
2. Use train_with_kabale_dataset.py
3. Get ~100k high-quality pairs

GOOD CASE (Public Access):
1. Combine available public datasets
2. Use train_with_mixed_datasets.py (if created)
3. May get lower quality translations

FALLBACK CASE (Limited Data):
1. Use local cultural training data
2. Use train_with_cultural_data.py
3. Limited to local resources only

================================================================================
HOW TO REQUEST DATASET ACCESS
================================================================================

For GATED datasets (Kabale, Sunbird):

Step 1: Visit the dataset page (URLs above)
Step 2: Click "Access repository" button
Step 3: Read and accept terms
Step 4: Wait for approval (usually instant)
Step 5: Authenticate locally:

   Option A - CLI:
   $ huggingface-cli login
   [Paste your token when prompted]

   Option B - Environment Variable:
   $ set HF_TOKEN=your_token_here

   Option C - Python:
   from huggingface_hub import login
   login(token="your_token_here")

Get your token from: https://huggingface.co/settings/tokens

================================================================================
TRAINING SCRIPTS PROVIDED
================================================================================

1. train_with_kabale_dataset.py
   - For Kabale dataset (if you have access)
   - Recommended: 5 epochs, batch size 16
   - Output: models/trained_model_cpu/
   - Usage: python train_with_kabale_dataset.py

2. train_with_public_datasets.py
   - For public Sunbird + JW300 (if accessible)
   - Fallback when Kabale unavailable
   - Output: models/trained_model_cpu/
   - Usage: python train_with_public_datasets.py

3. validate_setup.py
   - Check dataset accessibility
   - Verify model loading capability
   - Test tokenization and inference
   - Usage: python validate_setup.py

================================================================================
CURRENT STATUS
================================================================================

Most gated datasets now require HuggingFace authentication.
Public alternatives have limited availability.

RECOMMENDATION:
Request access to Kabale dataset first - it has the best quality and size.
It's the recommended approach for production-grade translation.

================================================================================
NEXT STEPS
================================================================================

1. Run DATASET_ACCESS_GUIDE.py for detailed access instructions
2. Request access to Kabale dataset
3. Once approved, authenticate with: huggingface-cli login
4. Run appropriate training script
5. Deploy with: streamlit run app_streamlit.py

For detailed setup instructions, see: QUICKSTART.md

""")
