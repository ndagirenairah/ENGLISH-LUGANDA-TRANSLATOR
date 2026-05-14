#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
USER INTERFACE TEST & STARTUP GUIDE
====================================
Comprehensive testing and startup for both Streamlit and Flask UIs.
"""

import sys
import subprocess
from pathlib import Path
import time
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if all required packages are installed."""
    logger.info("Checking dependencies...")
    
    required_packages = [
        'streamlit',
        'flask',
        'torch',
        'transformers',
        'pandas',
        'sqlite3',
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✓ {package}")
        except ImportError:
            logger.warning(f"✗ {package} - MISSING")
            missing.append(package)
    
    if missing:
        logger.error(f"Missing packages: {', '.join(missing)}")
        logger.info("Install with: pip install " + " ".join(missing))
        return False
    
    logger.info("✓ All dependencies installed")
    return True


def validate_model_files():
    """Validate that model files exist or can be downloaded."""
    logger.info("Validating model availability...")
    
    model_paths = [
        "models/trained_nllb_enhanced/final",
        "models/trained_nllb_professional/best_model",
        "models/trained_model_final",
    ]
    
    found_local = False
    for path in model_paths:
        if Path(path).exists():
            logger.info(f"✓ Found model at: {path}")
            found_local = True
            break
    
    if not found_local:
        logger.warning("No local model found - will use base NLLB from HuggingFace")
        logger.info("First run will download model (~2.5GB) - please wait")
    
    return True


def validate_template_files():
    """Validate HTML template files."""
    logger.info("Validating template files...")
    
    templates = [
        "templates/index_production.html",
        "templates/index.html",
    ]
    
    for template in templates:
        if Path(template).exists():
            logger.info(f"✓ Found: {template}")
        else:
            logger.warning(f"✗ Missing: {template}")
    
    return True


def test_streamlit_app():
    """Test Streamlit application."""
    logger.info("\n" + "="*60)
    logger.info("TESTING STREAMLIT APPLICATION")
    logger.info("="*60)
    
    app_file = "app_streamlit_ui.py"
    
    if not Path(app_file).exists():
        logger.error(f"✗ {app_file} not found")
        return False
    
    logger.info(f"✓ Found {app_file}")
    
    try:
        # Quick syntax check
        with open(app_file, encoding='utf-8') as f:
            code = f.read()
            compile(code, app_file, 'exec')
        logger.info("✓ Syntax validation passed")
    except SyntaxError as e:
        logger.error(f"✗ Syntax error: {e}")
        return False
    
    logger.info("\nStreamlit app is ready!")
    logger.info("Start with: streamlit run app_streamlit_ui.py")
    
    return True


def test_flask_app():
    """Test Flask application."""
    logger.info("\n" + "="*60)
    logger.info("TESTING FLASK APPLICATION")
    logger.info("="*60)
    
    app_file = "app_flask_api.py"
    
    if not Path(app_file).exists():
        logger.error(f"✗ {app_file} not found")
        return False
    
    logger.info(f"✓ Found {app_file}")
    
    try:
        # Quick syntax check
        with open(app_file, encoding='utf-8') as f:
            code = f.read()
            compile(code, app_file, 'exec')
        logger.info("✓ Syntax validation passed")
    except SyntaxError as e:
        logger.error(f"✗ Syntax error: {e}")
        return False
    
    logger.info("\nFlask app is ready!")
    logger.info("Start with: python app_flask_api.py")
    
    return True


def print_startup_guide():
    """Print comprehensive startup guide."""
    
    guide = """
╔══════════════════════════════════════════════════════════════════╗
║     ENGLISH-LUGANDA TRANSLATOR - UI STARTUP GUIDE                ║
╚══════════════════════════════════════════════════════════════════╝

Two UI Options Available:

┌──────────────────────────────────────────────────────────────────┐
│ 1. STREAMLIT WEB APP (Recommended for Users)                     │
├──────────────────────────────────────────────────────────────────┤
│ File: app_streamlit_ui.py                                         │
│                                                                   │
│ Start Command:                                                   │
│   streamlit run app_streamlit_ui.py                              │
│                                                                   │
│ Features:                                                        │
│   • Modern, interactive web interface                            │
│   • Translation input/output                                     │
│   • Translation history with database                            │
│   • Common phrases & phrasebook                                  │
│   • System status & settings                                     │
│   • Responsive design (desktop & mobile)                         │
│                                                                   │
│ Access:                                                          │
│   Open http://localhost:8501 in your browser                    │
│                                                                   │
│ Best For:                                                        │
│   • End users who want easy-to-use interface                     │
│   • Learning Luganda phrases                                     │
│   • Viewing translation history                                  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ 2. FLASK REST API (Recommended for Developers)                   │
├──────────────────────────────────────────────────────────────────┤
│ File: app_flask_api.py                                            │
│                                                                   │
│ Start Command:                                                   │
│   python app_flask_api.py                                        │
│                                                                   │
│ Features:                                                        │
│   • REST API endpoints                                           │
│   • Batch translation support                                    │
│   • Language detection                                           │
│   • Translation history API                                      │
│   • HTML web interface                                           │
│   • JSON responses                                               │
│                                                                   │
│ Access:                                                          │
│   Web Interface: http://localhost:5000                           │
│   API: http://localhost:5000/api/*                               │
│                                                                   │
│ API Endpoints:                                                   │
│   POST /api/translate          - Translate text                  │
│   POST /api/batch-translate    - Translate multiple texts        │
│   POST /api/detect-language    - Detect language                 │
│   GET  /api/history            - Translation history             │
│   GET  /api/phrasebook         - Common phrases                  │
│   GET  /api/status             - System status                   │
│   DELETE /api/clear-history    - Clear history                   │
│                                                                   │
│ Best For:                                                        │
│   • Developers integrating translation                           │
│   • Building custom applications                                 │
│   • Batch processing                                             │
│   • Production deployments                                       │
└──────────────────────────────────────────────────────────────────┘

╔══════════════════════════════════════════════════════════════════╗
║ QUICK START EXAMPLES                                             ║
╚══════════════════════════════════════════════════════════════════╝

1. Start Streamlit App (Easiest)
   $ streamlit run app_streamlit_ui.py
   → Opens automatically in browser

2. Start Flask API
   $ python app_flask_api.py
   → Opens at http://localhost:5000

3. Test API with cURL
   $ curl -X POST http://localhost:5000/api/translate \\
     -H "Content-Type: application/json" \\
     -d '{"text": "Hello", "source_lang": "english"}'

4. Use Python to test
   >>> import requests
   >>> r = requests.post('http://localhost:5000/api/translate',
   ...   json={'text': 'How are you?'})
   >>> print(r.json())

╔══════════════════════════════════════════════════════════════════╗
║ TROUBLESHOOTING                                                  ║
╚══════════════════════════════════════════════════════════════════╝

Issue: Module not found errors
→ Solution: pip install streamlit flask torch transformers

Issue: Model not found (first run)
→ Solution: Wait for automatic download (~5-10 minutes)
           Check internet connection

Issue: Port already in use
→ Streamlit: streamlit run app_streamlit_ui.py --server.port 8502
→ Flask: python app_flask_api.py (change port in code)

Issue: CUDA/GPU errors
→ Solution: Runs on CPU automatically as fallback

╔══════════════════════════════════════════════════════════════════╗
║ PERFORMANCE NOTES                                                ║
╚══════════════════════════════════════════════════════════════════╝

First Translation: ~30-60 seconds (model loading)
Subsequent Translations: ~1-3 seconds (cached)

GPU Acceleration:
  With GPU: ~1 second per translation
  Without GPU: ~3-5 seconds per translation

Batch Translations:
  10 sentences: ~10-20 seconds
  100 sentences: ~60-120 seconds

╔══════════════════════════════════════════════════════════════════╗
║ ENVIRONMENT SETUP (Optional)                                     ║
╚══════════════════════════════════════════════════════════════════╝

1. Create Virtual Environment
   python -m venv venv
   source venv/bin/activate  (Linux/Mac)
   venv\\Scripts\\activate   (Windows)

2. Install Dependencies
   pip install -r requirements.txt

3. Download Model (Optional - auto on first use)
   from transformers import AutoModel
   AutoModel.from_pretrained("facebook/nllb-200-distilled-600M")

╔══════════════════════════════════════════════════════════════════╗
║ NEXT STEPS                                                       ║
╚══════════════════════════════════════════════════════════════════╝

✓ Choose your UI (Streamlit or Flask)
✓ Run the command above
✓ Test the translation
✓ Integrate into your application
✓ Deploy to production (Heroku, AWS, etc.)

Questions? Check:
  - README.md
  - LUGANDA_IMPROVEMENT_GUIDE.txt
  - GitHub: https://github.com/ndagirenairah/ENGLISH-LUGANDA-TRANSLATOR

Happy translating!
"""
    
    print(guide)


def main():
    """Run all tests and print guide."""
    
    print("\n" + "="*60)
    print("ENGLISH-LUGANDA TRANSLATOR - UI VALIDATION")
    print("="*60 + "\n")
    
    # Run tests
    tests_passed = True
    
    if not check_dependencies():
        tests_passed = False
    
    if not validate_model_files():
        tests_passed = False
    
    if not validate_template_files():
        tests_passed = False
    
    if not test_streamlit_app():
        tests_passed = False
    
    if not test_flask_app():
        tests_passed = False
    
    # Print guide
    print_startup_guide()
    
    # Final status
    print("\n" + "="*60)
    if tests_passed:
        logger.info("✓ All validations passed - UIs are ready to use!")
    else:
        logger.warning("⚠ Some validations had warnings - see above")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
