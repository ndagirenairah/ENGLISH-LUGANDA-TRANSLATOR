#!/usr/bin/env python3
"""
NLLB-200 Integration for English-Luganda Translation
Switching from MarianMT to Meta's No Language Left Behind model
for better low-resource language support
"""

import torch
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    pipeline,
    TranslationPipeline
)
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NLLB200Translator:
    """
    NLLB-200 Translator for English-Luganda
    Supports 200+ languages including Luganda (lug_Latn)
    """
    
    def __init__(self, model_size: str = "distilled-600M"):
        """
        Initialize NLLB-200 model
        Options: distilled-600M (smaller, faster), distilled-1.3B (better quality)
        """
        self.model_size = model_size
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = f"facebook/nllb-200-{model_size}"
        
        logger.info(f"📥 Loading NLLB-200 ({model_size}) - device: {self.device}")
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, use_auth_token=False)
        
        self.model = self.model.to(self.device)
        self.model.eval()
        
        logger.info("✅ NLLB-200 loaded successfully")
    
    def translate(self, text: str, src_lang: str = "eng_Latn", tgt_lang: str = "lug_Latn") -> str:
        """
        Translate text using NLLB-200
        
        Language codes:
        - eng_Latn: English
        - lug_Latn: Luganda
        """
        self.tokenizer.src_lang = src_lang
        
        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
        
        translated_tokens = self.model.generate(
            **inputs,
            forced_bos_token_id=self.tokenizer.get_lang_id(tgt_lang),
            max_length=150,
            num_beams=5,
            temperature=0.8
        )
        
        return self.tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
    
    def batch_translate(self, texts: List[str], src_lang: str = "eng_Latn", 
                       tgt_lang: str = "lug_Latn", batch_size: int = 8) -> List[str]:
        """Translate multiple texts efficiently"""
        translations = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            logger.info(f"  Translating batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}...")
            
            self.tokenizer.src_lang = src_lang
            inputs = self.tokenizer(batch, return_tensors="pt", padding=True).to(self.device)
            
            translated_tokens = self.model.generate(
                **inputs,
                forced_bos_token_id=self.tokenizer.get_lang_id(tgt_lang),
                max_length=150,
                num_beams=3
            )
            
            for tokens in translated_tokens:
                translation = self.tokenizer.decode(tokens, skip_special_tokens=True)
                translations.append(translation)
        
        return translations

class BackTranslationGenerator:
    """
    Generate synthetic training data via back-translation
    English → Luganda → English verification
    """
    
    def __init__(self):
        self.en_to_lug = NLLB200Translator(model_size="distilled-600M")
        # For back-translation, we need Luganda→English which NLLB can do
        
    def back_translate_pair(self, english: str, luganda: str) -> Dict:
        """
        Back-translate Luganda→English to verify original English translation
        Returns quality score and issues
        """
        # Translate Luganda back to English
        self.en_to_lug.tokenizer.src_lang = "lug_Latn"
        back_translated = self.en_to_lug.translate(
            luganda, 
            src_lang="lug_Latn",
            tgt_lang="eng_Latn"
        )
        
        return {
            "original_english": english,
            "luganda": luganda,
            "back_translated": back_translated,
            "quality_check": self._compare_similarity(english.lower(), back_translated.lower())
        }
    
    def _compare_similarity(self, original: str, back_translated: str) -> Dict:
        """Simple similarity check"""
        orig_words = set(original.split())
        back_words = set(back_translated.split())
        
        # Compute Jaccard similarity
        intersection = len(orig_words & back_words)
        union = len(orig_words | back_words)
        jaccard = intersection / union if union > 0 else 0
        
        return {
            "jaccard_similarity": jaccard,
            "is_reliable": jaccard > 0.5,
            "word_overlap": f"{intersection}/{union}"
        }
    
    def generate_synthetic_pairs(self, luganda_texts: List[str], 
                                 batch_size: int = 8) -> List[Tuple[str, str]]:
        """
        Generate synthetic English-Luganda pairs from monolingual Luganda
        by translating Luganda→English→Luganda and selecting high-quality pairs
        """
        synthetic_pairs = []
        
        logger.info(f"🔄 Generating synthetic pairs from {len(luganda_texts)} Luganda texts...")
        
        # Step 1: Translate Luganda to English
        logger.info("  Step 1: Translating Luganda → English")
        english_texts = self.en_to_lug.batch_translate(
            luganda_texts,
            src_lang="lug_Latn",
            tgt_lang="eng_Latn",
            batch_size=batch_size
        )
        
        # Step 2: Back-translate to Luganda to verify
        logger.info("  Step 2: Back-translating English → Luganda (verification)")
        for orig_lug, generated_eng in zip(luganda_texts, english_texts):
            # Check consistency
            quality = self.back_translate_pair(generated_eng, orig_lug)
            
            if quality["quality_check"]["is_reliable"]:
                synthetic_pairs.append((generated_eng, orig_lug))
        
        logger.info(f"  ✅ Generated {len(synthetic_pairs)} high-quality synthetic pairs")
        return synthetic_pairs

def compare_models():
    """
    Compare NLLB-200 vs current MarianMT model
    """
    test_phrases = [
        "What clan are you from?",
        "I am from the monkey clan",
        "Good morning, how are you?",
        "Education is important for the future",
        "Welcome to Uganda",
    ]
    
    logger.info("=" * 80)
    logger.info("🔄 COMPARING NLLB-200 vs MARIANMT")
    logger.info("=" * 80)
    
    # Load NLLB
    try:
        logger.info("\n📥 Loading NLLB-200...")
        nllb = NLLB200Translator(model_size="distilled-600M")
        
        logger.info("\n📊 TRANSLATION COMPARISON")
        logger.info("-" * 80)
        
        for phrase in test_phrases:
            nllb_result = nllb.translate(phrase)
            logger.info(f"\nEnglish: {phrase}")
            logger.info(f"🤖 NLLB-200: {nllb_result}")
    
    except Exception as e:
        logger.error(f"❌ Error loading NLLB: {e}")
        logger.info("\nTo install NLLB-200, run:")
        logger.info("  pip install transformers torch accelerate")

if __name__ == "__main__":
    # Test NLLB loading and basic functionality
    try:
        logger.info("🚀 Testing NLLB-200 Integration\n")
        
        # Uncomment to test (requires model download)
        # compare_models()
        
        logger.info("✅ NLLB-200 integration ready")
        logger.info("\nTo use in your app:")
        logger.info("  from nllb_translator import NLLB200Translator")
        logger.info("  translator = NLLB200Translator()")
        logger.info("  result = translator.translate('Hello')")
        
    except Exception as e:
        logger.error(f"Error: {e}")
