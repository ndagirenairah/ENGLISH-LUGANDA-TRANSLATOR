"""
Flask Web Server for English-Luganda Translator
=============================================

Advanced web interface with error handling, logging, rate limiting, and batch API.
Access at: http://localhost:5000
"""

import os
import sys
import logging
import re
import time
import json
from pathlib import Path
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
def setup_logging():
    """Configure logging for the application."""
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"translator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s - %(name)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

logger = setup_logging()

# ============================================================================
# SETUP FLASK APP
# ============================================================================
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
CORS(app)  # Enable Cross-Origin Resource Sharing

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Global model and tokenizer
model = None
tokenizer = None
device = "cuda" if torch.cuda.is_available() else "cpu"

# Rate limiting tracking
rate_limit_store = {}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def rate_limit(max_requests=100, window=3600):
    """Decorator for rate limiting requests by IP address."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            ip = request.remote_addr
            now = time.time()
            
            # Clean old entries
            if ip in rate_limit_store:
                rate_limit_store[ip] = [t for t in rate_limit_store[ip] if now - t < window]
            else:
                rate_limit_store[ip] = []
            
            # Check limit
            if len(rate_limit_store[ip]) >= max_requests:
                logger.warning(f"Rate limit exceeded for IP {ip}")
                return jsonify({'error': 'Rate limit exceeded. Max 100 requests per hour.', 'success': False}), 429
            
            rate_limit_store[ip].append(now)
            return f(*args, **kwargs)
        return wrapper
    return decorator


def sanitize_input(text, max_length=512):
    """Sanitize and validate input text."""
    if not isinstance(text, str):
        raise ValueError("Input must be text")
    
    text = text.strip()
    
    if not text:
        raise ValueError("Input cannot be empty")
    
    if len(text) > max_length:
        raise ValueError(f"Input exceeds maximum length of {max_length} characters")
    
    # Remove excessive special characters
    text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', '', text)
    
    return text


def load_model():
    """Load the trained model and tokenizer with error handling."""
    global model, tokenizer
    
    try:
        model_path = Path(__file__).parent / "models" / "trained_model"
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found at {model_path}")
        
        logger.info(f"Loading model from {model_path}...")
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        logger.info("Tokenizer loaded successfully")
        
        # Load model
        model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
        model = model.to(device)
        model.eval()
        
        logger.info(f"Model loaded successfully on device: {device}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        raise


def translate(text, num_beams=4, max_length=256):
    """Translate English text to Luganda with error handling."""
    if not model or not tokenizer:
        logger.error("Model or tokenizer not loaded")
        raise RuntimeError("Model not loaded")
    
    try:
        start_time = time.time()
        
        # Validate input
        text = sanitize_input(text, max_length=512)
        
        # Tokenize
        inputs = tokenizer(text, return_tensors="pt", padding=True, max_length=256, truncation=True)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Generate translation
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=max_length,
                num_beams=num_beams,
                early_stopping=True,
                temperature=0.9
            )
        
        # Decode
        translation = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        inference_time = time.time() - start_time
        logger.info(f"Translation completed in {inference_time:.3f}s")
        
        return translation
    
    except ValueError as e:
        logger.warning(f"Input validation error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        raise




# ============================================================================
# API ROUTES
# ============================================================================
@app.route('/')
def index():
    """Render the main page."""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index: {str(e)}")
        return jsonify({'error': 'Failed to load page'}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring."""
    try:
        return jsonify({
            'status': 'healthy',
            'model_loaded': model is not None,
            'device': device,
            'timestamp': datetime.now().isoformat(),
            'version': '1.0'
        }), 200
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500


