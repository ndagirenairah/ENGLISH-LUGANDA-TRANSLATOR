from datasets import load_dataset
import pandas as pd

print("[LOADING] Attempting to load Kabale dataset from HuggingFace...")

try:
    dataset = load_dataset("kambale/luganda-english-parallel-corpus")
    print("[SUCCESS] Dataset loaded successfully!")
    print(f"\n[INFO] Dataset structure:\n{dataset}\n")
    
    print("[INFO] Loading first example from train split...\n")
    print(f"FIRST EXAMPLE:\n{dataset['train'][0]}\n")
    
    print("[CONVERTING] Converting to pandas DataFrame...")
    df = pd.DataFrame(dataset["train"])
    
    print(f"\n[SUCCESS] DataFrame created with {len(df)} rows\n")
    print("[DISPLAYING] First 20 rows:\n")
    print(df.head(20))
    
    print(f"\n[SAVING] Saving dataset to CSV...")
    df.to_csv("luganda_dataset.csv", index=False)
    print("[SUCCESS] Dataset saved to: luganda_dataset.csv\n")
    
    print(f"[STATS] Dataset statistics:")
    print(f"  - Total rows: {len(df)}")
    print(f"  - Columns: {list(df.columns)}")
    print(f"  - Column 1: {df.columns[0]} (samples: {df.iloc[0][0][:50]}...)")
    print(f"  - Column 2: {df.columns[1]} (samples: {df.iloc[0][1][:50]}...)")
    
except Exception as e:
    print(f"[ERROR] Failed to load dataset: {e}")
    print(f"[INFO] Error type: {type(e).__name__}")
    print(f"\n[HELP] Make sure you have:")
    print(f"  1. datasets library installed: pip install datasets")
    print(f"  2. Access to Kabale dataset approved at:")
    print(f"     https://huggingface.co/datasets/kambale/luganda-english-parallel-corpus")
    print(f"  3. HuggingFace token set (if needed):")
    print(f"     huggingface-cli login")
