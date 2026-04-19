#!/usr/bin/env python
# ============================================================================
# ENGLISH-LUGANDA TRANSLATOR WEB APP
# ============================================================================
# Flask backend for the translation service
# ============================================================================

from flask import Flask, render_template, request, jsonify
from transformers import MarianMTModel, MarianTokenizer
import torch
import logging
import os

# ============================================================================
# SETUP
# ============================================================================

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# GLOBAL MODEL
# ============================================================================

model = None
tokenizer = None
model_ready = False

def load_model():
    """Load the translation model and tokenizer"""
    global model, tokenizer, model_ready
    
    if model_ready:
        return True
    
    try:
        logger.info("🔄 Loading translation model...")
        model_name = 'Helsinki-NLP/opus-mt-mul-en'
        
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name)
        
        # Move to GPU if available
        if torch.cuda.is_available():
            model = model.to('cuda')
            device_info = "GPU (CUDA)"
        else:
            device_info = "CPU"
        
        model_ready = True
        logger.info(f"✅ Model loaded successfully on {device_info}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error loading model: {e}")
        return False

def translate_luganda_to_english(luganda_text):
    """Translate Luganda text to English"""
    if not model_ready or model is None or tokenizer is None:
        return None, "Model not loaded"
    
    try:
        # Tokenize input
        inputs = tokenizer(luganda_text, return_tensors="pt", padding=True)
        
        # Move to GPU if available
        if torch.cuda.is_available():
            inputs = {k: v.to('cuda') for k, v in inputs.items()}
        
        # Generate translation
        with torch.no_grad():
            outputs = model.generate(**inputs, max_length=512)
        
        # Decode translation
        translation = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return translation.strip(), None
    
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return None, str(e)

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/translate', methods=['POST'])
def api_translate():
    """API endpoint for translation"""
    try:
        data = request.get_json()
        luganda_text = data.get('text', '').strip()
        
        if not luganda_text:
            return jsonify({'error': 'Empty text'}), 400
        
        if len(luganda_text) > 1000:
            return jsonify({'error': 'Text too long (max 1000 characters)'}), 400
        
        translation, error = translate_luganda_to_english(luganda_text)
        
        if error:
            return jsonify({'error': error}), 500
        
        return jsonify({
            'original': luganda_text,
            'translation': translation,
            'status': 'success'
        })
    
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def api_status():
    """Check model status"""
    return jsonify({
        'ready': model_ready,
        'device': 'GPU' if torch.cuda.is_available() else 'CPU'
    })

@app.route('/api/examples', methods=['GET'])
def api_examples():
    """Get example translations"""
    examples = [
        {
            "luganda": "Oli otya",
            "english": "How are you?",
            "category": "Greeting"
        },
        {
            "luganda": "Ndi Muganda",
            "english": "I am Lugandan",
            "category": "Identity"
        },
        {
            "luganda": "Webale nnyo",
            "english": "Thank you very much",
            "category": "Gratitude"
        },
        {
            "luganda": "Kabaka yalambula abantu",
            "english": "The Kabaka visited people",
            "category": "Cultural"
        },
        {
            "luganda": "Ssegeza abakulu",
            "english": "Respect the elders",
            "category": "Values"
        }
    ]
    return jsonify(examples)

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Server error'}), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("🚀 ENGLISH-LUGANDA TRANSLATOR WEB APP")
    print("=" * 80)
    
    # Load model on startup
    if load_model():
        print("\n✅ Starting Flask server...")
        print("\n📱 Open your browser and go to: http://localhost:5000")
        print("   or http://127.0.0.1:5000")
        print("\n⏹️  Press Ctrl+C to stop the server\n")
        
        # Run the app
        app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
    else:
        print("\n❌ Failed to load the model. Please check your internet connection.")
        print("   Exiting...")
