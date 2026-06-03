"""
Back-translation Data Augmentation for English-Luganda Translation
===================================================================
Generates synthetic training pairs by translating Luganda back to English,
then using the original English as targets. This improves model robustness.

Example:
  Original pair:  EN: "Hello" -> LU: "Nayo"
  Synthetic pair: EN: "Nayo" -> LU: "Translated back version"
"""

from pathlib import Path
import sys
import pandas as pd
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from tqdm import tqdm

try:
    from config import (
        BACK_TRANSLATION_MODEL, BACK_TRANSLATION_SAMPLES,
        BACK_TRANSLATION_BEAM_SIZE, DEVICE, OUTPUTS_DIR, AUGMENTED_DATA_FILE
    )
    from utils import print_section
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from config import (
        BACK_TRANSLATION_MODEL, BACK_TRANSLATION_SAMPLES,
        BACK_TRANSLATION_BEAM_SIZE, DEVICE, OUTPUTS_DIR, AUGMENTED_DATA_FILE
    )
    from utils import print_section


def generate_back_translations(model, tokenizer, luganda_texts, batch_size=32):
    """
    Generate English text from Luganda using back-translation model.
    
    Args:
        model: Pre-trained LU->EN model
        tokenizer: Tokenizer for the model
        luganda_texts: List of Luganda sentences
        batch_size: Processing batch size
        
    Returns:
        List of back-translated English texts
    """
    translations = []
    
    for i in tqdm(range(0, len(luganda_texts), batch_size), desc="Back-translating"):
        batch = luganda_texts[i:i+batch_size]
        
        inputs = tokenizer(
            batch,
            max_length=128,
            truncation=True,
            padding="max_length",
            return_tensors="pt"
        )
        
        inputs = {k: v.to(DEVICE) for k, v in inputs.items()}
        
        with torch.no_grad():
            output_ids = model.generate(
                inputs['input_ids'],
                attention_mask=inputs['attention_mask'],
                max_length=128,
                num_beams=BACK_TRANSLATION_BEAM_SIZE,
                early_stopping=True,
            )
        
        batch_translations = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
        translations.extend(batch_translations)
    
    return translations


def generate_augmented_data(train_df, num_samples=BACK_TRANSLATION_SAMPLES):
    """
    Generate synthetic data pairs via back-translation.
    
    Steps:
      1. Load LU->EN model
      2. Translate sample of Luganda -> English (back-translation)
      3. Create synthetic pairs: (back_translated_EN -> original_LU)
      4. Combine with original data
      
    Args:
        train_df: Training dataframe with 'english' and 'luganda' columns
        num_samples: Number of pairs to augment (default from config)
        
    Returns:
        Augmented dataframe with original + synthetic pairs
    """
    print_section("BACK-TRANSLATION DATA AUGMENTATION", width=80)
    
    # Sample pairs for back-translation
    sample_df = train_df.sample(n=min(num_samples, len(train_df)), random_state=42)
    print(f"\n📊 Selected {len(sample_df):,} pairs for back-translation")
    
    # Load back-translation model
    print(f"\n📂 Loading back-translation model: {BACK_TRANSLATION_MODEL}")
    try:
        bt_tokenizer = AutoTokenizer.from_pretrained(BACK_TRANSLATION_MODEL)
        bt_model = AutoModelForSeq2SeqLM.from_pretrained(BACK_TRANSLATION_MODEL)
        bt_model = bt_model.to(DEVICE)
    except Exception as e:
        print(f"⚠️  Back-translation model unavailable: {e}")
        print(f"   Using original data only")
        return train_df
    
    # Generate back-translations
    print(f"\n🔄 Generating back-translations (LU -> EN)...")
    luganda_texts = sample_df['luganda'].tolist()
    back_translated_en = generate_back_translations(bt_model, bt_tokenizer, luganda_texts)
    
    # Create synthetic dataset
    synthetic_df = pd.DataFrame({
        'english': back_translated_en,
        'luganda': sample_df['luganda'].tolist(),
    }).reset_index(drop=True)
    
    print(f"\n✅ Generated {len(synthetic_df):,} synthetic pairs via back-translation")
    
    # Combine original + synthetic
    augmented_df = pd.concat([train_df, synthetic_df], ignore_index=True)
    
    print(f"\n📈 Final augmented dataset:")
    print(f"   Original:  {len(train_df):,} pairs")
    print(f"   Synthetic: {len(synthetic_df):,} pairs")
    print(f"   Total:     {len(augmented_df):,} pairs")
    
    # Save augmented data
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    augmented_df.to_csv(AUGMENTED_DATA_FILE, index=False)
    print(f"\n💾 Saved to {AUGMENTED_DATA_FILE}")
    
    return augmented_df


def main():
    """Generate augmented dataset."""
    # Load original training data
    train_path = Path("data/processed/train.csv")
    if not train_path.exists():
        print(f"❌ Training data not found: {train_path}")
        return None
    
    train_df = pd.read_csv(train_path)
    print(f"\n📁 Loaded {len(train_df):,} original training pairs")
    
    # Generate augmented data
    augmented_df = generate_augmented_data(train_df, num_samples=BACK_TRANSLATION_SAMPLES)
    
    print_section("AUGMENTATION COMPLETE", width=80)
    print(f"\n✅ Augmented dataset ready for training!")
    print(f"   Use augmented data: pd.read_csv('{AUGMENTED_DATA_FILE}')")
    
    return augmented_df


if __name__ == "__main__":
    main()