@app.route('/api/translate', methods=['POST'])
@rate_limit(max_requests=100, window=3600)
def api_translate():
    """Single text translation endpoint."""
    try:
        data = request.get_json()
        
        if not data:
            logger.warning("No JSON data received")
            return jsonify({'error': 'No data provided', 'success': False}), 400
        
        text = data.get('text', '').strip()
        
        if not text:
            logger.warning("Empty text received")
            return jsonify({'error': 'Text field is required and cannot be empty', 'success': False}), 400
        
        # Translate
        translation = translate(text)
        
        logger.info(f"Successfully translated: '{text[:50]}...' to '{translation[:50]}...'")
        
        return jsonify({
            'english': text,
            'luganda': translation,
            'success': True,
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return jsonify({'error': str(e), 'success': False}), 400
    except RuntimeError as e:
        logger.error(f"Runtime error: {str(e)}")
        return jsonify({'error': str(e), 'success': False}), 503
    except Exception as e:
        logger.error(f"Unexpected error in translate: {str(e)}")
        return jsonify({'error': 'Internal server error', 'success': False}), 500


@app.route('/api/translate-batch', methods=['POST'])
@rate_limit(max_requests=50, window=3600)
def api_translate_batch():
    """Batch translation endpoint for multiple texts."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided', 'success': False}), 400
        
        texts = data.get('texts', [])
        
        if not isinstance(texts, list):
            return jsonify({'error': 'Texts field must be a list', 'success': False}), 400
        
        if not texts:
            return jsonify({'error': 'Texts list cannot be empty', 'success': False}), 400
        
        if len(texts) > 50:
            logger.warning(f"Batch size too large: {len(texts)}")
            return jsonify({'error': 'Maximum 50 texts per batch', 'success': False}), 400
        
        results = []
        errors = []
        
        for i, text in enumerate(texts):
            try:
                text_clean = sanitize_input(text, max_length=512)
                translation = translate(text_clean)
                results.append({
                    'index': i,
                    'english': text_clean,
                    'luganda': translation,
                    'success': True
                })
            except Exception as e:
                logger.warning(f"Error translating item {i}: {str(e)}")
                errors.append({
                    'index': i,
                    'error': str(e)
                })
        
        logger.info(f"Batch translation completed: {len(results)} successful, {len(errors)} failed")
        
        return jsonify({
            'results': results,
            'errors': errors,
            'summary': {
                'total': len(texts),
                'successful': len(results),
                'failed': len(errors)
            },
            'success': True,
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Batch translation error: {str(e)}")
        return jsonify({'error': 'Internal server error', 'success': False}), 500


@app.route('/api/status', methods=['GET'])
def api_status():
    """Get detailed status information."""
    try:
        return jsonify({
            'model_loaded': model is not None,
            'device': device,
            'status': 'Ready' if model is not None else 'Model not loaded',
            'gpu_available': torch.cuda.is_available(),
            'torch_version': torch.__version__,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Status error: {str(e)}")
        return jsonify({'error': 'Failed to get status', 'success': False}), 500


@app.route('/api/docs', methods=['GET'])
def api_docs():
    """API documentation."""
    docs = {
        'title': 'English-Luganda Translator API',
        'version': '1.0',
        'endpoints': {
            'GET /api/health': {
                'description': 'Health check endpoint',
                'response': {'status': 'healthy', 'model_loaded': True}
            },
            'GET /api/status': {
                'description': 'Get detailed status information',
                'response': {'model_loaded': True, 'device': 'cuda'}
            },
            'POST /api/translate': {
                'description': 'Translate single text',
                'request': {'text': 'Hello world'},
                'response': {'english': 'Hello world', 'luganda': '...', 'success': True}
            },
            'POST /api/translate-batch': {
                'description': 'Translate multiple texts (max 50)',
                'request': {'texts': ['Hello', 'World']},
                'response': {'results': [], 'errors': [], 'summary': {}}
            }
        }
    }
    return jsonify(docs), 200




# ============================================================================
# ERROR HANDLERS
# ============================================================================
@app.errorhandler(400)
def bad_request(e):
    """Handle bad request errors."""
    logger.warning(f"Bad request: {str(e)}")
    return jsonify({'error': 'Bad request', 'success': False}), 400


@app.errorhandler(404)
def not_found(e):
    """Handle not found errors."""
    logger.warning(f"Endpoint not found: {request.path}")
    return jsonify({'error': f'Endpoint not found: {request.path}', 'success': False}), 404


@app.errorhandler(429)
def rate_limit_handler(e):
    """Handle rate limit errors."""
    logger.warning(f"Rate limit exceeded for {request.remote_addr}")
    return jsonify({'error': 'Rate limit exceeded', 'success': False}), 429


@app.errorhandler(500)
def server_error(e):
    """Handle server errors."""
    logger.error(f"Server error: {str(e)}")
    return jsonify({'error': 'Internal server error', 'success': False}), 500


# ============================================================================
# APPLICATION STARTUP
# ============================================================================
if __name__ == '__main__':
    try:
        logger.info("Starting English-Luganda Translator Web Server")
        logger.info(f"Device: {device}")
        logger.info(f"GPU Available: {torch.cuda.is_available()}")
        
        # Load model before starting server
        load_model()
        
        # Run Flask app
        print("\n" + "="*80)
        print("English-Luganda Translator - Web Server v1.0")
        print("="*80)
        print(f"\n[INFO] Server running at: http://localhost:5000")
        print(f"[INFO] API Documentation: http://localhost:5000/api/docs")
        print(f"[INFO] Health Check: http://localhost:5000/api/health")
        print(f"[INFO] Model device: {device}")
        print(f"[INFO] Open your browser and go to http://localhost:5000\n")
        print("="*80 + "\n")
        
        logger.info("Server started successfully")
        app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
    
    except FileNotFoundError as e:
        logger.error(f"Model file not found: {str(e)}")
        print(f"\nError: {e}")
        print("Please train the model first using the Colab notebook")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"Unexpected startup error: {str(e)}")
        print(f"\nUnexpected error: {e}")
        sys.exit(1)

