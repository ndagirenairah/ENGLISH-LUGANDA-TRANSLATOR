"""
Configuration file for English-Luganda Translator ML Pipeline
Following Week 2 ML Workflow concepts
"""

from pathlib import Path

# ============================================================================
# PROJECT PATHS
# ============================================================================
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# Create directories if they don't exist
MODELS_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)

# ============================================================================
# DATA CONFIGURATION
# ============================================================================
# Source datasets (Week 2: Data Loading)
RAW_DATASETS = {
    "kambale": RAW_DATA_DIR / "kambale_train.csv",
    "cultural": RAW_DATA_DIR / "cultural_training.csv",
    "jw300": RAW_DATA_DIR / "jw300_parallel.csv",
    "makerere": RAW_DATA_DIR / "makerere_nlp.csv",
    "sunbird": RAW_DATA_DIR / "sunbird_salt.csv",
}

# Data preprocessing settings
TEXT_MIN_LENGTH = 3
TEXT_MAX_LENGTH = 256

# ============================================================================
# TRAINING CONFIGURATION
# ============================================================================
# Model settings
MODEL_NAME = "Helsinki-NLP/opus-mt-en-mul"  # Base model
DEVICE = "cuda"  # or "cpu"

# Training hyperparameters (Week 2: ML Pipeline)
BATCH_SIZE = 8
LEARNING_RATE = 3e-5
NUM_EPOCHS = 8
MAX_SOURCE_LENGTH = 128
MAX_TARGET_LENGTH = 128

# Regularization (Week 3: Dropout, L2)
DROPOUT = 0.1
ATTENTION_DROPOUT = 0.1
WEIGHT_DECAY = 0.01
LABEL_SMOOTHING = 0.1
LR_SCHEDULER = "cosine"

# Learning rate scheduler (Week 3 concepts)
WARMUP_STEPS = 1000
GRADIENT_ACCUMULATION_STEPS = 2

# ============================================================================
# EVALUATION CONFIGURATION (Week 6: Metrics)
# ============================================================================
# Test set evaluation
TEST_SET_FRACTION = 0.1  # 10% for testing
VAL_SET_FRACTION = 0.1   # 10% for validation
RANDOM_SEED = 42

# Evaluation metrics (Week 6: Cross-validation, Performance Metrics)
MAX_EVAL_SAMPLES = 500  # Evaluate on first 500 samples
BLEU_METRIC = "sacrebleu"

# ============================================================================
# OUTPUT CONFIGURATION
# ============================================================================
TRAIN_OUTPUT_DIR = MODELS_DIR / "trained_model"
EVAL_OUTPUT_FILE = OUTPUTS_DIR / "evaluation_results.json"
PREDICTIONS_FILE = OUTPUTS_DIR / "predictions.csv"
METRICS_FILE = OUTPUTS_DIR / "metrics.json"

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
LOG_INTERVAL = 50  # Log every N steps
EVAL_STEPS = 200   # Evaluate every N steps
SAVE_STEPS = 500   # Save checkpoint every N steps
