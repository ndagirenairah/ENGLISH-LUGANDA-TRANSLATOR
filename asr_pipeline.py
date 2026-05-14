#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STEP 9: PROFESSIONAL SPEECH RECOGNITION (ASR) MODULE
=====================================================
Implements robust speech recognition using OpenAI Whisper:
- Whisper medium/large model (state-of-the-art ASR)
- Multi-language support (handles Luganda and Ugandan English accents)
- Automatic language detection
- Post-processing and cleaning
- Confidence scoring
- Error handling and fallbacks

Whisper is superior to Google Speech Recognition for African accents and Luganda.
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
import torchaudio

# Whisper ASR
import whisper

# Fallback ASR
try:
    import speech_recognition as sr
except:
    sr = None

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


class WhisperASR:
    """
    Speech recognition using OpenAI Whisper.
    """
    
    # Whisper model sizes (larger = better quality, slower)
    MODEL_SIZES = ['tiny', 'base', 'small', 'medium', 'large']
    
    def __init__(self, model_size: str = 'medium', device: Optional[str] = None):
        """
        Initialize Whisper ASR.
        
        Args:
            model_size: Model size ('tiny', 'base', 'small', 'medium', 'large')
            device: Device to use (auto-detect if None)
        """
        if model_size not in self.MODEL_SIZES:
            raise ValueError(f"Model size must be one of {self.MODEL_SIZES}")
        
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_size = model_size
        
        logger.info("=" * 80)
        logger.info("[ASR] Initializing Whisper Speech Recognition")
        logger.info("=" * 80)
        logger.info(f"[ASR] Model size: {model_size}")
        logger.info(f"[ASR] Device: {self.device.upper()}")
        
        # Load model
        logger.info(f"\n[LOAD] Loading Whisper {model_size} model...")
        self.model = whisper.load_model(model_size, device=self.device)
        logger.info("[LOAD] Model loaded successfully")
    
    def transcribe_file(self, audio_path: str,
                       language: Optional[str] = None,
                       task: str = 'transcribe') -> Tuple[str, float]:
        """
        Transcribe audio file.
        
        Args:
            audio_path: Path to audio file
            language: Language code ('en', 'lg', None for auto-detect)
            task: 'transcribe' or 'translate'
            
        Returns:
            Tuple of (transcription, confidence)
        """
        if not Path(audio_path).exists():
            logger.error(f"[ERROR] Audio file not found: {audio_path}")
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        logger.info(f"\n[TRANSCRIBE] Processing: {audio_path}")
        logger.info(f"[TRANSCRIBE] Language: {language or 'auto-detect'}")
        
        try:
            # Map language codes
            lang_map = {
                'english': 'en',
                'luganda': 'lg',
                'en': 'en',
                'lg': 'lg',
                'ug': 'en',  # Uganda uses English
                None: None
            }
            lang_code = lang_map.get(language, language)
            
            # Transcribe
            result = self.model.transcribe(
                audio_path,
                language=lang_code,
                task=task,
                verbose=False,
                fp16=self.device == 'cuda'
            )
            
            text = result['text'].strip()
            
            # Confidence (average probability of segments)
            if 'segments' in result and result['segments']:
                confidences = [seg.get('confidence', 1.0) for seg in result['segments']]
                confidence = np.mean(confidences)
            else:
                confidence = result.get('confidence', 1.0)
            
            logger.info(f"[RESULT] Confidence: {confidence:.2%}")
            logger.info(f"[RESULT] Text: {text[:100]}...")
            
            return text, confidence
            
        except Exception as e:
            logger.error(f"[ERROR] Transcription failed: {e}")
            raise
    
    def transcribe_microphone(self, language: Optional[str] = None,
                             duration: int = 10,
                             task: str = 'transcribe') -> Tuple[str, float]:
        """
        Transcribe from microphone.
        
        Args:
            language: Language code
            duration: Maximum recording duration (seconds)
            task: 'transcribe' or 'translate'
            
        Returns:
            Tuple of (transcription, confidence)
        """
        logger.info(f"\n[RECORD] Recording from microphone ({duration}s max)...")
        
        try:
            import sounddevice as sd
            import soundfile as sf
            
            # Record audio
            logger.info("[RECORD] Please speak now...")
            audio = sd.rec(int(duration * 16000), samplerate=16000, channels=1)
            sd.wait()
            
            # Save temporarily
            temp_path = Path('temp_recording.wav')
            sf.write(temp_path, audio, 16000)
            
            # Transcribe
            text, confidence = self.transcribe_file(
                str(temp_path),
                language=language,
                task=task
            )
            
            # Clean up
            temp_path.unlink()
            
            return text, confidence
            
        except ImportError:
            logger.error("[ERROR] sounddevice or soundfile not installed")
            raise
        except Exception as e:
            logger.error(f"[ERROR] Microphone recording failed: {e}")
            raise
    
    def post_process(self, text: str, language: str = 'english') -> str:
        """
        Post-process transcription (capitalization, punctuation).
        
        Args:
            text: Transcribed text
            language: Language code
            
        Returns:
            Post-processed text
        """
        text = text.strip()
        
        # Capitalize first character
        if text:
            text = text[0].upper() + text[1:]
        
        # Add period if missing
        if text and text[-1] not in '.!?':
            text += '.'
        
        return text
    
    def detect_language_from_audio(self, audio_path: str) -> Tuple[str, float]:
        """
        Detect language from audio file.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Tuple of (language_code, confidence)
        """
        logger.info(f"\n[DETECT] Detecting language from: {audio_path}")
        
        # Load audio
        audio = whisper.load_audio(audio_path)
        audio = whisper.pad_or_trim(audio)
        
        # Detect language
        mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
        _, probs = self.model.detect_language(mel)
        
        # Get top language
        detected_lang = max(probs, key=probs.get)
        confidence = probs[detected_lang]
        
        logger.info(f"[DETECT] Language: {detected_lang} (confidence: {confidence:.2%})")
        
        return detected_lang, confidence


