"""
Flask Web Server for English-Luganda Translator
=============================================

Simple web interface for the trained translation model.
Access at: http://localhost:5000
"""

import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Setup Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Global model and tokenizer
model = None
tokenizer = None
device = "cuda" if torch.cuda.is_available() else "cpu"

def load_model():
    """Load the trained model and tokenizer."""
    global model, tokenizer
    
    model_path = Path(__file__).parent / "models" / "trained_model"
    
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found at {model_path}. Please train the model first!")
    
    print(f"Loading model from {model_path}...")
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
    model = model.to(device)
    model.eval()
    print(f"✅ Model loaded on {device}")


def translate(text):
    """Translate English text to Luganda."""
    if not model or not tokenizer:
        return "Error: Model not loaded"
    
    try:
        # Tokenize
        inputs = tokenizer(text, return_tensors="pt", padding=True, max_length=256, truncation=True)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Generate
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=256,
                num_beams=4,
                early_stopping=True
            )
        
        # Decode
        translation = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return translation
    
    except Exception as e:
        return f"Error: {str(e)}"


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/api/translate', methods=['POST'])
def api_translate():
    """API endpoint for translation."""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'Please enter text to translate'}), 400
        
        translation = translate(text)
        
        return jsonify({
            'english': text,
            'luganda': translation,
            'success': True
        })
    
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


@app.route('/api/status', methods=['GET'])
def api_status():
    """Check if model is loaded."""
    return jsonify({
        'model_loaded': model is not None,
        'device': device,
        'status': 'Ready' if model is not None else 'Model not loaded'
    })


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Server error: ' + str(e)}), 500


if __name__ == '__main__':
    try:
        # Load model before starting server
        load_model()
        
        # Run Flask app
        print("\n" + "="*80)
        print("English-Luganda Translator - Web Server")
        print("="*80)
        print(f"\n[INFO] Server running at: http://localhost:5000")
        print(f"[INFO] Model device: {device}")
        print(f"[INFO] Open your browser and go to http://localhost:5000\n")
        
        app.run(debug=True, host='0.0.0.0', port=5000)
    
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Please train the model first using the Colab notebook")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
