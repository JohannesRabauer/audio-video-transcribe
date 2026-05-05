"""Whisper-based audio transcription."""

import logging
from pathlib import Path
from typing import List

import whisper

logger = logging.getLogger(__name__)


def transcribe(
    audio_path: Path,
    model_name: str = "base",
    device: str = "cpu",
) -> List[dict]:
    """Transcribe an audio file using Whisper and return segment-level results.

    Args:
        audio_path: Path to the WAV (or any audio) file to transcribe.
        model_name: Whisper model size: tiny, base, small, medium, or large.
        device: Compute device – "cpu" or "cuda".

    Returns:
        A list of dicts with keys ``start`` (float), ``end`` (float),
        and ``text`` (str).

    Raises:
        FileNotFoundError: If the audio file does not exist.
        RuntimeError: If the Whisper model cannot be loaded or transcription fails.
    """
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    logger.info("Loading Whisper model '%s' on device '%s'", model_name, device)
    try:
        model = whisper.load_model(model_name, device=device)
    except Exception as exc:
        raise RuntimeError(
            f"Failed to load Whisper model '{model_name}': {exc}"
        ) from exc

    logger.info("Transcribing '%s' …", audio_path)
    try:
        result = model.transcribe(str(audio_path), verbose=False)
    except Exception as exc:
        raise RuntimeError(f"Whisper transcription failed: {exc}") from exc

    segments = [
        {
            "start": float(seg["start"]),
            "end": float(seg["end"]),
            "text": seg["text"].strip(),
        }
        for seg in result.get("segments", [])
    ]

    logger.info("Transcription complete: %d segment(s)", len(segments))
    return segments
