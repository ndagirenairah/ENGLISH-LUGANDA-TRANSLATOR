#!/usr/bin/env python3
"""Run BLEU evaluation + sample translations after training."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from sacrebleu import corpus_bleu

from inference import TransformerTranslator


SAMPLES = [
    "How are you today?",
    "Thank you very much",
    "I love Luganda language",
    "Oli otya ssebo",
    "Webale nnyo",
    "Ndi muganda",
]


def evaluate_direction(
    translator: TransformerTranslator,
    df: pd.DataFrame,
    source_col: str,
    target_col: str,
    source_lang: str,
    target_lang: str,
    max_samples: int,
) -> Dict[str, float]:
    eval_df = df[[source_col, target_col]].dropna().head(max_samples).copy()

    predictions: List[str] = []
    references: List[List[str]] = []

    for _, row in eval_df.iterrows():
        src_text = str(row[source_col]).strip()
        ref_text = str(row[target_col]).strip()
        if not src_text or not ref_text:
            continue

        out = translator.translate(src_text, source_lang=source_lang, target_lang=target_lang)
        predictions.append(out["translation"])
        references.append([ref_text])

    if not predictions:
        return {"bleu": 0.0, "count": 0}

    bleu = corpus_bleu(predictions, references)
    return {
        "bleu": float(bleu.score),
        "count": len(predictions),
    }


def print_sample_translations(translator: TransformerTranslator) -> None:
    print("\n=== Sample Translations ===")
    for text in SAMPLES:
        out = translator.translate(text)
        print(f"[{out['source_lang']} -> {out['target_lang']}] {text}")
        print(f"  => {out['translation']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Post-training BLEU + sample translation test")
    parser.add_argument("--test-csv", default="data/processed/test.csv")
    parser.add_argument("--max-samples", type=int, default=200)
    parser.add_argument("--output", default="outputs/post_training_test_report.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    test_path = Path(args.test_csv)
    if not test_path.exists():
        raise FileNotFoundError(f"Missing test split: {test_path}")

    df = pd.read_csv(test_path)
    required = {"english", "luganda"}
    if not required.issubset(df.columns):
        raise ValueError(f"{test_path} must contain columns: {required}")

    translator = TransformerTranslator(
        en_lg_model_path="models/en-lg/final",
        lg_en_model_path="models/lg-en/final",
    )

    en_lg = evaluate_direction(
        translator=translator,
        df=df,
        source_col="english",
        target_col="luganda",
        source_lang="english",
        target_lang="luganda",
        max_samples=args.max_samples,
    )

    lg_en = evaluate_direction(
        translator=translator,
        df=df,
        source_col="luganda",
        target_col="english",
        source_lang="luganda",
        target_lang="english",
        max_samples=args.max_samples,
    )

    report = {
        "test_file": str(test_path),
        "max_samples": args.max_samples,
        "metrics": {
            "en_lg": en_lg,
            "lg_en": lg_en,
        },
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)

    print("\n=== BLEU Results ===")
    print(f"EN -> LG BLEU: {en_lg['bleu']:.2f} (n={en_lg['count']})")
    print(f"LG -> EN BLEU: {lg_en['bleu']:.2f} (n={lg_en['count']})")
    print(f"Report saved to: {output_path}")

    print_sample_translations(translator)


if __name__ == "__main__":
    main()
