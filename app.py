from flask import Flask, render_template, request, jsonify
import torch
from transformers import MarianMTModel, MarianTokenizer
import logging
import os

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize model and tokenizer (loaded on first use)
model = None
tokenizer = None

# CLAN-FOCUSED GUARANTEED TRANSLATIONS (Luganda)
GUARANTEED_TRANSLATIONS = {
    # Basic Greetings & Politeness
    "hello, how are you?": "Nkulamusizza, oyagala?",
    "good morning": "Wasuubire nnyo",
    "good afternoon": "Wawummule nnyo",
    "good evening": "Waggulo nnyo",
    "thank you very much": "Webale nnyo",
    "you are welcome": "Welcome",
    "pleased to meet you": "Nsekedde okukulaba",
    "what is your name?": "Linnya lyo liwa ki?",
    "i am very glad": "Ndi mu ngeri nnyo",
    "sorry, forgive me": "Nsaba mwayogere",
    
    # CLAN IDENTIFICATION & QUESTIONS (22 Baganda Clans)
    "what clan are you from?": "Oli mu kika ki?",
    "which clan do you belong to?": "Oli mu kika ki?",
    "i am from the monkey clan": "Ndi mu kika kya Ngo",
    "i am from the lungfish clan": "Ndi mu kika kya Mmamba",
    "i am from the elephant clan": "Ndi mu kika kya Njovu",
    "i am from the lion clan": "Ndi mu kika kya Mpologoma",
    "i am from the buffalo clan": "Ndi mu kika kya Mbogo",
    "i am from the leopard clan": "Ndi mu kika kya Ng'e",
    "i am from the antelope clan": "Ndi mu kika kya Mponya",
    "i am from the dog clan": "Ndi mu kika kya Nte",
    "i am from the cat clan": "Ndi mu kika kya Njagatsi",
    "i am from the bird clan": "Ndi mu kika kya Ennyonyi",
    "i am from the civet clan": "Ndi mu kika kya Mwana",
    "i am from the fish clan": "Ndi mu kika kya Nsiru",
    "i am from the frog clan": "Ndi mu kika kya Ogezi",
    "i am from the mushroom clan": "Ndi mu kika kya Omucwecwe",
    "i am from the cowrie clan": "Ndi mu kika kya Amasengeri",
    "i am from the bean clan": "Ndi mu kika kya Enjala",
    "i am from the yam clan": "Ndi mu kika kya Enjala",
    "i am from the root clan": "Ndi mu kika kya Okwo",
    "i am from the bee clan": "Ndi mu kika kya Nyinyi",
    "i am from the termite clan": "Ndi mu kika kya Kkoona",
    
    # TOTEM & SPIRITUAL PHRASES
    "the monkey is our totem": "Ngo ye kinene kyaffe",
    "we respect our clan symbol": "Tukkiriza kinene kyaffe",
    "the totem must be respected": "Kinene kya kika kyetaagisa okukiriza",
    "our ancestors guarded the clan": "Bajjajjaffe baliwo okukuuma kika",
    "the spirits of our forefathers protect us": "Zimu za bajjajjaffe zituwa okuteekawo",
    
    # FAMILY & CLAN KNOWLEDGE
    "who is your clan elder?": "Sebalija w'okika kwo ali ani?",
    "my father is from this clan": "Taata wange ali mu kika kino",
    "my mother taught me about our clan": "Mama wange yapiganya nga clan yafe",
    "clan members are like brothers": "Abakika baffe bali nga bakibito",
    "i know my clan history": "Nmanyi amawendo ga kika kyange",
    "our clan has many families": "Kika kyaffe kirina nnyumba zingi",
    "clan unity is important": "Kumanyidde mu kika kye kintu kya maanyi",
    "we share the same ancestor": "Tuva mu mutwa gumwe",
    "clan loyalty is sacred": "Okwama kika kwe kinagiro kya Katonda",
    "family trees connect us": "Ensi za nnyumba zitula tutwalangira",
    
    # TEACHING CHILDREN ABOUT CLAN
    "teach the children about their clan": "Funza abaana bo ebya kika kyabwe",
    "know your roots": "Manyi ku mkazzi gwo",
    "remember where you come from": "Kumanya ekigazi kyo",
    "pass the clan knowledge to children": "Wasigeze abaana b'okumanyi amawendo ga kika",
    "children must know their totem": "Abaana balina okumanyi kinene",
    "tell them about the clan ancestors": "Kigambye bye ba bajjajjaffe ba kika",
    "clan stories are our history": "Amategeeza ga kika bye tassibira taffe",
    "your name connects you to the clan": "Linnya lyo likumalamu mu kika",
    "the clan protects its members": "Kika kituwa okuteekawo abakika",
    "every child must know their clan": "Omwana buli ki avvunaavvuna okwada mu kika ky'abakibito be",
    
    # CLAN PRIDE & IDENTITY
    "i am proud to be baganda": "Ndi jjudde okuba Muganda",
    "our clan is strong": "Kika kyaffe kike kinene",
    "we are baganda and proud": "Tuli Abaganda era tujjudde ettima",
    "clan unity makes us strong": "Okukola okukola mu kika kwe kintu kya maanyi",
    "our ancestors were brave": "Bajjajjaffe baali ba magezi",
    "the baganda clan system is ancient": "Kika kya Baganda kine nnafuu addala",
    "we preserve our cultural heritage": "Tukuuma ensi yaffe",
    "baganda identity is in our blood": "Okuba Muganda kwe mu mutwe gwo",
    "respect your clan name": "Kiriza linnya lya kika kyangye",
    "clan membership is lifelong": "Okuba mu kika kwe ttaka",
    
    # DIASPORA & CULTURAL IDENTITY ABROAD
    "i am baganda even though i live far away": "Ndi Muganda naye ndimubaamu",
    "we bring baganda culture wherever we go": "Tuva mu ensi yaffe ffe wonna",
    "my children know their baganda heritage": "Abaana bange bamanyi ssente zaffe",
    "luganda connects us to home": "Olulimi lwaffe lwatuwalira eri eka",
    "i teach my children luganda": "Nfuna abaana bange olulimi lwaffe",
    "baganda culture is my identity": "Kika kya Baganda kye kintu kyange",
    "we are baganda no matter where we are": "Tuli Abaganda wonna wiwa tuvaamu",
    "staying connected to clan traditions": "Okukuuma amategeeza ga kika",
    "luganda is our cultural link": "Olulimi lwaffe lwe kufeeza ku nsi",
    "homeland in my heart": "Eka liri mu mutima gwange",
    "passing tradition to next generation": "Wasigeze abaana b'amategeeza ga ensi yaffu",
    "i remember my clan even abroad": "Nkubadde okwawuka naye ntinakakakasa kika kyange",
    "baganda pride transcends borders": "Okuba Muganda si kitesela ku nsi",
    "my roots are in kampala": "Mizizi yange iri mu Kampala",
    "luganda is my wealth": "Olulimi lwange lwe mboozi yange",
    
    # BAGANDA IDENTITY & CULTURE
    "who are the baganda?": "Abaganda bali ani?",
    "baganda are from kampala": "Abaganda bva mu Kampala",
    "the kabaka is our king": "Kabaka ye kabaka waffe",
    "mengo is our cultural center": "Mengo ye kifo kya abalala waffe",
    "we speak luganda": "Tugamba Luganda",
    "luganda is our language": "Olulimi lwange lwe Luganda",
    "our culture is our pride": "Ensi yaffe ye ttima lyaffe",
    "baganda heritage is rich": "Amagezi ga Baganda garungi nnyo",
    "we are defenders of our customs": "Tuli abakunguzi b'amategeeza gaffe",
    "baganda traditions endure": "Amawendo ga Baganda tabulagira",
    
    # SIMPLE LUGANDA BASICS
    "mother": "Maama",
    "father": "Taata",
    "sister": "Mukwano",
    "brother": "Mulamu/Mukwano",
    "grandmother": "Jjaja",
    "grandfather": "Jjajja",
    "family": "Nnyumba",
    "home": "Eka",
    "thank you": "Webale",
    "i love my clan": "Nkwagala kika kyange",
}

