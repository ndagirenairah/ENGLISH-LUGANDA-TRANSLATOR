#!/usr/bin/env python3
"""Preprocess English <-> Luganda parallel data for MarianMT training."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable, List

import pandas as pd
from sklearn.model_selection import train_test_split


DEFAULT_LOCAL_SOURCES = [
    "data/raw/sunbird_salt.csv",
    "data/raw/makerere_nlp.csv",
    "data/raw/jw300_parallel.csv",
    "data/cultural/cultural_training_data.csv",
    "cultural_dataset.csv",
]

LUGANDA_HINTS = {
    "oli", "otya", "nnyo", "webale", "muganda", "luganda", "kabaka", "abantu", "ekika",
}


def clean_text(text: str) -> str:
    """Normalize whitespace and remove obvious URL/email noise."""
    text = str(text or "")
    text = re.sub(r"https?://\S+|www\.\S+", "", text)
    text = re.sub(r"\S+@\S+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map heterogeneous dataset schemas into english/luganda columns."""
    lower_map = {c.lower().strip(): c for c in df.columns}

    english_candidates = ["english", "eng", "en", "translation_en", "target"]
    luganda_candidates = ["luganda", "lug", "lg", "translation_lg"]

    en_col = next((lower_map[c] for c in english_candidates if c in lower_map), None)
    lg_col = next((lower_map[c] for c in luganda_candidates if c in lower_map), None)

    if en_col is None or lg_col is None:
        raise ValueError("Missing english/luganda columns")

    return pd.DataFrame(
        {
            "english": df[en_col].astype(str),
            "luganda": df[lg_col].astype(str),
        }
    )


def load_local_sources(paths: Iterable[str]) -> pd.DataFrame:
    frames: List[pd.DataFrame] = []
    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists():
            continue
        try:
            df = pd.read_csv(path)
            normalized = normalize_columns(df)
            normalized["source"] = str(path)
            frames.append(normalized)
            print(f"Loaded {len(normalized):,} rows from {path}")
        except Exception as exc:
            print(f"Skipped {path}: {exc}")

    if not frames:
        raise FileNotFoundError("No valid local parallel files found")

    return pd.concat(frames, ignore_index=True)


def try_load_hf_sources() -> pd.DataFrame:
    """Optionally add online corpora from Hugging Face datasets."""
    frames: List[pd.DataFrame] = []
    try:
        from datasets import load_dataset

        try:
            salt = load_dataset("Sunbird/salt", "lug-eng", split="train")
            rows = [
                {
                    "english": row["translation"]["eng"],
                    "luganda": row["translation"]["lug"],
                    "source": "hf:Sunbird/salt",
                }
                for row in salt
            ]
            frames.append(pd.DataFrame(rows))
            print(f"Loaded {len(rows):,} rows from hf:Sunbird/salt")
        except Exception as exc:
            print(f"Skipped hf:Sunbird/salt: {exc}")

        try:
            opus = load_dataset("opus100", "en-lg", split="train")
            rows = [
                {
                    "english": row["translation"]["en"],
                    "luganda": row["translation"]["lg"],
                    "source": "hf:opus100/en-lg",
                }
                for row in opus
            ]
            frames.append(pd.DataFrame(rows))
            print(f"Loaded {len(rows):,} rows from hf:opus100/en-lg")
        except Exception as exc:
            print(f"Skipped hf:opus100/en-lg: {exc}")

    except Exception as exc:
        print(f"Hugging Face datasets unavailable: {exc}")

    if not frames:
        return pd.DataFrame(columns=["english", "luganda", "source"])
    return pd.concat(frames, ignore_index=True)


def luganda_signal_ratio(text: str) -> float:
    tokens = re.findall(r"[a-zA-Z']+", text.lower())
    if not tokens:
        return 0.0
    hits = sum(1 for token in tokens if token in LUGANDA_HINTS)
    return hits / len(tokens)


def filter_parallel_data(df: pd.DataFrame, min_chars: int, max_chars: int) -> pd.DataFrame:
    """Clean rows, remove low-quality pairs, and deduplicate."""
    out = df.copy()
    out["english"] = out["english"].map(clean_text)
    out["luganda"] = out["luganda"].map(clean_text)

    out = out[(out["english"] != "") & (out["luganda"] != "")]
    out = out[out["english"].str.len().between(min_chars, max_chars)]
    out = out[out["luganda"].str.len().between(min_chars, max_chars)]

    # Remove near-identical source/target rows that often indicate noise.
    out = out[out["english"].str.lower() != out["luganda"].str.lower()]

    # Filter obvious direction mistakes: English side with too much Luganda signal.
    out = out[out["english"].map(luganda_signal_ratio) < 0.45]

    # Case-insensitive dedupe to prevent train/test leakage through capitalization.
    out["_en_norm"] = out["english"].str.lower()
    out["_lg_norm"] = out["luganda"].str.lower()
    out = out.drop_duplicates(subset=["_en_norm", "_lg_norm"]).drop(columns=["_en_norm", "_lg_norm"])

    return out.reset_index(drop=True)


def split_and_save(df: pd.DataFrame, out_dir: Path, seed: int) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    train_df, temp_df = train_test_split(df, test_size=0.2, random_state=seed, shuffle=True)
    val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=seed, shuffle=True)

    train_df.to_csv(out_dir / "train.csv", index=False)
    val_df.to_csv(out_dir / "val.csv", index=False)
    test_df.to_csv(out_dir / "test.csv", index=False)

    stats = {
        "total_rows": int(len(df)),
        "train_rows": int(len(train_df)),
        "val_rows": int(len(val_df)),
        "test_rows": int(len(test_df)),
        "avg_english_chars": float(df["english"].str.len().mean()),
        "avg_luganda_chars": float(df["luganda"].str.len().mean()),
        "sources": df["source"].value_counts().to_dict() if "source" in df.columns else {},
    }

    with open(out_dir / "stats.json", "w", encoding="utf-8") as handle:
        json.dump(stats, handle, indent=2, ensure_ascii=False)

    print("Saved split datasets:")
    print(f"  - {out_dir / 'train.csv'}")
    print(f"  - {out_dir / 'val.csv'}")
    print(f"  - {out_dir / 'test.csv'}")
    print(f"  - {out_dir / 'stats.json'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preprocess English-Luganda parallel data")
    parser.add_argument("--local-sources", nargs="*", default=DEFAULT_LOCAL_SOURCES)
    parser.add_argument("--use-hf", action="store_true", help="Include online Hugging Face datasets")
    parser.add_argument("--min-chars", type=int, default=3)
    parser.add_argument("--max-chars", type=int, default=240)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", default="data/processed")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    local_df = load_local_sources(args.local_sources)
    hf_df = try_load_hf_sources() if args.use_hf else pd.DataFrame(columns=local_df.columns)

    full_df = pd.concat([local_df, hf_df], ignore_index=True)
    print(f"Total collected rows before cleaning: {len(full_df):,}")

    cleaned_df = filter_parallel_data(full_df, min_chars=args.min_chars, max_chars=args.max_chars)
    print(f"Rows after cleaning and deduplication: {len(cleaned_df):,}")

    split_and_save(cleaned_df, Path(args.output_dir), seed=args.seed)


if __name__ == "__main__":
    main()
