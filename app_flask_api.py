#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ENGLISH-LUGANDA TRANSLATOR - FLASK API
======================================
Production REST API for translation service.
"""

from flask import Flask, render_template, request, jsonify
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import logging
from datetime import datetime
import sqlite3
from pathlib import Path
from typing import Dict, Tuple, Optional
import json

# Initialize Flask app
app = Flask(__name__, template_folder='templates')
app.config['JSON_SORT_KEYS'] = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model variables
tokenizer = None
model = None
device = None
model_source = None


def load_model():
    """Load NLLB translation model."""
    global tokenizer, model, device, model_source
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Using device: {device}")
    
    # Try to load enhanced model first
    model_candidates = [
        "models/trained_nllb_enhanced/final",
        "models/trained_nllb_professional/best_model",
        "models/trained_model_final",
    ]
    
    for candidate in model_candidates:
        try:
            if Path(candidate).exists():
                logger.info(f"Loading model from: {candidate}")
                tokenizer = AutoTokenizer.from_pretrained(candidate)
                model = AutoModelForSeq2SeqLM.from_pretrained(candidate)
                model_source = candidate
                model.to(device)
                model.eval()
                return
        except Exception as e:
            logger.debug(f"Could not load from {candidate}: {e}")
            continue
    
    # Fallback to base NLLB model
    logger.info("Loading base NLLB model from HuggingFace...")
    tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")
    model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M")
    model_source = "facebook/nllb-200-distilled-600M"
    model.to(device)
    model.eval()


def detect_language(text: str) -> str:
    """Detect if text is English or Luganda."""
    if not text.strip():
        return "unknown"
    
    ascii_count = sum(1 for c in text if ord(c) < 128)
    ascii_ratio = ascii_count / len(text) if text else 0
    
    return "english" if ascii_ratio > 0.85 else "luganda"


def translate_text(
    text: str,
    source_lang: str,
    target_lang: str
) -> Tuple[str, float]:
    """Translate text using NLLB model."""
    
    if not text.strip():
        return "", 0.0
    
    try:
        # NLLB language codes
        lang_codes = {
            "english": "eng_Latn",
            "luganda": "lug_Latn"
        }
        
        src_code = lang_codes.get(source_lang.lower(), "eng_Latn")
        tgt_code = lang_codes.get(target_lang.lower(), "lug_Latn")
        
        with torch.no_grad():
            # Tokenize input
            inputs = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=256,
                padding=True
            ).to(device)
            
            # Generate translation
            outputs = model.generate(
                **inputs,
                forced_bos_token_id=tokenizer.convert_tokens_to_ids(tgt_code),
                max_length=256,
                num_beams=5,
                early_stopping=True,
                temperature=0.9
            )
            
            # Decode translation
            translation = tokenizer.decode(
                outputs[0],
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True
            )
            
            confidence = 0.85  # Default for NLLB
        
        return translation.strip(), confidence
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return f"Error: {str(e)}", 0.0


def init_database():
    """Initialize translation history database."""
    db_path = "translator_history.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS translations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            source_lang TEXT NOT NULL,
            source_text TEXT NOT NULL,
            target_text TEXT NOT NULL,
            confidence REAL
        )
    """)
    
    conn.commit()
    conn.close()


def save_translation(source_lang: str, source_text: str, target_text: str, confidence: float):
    """Save translation to database."""
    try:
        db_path = "translator_history.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO translations 
            (timestamp, source_lang, source_text, target_text, confidence)
            VALUES (?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            source_lang,
            source_text,
            target_text,
            confidence
        ))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        logger.error(f"Database error: {e}")


# Routes

@app.route('/', methods=['GET'])
def home():
    """Serve main HTML page."""
    return render_template('index.html')


