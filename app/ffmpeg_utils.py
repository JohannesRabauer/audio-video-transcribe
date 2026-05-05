"""Audio extraction utilities using FFmpeg."""

import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def extract_audio(input_path: Path, output_path: Path) -> None:
    """Extract mono 16kHz WAV audio from a video file using FFmpeg.

    Args:
        input_path: Path to the input video file.
        output_path: Path where the extracted WAV file will be written.

    Raises:
        FileNotFoundError: If the input file does not exist.
        RuntimeError: If FFmpeg fails or is not installed.
    """
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    logger.info("Extracting audio from '%s' → '%s'", input_path, output_path)

    command = [
        "ffmpeg",
        "-y",                   # overwrite output without prompt
        "-i", str(input_path),
        "-vn",                  # no video
        "-ac", "1",             # mono
        "-ar", "16000",         # 16 kHz
        "-f", "wav",
        str(output_path),
    ]

    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "FFmpeg not found. Please ensure FFmpeg is installed and available on PATH."
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"FFmpeg failed (exit code {exc.returncode}):\n{exc.stderr}"
        ) from exc

    logger.info("Audio extraction complete: '%s'", output_path)
