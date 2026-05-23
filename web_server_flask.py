#!/usr/bin/env python3
"""Production Flask app for English <-> Luganda Transformer translation."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Optional

import speech_recognition as sr
from flask import Flask, jsonify, render_template, request, send_file
from gtts import gTTS

from inference import TransformerTranslator


app = Flask(__name__)
translator: Optional[TransformerTranslator] = None


def get_translator() -> TransformerTranslator:
    """Lazy-load model stack to avoid crashing app import/startup."""
    global translator
    if translator is None:
        translator = TransformerTranslator(
            en_lg_model_path="models/en-lg/final",
            lg_en_model_path="models/lg-en/final",
        )
    return translator


def transcribe_audio_file(file_path: str) -> str:
    """Speech-to-text using SpeechRecognition with Google backend."""
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)
    return recognizer.recognize_google(audio_data)


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/api", methods=["GET"])
def api_info():
    return jsonify(
        {
            "service": "English-Luganda Transformer NMT API",
            "status": "running",
            "routes": [
                "POST /api/translate",
                "POST /api/stt",
                "POST /api/tts",
                "POST /api/attention",
            ],
        }
    )


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/api/translate", methods=["POST"])
def translate():
    payload = request.get_json(silent=True) or {}
    text = (payload.get("text") or "").strip()
    source_lang = payload.get("source_lang")
    target_lang = payload.get("target_lang")

    if not text:
        return jsonify({"error": "Missing non-empty 'text'"}), 400

    max_new_tokens = int(payload.get("max_new_tokens", 120))
    num_beams = int(payload.get("num_beams", 5))

    if max_new_tokens < 1 or max_new_tokens > 256:
        return jsonify({"error": "max_new_tokens must be in [1, 256]"}), 400
    if num_beams < 1 or num_beams > 8:
        return jsonify({"error": "num_beams must be in [1, 8]"}), 400

    try:
        result = get_translator().translate(
            text=text,
            source_lang=source_lang,
            target_lang=target_lang,
            max_new_tokens=max_new_tokens,
            num_beams=num_beams,
        )
    except Exception as exc:
        return jsonify({"error": f"Translation unavailable: {exc}"}), 503

    return jsonify(
        {
            "input_text": text,
            **result,
        }
    )


@app.route("/api/stt", methods=["POST"])
def speech_to_text():
    if "audio" not in request.files:
        return jsonify({"error": "Upload an audio file in 'audio' form field"}), 400

    audio_file = request.files["audio"]
    suffix = Path(audio_file.filename or "sample.wav").suffix or ".wav"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        audio_file.save(tmp.name)
        tmp_path = tmp.name

    try:
        text = transcribe_audio_file(tmp_path)
        return jsonify({"text": text})
    except Exception as exc:
        return jsonify({"error": f"STT failed: {exc}"}), 500
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.route("/api/tts", methods=["POST"])
def text_to_speech():
    payload = request.get_json(silent=True) or {}
    text = (payload.get("text") or "").strip()
    lang = (payload.get("lang") or "en").strip()

    if not text:
        return jsonify({"error": "Missing non-empty 'text'"}), 400

    # gTTS does not support Luganda directly, so we keep language configurable.
    tts_lang = lang if lang in {"en", "sw"} else "en"
    tts = gTTS(text=text, lang=tts_lang)

    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "tts_output.mp3"
    tts.save(str(output_file))

    return send_file(output_file, mimetype="audio/mpeg", as_attachment=True, download_name="tts_output.mp3")


@app.route("/api/attention", methods=["POST"])
def attention_visualization():
    payload = request.get_json(silent=True) or {}
    text = (payload.get("text") or "").strip()
    direction = payload.get("direction", "en-lg")

    if not text:
        return jsonify({"error": "Missing non-empty 'text'"}), 400

    try:
        path = get_translator().save_attention_plot(
            text=text,
            direction=direction,
            save_path="outputs/attention.png",
        )
        return jsonify({"attention_plot": path, "direction": direction})
    except Exception as exc:
        return jsonify({"error": f"Attention visualization failed: {exc}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
