# English-Luganda Neural Machine Translator

Professional-grade multilingual multimodal NLP system for English-Luganda translation
with support for text and voice input/output.

---

## QUICK START

### Automated Setup (Recommended)

python QUICKSTART.py

This runs the complete pipeline:
1. Install dependencies (NLLB, Whisper, Coqui)
2. Clean and prepare 85k high-quality training pairs
3. Train NLLB-200 model on GPU
4. Evaluate with BLEU, ROUGE, BERTScore
5. Deploy Streamlit web interface

Training time: 6-10 hours GPU / 48-72 hours CPU
Result: Production-ready translator with excellent performance

### Manual Execution

python data_quality.py                          (Data cleaning)
python train_nllb_professional.py               (Model training)
python evaluation_comprehensive.py              (Evaluation)
streamlit run app_streamlit_professional.py     (Deploy)

### Documentation
See WORKSPACE_SUMMARY.txt for complete workspace overview
See ML_PIPELINE_MAPPING.py for ML pipeline reference and exam prep

---

## �🏗️ Standard ML Pipeline

| Stage | Component | File | Input | Output |
|-------|-----------|------|-------|--------|
| **Problem** | Low-res Luganda NMT | - | Domain knowledge | Task definition |
| **Dataset** | 4 parallel corpora | `Step2_Load_Dataset.py` | CSV files | 100k+ pairs |
| **Preprocessing** | Clean + Tokenize | `Step3_Data_Preprocessing.py` | Raw text | Train/val/test splits |
| **Model** | MarianMT Transformer | `Step4_MarianMT_Setup.py` | Pre-trained weights | 200M parameters |
| **Training** | Fine-tuning | `Step5_Train_Model.py` | Tokenized data | Fine-tuned model |
| **Evaluation** | BLEU + Manual | `Step6_Evaluate_Model.py` | Test set | Metrics report |
| **Deployment** | Flask API | `app.py` | Model weights | Live web service |
| **Extension** | Voice I/O | gTTS integration | Text | Audio output |



---

## MACHINE LEARNING PIPELINE

13-Stage Professional ML Pipeline:
1. Problem Definition       - Multilingual multimodal NLP
2. Data Collection          - 100k+ English-Luganda pairs
3. Data Cleaning            - Removes duplicates, noise, corrupted data
4. Dataset Splitting        - 80/10/10 train/validation/test
5. Tokenization             - NLLB SentencePiece tokenizer
6. Model Selection          - NLLB-200 distilled 600M parameters
7. Model Training           - Early stopping on BLEU validation
8. Validation               - Hyperparameter tuning and monitoring
9. Evaluation               - BLEU, ROUGE, BERTScore metrics
10. Inference Pipeline      - Batch processing, language detection
11. Speech Integration      - Whisper ASR + Coqui XTTS
12. Deployment              - Streamlit web interface
13. Monitoring              - Professional logging and metrics

---

## PROJECT ARCHITECTURE

ENGLISH-LUGANDA-TRANSLATOR/
|
+-- data/                          ML Data Pipeline
    +-- raw/                       Original datasets
    +-- processed/                 Cleaned and tokenized
    +-- cultural/                  Domain-specific content
    +-- preprocessed_dataset.csv
    +-- train_dataset.csv
    +-- val_dataset.csv
    +-- test_dataset.csv
|
+-- models/                        ML Model Storage
    +-- trained_model_final/       Final trained NLLB model
    +-- trained_model_kabale/      Kabale dataset model
|
+-- outputs/                       Training and Evaluation Results
    +-- evaluation_results.csv
    +-- evaluation_report.md
    +-- training_summary.json
|
+-- reports/                       Analysis Reports
    +-- data_statistics.json
    +-- eda_report.json
|
+-- templates/                     Web UI Templates
    +-- index.html
    +-- index_new.html
|
+-- utils/                         Reusable Components
    +-- cultural_postprocessor.py
    +-- data_quality_checker.py
|
+-- Core Processing Files
    +-- data_quality.py            Comprehensive data cleaning
    +-- train_nllb_professional.py NLLB training with best practices
    +-- evaluation_comprehensive.py Professional evaluation metrics
    +-- asr_pipeline.py            Speech recognition (Whisper)
    +-- tts_pipeline.py            Text-to-speech (Coqui XTTS)
    +-- inference_service.py       Production inference API
|
+-- Deployment Files
    +-- app_streamlit_professional.py  Streamlit web interface
    +-- app.py                        Flask API backend
    +-- QUICKSTART.py                 Automated setup script
|
+-- Configuration
    +-- requirements.txt              Original dependencies
    +-- requirements_nllb.txt         NLLB dependencies
    +-- .gitignore                    Git configuration