class GoogleSpeechRecognitionFallback:
    """
    Fallback speech recognition using Google (for compatibility).
    """
    
    def __init__(self):
        """Initialize fallback ASR."""
        if sr is None:
            raise ImportError("speech_recognition library not installed")
        
        logger.info("[ASR] Initializing Google Speech Recognition (fallback)")
        self.recognizer = sr.Recognizer()
    
    def transcribe_microphone(self, language: str = 'en',
                             timeout: int = 10) -> Tuple[str, float]:
        """
        Transcribe from microphone using Google.
        
        Args:
            language: Language code ('en', 'lg')
            timeout: Timeout in seconds
            
        Returns:
            Tuple of (transcription, confidence)
        """
        logger.info(f"[RECORD] Recording from microphone (Google) ({timeout}s max)...")
        
        try:
            with sr.Microphone() as source:
                logger.info("[RECORD] Please speak now...")
                audio = self.recognizer.listen(source, timeout=timeout)
            
            logger.info("[TRANSCRIBE] Sending to Google...")
            text = self.recognizer.recognize_google(audio, language=language)
            
            # Confidence not provided by Google API
            confidence = 0.7  # Default moderate confidence
            
            logger.info(f"[RESULT] Text: {text}")
            
            return text, confidence
            
        except sr.UnknownValueValue:
            logger.error("[ERROR] Could not understand speech")
            raise
        except sr.RequestError as e:
            logger.error(f"[ERROR] Google Speech Recognition error: {e}")
            raise
        except Exception as e:
            logger.error(f"[ERROR] Microphone error: {e}")
            raise


def create_asr_pipeline(asr_type: str = 'whisper',
                        model_size: str = 'medium') -> 'WhisperASR':
    """
    Create ASR pipeline.
    
    Args:
        asr_type: 'whisper' or 'google'
        model_size: Model size for Whisper
        
    Returns:
        ASR pipeline instance
    """
    if asr_type == 'whisper':
        return WhisperASR(model_size=model_size)
    elif asr_type == 'google':
        return GoogleSpeechRecognitionFallback()
    else:
        raise ValueError(f"Unknown ASR type: {asr_type}")


# Example usage
if __name__ == '__main__':
    # Initialize Whisper ASR
    asr = WhisperASR(model_size='medium')
    
    # Example: transcribe microphone
    try:
        text, confidence = asr.transcribe_microphone(language='en', duration=5)
        print(f"\nTranscription: {text}")
        print(f"Confidence: {confidence:.2%}")
    except KeyboardInterrupt:
        print("\nCancelled")
    except Exception as e:
        print(f"\nError: {e}")
