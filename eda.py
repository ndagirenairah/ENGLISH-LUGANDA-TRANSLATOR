"""
STAGE 3: EXPLORATORY DATA ANALYSIS (EDA)
========================================
Analyzes dataset characteristics, vocabulary, and text patterns.
Generates visualizations and statistical reports.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns

class EDA:
    """
    Exploratory Data Analysis for English-Luganda parallel corpus.
    """
    
    def __init__(self, df):
        self.df = df
        self.report = {}
        self.figures_dir = Path("reports/figures")
        self.figures_dir.mkdir(parents=True, exist_ok=True)
    
    def analyze_sentence_lengths(self):
        """Analyze sentence length distributions."""
        print("\n[EDA] Analyzing sentence lengths...")
        
        self.df['english_words'] = self.df['english'].str.split().str.len()
        self.df['luganda_words'] = self.df['luganda'].str.split().str.len()
        
        en_stats = {
            'min': self.df['english_words'].min(),
            'max': self.df['english_words'].max(),
            'mean': self.df['english_words'].mean(),
            'median': self.df['english_words'].median(),
            'std': self.df['english_words'].std()
        }
        
        lg_stats = {
            'min': self.df['luganda_words'].min(),
            'max': self.df['luganda_words'].max(),
            'mean': self.df['luganda_words'].mean(),
            'median': self.df['luganda_words'].median(),
            'std': self.df['luganda_words'].std()
        }
        
        print(f"  English: {en_stats['min']:.0f}-{en_stats['max']:.0f} words, "
              f"avg: {en_stats['mean']:.1f}, median: {en_stats['median']:.0f}")
        print(f"  Luganda: {lg_stats['min']:.0f}-{lg_stats['max']:.0f} words, "
              f"avg: {lg_stats['mean']:.1f}, median: {lg_stats['median']:.0f}")
        
        self.report['sentence_length'] = {'english': en_stats, 'luganda': lg_stats}
        
        # Plot
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        axes[0].hist(self.df['english_words'], bins=50, edgecolor='black', alpha=0.7)
        axes[0].set_title('English Sentence Lengths')
        axes[0].set_xlabel('Number of Words')
        axes[0].set_ylabel('Frequency')
        
        axes[1].hist(self.df['luganda_words'], bins=50, edgecolor='black', alpha=0.7, color='orange')
        axes[1].set_title('Luganda Sentence Lengths')
        axes[1].set_xlabel('Number of Words')
        axes[1].set_ylabel('Frequency')
        
        plt.tight_layout()
        plt.savefig(self.figures_dir / 'sentence_lengths.png', dpi=100)
        print("  ✓ Saved: sentence_lengths.png")
        plt.close()
    
    def analyze_vocabulary(self):
        """Analyze vocabulary size and frequency."""
        print("\n[EDA] Analyzing vocabulary...")
        
        # English vocabulary
        en_words = ' '.join(self.df['english']).lower().split()
        en_vocab = Counter(en_words)
        en_unique = len(en_vocab)
        
        # Luganda vocabulary
        lg_words = ' '.join(self.df['luganda']).lower().split()
        lg_vocab = Counter(lg_words)
        lg_unique = len(lg_vocab)
        
        print(f"  English vocabulary: {en_unique:,} unique words ({len(en_words):,} total)")
        print(f"  Luganda vocabulary: {lg_unique:,} unique words ({len(lg_words):,} total)")
        
        # Top words
        en_top = en_vocab.most_common(10)
        lg_top = lg_vocab.most_common(10)
        
        print(f"\n  Top 10 English words: {', '.join([w[0] for w in en_top])}")
        print(f"  Top 10 Luganda words: {', '.join([w[0] for w in lg_top])}")
        
        self.report['vocabulary'] = {
            'english_unique': en_unique,
            'luganda_unique': lg_unique,
            'english_total': len(en_words),
            'luganda_total': len(lg_words),
            'english_top10': en_top,
            'luganda_top10': lg_top
        }
        
        # Plot word frequencies
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        words, freqs = zip(*en_top)
        axes[0].barh(words, freqs, color='skyblue')
        axes[0].set_title('Top 10 English Words')
        axes[0].set_xlabel('Frequency')
        
        words, freqs = zip(*lg_top)
        axes[1].barh(words, freqs, color='salmon')
        axes[1].set_title('Top 10 Luganda Words')
        axes[1].set_xlabel('Frequency')
        
        plt.tight_layout()
        plt.savefig(self.figures_dir / 'vocabulary_frequency.png', dpi=100)
        print("  ✓ Saved: vocabulary_frequency.png")
        plt.close()
    
    def analyze_missing_values(self):
        """Check for missing and empty values."""
        print("\n[EDA] Checking for missing values...")
        
        missing = self.df.isnull().sum()
        empty_en = (self.df['english'].str.strip() == '').sum()
        empty_lg = (self.df['luganda'].str.strip() == '').sum()
        
        print(f"  Null values: English={missing['english']}, Luganda={missing['luganda']}")
        print(f"  Empty strings: English={empty_en}, Luganda={empty_lg}")
        
        self.report['missing_values'] = {
            'null_english': int(missing['english']),
            'null_luganda': int(missing['luganda']),
            'empty_english': int(empty_en),
            'empty_luganda': int(empty_lg)
        }
    
    def analyze_duplicates(self):
        """Detect duplicate translations."""
        print("\n[EDA] Checking for duplicates...")
        
        dup_pairs = self.df.duplicated(subset=['english', 'luganda']).sum()
        dup_english = self.df.duplicated(subset=['english'], keep=False).sum()
        dup_luganda = self.df.duplicated(subset=['luganda'], keep=False).sum()
        
        print(f"  Duplicate pairs: {dup_pairs}")
        print(f"  Duplicate English sentences: {dup_english}")
        print(f"  Duplicate Luganda sentences: {dup_luganda}")
        
        self.report['duplicates'] = {
            'duplicate_pairs': int(dup_pairs),
            'duplicate_english': int(dup_english),
            'duplicate_luganda': int(dup_luganda)
        }
    
    def analyze_data_quality(self):
        """Overall data quality assessment."""
        print("\n[EDA] Overall data quality...")
        
        quality_score = 100
        issues = []
        
        # Check sentence length balance
        en_len = self.df['english_words'].mean()
        lg_len = self.df['luganda_words'].mean()
        
        if abs(en_len - lg_len) / max(en_len, lg_len) > 0.3:
            quality_score -= 5
            issues.append(f"Length imbalance: EN avg={en_len:.1f}, LG avg={lg_len:.1f}")
        
        # Check vocabulary coverage
        if self.report.get('vocabulary', {}).get('english_unique', 0) < 5000:
            quality_score -= 10
            issues.append("Small English vocabulary")
        
        if self.report.get('vocabulary', {}).get('luganda_unique', 0) < 5000:
            quality_score -= 10
            issues.append("Small Luganda vocabulary")
        
        print(f"  Quality Score: {quality_score}/100")
        if issues:
            for issue in issues:
                print(f"    ⚠ {issue}")
        else:
            print(f"    ✓ No major issues detected")
        
        self.report['data_quality'] = {
            'score': quality_score,
            'issues': issues
        }
    
    def generate_report(self):
        """Generate complete EDA report."""
        print("\n" + "=" * 80)
        print("STAGE 3: EXPLORATORY DATA ANALYSIS (EDA)")
        print("=" * 80)
        
        self.analyze_sentence_lengths()
        self.analyze_vocabulary()
        self.analyze_missing_values()
        self.analyze_duplicates()
        self.analyze_data_quality()
        
        print("\n" + "=" * 80)
        print("EDA COMPLETE")
        print("=" * 80)
        
        return self.report
    
    def save_report(self, filepath="reports/eda_report.json"):
        """Save EDA report as JSON."""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        def to_json_safe(value):
            """Recursively convert numpy types to JSON-serializable values."""
            if isinstance(value, dict):
                return {key: to_json_safe(item) for key, item in value.items()}
            if isinstance(value, list):
                return [to_json_safe(item) for item in value]
            if isinstance(value, tuple):
                return [to_json_safe(item) for item in value]
            if isinstance(value, (np.integer, np.floating)):
                return value.item()
            if isinstance(value, np.ndarray):
                return value.tolist()
            return value

        report_clean = to_json_safe(self.report)
        
        with open(filepath, 'w') as f:
            json.dump(report_clean, f, indent=2)
        
        print(f"\n✓ EDA report saved to: {filepath}")


def perform_eda(df):
    """
    Main EDA pipeline.
    
    Args:
        df (pd.DataFrame): Dataset with 'english' and 'luganda' columns
        
    Returns:
        dict: EDA report
    """
    eda = EDA(df)
    report = eda.generate_report()
    eda.save_report()
    return report


if __name__ == "__main__":
    # Load example dataset
    try:
        df = pd.read_csv("data/train_dataset.csv")
        perform_eda(df)
    except FileNotFoundError:
        print("Dataset not found. Run data_collection.py first.")
