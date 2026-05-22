# Architecture & Data Flow Diagram

## Complete Training Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ENGLISH-LUGANDA TRANSLATOR                               │
│                   Kambale + Combined Dataset Training                       │
└─────────────────────────────────────────────────────────────────────────────┘

                              EXECUTION FLOW
                              ──────────────

┌──────────────────────────────────────────────────────────────────────────────┐
│                         STEP 1: ENVIRONMENT SETUP                            │
├──────────────────────────────────────────────────────────────────────────────┤
│ Google Colab                                                                 │
│ ├─ GPU: Tesla T4 (~16GB VRAM)                                               │
│ ├─ Python 3.8+                                                              │
│ └─ CUDA enabled                                                             │
└──────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│                      STEP 2: REPOSITORY CLONE                               │
├──────────────────────────────────────────────────────────────────────────────┤
│ GitHub: ndagirenairah/ENGLISH-LUGANDA-TRANSLATOR                            │
│ ├─ Clone to: /content/translator/                                           │
│ ├─ All scripts downloaded                                                   │
│ └─ Data files available                                                     │
└──────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│                    STEP 3: DATASET COMBINATION                              │
├──────────────────────────────────────────────────────────────────────────────┤
│ combine_datasets_with_token.py (Executed automatically)                    │
│                                                                              │
│ INPUT DATASETS:                                                              │
│ ┌────────────────────────────────────────────────────────────────────────┐  │
│ │ 1. Kambale Corpus (gated HF dataset)                                   │  │
│ │    ├─ 100k+ professional translation pairs                            │  │
│ │    ├─ Access: HF token authentication                                 │  │
│ │    └─ Quality: HIGH (curated corpus)                                  │  │
│ │                                                                        │  │
│ │ 2. Cultural Dictionary (local CSV)                                    │  │
│ │    ├─ Domain-specific phrases                                         │  │
│ │    └─ Quality: HIGH (curated by team)                                 │  │
│ │                                                                        │  │
│ │ 3. JW300 Parallel Corpus (local CSV)                                  │  │
│ │    ├─ Religious & cultural texts                                      │  │
│ │    └─ Quality: MEDIUM-HIGH                                            │  │
│ │                                                                        │  │
│ │ 4. Makerere NLP (local CSV)                                           │  │
│ │    ├─ University corpus                                               │  │
│ │    └─ Quality: MEDIUM                                                 │  │
│ │                                                                        │  │
│ │ 5. Sunbird Salt (local CSV)                                           │  │
│ │    ├─ Additional parallel data                                        │  │
│ │    └─ Quality: MEDIUM                                                 │  │
│ └────────────────────────────────────────────────────────────────────────┘  │
│                                    ↓                                         │
│ DATA PROCESSING:                                                             │
│ ├─ Detect column formats ('english'/'luganda' vs 'en'/'lg')                 │
│ ├─ Normalize all columns to 'english'/'luganda'                            │
│ ├─ Deduplicate: Remove duplicate (english.lower(), luganda.lower()) pairs  │
│ ├─ Clean: Remove <2 word sentences                                        │
│ ├─ Clean: Remove >50 word sentences                                       │
│ ├─ Combine: Merge all valid pairs                                         │
│ └─ Split: 80% train, 10% val, 10% test (seed=42)                         │
│                                    ↓                                         │
│ OUTPUT: data/combined_kambale/                                              │
│ ├─ train.csv (80% ≈ 280-400 pairs)                                         │
│ ├─ val.csv (10% ≈ 35-50 pairs)                                             │
│ ├─ test.csv (10% ≈ 35-50 pairs)                                            │
│ └─ stats.json (source breakdown, token stats)                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│                       STEP 4: MODEL INITIALIZATION                          │
├──────────────────────────────────────────────────────────────────────────────┤
│ Model: Helsinki-NLP/opus-mt-en-mul                                          │
│ ├─ Base Model: MarianMT (Multilingual English→Multiple)                     │
│ ├─ Parameters: 300M                                                         │
│ ├─ Download: ~600MB (first time only, then cached)                         │
│ ├─ Tokenizer: AutoTokenizer                                                │
│ │  ├─ Max length: 128 tokens                                              │
│ │  ├─ Padding: max_length                                                │
│ │  └─ Truncation: enabled                                                │
│ ├─ Device: GPU (CUDA)                                                      │
│ └─ Precision: float32                                                      │
└──────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│                         STEP 5: TRAINING                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│ Seq2SeqTrainer Configuration:                                               │
│ ├─ Epochs: 3                                                               │
│ ├─ Batch size: 8 (train) / 8 (eval)                                       │
│ ├─ Learning rate: 2e-5 (fine-tuning rate)                                 │
│ ├─ Warmup steps: 500                                                       │
│ ├─ Scheduler: linear warmup + linear decay                                │
│ ├─ Optimizer: AdamW (default)                                             │
│ ├─ Save strategy: epoch (save after each epoch)                           │
│ ├─ Eval strategy: epoch (evaluate after each epoch)                       │
│ ├─ Logging: every 50 steps                                                │
│ └─ Predict with generate: True                                            │
│                                                                             │
│ TRAINING LOOP:                                                              │
│ Epoch 1/3                                                                  │
│ ├─ Training steps: ≈35-50 steps                                           │
│ ├─ Validation: Compute loss                                               │
│ └─ Save checkpoint                                                         │
│                                                                             │
│ Epoch 2/3                                                                  │
│ ├─ Training steps: ≈35-50 steps                                           │
│ ├─ Validation: Compute loss                                               │
│ └─ Save checkpoint                                                         │
│                                                                             │
│ Epoch 3/3                                                                  │
│ ├─ Training steps: ≈35-50 steps                                           │
│ ├─ Validation: Compute loss                                               │
│ └─ Save final model                                                        │
└──────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│                       STEP 6: EVALUATION                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│ Test Set Evaluation (10% ≈ 35-50 pairs):                                   │
│ ├─ Model generates translations for all test pairs                         │
│ ├─ Use generation parameters:                                             │
│ │  ├─ max_length: 120                                                    │
│ │  ├─ num_beams: 5 (beam search)                                         │
│ │  └─ no_repeat_ngram_size: 3                                            │
│ ├─ Decode predictions and references                                      │
│ ├─ Calculate BLEU score using sacrebleu                                  │
│ └─ Generate sample predictions (first 5)                                  │
│                                                                             │
│ BLEU SCORE RANGE:                                                           │
│ Expected: 25-35 (good to excellent quality)                               │
│ ├─ < 20: Poor quality (need more data)                                    │
│ ├─ 20-25: Baseline (acceptable start)                                     │
│ ├─ 25-30: Good quality ✓ (ready for use)                                 │
│ ├─ 30-35: Excellent quality ✓✓ (production ready)                        │
│ └─ > 35: Exceptional ✓✓✓ (state-of-art)                                  │
└──────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│                    STEP 7: MODEL SAVE & METRICS                             │
├──────────────────────────────────────────────────────────────────────────────┤
│ Model Save:                                                                  │
│ └─ Path: /content/translator/models/kambale_combined_model/                │
│    ├─ config.json (model configuration)                                    │
│    ├─ pytorch_model.bin (model weights - 600MB)                           │
│    ├─ sentencepiece.bpe.model (tokenizer)                                 │
│    └─ source.spm, target.spm (language models)                            │
│                                                                             │
│ Metrics Save & Download:                                                   │
│ └─ File: metrics_kambale_combined.json                                     │
│    ├─ bleu_score: XX.XX                                                   │
│    ├─ training_loss: X.XXXX                                               │
│    ├─ train_samples: (count)                                              │
│    ├─ val_samples: (count)                                                │
│    ├─ test_samples: (count)                                               │
│    ├─ dataset: "kambale_combined_local"                                   │
│    ├─ model: "Helsinki-NLP/opus-mt-en-mul"                               │
│    └─ timestamp: (ISO timestamp)                                          │
└──────────────────────────────────────────────────────────────────────────────┘
                                    ↓
                    ✅ TRAINING COMPLETE & SUCCESSFUL


