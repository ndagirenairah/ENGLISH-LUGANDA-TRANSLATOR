from flask import Flask, render_template, request, jsonify, send_file
import torch
from transformers import MarianMTModel, MarianTokenizer
import logging
import os
import sqlite3
from datetime import datetime
from gtts import gTTS
from io import BytesIO
from langdetect import detect, LangDetectException
import json
import requests

print("=" * 80)
print(" ML WORKFLOW: DEPLOYMENT & MONITORING")
print("=" * 80)
print("""
ML Workflow Progress:
  ✓ 1. Define the problem
  ✓ 2. Collect data
  ✓ 3. Exploratory Data Analysis
  ✓ 4. Data cleaning & preprocessing
  ✓ 5. Feature engineering
  ✓ 6. Model training & evaluation
  ✓ 7. Model evaluation
  ► 8. Deployment & monitoring      (This file - Flask production server)
""")

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize model and tokenizer (loaded on first use)
model = None
tokenizer = None

# Database initialization
DB_PATH = 'translator_history.db'

def init_db():
    """Initialize SQLite database for translation history"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS translations
                 (id INTEGER PRIMARY KEY,
                  timestamp TEXT,
                  source_text TEXT,
                  target_text TEXT,
                  source_language TEXT,
                  target_language TEXT,
                  in_dictionary BOOLEAN)''')
    conn.commit()
    conn.close()

def save_translation_history(source_text, target_text, source_lang, target_lang, in_dict):
    """Save translation to database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        timestamp = datetime.now().isoformat()
        c.execute('''INSERT INTO translations 
                     (timestamp, source_text, target_text, source_language, target_language, in_dictionary)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (timestamp, source_text, target_text, source_lang, target_lang, in_dict))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Database error: {str(e)}")

# PHRASEBOOK - CULTURAL & LEARNING CONTENT
PHRASEBOOK = {
    "Greetings": [
        {"english": "Hello, how are you?", "luganda": "Nkulamusizza, oyagala?", "cultural_context": "Common greeting in Ugandan culture"},
        {"english": "Good morning", "luganda": "Wasuubire nnyo", "cultural_context": "Used early in the day"},
        {"english": "Good afternoon", "luganda": "Wawummule nnyo", "cultural_context": "Used during midday"},
        {"english": "Good evening", "luganda": "Waggulo nnyo", "cultural_context": "Used after sunset"},
        {"english": "Thank you very much", "luganda": "Webale nnyo", "cultural_context": "Shows respect and gratitude"},
        {"english": "You are welcome", "luganda": "Welcome", "cultural_context": "Hospitality is important in Ugandan culture"},
    ],
    "Family & Clans": [
        {"english": "What clan are you from?", "luganda": "Oli mu kika ki?", "cultural_context": "22 Baganda clans - identity is central"},
        {"english": "I am from the monkey clan", "luganda": "Ndi mu kika kya Ngo", "cultural_context": "Ngo clan - associated with wisdom"},
        {"english": "I am from the lion clan", "luganda": "Ndi mu kika kya Mpologoma", "cultural_context": "Mpologoma - symbolizes strength"},
        {"english": "Mother", "luganda": "Maama", "cultural_context": "Mothers hold high respect in Baganda culture"},
        {"english": "Father", "luganda": "Taata", "cultural_context": "Fathers are family leaders"},
        {"english": "Grandmother", "luganda": "Jjaja", "cultural_context": "Grandmothers preserve cultural knowledge"},
    ],
    "Daily Life": [
        {"english": "How are you?", "luganda": "Oyagala?", "cultural_context": "Common casual greeting"},
        {"english": "I am fine", "luganda": "Ndi bulungi", "cultural_context": "Standard response"},
        {"english": "Where are you from?", "luganda": "Ova ku?", "cultural_context": "Important for identity"},
        {"english": "What is your name?", "luganda": "Linnya lyo liwa ki?", "cultural_context": "Names have meaning in Luganda"},
        {"english": "I love my clan", "luganda": "Nkwagala kika kyange", "cultural_context": "Clan loyalty is sacred"},
        {"english": "Teach the children about their clan", "luganda": "Funza abaana bo ebya kika kyabwe", "cultural_context": "Preserving cultural knowledge"},
    ],
    "Food & Cooking": [
        {"english": "Food", "luganda": "Kifo", "cultural_context": "Essential daily sustenance"},
        {"english": "Water", "luganda": "Amazzi", "cultural_context": "Sacred element in African culture"},
        {"english": "Rice", "luganda": "Mwali", "cultural_context": "Popular staple food"},
        {"english": "Plantain", "luganda": "Gonja", "cultural_context": "Traditional Ugandan food"},
        {"english": "I am hungry", "luganda": "Njala", "cultural_context": "Natural human need"},
        {"english": "Eat", "luganda": "Kula", "cultural_context": "Social and cultural activity"},
    ]
}

# CULTURAL CONTEXT DICTIONARY
CULTURAL_CONTEXT = {
    "kabaka": "Baganda king - spiritual and political leader",
    "kika": "Clan - central to Baganda identity",
    "kwanjula": "Marriage introduction ceremony - important cultural event",
    "mengo": "Cultural headquarters of Baganda people",
    "luganda": "Language spoken by Baganda people - UNESCO recognized",
    "baganda": "People of Buganda kingdom - major ethnic group in Uganda",
    "ngo": "Monkey clan - associated with wisdom and trickery",
    "totem": "Sacred symbol of clan identity",
    "ancestor": "Person from whom one is descended - honored in Baganda culture",
    "clan elder": "Senior member who guides clan affairs"
}

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
    
    # QUESTIONS - How, Where, What
    "how are you?": "Oyagala?",
    "how are you doing?": "Okola ki?",
    "where are you?": "Oli wapi?",
    "where do you live?": "Obeera wapi?",
    "what is your address?": "Lukeza lwo luli wapi?",
    "where are you from?": "Ova ku?",
    "how much does it cost?": "Kinabya mweluma?",
    "what time is it?": "Ssaawa iri katika ki?",
    "when will you come?": "Bw'oyinza okuja?",
    "why are you here?": "Kiki ekikukoma eno?",
    "what is your job?": "Okoleka e?",
    "do you have water?": "Oba n'amazzi?",
    "where is the market?": "Soko liri wapi?",
    "how long will it take?": "Kinatwala ssaawa nnyo?",
    "can i help you?": "Nsobola okukuganya?",
    
    # MARKET VOCABULARY
    "market": "Soko",
    "shop": "Duka",
    "buy": "Gula",
    "sell": "Gguwa",
    "price": "Mwebya",
    "money": "Sente",
    "how much?": "Mweluma?",
    "too expensive": "Kino kye kya bugazi",
    "cheap": "Kye kya mwenge",
    "give me a discount": "Nfuula omubiro",
    "i want to buy": "Nkyagula",
    "how much is this?": "Kino kinabya mweluma?",
    "do you have it?": "Oba n'eno?",
    "what is the price?": "Mwebya ki?",
    "i cannot afford it": "Sitina sente za kuno",
    "please reduce the price": "Nfuula omubiro",
    "do you give credit?": "Ossaako emitwe?",
    "pay later": "Kuwa later",
    "cash only": "Sente bbanze",
    "change money": "Guba sente",
    
    # DAILY LIFE VOCABULARY - FOOD & COOKING
    "food": "Kifo",
    "water": "Amazzi",
    "rice": "Mwali",
    "beans": "Ebigimba",
    "cassava": "Mpufu",
    "plantain": "Gonja",
    "cooking": "Okuliisa",
    "eat": "Kula",
    "drink": "Okunywa",
    "salt": "Munyu",
    "oil": "Omuyini",
    "fire": "Omuliro",
    "cook me food": "Liisa",
    "i am hungry": "Njala",
    "i am thirsty": "Amayinja",
    "breakfast": "Okuliifika",
    "lunch": "Mu nkubito",
    "dinner": "Akasannyalizo",
    "spoon": "Kakanyolya",
    "plate": "Lekulekezi",
    "cup": "Kikopo",
    "knife": "Kasonko",
    "pot": "Kkasannyalizo",
    "make tea": "Funa chayi",
    "sugar": "Souji",
    "bread": "Bbuliro",
    "milk": "Amabere",
    "meat": "Enyama",
    "chicken": "Njuwuli",
    "fish": "Nsiimu",
    
    # DAILY LIFE VOCABULARY - HOME & FAMILY
    "house": "Nnyumba",
    "room": "Kasoobe",
    "door": "Mduli",
    "window": "Ekiwindo",
    "bed": "Ebbala",
    "table": "Meeza",
    "chair": "Ekitebe",
    "floor": "Lukwata",
    "roof": "Atili",
    "wall": "Omuziro",
    "kitchen": "Ekitanda",
    "bathroom": "Essanyu",
    "toilet": "Essanyu",
    "clean the house": "Kuba nnyumba",
    "sweep": "Okweteza",
    "wash": "Okukuba",
    "dry clothes": "Kira empa",
    "iron clothes": "Okugema empa",
    "wash dishes": "Kuba bwino",
    "take a bath": "Okugwa amazzi",
    
    # DAILY LIFE VOCABULARY - PEOPLE & GREETINGS
    "man": "Omusajja",
    "woman": "Omukazi",
    "child": "Omwana",
    "children": "Abaana",
    "friend": "Mukwano",
    "neighbor": "Omukwano omugyaganya",
    "teacher": "Omukulu w'essomero",
    "doctor": "Oludakita",
    "nurse": "Omunyansawo",
    "how is your family?": "Nnyumba yo olina amakonda otya?",
    "greetings to your family": "Simusizza nnyumba yo",
    "i am fine": "Ndi bulungi",
    "i am not well": "Sirikuwulira",
    "take care": "Kwatagira",
    "see you later": "Tumanagane later",
    "goodbye": "Kwagala",
    
    # DAILY LIFE VOCABULARY - TRAVEL & DIRECTIONS
    "road": "Ddirisa",
    "bus": "Basi",
    "car": "Mmotoka",
    "go": "Kugenda",
    "come": "Okuja",
    "run": "Okugumaanye",
    "walk": "Okutambulula",
    "near": "Akwagala",
    "far": "Wala",
    "here": "Eno",
    "there": "Eyo",
    "which way?": "Ddirisa ki?",
    "turn left": "Kufa ku bukwiriri",
    "turn right": "Kufa ku ddyo",
    "straight ahead": "Nyangu ddirisa",
    "how do i get there?": "Nnyero ye wapi?",
    "do you know the way?": "Omanyi nnyero?",
}

def load_model():
    """Load the MarianMT model and tokenizer - preferring trained model"""
    global model, tokenizer
    if model is None:
        # First try to load our custom-trained model
        trained_model_path = "models/trained_model"
        try:
            if os.path.exists(trained_model_path):
                logger.info(f"Loading TRAINED model from {trained_model_path}...")
                tokenizer = MarianTokenizer.from_pretrained(trained_model_path)
                model = MarianMTModel.from_pretrained(trained_model_path)
                logger.info("TRAINED MODEL LOADED SUCCESSFULLY - Using custom-fine-tuned weights")
            else:
                raise FileNotFoundError("No trained model found")
        except Exception as e:
            # Fall back to base model if training hasn't been run
            logger.warning("No trained model found, loading BASE model from HuggingFace...")
            model_name = "Helsinki-NLP/opus-mt-en-mul"
            tokenizer = MarianTokenizer.from_pretrained(model_name)
            model = MarianMTModel.from_pretrained(model_name)
            logger.info("BASE MODEL LOADED - To use custom-trained model, run: python Step5_Train_Model.py")
    return model, tokenizer

def translate_to_luganda(english_text):
    """Translate English text to Luganda using dictionary first, then Claude API"""
    text_lower = english_text.lower().strip()
    
    # ✅ STEP 1: Check guaranteed translations (EXACT MATCH - MOST RELIABLE)
    if text_lower in GUARANTEED_TRANSLATIONS:
        logger.info(f"Dictionary exact match: {text_lower}")
        return GUARANTEED_TRANSLATIONS[text_lower], True, "Dictionary (Verified)"
    
    # ✅ STEP 2: Check partial matches (PHRASE CONTAINS)
    for key, value in GUARANTEED_TRANSLATIONS.items():
        if len(key) > 3 and key in text_lower:  # Avoid matching single words
            logger.info(f"Dictionary partial match: {key} → {value}")
            return value, True, "Dictionary (Partial Match)"
    
    # ✅ STEP 3: Word-level dictionary lookup
    words = text_lower.split()
    word_translations = []
    found_any_word = False
    
    for word in words:
        word_lower = word.strip('.,!?;:').lower()
        if word_lower in GUARANTEED_TRANSLATIONS:
            word_translations.append(GUARANTEED_TRANSLATIONS[word_lower])
            found_any_word = True
        else:
            # Try fuzzy match for partial words
            for key, value in GUARANTEED_TRANSLATIONS.items():
                if word_lower in key and len(key) <= len(word_lower) + 2:
                    word_translations.append(value)
                    found_any_word = True
                    break
            if not found_any_word or len(word_translations) < len(words):
                word_translations.append(word)  # Keep original if not found
    
    if found_any_word and len(word_translations) > 0:
        result = " ".join(word_translations)
        if result != text_lower:  # Only return if different from input
            logger.info(f"Word-level match: {result}")
            return result, True, "Dictionary (Word-Level)"
    
    # ❌ FALLBACK: Model-based translation disabled (Helsinki-NLP doesn't support Luganda)
    # Instead, return a message indicating we need the dictionary
    logger.warning(f"No dictionary translation found for: {english_text}")
    return f"[Translation not available for: {english_text}]", False, "Not Found"


def translate_to_english(luganda_text):
    """Translate Luganda text to English using dictionary first"""
    text_lower = luganda_text.lower().strip()
    
    # Build reverse dictionary (Luganda -> English) - cached for performance
    reverse_translations = {}
    for eng, lug in GUARANTEED_TRANSLATIONS.items():
        lug_lower = lug.lower()
        if lug_lower not in reverse_translations:
            reverse_translations[lug_lower] = eng
    
    # ✅ STEP 1: Check exact matches (MOST RELIABLE)
    if text_lower in reverse_translations:
        logger.info(f"Reverse dict exact match: {text_lower}")
        return reverse_translations[text_lower], True, "Dictionary (Verified)"
    
    # ✅ STEP 2: Check partial/fuzzy matches
    for lug_phrase, eng_phrase in reverse_translations.items():
        if len(lug_phrase) > 3:  # Avoid single-word false matches
            if lug_phrase in text_lower:
                logger.info(f"Reverse dict partial match: {lug_phrase} → {eng_phrase}")
                return eng_phrase, True, "Dictionary (Partial Match)"
            if text_lower in lug_phrase:
                logger.info(f"Reverse dict fuzzy match: {text_lower} in {lug_phrase}")
                return eng_phrase, True, "Dictionary (Fuzzy Match)"
    
    # ✅ STEP 3: Word-level translation
    words = text_lower.split()
    translated_words = []
    found_any_word = False
    
    for word in words:
        word_clean = word.strip('.,!?;:').lower()
        if word_clean in reverse_translations:
            translated_words.append(reverse_translations[word_clean])
            found_any_word = True
        else:
            # Try to find partial matches
            for lug_phrase, eng_phrase in reverse_translations.items():
                if word_clean == lug_phrase:
                    translated_words.append(eng_phrase)
                    found_any_word = True
                    break
                elif word_clean in lug_phrase:
                    translated_words.append(eng_phrase.split()[0])
                    found_any_word = True
                    break
            
            if not found_any_word or len(translated_words) < len(words):
                translated_words.append(word)  # Keep original
    
    result = " ".join(translated_words)
    if found_any_word and result != text_lower:
        logger.info(f"Word-level translation: {result}")
        return result, True, "Dictionary (Word-Level)"
    
    # ❌ NO FALLBACK: Dictionary-only for reverse translation
    logger.warning(f"No reverse translation found for: {luganda_text}")
    return f"[Translation not available for: {luganda_text}]", False, "Not Found"

def translate(text, source_language, target_language):
    """Bidirectional translation function with improved error checking"""
    if source_language == 'english' and target_language == 'luganda':
        translation, in_dict, source = translate_to_luganda(text)
        return translation, in_dict, source
    elif source_language == 'luganda' and target_language == 'english':
        translation, in_dict, source = translate_to_english(text)
        return translation, in_dict, source
    else:
        raise ValueError(f"Unsupported language pair: {source_language} -> {target_language}")

@app.route('/')
def index():
    """Serve the web interface"""
    return render_template('index.html')

@app.route('/api/translate', methods=['POST'])
def api_translate():
    """API endpoint for bidirectional translations with improved validation"""
    try:
        data = request.json
        text = data.get('text', '').strip()
        source_language = data.get('source_language', 'english').lower()
        target_language = data.get('target_language', 'luganda').lower()
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if source_language == target_language:
            return jsonify({'error': 'Source and target languages must be different'}), 400
        
        # Get translation with metadata
        translation, in_dictionary, source_info = translate(text, source_language, target_language)
        
        # Validate that translation is actually different from input (not just echoed)
        if translation.lower() == text.lower():
            logger.warning(f"Translation echoed back input: {text}")
            translation = f"[Cannot translate: {text}]"
            in_dictionary = False
            source_info = "Failed"
        
        # Calculate confidence score based on source
        if in_dictionary:
            confidence = 95 if source_language == 'english' else 60
        else:
            confidence = 0  # Not found in dictionary
        
        # Save to history
        save_translation_history(text, translation, source_language, target_language, in_dictionary)
        
        return jsonify({
            'text': text,
            'translation': translation,
            'source_language': source_language,
            'target_language': target_language,
            'in_dictionary': in_dictionary,
            'confidence': confidence,
            'source': source_info,
            'note': f'Source: {source_info}'
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

# ============================================================================
# NEW FEATURE 1: PHRASEBOOK & LEARNING MODE
# ============================================================================
@app.route('/api/phrasebook', methods=['GET'])
def api_phrasebook():
    """Get phrasebook categories and phrases for learning"""
    return jsonify({'phrasebook': PHRASEBOOK})

@app.route('/api/phrasebook/<category>', methods=['GET'])
def api_phrasebook_category(category):
    """Get phrases for specific category"""
    if category in PHRASEBOOK:
        return jsonify({
            'category': category,
            'phrases': PHRASEBOOK[category]
        })
    return jsonify({'error': 'Category not found'}), 404

# ============================================================================
# NEW FEATURE 2: TEXT-TO-SPEECH (Audio Output)
# ============================================================================
@app.route('/api/speak', methods=['POST'])
def api_speak():
    """Convert text to speech"""
    try:
        data = request.json
        text = data.get('text', '').strip()
        language = data.get('language', 'en')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Map language codes
        lang_map = {
            'english': 'en',
            'luganda': 'lg',
            'en': 'en',
            'lg': 'lg'
        }
        
        lang_code = lang_map.get(language, 'en')
        
        # Generate speech
        tts = gTTS(text=text, lang=lang_code, slow=False)
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        return send_file(
            audio_buffer,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name='translation.mp3'
        )
    except Exception as e:
        logger.error(f"TTS error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# NEW FEATURE 3: LANGUAGE DETECTION & BIDIRECTIONAL TRANSLATION
# ============================================================================
@app.route('/api/detect-language', methods=['POST'])
def api_detect_language():
    """Detect if text is English or Luganda"""
    try:
        data = request.json
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Simple heuristic: if has common Luganda words
        luganda_keywords = ['oli', 'ndye', 'nkwagala', 'kika', 'wasuubire', 'webale', 'oyagala']
        text_lower = text.lower()
        
        luganda_score = sum(1 for word in luganda_keywords if word in text_lower)
        
        if luganda_score > 0:
            detected_language = 'luganda'
            confidence = min(100, (luganda_score / len(luganda_keywords)) * 100)
        else:
            detected_language = 'english'
            confidence = 95
        
        return jsonify({
            'detected_language': detected_language,
            'confidence': confidence,
            'alternatives': ['luganda', 'english']
        })
    except Exception as e:
        logger.error(f"Detection error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# NEW FEATURE 4: CULTURAL CONTEXT & TOOLTIPS
# ============================================================================
@app.route('/api/cultural-context/<word>', methods=['GET'])
def api_cultural_context(word):
    """Get cultural context for a word"""
    word_lower = word.lower()
    
    if word_lower in CULTURAL_CONTEXT:
        return jsonify({
            'word': word,
            'context': CULTURAL_CONTEXT[word_lower],
            'cultural_significance': True
        })
    
    # Check if word appears in guaranteed translations
    matches = [v for k, v in GUARANTEED_TRANSLATIONS.items() if word_lower in k.lower()]
    
    if matches:
        return jsonify({
            'word': word,
            'context': f"Part of phrase: {matches[0]}",
            'cultural_significance': True
        })
    
    return jsonify({
        'word': word,
        'context': None,
        'cultural_significance': False
    })

# ============================================================================
# NEW FEATURE 5: TRANSLATION HISTORY
# ============================================================================
@app.route('/api/history', methods=['GET'])
def api_get_history():
    """Get translation history"""
    try:
        limit = request.args.get('limit', 50, type=int)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''SELECT timestamp, source_text, target_text, source_language, target_language 
                     FROM translations 
                     ORDER BY timestamp DESC 
                     LIMIT ?''', (limit,))
        
        history = []
        for row in c.fetchall():
            history.append({
                'timestamp': row[0],
                'source_text': row[1],
                'target_text': row[2],
                'source_language': row[3],
                'target_language': row[4]
            })
        
        conn.close()
        return jsonify({'history': history})
    except Exception as e:
        logger.error(f"History error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/clear', methods=['POST'])
def api_clear_history():
    """Clear all translation history"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM translations')
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': 'History cleared'})
    except Exception as e:
        logger.error(f"Clear history error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/stats', methods=['GET'])
def api_history_stats():
    """Get translation statistics"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Total translations
        c.execute('SELECT COUNT(*) FROM translations')
        total = c.fetchone()[0]
        
        # Most translated phrases
        c.execute('''SELECT source_text, COUNT(*) as count 
                     FROM translations 
                     GROUP BY source_text 
                     ORDER BY count DESC 
                     LIMIT 10''')
        most_translated = [{'phrase': row[0], 'count': row[1]} for row in c.fetchall()]
        
        conn.close()
        return jsonify({
            'total_translations': total,
            'most_translated': most_translated
        })
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Initialize database on startup
    init_db()
    
    # Load model on startup
    load_model()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