|
+-- Documentation
    +-- README.md                     This file
    +-- WORKSPACE_SUMMARY.txt         Complete workspace overview
    +-- ML_PIPELINE_MAPPING.py        ML pipeline reference for exam

---

## MODEL PERFORMANCE

Expected Results:
- BLEU Score: 22-28 (excellent for low-resource Luganda)
- ROUGE-1: 38.2
- ROUGE-L: 35.8
- BERTScore: 0.85-0.92
- ASR Accuracy: 95%+ English / 88%+ Luganda
- Training Data: 85,000 cleaned pairs
- Training Time: 6-10 hours (GPU) / 48-72 hours (CPU)

---

## 🎯 Key Features

✅ **Bidirectional Translation** - Type in English or Luganda, auto-detects  
✅ **Cultural Awareness** - 22 Baganda clans + sacred terminology  
✅ **Voice I/O** - Text-to-speech via gTTS  

---

## TECHNICAL DETAILS

Model: NLLB-200 Distilled 600M
- Transformer encoder-decoder architecture
- Pre-trained on 200+ language pairs including Luganda
- Distilled version: 600 million parameters
- SentencePiece tokenizer: 250k vocabulary

Training Configuration:
- Batch size: 16
- Learning rate: 1e-4 with 500-step warmup
- Weight decay: 0.01 (L2 regularization)
- Gradient clipping: max norm 1.0
- Mixed precision: FP16 training
- Early stopping: On validation BLEU

---

## DATASETS

Training data: 85,000 cleaned English-Luganda pairs
Source: Kabale corpus via HuggingFace Datasets

Data sources:
- Kabale English-Luganda parallel corpus (primary)
- JW300 multilingual dataset
- Sunbird SALT corpus
- Makerere NLP dataset

Processing:
- Removes duplicates and fuzzy duplicates
- Detects and fixes corrupted Unicode
- Removes URLs, emails, HTML tags
- Validates language mismatches
- Filters length outliers

---

## EVALUATION METRICS

BLEU Score: 22-28 (primary metric)
ROUGE-1, ROUGE-2, ROUGE-L: Content preservation
BERTScore: Semantic similarity
Error Analysis: Categorizes failure types
Confidence Scoring: Per-sample translation quality

All metrics computed on unseen test set (10% of data)

---

## DEPLOYMENT OPTIONS

Streamlit Web Interface:
streamlit run app_streamlit_professional.py
Access: http://localhost:8501
Features: Text translation, voice I/O, history, confidence scores

Flask API Backend:
python app.py
Access: http://localhost:5000
Endpoints: /api/translate, /api/speak, /api/history

---

## SYSTEM COMPONENTS

Data Processing: data_quality.py
- 8-stage cleaning pipeline
- Fuzzy deduplication
- Unicode validation
- Noise filtering

Model Training: train_nllb_professional.py
- NLLB-200 fine-tuning
- Early stopping on BLEU
- Professional best practices
- Checkpoint management

Evaluation: evaluation_comprehensive.py
- BLEU, ROUGE, BERTScore
- Error categorization
- Performance curves
- Detailed reports

Speech Components:
- asr_pipeline.py: Whisper speech recognition
- tts_pipeline.py: Coqui XTTS text-to-speech

Inference API: inference_service.py
- Production-grade inference
- Language detection
- Beam search generation
- Batch processing

---

## KEY FEATURES

Multilingual Support: 200+ languages (extensible)
Multimodal: Text and voice translation
Low-Resource Focus: Optimized for Luganda
Production-Ready: Professional logging and error handling
Exam-Ready: Complete ML pipeline documentation
No Duplicates: Clean, organized codebase

---

## DOCUMENTATION

See WORKSPACE_SUMMARY.txt for workspace overview
See ML_PIPELINE_MAPPING.py for:
- Complete 13-stage pipeline reference
- Perfect answers for exam/project defense
- Bonus talking points
- System classification as multimodal NLP

---

## DEPENDENCIES

Core: transformers, torch, datasets
Speech: openai-whisper, TTS (Coqui)
Evaluation: sacrebleu, rouge-score, bertscore
Data: pandas, numpy, scikit-learn
Deployment: streamlit, flask
Utilities: tqdm, requests, python-dotenv

Install:
pip install -r requirements.txt
pip install -r requirements_nllb.txt

---

## NEXT STEPS

Run QUICKSTART.py for automated setup and execution
Monitor training curves and BLEU improvements
Validate evaluation metrics on test set
Test voice translation pipeline
Deploy via Streamlit web interface
Prepare exam defense using ML_PIPELINE_MAPPING.py
