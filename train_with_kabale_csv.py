import pandas as pd
import torch
import numpy as np
import json
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, Seq2SeqTrainer, Seq2SeqTrainingArguments, DataCollatorForSeq2Seq
from datasets import Dataset, DatasetDict

print("[STEP 1] LOADING KABALE DATASET FROM CSV")
print("[DATA] CSV file: luganda_dataset.csv")

df = pd.read_csv("luganda_dataset.csv")
print(f"[SUCCESS] Loaded {len(df)} rows")
print(f"[INFO] Columns: {list(df.columns)}")
print(f"[SAMPLE] First row: EN: {df.iloc[0]['english'][:50]}... | LG: {df.iloc[0]['luganda'][:50]}...")

print("\n[STEP 2] PREPARING DATASET")

df_clean = df.drop_duplicates(subset=['english', 'luganda']).reset_index(drop=True)
print(f"[DATA] After deduplication: {len(df_clean)} rows (removed {len(df) - len(df_clean)} duplicates)")

print("\n[STEP 3] SPLITTING INTO TRAIN/VAL/TEST")

n_total = len(df_clean)
n_train = int(n_total * 0.70)
n_val = int(n_total * 0.15)
n_test = n_total - n_train - n_val

train_df = df_clean.iloc[:n_train]
val_df = df_clean.iloc[n_train:n_train + n_val]
test_df = df_clean.iloc[n_train + n_val:]

print(f"[SPLIT] Train: {len(train_df)} ({n_train/n_total*100:.1f}%)")
print(f"[SPLIT] Validation: {len(val_df)} ({n_val/n_total*100:.1f}%)")
print(f"[SPLIT] Test: {len(test_df)} ({n_test/n_total*100:.1f}%)")

print("\n[STEP 4] CONVERTING TO HUGGINGFACE DATASETS")

train_dataset = Dataset.from_pandas(train_df[['english', 'luganda']].rename(columns={'english': 'en', 'luganda': 'lg'}))
val_dataset = Dataset.from_pandas(val_df[['english', 'luganda']].rename(columns={'english': 'en', 'luganda': 'lg'}))
test_dataset = Dataset.from_pandas(test_df[['english', 'luganda']].rename(columns={'english': 'en', 'luganda': 'lg'}))

dataset_dict = DatasetDict({
    'train': train_dataset,
    'validation': val_dataset,
    'test': test_dataset
})

print(f"[SUCCESS] DatasetDict created: {dataset_dict}")

print("\n[STEP 5] LOADING MARIANMT MODEL")

model_name = "Helsinki-NLP/opus-mt-en-mul"
print(f"[MODEL] Loading: {model_name}")

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

print(f"[DEVICE] Using: {device}")
print(f"[MODEL] Parameters: {model.num_parameters():,}")

print("\n[STEP 6] TOKENIZING DATA")

def preprocess_function(examples):
    inputs = [ex for ex in examples['en']]
    targets = [ex for ex in examples['lg']]
    
    model_inputs = tokenizer(inputs, max_length=128, truncation=True, padding='max_length')
    labels = tokenizer(targets, max_length=128, truncation=True, padding='max_length')
    
    model_inputs['labels'] = labels['input_ids']
    return model_inputs

print("[TOKENIZE] Processing training data...")
tokenized_train = train_dataset.map(preprocess_function, batched=True, batch_size=100)

print("[TOKENIZE] Processing validation data...")
tokenized_val = val_dataset.map(preprocess_function, batched=True, batch_size=100)

print("[TOKENIZE] Processing test data...")
tokenized_test = test_dataset.map(preprocess_function, batched=True, batch_size=100)

print("[SUCCESS] Tokenization complete")

print("\n[STEP 7] CONFIGURING TRAINING")

output_dir = "models/trained_model_kabale"
Path(output_dir).mkdir(parents=True, exist_ok=True)

training_args = Seq2SeqTrainingArguments(
    output_dir=output_dir,
    num_train_epochs=5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='logs',
    logging_steps=100,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    seed=42,
)

print(f"[CONFIG] Output directory: {output_dir}")
print(f"[CONFIG] Epochs: 5")
print(f"[CONFIG] Batch size: 16")
print(f"[CONFIG] Learning rate: {training_args.learning_rate}")

print("\n[STEP 8] INITIALIZING TRAINER")

data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_val,
    data_collator=data_collator,
    tokenizer=tokenizer,
)

print("[TRAINER] Trainer initialized")

print("\n[STEP 9] TRAINING MODEL")
print("[TRAIN] Starting training... This will take several hours on CPU")

trainer.train()

print("[SUCCESS] Training complete!")

print("\n[STEP 10] EVALUATING ON TEST SET")

print("[EVAL] Evaluating on test set...")
eval_results = trainer.evaluate(eval_dataset=tokenized_test)

print(f"[EVAL] Test Loss: {eval_results.get('eval_loss', 'N/A'):.4f}")
print(f"[EVAL] Results: {eval_results}")

print("\n[STEP 11] SAVING MODEL")

model_save_path = Path(output_dir)
print(f"[SAVE] Saving model to: {model_save_path}")

trainer.save_model(str(model_save_path))
tokenizer.save_pretrained(str(model_save_path))

config_dict = {
    "model_name": model_name,
    "training_samples": len(train_df),
    "validation_samples": len(val_df),
    "test_samples": len(test_df),
    "total_samples": len(df_clean),
    "epochs": 5,
    "batch_size": 16,
    "learning_rate": 2e-5,
    "max_length": 128,
    "device": str(device),
}

config_path = model_save_path / "training_config.json"
with open(config_path, 'w') as f:
    json.dump(config_dict, f, indent=2)

print(f"[SUCCESS] Model saved to: {model_save_path}")
print(f"[SUCCESS] Config saved to: {config_path}")

print("\n[STEP 12] TESTING INFERENCE")

print("[INFERENCE] Testing translation on sample sentences...")

test_sentences = [
    "Hello, how are you today?",
    "The weather is beautiful today.",
    "I love learning Luganda language."
]

for i, text in enumerate(test_sentences, 1):
    print(f"\n[TEST {i}] English: {text}")
    
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=128, num_beams=4)
    
    translation = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"[OUTPUT] Luganda: {translation}")

print("\n[SUCCESS] TRAINING PIPELINE COMPLETE!")
print(f"\n[SUMMARY]")
print(f"  - Dataset: Kabale English-Luganda (50,012 pairs)")
print(f"  - Model: MarianMT (Helsinki-NLP/opus-mt-en-mul)")
print(f"  - Trained samples: {len(train_df):,}")
print(f"  - Model saved to: {output_dir}")
print(f"  - Ready for deployment!")