═══════════════════════════════════════════════════════════════════════════════
                            SAMPLE TRANSLATION FLOW
═══════════════════════════════════════════════════════════════════════════════

ENGLISH INPUT: "Good morning, how are you?"
       ↓
[Tokenizer] Encode to token IDs (max 128)
       ↓
[Model Encoder] Process English tokens → Context vectors
       ↓
[Model Decoder] Generate Luganda tokens (beam search, num_beams=5)
       ↓
[Tokenizer] Decode tokens → Luganda text
       ↓
LUGANDA OUTPUT: "Olubiimu, olyegeeka?"

═══════════════════════════════════════════════════════════════════════════════
                              OUTPUT ARTIFACTS
═══════════════════════════════════════════════════════════════════════════════

LOCAL WORKSPACE:
├─ data/combined_kambale/
│  ├─ train.csv (80% pairs)
│  ├─ val.csv (10% pairs)
│  ├─ test.csv (10% pairs)
│  └─ stats.json (dataset statistics)
├─ models/kambale_combined_model/ (trained model)
│  ├─ config.json
│  ├─ pytorch_model.bin (600MB)
│  ├─ sentencepiece.bpe.model
│  ├─ source.spm
│  └─ target.spm
└─ results/ (training checkpoints)
   ├─ checkpoint-*/
   └─ training_args.bin

DOWNLOADS (from Colab):
└─ metrics_kambale_combined.json

═══════════════════════════════════════════════════════════════════════════════
                              TIMELINE ESTIMATE
═══════════════════════════════════════════════════════════════════════════════

Minute  0:  Start Cell 2 execution
Minute  1:  GPU verification, package installation
Minute  2:  HF token prompt
Minute  3:  Kambale dataset download starts
Minute  5:  Local datasets loaded, combination starts
Minute  8:  Dataset ready (deduped, split)
Minute  9:  Model download (600MB)
Minute 10:  Model loaded to GPU
Minute 11:  Training starts (Epoch 1)
Minute 14:  Epoch 1 complete
Minute 17:  Epoch 2 complete
Minute 20:  Epoch 3 complete + Evaluation
Minute 21:  Model save + metrics download
Minute 21:  ✅ COMPLETE

═══════════════════════════════════════════════════════════════════════════════
                            SUCCESS INDICATORS
═══════════════════════════════════════════════════════════════════════════════

✅ Training successful when:
   1. No errors in execution
   2. All 3 epochs complete
   3. BLEU score printed (should be 25+)
   4. Model folder created
   5. metrics_kambale_combined.json downloaded

⚠️  If any errors:
   - Check HF token validity
   - Check internet connection
   - Review TRAINING_CHECKLIST.md for troubleshooting

═══════════════════════════════════════════════════════════════════════════════
