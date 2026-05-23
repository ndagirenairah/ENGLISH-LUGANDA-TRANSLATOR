#!/usr/bin/env python3
"""Evaluate MarianMT English <-> Luganda models with BLEU and sample outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List

import pandas as pd
from sacrebleu import corpus_bleu

from translate_english_luganda import TransformerTranslator


def evaluate_direction(
    translator: TransformerTranslator,
    frame: pd.DataFrame,
    source_col: str,
    target_col: str,
    source_lang: str,
    target_lang: str,
    max_samples: int,
) -> Dict[str, float]:
    subset = frame[[source_col, target_col]].dropna().head(max_samples).copy()

    predictions: List[str] = []
    references: List[List[str]] = []

    for _, row in subset.iterrows():
        source_text = str(row[source_col]).strip()
        target_text = str(row[target_col]).strip()
        if not source_text or not target_text:
            continue

        result = translator.translate(source_text, source_lang=source_lang, target_lang=target_lang)
        predictions.append(result["translation"])
        references.append([target_text])

    if not predictions:
        return {"bleu": 0.0, "count": 0}

    bleu = corpus_bleu(predictions, references)
    return {"bleu": float(bleu.score), "count": len(predictions)}


def generate_samples(translator: TransformerTranslator) -> List[Dict[str, str]]:
    prompts = [
        ("english", "luganda", "How are you today?"),
        ("english", "luganda", "Thank you very much."),
        ("luganda", "english", "Oli otya?"),
        ("luganda", "english", "Webale nnyo"),
    ]

    samples: List[Dict[str, str]] = []
    for source_lang, target_lang, text in prompts:
        out = translator.translate(text, source_lang=source_lang, target_lang=target_lang)
        samples.append(
            {
                "source_lang": source_lang,
                "target_lang": target_lang,
                "input": text,
                "prediction": out["translation"],
            }
        )
    return samples


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate English-Luganda MarianMT models")
    parser.add_argument("--test-csv", default="data/processed/test.csv")
    parser.add_argument("--max-samples", type=int, default=300)
    parser.add_argument("--output", default="outputs/evaluation_report_transformer.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    test_path = Path(args.test_csv)

    if not test_path.exists():
        raise FileNotFoundError(f"Missing test split: {test_path}")

    data = pd.read_csv(test_path)
    required = {"english", "luganda"}
    if not required.issubset(data.columns):
        raise ValueError(f"{test_path} must include columns: {required}")

    translator = TransformerTranslator(
        en_lg_model_path="models/en-lg/final",
        lg_en_model_path="models/lg-en/final",
    )

    en_lg = evaluate_direction(
        translator=translator,
        frame=data,
        source_col="english",
        target_col="luganda",
        source_lang="english",
        target_lang="luganda",
        max_samples=args.max_samples,
    )
    lg_en = evaluate_direction(
        translator=translator,
        frame=data,
        source_col="luganda",
        target_col="english",
        source_lang="luganda",
        target_lang="english",
        max_samples=args.max_samples,
    )

    samples = generate_samples(translator)

    report = {
        "test_csv": str(test_path),
        "max_samples": args.max_samples,
        "metrics": {
            "en_lg": en_lg,
            "lg_en": lg_en,
        },
        "samples": samples,
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)

    print("Evaluation complete")
    print(f"EN->LG BLEU: {en_lg['bleu']:.2f} (n={en_lg['count']})")
    print(f"LG->EN BLEU: {lg_en['bleu']:.2f} (n={lg_en['count']})")
    print(f"Saved report: {output_path}")


if __name__ == "__main__":
    main()
