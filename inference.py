#!/usr/bin/env python3
"""Inference module for production English <-> Luganda MarianMT translation."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional, Tuple

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


DEFAULT_MODELS = {
    "en-lg": "Helsinki-NLP/opus-mt-en-lg",
    "lg-en": "Helsinki-NLP/opus-mt-lg-en",
}

FALLBACK_MODELS = {
    "en-lg": "Helsinki-NLP/opus-mt-en-mul",
    "lg-en": "Helsinki-NLP/opus-mt-mul-en",
}


class TransformerTranslator:
    """Bidirectional MarianMT inference wrapper with strict direction routing."""

    def __init__(
        self,
        en_lg_model_path: str = "models/en-lg/final",
        lg_en_model_path: str = "models/lg-en/final",
        device: Optional[str] = None,
    ) -> None:
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.models: Dict[str, AutoModelForSeq2SeqLM] = {}
        self.tokenizers: Dict[str, AutoTokenizer] = {}

        self._load_direction("en-lg", en_lg_model_path)
        self._load_direction("lg-en", lg_en_model_path)

    def _resolve_model_name(self, direction: str, local_path: str) -> str:
        local = Path(local_path)
        if local.exists():
            return str(local)
        return DEFAULT_MODELS[direction]

    def _load_direction(self, direction: str, local_path: str) -> None:
        model_ref = self._resolve_model_name(direction, local_path)
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_ref)
            model = AutoModelForSeq2SeqLM.from_pretrained(model_ref)
        except Exception:
            fallback = FALLBACK_MODELS[direction]
            tokenizer = AutoTokenizer.from_pretrained(fallback)
            model = AutoModelForSeq2SeqLM.from_pretrained(fallback)

        model.to(self.device)
        model.eval()
        self.tokenizers[direction] = tokenizer
        self.models[direction] = model

    @staticmethod
    def detect_language(text: str) -> str:
        value = (text or "").strip().lower()
        if not value:
            return "english"

        luganda_markers = {
            "oli", "otya", "webale", "nnyo", "muganda", "luganda", "kabaka", "abantu",
        }
        tokens = value.split()
        hits = sum(1 for tok in tokens if tok in luganda_markers)
        return "luganda" if hits >= 1 else "english"

    @staticmethod
    def _normalize_lang(value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        lowered = value.strip().lower()
        if lowered in {"en", "english"}:
            return "english"
        if lowered in {"lg", "lug", "luganda"}:
            return "luganda"
        raise ValueError(f"Unsupported language: {value}")

    def _resolve_direction(self, source_lang: Optional[str], target_lang: Optional[str], text: str) -> Tuple[str, str, str]:
        source = self._normalize_lang(source_lang) or self.detect_language(text)
        target = self._normalize_lang(target_lang) or ("luganda" if source == "english" else "english")

        if source == target:
            raise ValueError("Source and target languages must be different")

        if source == "english" and target == "luganda":
            return source, target, "en-lg"
        if source == "luganda" and target == "english":
            return source, target, "lg-en"

        raise ValueError(f"Unsupported translation direction: {source} -> {target}")

    @staticmethod
    def reduce_hallucination(text: str) -> str:
        words = text.split()
        if not words:
            return text

        deduped = [words[0]]
        for token in words[1:]:
            if token != deduped[-1]:
                deduped.append(token)
        return " ".join(deduped).strip()

    def translate(
        self,
        text: str,
        source_lang: Optional[str] = None,
        target_lang: Optional[str] = None,
        max_new_tokens: int = 120,
        num_beams: int = 5,
    ) -> Dict[str, str]:
        value = (text or "").strip()
        if not value:
            raise ValueError("Input text cannot be empty")

        source, target, direction = self._resolve_direction(source_lang, target_lang, value)
        tokenizer = self.tokenizers[direction]
        model = self.models[direction]

        encoded = tokenizer(value, return_tensors="pt", truncation=True, max_length=256)
        encoded = {name: tensor.to(self.device) for name, tensor in encoded.items()}

        with torch.no_grad():
            generated = model.generate(
                **encoded,
                max_new_tokens=max_new_tokens,
                num_beams=max(1, num_beams),
                no_repeat_ngram_size=3,
                repetition_penalty=1.2,
                length_penalty=0.9,
                early_stopping=True,
            )

        translation = tokenizer.decode(generated[0], skip_special_tokens=True)
        translation = self.reduce_hallucination(translation)

        return {
            "source_lang": source,
            "target_lang": target,
            "translation": translation,
            "direction": direction,
        }

    def save_attention_plot(self, text: str, direction: str = "en-lg", save_path: str = "outputs/attention.png") -> str:
        """Save an encoder self-attention heatmap for debugging."""
        import matplotlib.pyplot as plt

        if direction not in self.models:
            raise ValueError(f"Unknown direction: {direction}")

        tokenizer = self.tokenizers[direction]
        model = self.models[direction]

        encoded = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
        encoded = {name: tensor.to(self.device) for name, tensor in encoded.items()}

        with torch.no_grad():
            outputs = model(**encoded, output_attentions=True, return_dict=True)

        if not outputs.encoder_attentions:
            raise RuntimeError("Model did not return encoder attentions")

        matrix = outputs.encoder_attentions[-1][0].mean(dim=0).detach().cpu().numpy()
        tokens = tokenizer.convert_ids_to_tokens(encoded["input_ids"][0].detach().cpu())

        plt.figure(figsize=(10, 8))
        plt.imshow(matrix, aspect="auto")
        plt.xticks(range(len(tokens)), tokens, rotation=90)
        plt.yticks(range(len(tokens)), tokens)
        plt.title(f"Encoder Attention ({direction})")
        plt.tight_layout()

        out_path = Path(save_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(out_path)
        plt.close()
        return str(out_path)
