# ============================================================================
# DATA QUALITY FILTERING FOR LUGANDA TRANSLATION DATASET
# ============================================================================
# Removes noisy/broken Luganda sentences
# Keeps only clean, grammatically correct data
# ============================================================================

import pandas as pd
import re

class LugandaDataCleaner:
    """
    Cleans and filters Luganda translation datasets
    Removes broken/noisy sentences
    Keeps only high-quality Luganda text
    """
    
    def __init__(self):
        """Initialize cleaning rules"""
        
        # BAD PATTERNS (indicate broken/noisy data)
        self.bad_patterns = [
            r"ere gye",          # broken construction
            r"werebwamu",        # incomplete word
            r"gye were",         # malformed
            r"xxxx",             # placeholder
            r"xxx",              # placeholder
            r"\d{5,}",           # long numbers
            r"[^a-zA-Z\s']",     # unwanted characters
        ]
        
        # GOOD PATTERNS (indicate clean data)
        self.good_starters = [
            "ndi", "oli", "twali", "bali",  # verbs
            "webale", "ssebo", "nnyabo",    # common phrases
            "kabaka", "omukulu", "abantu",  # nouns
            "nkekkaanya", "okusoma",        # verbs
            "eggwanga", "buganda",          # places
        ]
        
        print("✅ Luganda Data Cleaner initialized")
    
    def is_valid_length(self, text, min_words=2, max_words=25):
        """Check if sentence length is reasonable"""
        if not isinstance(text, str):
            return False
        
        word_count = len(text.split())
        return min_words <= word_count <= max_words
    
    def has_bad_patterns(self, text):
        """Check if text contains broken/noisy patterns"""
        if not isinstance(text, str):
            return True
        
        text_lower = text.lower()
        
        for pattern in self.bad_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def is_mostly_lowercase(self, text):
        """Luganda is typically lowercase - check for sanity"""
        if not isinstance(text, str):
            return False
        
        # Remove common proper nouns that should be capitalized
        proper_nouns = ["kabaka", "buganda", "luganda", "uganda"]
        temp_text = text.lower()
        
        # Check if mostly lowercase (with some exceptions)
        uppercase_count = sum(1 for c in text if c.isupper())
        total_letters = sum(1 for c in text if c.isalpha())
        
        # Allow up to 20% uppercase (for proper nouns)
        if total_letters > 0:
            uppercase_ratio = uppercase_count / total_letters
            return uppercase_ratio < 0.3  # Allow some uppercase
        
        return True
    
    def is_repetitive(self, text, max_repetition=2):
        """Remove sentences with excessive word repetition"""
        if not isinstance(text, str):
            return False
        
        words = text.split()
        unique_words = set(words)
        
        # If too many repeated words, it's probably broken
        if len(unique_words) < len(words) * 0.5:
            return True
        
        return False
    
    def has_reasonable_vowels(self, text):
        """Luganda has lots of vowels - check for this"""
        if not isinstance(text, str):
            return False
        
        vowels = "aeiouAEIOU"
        vowel_count = sum(1 for c in text if c in vowels)
        total_letters = sum(1 for c in text if c.isalpha())
        
        if total_letters > 0:
            vowel_ratio = vowel_count / total_letters
            # Luganda typically has 40-60% vowels
            return 0.3 < vowel_ratio < 0.8
        
        return True
    
    def is_clean_luganda(self, text, verbose=False):
        """
        Comprehensive check - is this clean Luganda?
        
        Args:
            text: Luganda sentence to check
            verbose: Print why if rejected
        
        Returns:
            bool: True if clean, False if noisy
        """
        
        # Check 1: Valid length
        if not self.is_valid_length(text):
            if verbose:
                print(f"  ❌ Length: {text}")
            return False
        
        # Check 2: No bad patterns
        if self.has_bad_patterns(text):
            if verbose:
                print(f"  ❌ Bad pattern: {text}")
            return False
        
        # Check 3: Not excessively repetitive
        if self.is_repetitive(text):
            if verbose:
                print(f"  ❌ Repetitive: {text}")
            return False
        
        # Check 4: Reasonable case sensitivity
        if not self.is_mostly_lowercase(text):
            if verbose:
                print(f"  ❌ Case issue: {text}")
            return False
        
        # Check 5: Reasonable vowel ratio
        if not self.has_reasonable_vowels(text):
            if verbose:
                print(f"  ❌ Vowel ratio: {text}")
            return False
        
        return True
    
    def clean_dataset(self, df, luganda_column="luganda", verbose=False):
        """
        Clean entire dataset
        
        Args:
            df: DataFrame with Luganda sentences
            luganda_column: Name of column with Luganda text
            verbose: Print removed sentences
        
        Returns:
            DataFrame: Cleaned dataset
        """
        
        print(f"\n{'='*70}")
        print(f"CLEANING DATASET")
        print(f"{'='*70}")
        
        original_count = len(df)
        print(f"\n📊 Starting with: {original_count} sentences")
        
        # Apply cleaner
        mask = df[luganda_column].apply(
            lambda x: self.is_clean_luganda(x, verbose=verbose)
        )
        
        df_clean = df[mask].copy()
        
        removed_count = original_count - len(df_clean)
        kept_count = len(df_clean)
        
        print(f"\n✅ Results:")
        print(f"   - Kept: {kept_count} sentences ({kept_count/original_count*100:.1f}%)")
        print(f"   - Removed: {removed_count} sentences ({removed_count/original_count*100:.1f}%)")
        print(f"   - Quality: {kept_count/original_count*100:.1f}% → 100%")
        
        return df_clean
    
    def get_statistics(self, df, luganda_column="luganda"):
        """Get dataset statistics"""
        
        print(f"\n{'='*70}")
        print(f"DATASET STATISTICS")
        print(f"{'='*70}\n")
        
        avg_length = df[luganda_column].str.split().str.len().mean()
        min_length = df[luganda_column].str.split().str.len().min()
        max_length = df[luganda_column].str.split().str.len().max()
        
        print(f"📊 Sentence Length:")
        print(f"   - Average: {avg_length:.1f} words")
        print(f"   - Min: {min_length} words")
        print(f"   - Max: {max_length} words")
        
        # Duplicate check
        duplicates = df[luganda_column].duplicated().sum()
        print(f"\n🔄 Duplicates:")
        print(f"   - Found: {duplicates} duplicates")
        
        if duplicates > 0:
            print(f"   - Unique: {len(df) - duplicates} unique sentences")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    
    print("=" * 70)
    print("LUGANDA DATASET QUALITY FILTERING")
    print("=" * 70)
    
    # Initialize cleaner
    cleaner = LugandaDataCleaner()
    
    # ========================================================================
    # TEST WITH EXAMPLES
    # ========================================================================
    
    print("\n" + "=" * 70)
    print("TESTING WITH EXAMPLES")
    print("=" * 70)
    
    test_sentences = {
        "✅ GOOD": [
            "Ndi Muganda",
            "Webale nnyo",
            "Kabaka yalambula abantu",
            "Ssegeza abakulu",
            "Nkekkaanya Oluganda",
        ],
        "❌ BAD": [
            "ere gye werebwamu",     # broken pattern
            "xxxx",                  # placeholder
            "a b c",                 # too short/weird
            "word word word word word word word word word word word",  # too long
            "AAAAAAA BBBBBBB",       # weird pattern
        ]
    }
    
    for category, sentences in test_sentences.items():
        print(f"\n{category} Examples:")
        for sent in sentences:
            result = cleaner.is_clean_luganda(sent)
            status = "✅" if (("✅" in category and result) or ("❌" in category and not result)) else "⚠️"
            print(f"  {status} {sent}: {result}")
    
    # ========================================================================
    # CLEAN REAL DATASET (if available)
    # ========================================================================
    
    print("\n" + "=" * 70)
    print("CLEANING REAL DATASET")
    print("=" * 70)
    
    try:
        # Try to load your dataset
        df = pd.read_csv("data/luganda_english_dataset_combined.csv")
        print(f"\n✅ Loaded: data/luganda_english_dataset_combined.csv")
        
        # Get statistics before
        print("\n📊 BEFORE CLEANING:")
        cleaner.get_statistics(df, luganda_column="luganda")
        
        # Clean dataset
        df_clean = cleaner.clean_dataset(df, luganda_column="luganda", verbose=False)
        
        # Get statistics after
        print("\n📊 AFTER CLEANING:")
        cleaner.get_statistics(df_clean, luganda_column="luganda")
        
        # Remove duplicates
        print(f"\n🔄 Removing duplicates...")
        df_clean = df_clean.drop_duplicates(subset=["luganda"])
        print(f"   ✅ Final count: {len(df_clean)} unique sentences")
        
        # Save cleaned dataset
        output_path = "data/luganda_english_dataset_cleaned.csv"
        df_clean.to_csv(output_path, index=False)
        print(f"\n✅ Cleaned dataset saved to: {output_path}")
        
        # Show samples
        print(f"\n📝 Sample of cleaned data:")
        print("-" * 70)
        for idx, row in df_clean.head(5).iterrows():
            print(f"  LG: {row['luganda']}")
            print(f"  EN: {row['english']}")
            print()
        
    except FileNotFoundError:
        print("\n⚠️  Dataset not found. Using example data only.")
    
    print("\n" + "=" * 70)
    print("✨ QUALITY FILTERING COMPLETE")
    print("=" * 70 + "\n")
