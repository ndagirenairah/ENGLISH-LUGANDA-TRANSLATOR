#!/usr/bin/env python3
"""
SETUP GUIDE - Gated Dataset Access
Instructions for accessing the Kabale English-Luganda dataset
"""

print("=" * 80)
print("🔐 GATED DATASET ACCESS GUIDE")
print("=" * 80)
print("""
The Kabale English-Luganda Parallel Corpus is a GATED DATASET on HuggingFace.
This means you need to request access before using it.

📋 STEP-BY-STEP GUIDE TO GET ACCESS:

1️⃣  Go to the dataset page:
   https://huggingface.co/datasets/kambale/luganda-english-parallel-corpus

2️⃣  Click "Access repository"
   (You may need to scroll down to find this button)

3️⃣  Read and accept the terms (if any)

4️⃣  Click "Accept" to request access

5️⃣  Wait for approval (usually instant to a few hours)

6️⃣  Once approved, your HuggingFace account has access

7️⃣  Authenticate locally with your HuggingFace token:
   
   Option A: Using the CLI:
   $ huggingface-cli login
   (Then paste your token when prompted)
   
   Option B: Set environment variable:
   $ set HF_TOKEN=your_token_here
   
   Option C: In Python:
   from huggingface_hub import login
   login(token="your_token_here")

🔑 HOW TO GET YOUR HUGGINGFACE TOKEN:

1. Go to: https://huggingface.co/settings/tokens
2. Click "New token"
3. Name it: "Luganda Translator"
4. Select "Read" permission
5. Click "Create token"
6. Copy and save it (you'll need it)

✅ AFTER GETTING ACCESS:

Run the training script:
   python train_with_kabale_dataset.py

Or run the validation script:
   python validate_setup.py

📌 ALTERNATIVE DATASETS (if you can't access Kabale):

If you don't have access to Kabale, you can use these public datasets:

1. Sunbird AI SALT Dataset (Public):
   - URL: https://huggingface.co/datasets/Sunbird/salt
   - Split: "lug-eng"
   - ~10k pairs
   
   To use:
   dataset = load_dataset("Sunbird/salt", "lug-eng", split="train")

2. JW300 Corpus (Public):
   - URL: https://huggingface.co/datasets/opus_100
   - Split: "en-lg"
   - ~50k pairs
   
   To use:
   dataset = load_dataset("opus_100", "en-lg", split="train", trust_remote_code=True)

3. Opus MT Collections (Public):
   - Various sizes and quality levels
   - Access via `datasets` library

❓ TROUBLESHOOTING:

Q: "Dataset is a gated dataset" - What should I do?
A: Follow steps 1-7 above to request and authenticate access.

Q: "Authentication failed" error
A: Make sure your token is correct. Re-run: huggingface-cli login

Q: Still having issues?
A: Try using one of the alternative public datasets listed above.

💡 RECOMMENDED APPROACH:

For the best results:
1. Request access to Kabale dataset (it's the highest quality)
2. If access is denied, use Sunbird AI SALT + JW300 combined
3. The training script will work with any properly formatted dataset

🚀 NEXT STEPS:

1. Request access to Kabale dataset
2. Authenticate with: huggingface-cli login
3. Run: python train_with_kabale_dataset.py
4. Wait for training to complete
5. Deploy with: streamlit run app_streamlit.py

For more help, see: QUICKSTART.md
""")