@app.route('/api/status', methods=['GET'])
def status():
    """Get API status and system info."""
    return jsonify({
        "status": "running",
        "device": device,
        "model": model_source,
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/translate', methods=['POST'])
def translate():
    """Translate text via POST request."""
    try:
        data = request.get_json()
        
        # Validate input
        if not data or 'text' not in data:
            return jsonify({"error": "Missing 'text' field"}), 400
        
        text = data['text'].strip()
        if not text:
            return jsonify({"error": "Empty text"}), 400
        
        # Get source language (auto-detect if not provided)
        source_lang = data.get('source_lang', 'auto')
        if source_lang == 'auto':
            source_lang = detect_language(text)
        
        # Determine target language
        target_lang = "luganda" if source_lang == "english" else "english"
        
        # Translate
        translation, confidence = translate_text(text, source_lang, target_lang)
        
        # Save to history
        save_translation(source_lang, text, translation, confidence)
        
        # Return response
        return jsonify({
            "source_text": text,
            "target_text": translation,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/detect-language', methods=['POST'])
def detect():
    """Detect language of input text."""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({"error": "Missing 'text' field"}), 400
        
        text = data['text'].strip()
        language = detect_language(text)
        
        return jsonify({
            "text": text,
            "detected_language": language,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Detection error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/batch-translate', methods=['POST'])
def batch_translate():
    """Translate multiple texts in one request."""
    try:
        data = request.get_json()
        
        if not data or 'texts' not in data:
            return jsonify({"error": "Missing 'texts' field"}), 400
        
        texts = data['texts']
        if not isinstance(texts, list):
            return jsonify({"error": "'texts' must be a list"}), 400
        
        results = []
        for text in texts:
            if not text.strip():
                continue
            
            source_lang = detect_language(text)
            target_lang = "luganda" if source_lang == "english" else "english"
            translation, confidence = translate_text(text, source_lang, target_lang)
            
            save_translation(source_lang, text, translation, confidence)
            
            results.append({
                "source_text": text,
                "target_text": translation,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "confidence": confidence
            })
        
        return jsonify({
            "results": results,
            "count": len(results),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Batch translation error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/history', methods=['GET'])
def history():
    """Get translation history."""
    try:
        limit = request.args.get('limit', default=20, type=int)
        
        db_path = "translator_history.db"
        if not Path(db_path).exists():
            return jsonify({"results": []})
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM translations
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        results = [dict(row) for row in rows]
        
        conn.close()
        
        return jsonify({"results": results, "count": len(results)})
        
    except Exception as e:
        logger.error(f"History error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/phrasebook', methods=['GET'])
def phrasebook():
    """Get common phrases and learning content."""
    
    phrases = {
        "greetings": [
            {"english": "How are you?", "luganda": "Oli otya?"},
            {"english": "I am fine", "luganda": "Ndi bulungi"},
            {"english": "Thank you", "luganda": "Webale"},
            {"english": "Please", "luganda": "Ssebo"},
            {"english": "Goodbye", "luganda": "Bye bye"},
        ],
        "family": [
            {"english": "Mother", "luganda": "Maama"},
            {"english": "Father", "luganda": "Taata"},
            {"english": "Brother", "luganda": "Muganda"},
            {"english": "Sister", "luganda": "Mwannyina"},
            {"english": "Child", "luganda": "Omwana"},
        ],
        "daily": [
            {"english": "What is your name?", "luganda": "Linnya lyo liwa ki?"},
            {"english": "I love Luganda", "luganda": "Njagala Oluganda"},
            {"english": "Water", "luganda": "Amazzi"},
            {"english": "Food", "luganda": "Emmere"},
            {"english": "Help me", "luganda": "Twaganya"},
        ]
    }
    
    return jsonify(phrases)


@app.route('/api/clear-history', methods=['DELETE'])
def clear_history():
    """Clear translation history."""
    try:
        db_path = "translator_history.db"
        if Path(db_path).exists():
            Path(db_path).unlink()
            init_database()
            return jsonify({"status": "cleared"})
        else:
            return jsonify({"status": "no_history"})
            
    except Exception as e:
        logger.error(f"Clear history error: {e}")
        return jsonify({"error": str(e)}), 500


# Error handlers

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Load model
    logger.info("Loading translation model...")
    load_model()
    logger.info("Model loaded successfully")
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )
