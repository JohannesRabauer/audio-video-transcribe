"""Export transcription segments to JSON and SRT formats."""

import json
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


def _seconds_to_srt_time(seconds: float) -> str:
    """Convert a floating-point second value to SRT timestamp format (HH:MM:SS,mmm)."""
    total_ms = int(round(seconds * 1000))
    ms = total_ms % 1000
    total_s = total_ms // 1000
    s = total_s % 60
    total_m = total_s // 60
    m = total_m % 60
    h = total_m // 60
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def export_json(segments: List[dict], output_path: Path) -> None:
    """Write segments to a JSON file.

    Args:
        segments: List of segment dicts (start, end, text).
        output_path: Destination file path.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(segments, fh, ensure_ascii=False, indent=2)
    logger.info("JSON written to '%s'", output_path)


def export_srt(segments: List[dict], output_path: Path) -> None:
    """Write segments to an SRT subtitle file.

    Args:
        segments: List of segment dicts (start, end, text).
        output_path: Destination file path.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines: List[str] = []
    for idx, seg in enumerate(segments, start=1):
        start_ts = _seconds_to_srt_time(seg["start"])
        end_ts = _seconds_to_srt_time(seg["end"])
        lines.append(str(idx))
        lines.append(f"{start_ts} --> {end_ts}")
        lines.append(seg["text"])
        lines.append("")  # blank line between entries

    with output_path.open("w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    logger.info("SRT written to '%s'", output_path)
