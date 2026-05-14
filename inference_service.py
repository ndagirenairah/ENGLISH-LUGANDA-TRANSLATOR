#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STEP 8 & 11: UNIFIED TRANSLATION INFERENCE SERVICE
===================================================
Clean, modular inference service combining:
- Translation model (NLLB-200)
- Speech Recognition (Whisper ASR)
- Text-to-Speech (Coqui XTTS)

Provides high-level API for:
- Text translation (English ↔ Luganda)
- Voice translation (audio input → translation → audio output)
- Language detection
- Confidence scoring
- Comprehensive logging

This is the production inference pipeline.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Tuple, Dict
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class TranslationInference:
    """
    Production inference service for translation.
    """
    
    # NLLB-200 language codes
    LANGUAGE_CODES = {
        'english': 'eng_Latn',
        'luganda': 'lug_Latn',
    }
    
    def __init__(self, model_path: str, device: Optional[str] = None):
        """
        Initialize inference service.
        
        Args:
            model_path: Path to trained model (NLLB-200)
            device: Device to use (auto-detect if None)
        """
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_path = model_path
        
        logger.info("=" * 80)
        logger.info("[INFERENCE] Initializing Translation Service")
        logger.info("=" * 80)
        logger.info(f"[INFERENCE] Model: {model_path}")
        logger.info(f"[INFERENCE] Device: {self.device.upper()}")
        
        # Load model and tokenizer
        logger.info("\n[LOAD] Loading model...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=False)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
        self.model.to(self.device)
        self.model.eval()
        
        logger.info(f"[LOAD] Model parameters: {self.model.num_parameters():,}")
    
    def detect_language(self, text: str) -> Tuple[str, float]:
        """
        Detect if text is English or Luganda.
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (language, confidence)
        """
        if not text or len(text.strip()) == 0:
            return 'unknown', 0.0
        
        # Heuristic: ASCII ratio
        ascii_count = sum(1 for c in text if ord(c) < 128)
        ascii_ratio = ascii_count / len(text) if text else 0
        
        # Language keywords
        english_keywords = {'the', 'is', 'and', 'to', 'of', 'a', 'in', 'that', 'it'}
        luganda_keywords = {'oli', 'nkwagala', 'webale', 'ndye', 'ekikali', 'baganda'}
        
        text_lower = text.lower()
        en_hits = sum(1 for w in english_keywords if w in text_lower)
        lg_hits = sum(1 for w in luganda_keywords if w in text_lower)
        
        # Decision logic
        if lg_hits > en_hits and lg_hits > 0:
            return 'luganda', min(0.99, (lg_hits + 0.1) / 5)
        elif ascii_ratio > 0.85:
            return 'english', min(0.99, ascii_ratio)
        elif en_hits > 0:
            return 'english', 0.7
        else:
            return 'unknown', 0.5
    
    def translate(self, text: str,
                  source_lang: Optional[str] = None,
                  target_lang: Optional[str] = None,
                  max_length: int = 256,
                  num_beams: int = 4) -> Tuple[str, float]:
        """
        Translate text from source to target language.
        
        Args:
            text: Text to translate
            source_lang: Source language ('english' or 'luganda', auto-detect if None)
            target_lang: Target language (auto-inferred if None)
            max_length: Maximum output length
            num_beams: Number of beams for beam search
            
        Returns:
            Tuple of (translation, confidence)
        """
        text = text.strip()
        if not text:
            logger.warning("[WARN] Empty text provided")
            return "", 0.0
        
        # Auto-detect source language
        if source_lang is None:
            detected, _ = self.detect_language(text)
            source_lang = detected
        
        # Normalize language names
        source_lang = source_lang.lower()
        if source_lang not in self.LANGUAGE_CODES:
            logger.warning(f"[WARN] Unknown language: {source_lang}, defaulting to English")
            source_lang = 'english'
        
        # Infer target language
        if target_lang is None:
            target_lang = 'luganda' if source_lang == 'english' else 'english'
        
        target_lang = target_lang.lower()
        if target_lang not in self.LANGUAGE_CODES:
            logger.warning(f"[WARN] Unknown language: {target_lang}, defaulting to Luganda")
            target_lang = 'luganda'
        
        logger.info(f"\n[TRANSLATE] {source_lang.upper()} → {target_lang.upper()}")
        logger.info(f"[TRANSLATE] Input: {text[:80]}...")
        
        try:
            with torch.no_grad():
                # Set target language token
                self.tokenizer.tgt_lang = self.LANGUAGE_CODES[target_lang]
                
                # Tokenize
                inputs = self.tokenizer(
                    text,
                    max_length=max_length,
                    truncation=True,
                    padding=True,
                    return_tensors='pt'
                ).to(self.device)
                
                # Generate
                output_ids = self.model.generate(
                    **inputs,
                    max_length=max_length,
                    num_beams=num_beams,
                    early_stopping=True,
                    length_penalty=1.0,
                    no_repeat_ngram_size=3
                )
                
                # Decode
                translation = self.tokenizer.decode(
                    output_ids[0],
                    skip_special_tokens=True
                ).strip()
                
                # Confidence (log probability based)
                with torch.no_grad():
                    outputs = self.model(**inputs, labels=inputs['input_ids'])
                    logits = outputs.logits
                    log_probs = torch.log_softmax(logits, dim=-1)
                    avg_log_prob = log_probs.max(dim=-1)[0].mean().item()
                    confidence = max(0, min(1.0, (avg_log_prob + 10) / 20))
                
                logger.info(f"[RESULT] Translation: {translation[:80]}...")
                logger.info(f"[RESULT] Confidence: {confidence:.2%}")
                
                return translation, confidence
            
        except Exception as e:
            logger.error(f"[ERROR] Translation failed: {e}")
            return "", 0.0
    
    def translate_batch(self, texts: list,
                       source_lang: Optional[str] = None,
                       target_lang: Optional[str] = None,
                       batch_size: int = 8) -> list:
        """
        Translate multiple texts.
        
        Args:
            texts: List of texts to translate
            source_lang: Source language
            target_lang: Target language
            batch_size: Batch size for inference
            
        Returns:
            List of translations
        """
        translations = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            
            for text in batch:
                translation, _ = self.translate(
                    text,
                    source_lang=source_lang,
                    target_lang=target_lang
                )
                translations.append(translation)
        
        return translations
    
    def get_language_pair(self, text: str) -> Tuple[str, str]:
        """
        Get source and target languages.
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (source_lang, target_lang)
        """
        source_lang, _ = self.detect_language(text)
        target_lang = 'luganda' if source_lang == 'english' else 'english'
        
        return source_lang, target_lang


class UnifiedTranslationPipeline:
    """
    End-to-end voice translation pipeline (ASR → Translation → TTS).
    """
    
    def __init__(self, model_path: str,
                 use_asr: bool = True,
                 use_tts: bool = True):
        """
        Initialize unified pipeline.
        
        Args:
            model_path: Path to translation model
            use_asr: Whether to use Whisper ASR
            use_tts: Whether to use Coqui XTTS
        """
        logger.info("=" * 80)
        logger.info("[PIPELINE] Initializing Unified Translation Pipeline")
        logger.info("=" * 80)
        
        # Translation
        self.translator = TranslationInference(model_path)
        
        # ASR (optional)
        self.asr = None
        if use_asr:
            try:
                from asr_pipeline import WhisperASR
                self.asr = WhisperASR(model_size='medium')
                logger.info("[ASR] Whisper ASR loaded")
            except Exception as e:
                logger.warning(f"[WARN] ASR not available: {e}")
        
        # TTS (optional)
        self.tts = None
        if use_tts:
            try:
                from tts_pipeline import create_tts_pipeline
                self.tts = create_tts_pipeline('coqui')
                logger.info("[TTS] Coqui XTTS loaded")
            except Exception as e:
                logger.warning(f"[WARN] TTS not available: {e}")
                try:
                    self.tts = create_tts_pipeline('google')
                    logger.info("[TTS] Google TTS (fallback) loaded")
                except:
                    logger.warning("[WARN] TTS not available")
    
    def translate_text(self, text: str) -> Tuple[str, float]:
        """Translate text."""
        return self.translator.translate(text)
    
    def translate_audio(self, audio_path: str) -> Tuple[str, str, float]:
        """
        Translate audio file (ASR → Translation).
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Tuple of (asr_text, translation, confidence)
        """
        if not self.asr:
            raise RuntimeError("ASR not available")
        
        # ASR
        logger.info(f"\n[PIPELINE] Audio → ASR → Translation")
        asr_text, asr_conf = self.asr.transcribe_file(audio_path)
        logger.info(f"[ASR] Recognized: {asr_text}")
        
        # Translation
        translation, trans_conf = self.translator.translate(asr_text)
        
        confidence = (asr_conf + trans_conf) / 2
        
        return asr_text, translation, confidence
    
    def synthesize_audio(self, text: str, language: str = 'english') -> bytes:
        """
        Synthesize speech from text (TTS).
        
        Args:
            text: Text to synthesize
            language: Language code
            
        Returns:
            Audio bytes
        """
        if not self.tts:
            raise RuntimeError("TTS not available")
        
        return self.tts.synthesize(text, language=language)


def load_inference_service(model_path: str) -> TranslationInference:
    """
    Load inference service.
    
    Args:
        model_path: Path to trained model
        
    Returns:
        TranslationInference instance
    """
    return TranslationInference(model_path)


if __name__ == '__main__':
    # Example usage
    
    # Simple text translation
    model_path = 'models/nllb_trained'
    
    if not Path(model_path).exists():
        logger.error(f"Model not found: {model_path}")
        sys.exit(1)
    
    translator = load_inference_service(model_path)
    
    # Test translation
    texts = [
        "Hello, how are you?",
        "What is your name?",
        "I love learning languages"
    ]
    
    logger.info("\n[TEST] Testing translation service")
    
    for text in texts:
        translation, confidence = translator.translate(text)
        logger.info(f"\nInput:  {text}")
        logger.info(f"Output: {translation}")
        logger.info(f"Confidence: {confidence:.2%}")
    
    logger.info("\n[SUCCESS] Inference service working!")
