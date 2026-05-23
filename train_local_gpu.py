#!/usr/bin/env python3
"""Train MarianMT models for English <-> Luganda using Hugging Face + PyTorch."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

import evaluate
import numpy as np
import pandas as pd
import torch
from datasets import Dataset
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    DataCollatorForSeq2Seq,
    EarlyStoppingCallback,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
)


DEFAULT_MODELS = {
    "en-lg": "Helsinki-NLP/opus-mt-en-lg",
    "lg-en": "Helsinki-NLP/opus-mt-lg-en",
}

FALLBACK_MODELS = {
    "en-lg": "Helsinki-NLP/opus-mt-en-mul",
    "lg-en": "Helsinki-NLP/opus-mt-mul-en",
}


def get_source_target_columns(direction: str) -> Tuple[str, str]:
    if direction == "en-lg":
        return "english", "luganda"
    if direction == "lg-en":
        return "luganda", "english"
    raise ValueError(f"Unsupported direction: {direction}")


def load_split_csv(path: Path) -> Dataset:
    df = pd.read_csv(path)
    required = {"english", "luganda"}
    if not required.issubset(df.columns):
        raise ValueError(f"{path} must contain columns: {required}")
    return Dataset.from_pandas(df[["english", "luganda"]], preserve_index=False)


def resolve_model_ref(direction: str, requested: str | None) -> str:
    if requested:
        return requested
    return DEFAULT_MODELS[direction]


def build_tokenized_dataset(dataset: Dataset, tokenizer: AutoTokenizer, direction: str, max_length: int) -> Dataset:
    src_col, tgt_col = get_source_target_columns(direction)

    def preprocess_batch(batch: Dict[str, List[str]]) -> Dict[str, List[List[int]]]:
        model_inputs = tokenizer(
            batch[src_col],
            max_length=max_length,
            truncation=True,
            padding=False,
        )
        labels = tokenizer(
            text_target=batch[tgt_col],
            max_length=max_length,
            truncation=True,
            padding=False,
        )
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    return dataset.map(preprocess_batch, batched=True, remove_columns=dataset.column_names)


def train_direction(
    direction: str,
    data_dir: Path,
    output_root: Path,
    model_name: str | None,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    max_source_length: int,
    max_target_length: int,
    gradient_accumulation_steps: int,
    save_steps: int,
    eval_steps: int,
) -> Dict[str, float]:
    model_ref = resolve_model_ref(direction, model_name)

    try:
        tokenizer = AutoTokenizer.from_pretrained(model_ref)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_ref)
    except Exception:
        fallback = FALLBACK_MODELS[direction]
        tokenizer = AutoTokenizer.from_pretrained(fallback)
        model = AutoModelForSeq2SeqLM.from_pretrained(fallback)

    train_ds = load_split_csv(data_dir / "train.csv")
    val_ds = load_split_csv(data_dir / "val.csv")
    test_ds = load_split_csv(data_dir / "test.csv")

    # Use source/target max lengths independently for safer truncation behavior.
    src_col, tgt_col = get_source_target_columns(direction)

    def preprocess_batch(batch: Dict[str, List[str]]) -> Dict[str, List[List[int]]]:
        model_inputs = tokenizer(
            batch[src_col],
            max_length=max_source_length,
            truncation=True,
            padding=False,
        )
        labels = tokenizer(
            text_target=batch[tgt_col],
            max_length=max_target_length,
            truncation=True,
            padding=False,
        )
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    tokenized_train = train_ds.map(preprocess_batch, batched=True, remove_columns=train_ds.column_names)
    tokenized_val = val_ds.map(preprocess_batch, batched=True, remove_columns=val_ds.column_names)
    tokenized_test = test_ds.map(preprocess_batch, batched=True, remove_columns=test_ds.column_names)

    bleu_metric = evaluate.load("sacrebleu")

    def compute_metrics(eval_preds):
        preds, labels = eval_preds
        if isinstance(preds, tuple):
            preds = preds[0]

        decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)

        labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
        decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)
        decoded_labels = [[ref] for ref in decoded_labels]

        bleu = bleu_metric.compute(predictions=decoded_preds, references=decoded_labels)
        return {"bleu": float(bleu["score"])}

    direction_root = output_root / direction
    checkpoints_dir = direction_root / "checkpoints"
    final_dir = direction_root / "final"
    direction_root.mkdir(parents=True, exist_ok=True)

    use_cuda = torch.cuda.is_available()
    use_bf16 = use_cuda and torch.cuda.get_device_capability(0)[0] >= 8

    training_args = Seq2SeqTrainingArguments(
        output_dir=str(checkpoints_dir),
        do_train=True,
        do_eval=True,
        learning_rate=learning_rate,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        warmup_ratio=0.1,
        weight_decay=0.01,
        lr_scheduler_type="cosine",
        evaluation_strategy="steps",
        save_strategy="steps",
        eval_steps=eval_steps,
        save_steps=save_steps,
        logging_strategy="steps",
        logging_steps=max(20, min(eval_steps, save_steps) // 2),
        save_total_limit=3,
        predict_with_generate=True,
        generation_max_length=max_target_length,
        generation_num_beams=5,
        load_best_model_at_end=True,
        metric_for_best_model="bleu",
        greater_is_better=True,
        gradient_checkpointing=True,
        fp16=use_cuda and not use_bf16,
        bf16=use_bf16,
        dataloader_num_workers=2 if use_cuda else 0,
        report_to="none",
        seed=42,
    )

    collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        model=model,
        label_pad_token_id=-100,
        pad_to_multiple_of=8 if use_cuda else None,
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_val,
        tokenizer=tokenizer,
        data_collator=collator,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)],
    )

    trainer.train()
    test_metrics = trainer.evaluate(eval_dataset=tokenized_test, metric_key_prefix="test")

    final_dir.mkdir(parents=True, exist_ok=True)
    trainer.model.save_pretrained(final_dir)
    tokenizer.save_pretrained(final_dir)

    with open(direction_root / "metrics.json", "w", encoding="utf-8") as handle:
        json.dump(test_metrics, handle, indent=2)

    return {key: float(value) for key, value in test_metrics.items() if isinstance(value, (int, float))}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train MarianMT for English-Luganda translation")
    parser.add_argument("--data-dir", default="data/processed")
    parser.add_argument("--output-dir", default="models")
    parser.add_argument("--direction", choices=["en-lg", "lg-en", "both"], default="both")
    parser.add_argument("--en-lg-model", default=None)
    parser.add_argument("--lg-en-model", default=None)
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--learning-rate", type=float, default=3e-5)
    parser.add_argument("--max-source-length", type=int, default=192)
    parser.add_argument("--max-target-length", type=int, default=192)
    parser.add_argument("--grad-accum-steps", type=int, default=2)
    parser.add_argument("--save-steps", type=int, default=500)
    parser.add_argument("--eval-steps", type=int, default=500)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data_dir = Path(args.data_dir)
    output_root = Path(args.output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    directions = ["en-lg", "lg-en"] if args.direction == "both" else [args.direction]
    summary: Dict[str, Dict[str, float]] = {}

    for direction in directions:
        print(f"\n=== Training direction: {direction} ===")
        model_override = args.en_lg_model if direction == "en-lg" else args.lg_en_model
        summary[direction] = train_direction(
            direction=direction,
            data_dir=data_dir,
            output_root=output_root,
            model_name=model_override,
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            max_source_length=args.max_source_length,
            max_target_length=args.max_target_length,
            gradient_accumulation_steps=args.grad_accum_steps,
            save_steps=args.save_steps,
            eval_steps=args.eval_steps,
        )

    summary_path = Path("outputs") / "training_summary_transformer.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)

    print("\nTraining complete. Summary saved to outputs/training_summary_transformer.json")


if __name__ == "__main__":
    main()