def load_model():
    """Load the MarianMT model and tokenizer"""
    global model, tokenizer
    if model is None:
        logger.info("Loading model opus-mt-en-mul...")
        model_name = "Helsinki-NLP/opus-mt-en-mul"
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name)
        logger.info("Model loaded successfully")
    return model, tokenizer

def translate_to_luganda(english_text):
    """Translate English text to Luganda using guaranteed dictionary or AI model"""
    # Normalize input
    text_lower = english_text.lower().strip()
    
    # Check guaranteed translations first
    if text_lower in GUARANTEED_TRANSLATIONS:
        return GUARANTEED_TRANSLATIONS[text_lower]
    
    # Check partial matches
    for key, value in GUARANTEED_TRANSLATIONS.items():
        if key in text_lower or text_lower in key:
            return value
    
    # Fall back to AI model
    try:
        model, tokenizer = load_model()
        
        # Add Luganda language tag
        input_text = f">>lug<< {english_text}"
        
        # Tokenize and translate
        input_ids = tokenizer.encode(input_text, return_tensors="pt")
        outputs = model.generate(input_ids, max_length=100, num_beams=4)
        translation = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return translation
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        return f"[Translation error: {str(e)}]"

@app.route('/')
def index():
    """Serve the web interface"""
    return render_template('index.html')

@app.route('/api/translate', methods=['POST'])
def api_translate():
    """API endpoint for translations"""
    try:
        data = request.json
        english_text = data.get('text', '').strip()
        
        if not english_text:
            return jsonify({'error': 'No text provided'}), 400
        
        luganda_text = translate_to_luganda(english_text)
        
        return jsonify({
            'english': english_text,
            'translation': luganda_text,
            'in_dictionary': english_text.lower() in GUARANTEED_TRANSLATIONS
        })
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def api_status():
    """Check API status"""
    return jsonify({
        'status': 'ok',
        'dictionary_size': len(GUARANTEED_TRANSLATIONS),
        'model': 'Helsinki-NLP/opus-mt-en-mul'
    })

@app.route('/api/examples', methods=['GET'])
def api_examples():
    """Get example translations"""
    clan_examples = [
        {'english': 'What clan are you from?', 'luganda': 'Oli mu kika ki?'},
        {'english': 'I am from the monkey clan', 'luganda': 'Ndi mu kika kya Ngo'},
        {'english': 'We are Baganda and proud', 'luganda': 'Tuli Abaganda era tujjudde ettima'},
        {'english': 'Teach the children about their clan', 'luganda': 'Funza abaana bo ebya kika kyabwe'},
        {'english': 'I am Baganda even though I live far away', 'luganda': 'Ndi Muganda naye ndimubaamu'},
        {'english': 'Hello, how are you?', 'luganda': 'Nkulamusizza, oyagala?'},
        {'english': 'Good morning', 'luganda': 'Wasuubire nnyo'},
        {'english': 'Thank you very much', 'luganda': 'Webale nnyo'},
        {'english': 'Luganda connects us to home', 'luganda': 'Olulimi lwaffe lwatuwalira eri eka'},
        {'english': 'I love my clan', 'luganda': 'Nkwagala kika kyange'},
    ]
    return jsonify({'examples': clan_examples})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
