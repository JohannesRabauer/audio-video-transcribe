"""CLI entrypoint for the transcribe tool."""

import argparse
import logging
import sys
import tempfile
from pathlib import Path

from ffmpeg_utils import extract_audio
from transcriber import transcribe
from exporters import export_json, export_srt

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="transcribe",
        description="Transcribe a video file into text with segment-level timestamps.",
    )
    parser.add_argument(
        "input",
        metavar="INPUT",
        help="Path to the input video file (mp4, mkv, mov, …)",
    )
    parser.add_argument(
        "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: base)",
    )
    parser.add_argument(
        "--output-dir",
        default="./output",
        metavar="DIR",
        help="Directory for output files (default: ./output)",
    )
    parser.add_argument(
        "--device",
        default="cpu",
        choices=["cpu", "cuda"],
        help="Compute device (default: cpu)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        logger.error("Input file not found: %s", input_path)
        sys.exit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    stem = input_path.stem

    with tempfile.TemporaryDirectory() as tmp_dir:
        audio_path = Path(tmp_dir) / f"{stem}.wav"

        # Step 1: extract audio
        try:
            extract_audio(input_path, audio_path)
        except (FileNotFoundError, RuntimeError) as exc:
            logger.error("Audio extraction failed: %s", exc)
            sys.exit(1)

        # Step 2: transcribe
        try:
            segments = transcribe(audio_path, model_name=args.model, device=args.device)
        except (FileNotFoundError, RuntimeError) as exc:
            logger.error("Transcription failed: %s", exc)
            sys.exit(1)

    if not segments:
        logger.warning("No speech segments detected in '%s'.", input_path)

    # Step 3: export results
    json_path = output_dir / f"{stem}.json"
    srt_path = output_dir / f"{stem}.srt"

    export_json(segments, json_path)
    export_srt(segments, srt_path)

    logger.info("Done! Outputs written to '%s'", output_dir)
    logger.info("  JSON : %s", json_path)
    logger.info("  SRT  : %s", srt_path)


if __name__ == "__main__":
    main()
