from flask import Flask, render_template, request, jsonify
import json
import logging
import os

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load cultural dictionary from corrected_dictionary.json
CULTURAL_DICTIONARY = {}
DICTIONARY_PATH = "corrected_dictionary.json"

try:
    if os.path.exists(DICTIONARY_PATH):
        with open(DICTIONARY_PATH, 'r', encoding='utf-8') as f:
            CULTURAL_DICTIONARY = json.load(f)
        logger.info(f"✅ Loaded {len(CULTURAL_DICTIONARY)} cultural phrases from dictionary")
    else:
        logger.warning("⚠️ Dictionary file not found, using fallback phrases")
        # Fallback basic phrases
        CULTURAL_DICTIONARY = {
            "hello": "Nkulamusizza",
            "how are you": "Oli otya",
            "good morning": "Wasuubire nnyo",
            "thank you": "Webale",
            "my name is": "Linnya lyange lya",
            "i am from the monkey clan": "Ndi mu kika kya Ngo",
            "i am from the lion clan": "Ndi mu kika kya Mpologoma",
            "i am from the elephant clan": "Ndi mu kika kya Njovu",
            "welcome": "Karibu",
            "goodbye": "Alisema"
        }
except Exception as e:
    logger.error(f"❌ Error loading dictionary: {e}")
    CULTURAL_DICTIONARY = {}

@app.route('/')
def home():
    """Render home page"""
    return render_template('index.html')

@app.route('/api/translate', methods=['POST'])
def translate():
    """API endpoint for translation"""
    try:
        data = request.get_json()
        text = data.get('text', '').lower().strip()
        
        if not text:
            return jsonify({
                'status': 'error',
                'message': 'Please enter text to translate'
            }), 400
        
        # Check dictionary first
        if text in CULTURAL_DICTIONARY:
            translation = CULTURAL_DICTIONARY[text]
            return jsonify({
                'status': 'success',
                'original': text,
                'translation': translation,
                'source': 'dictionary',
                'confidence': 100
            })
        
        # Check partial matches
        for key, value in CULTURAL_DICTIONARY.items():
            if text in key or key in text:
                return jsonify({
                    'status': 'success',
                    'original': text,
                    'translation': value,
                    'source': 'dictionary_partial',
                    'confidence': 75
                })
        
        # Fallback message
        return jsonify({
            'status': 'success',
            'original': text,
            'translation': 'Translation not in dictionary (Model would generate this)',
            'source': 'ai_model',
            'confidence': 50,
            'note': 'This phrase is not in our verified dictionary. AI model translation would go here.'
        })
    
    except Exception as e:
        logger.error(f"❌ Translation error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Translation error: {str(e)}'
        }), 500

@app.route('/api/examples', methods=['GET'])
def get_examples():
    """Get example translations"""
    examples = [
        {'english': 'How are you?', 'luganda': 'Oli otya?'},
        {'english': 'Good morning', 'luganda': 'Wasuubire nnyo'},
        {'english': 'Thank you very much', 'luganda': 'Webale nnyo'},
        {'english': 'I am from the lion clan', 'luganda': 'Ndi mu kika kya Mpologoma'},
        {'english': 'My name is', 'luganda': 'Linnya lyange lya'},
    ]
    return jsonify({
        'status': 'success',
        'examples': examples
    })

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    return jsonify({
        'status': 'success',
        'system': 'operational',
        'dictionary_phrases': len(CULTURAL_DICTIONARY),
        'version': '1.0',
        'model': 'Cultural Dictionary + Helsinki-NLP',
        'timestamp': __import__('datetime').datetime.now().isoformat()
    })

if __name__ == '__main__':
    logger.info("🚀 Starting English-Luganda Translator Web Interface...")
    logger.info("📍 Open browser to http://localhost:5000")
    logger.info(f"📚 Loaded {len(CULTURAL_DICTIONARY)} cultural phrases")
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        use_reloader=False,
        use_debugger=False
    )
