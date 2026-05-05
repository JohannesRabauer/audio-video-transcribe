"""Suggest viral clip timespans from a transcription JSON using a local Docker model."""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

DEFAULT_API_URL = os.environ.get(
    "HIGHLIGHT_API_URL",
    "http://model-runner.docker.internal/engines/llama.cpp/v1/chat/completions",
)

SYSTEM_PROMPT = (
    "You are a viral video editor assistant. "
    "Given a timestamped transcript, return a JSON object with exactly two keys:\n"
    '  "summary": a 2-3 sentence summary of the full content\n'
    '  "clips": an array of at least 10 objects, each with:\n'
    '    "rank": integer starting at 1 (1 = best viral potential)\n'
    '    "start": float (start time in seconds)\n'
    '    "end": float (end time in seconds; clip duration must be 10-30 seconds)\n'
    '    "description": string explaining why this moment works as a viral short\n'
    "Clips must be sorted by rank ascending (best first). "
    "Respond with ONLY the raw JSON object — no markdown fences, no extra text."
)


def build_transcript(segments: list) -> str:
    lines = []
    for seg in segments:
        lines.append(f"[{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['text'].strip()}")
    return "\n".join(lines)


def call_model(api_url: str, model: str, transcript: str) -> str:
    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Transcript:\n{transcript}"},
        ],
        "temperature": 0.3,
        "stream": True,
    }).encode("utf-8")

    req = urllib.request.Request(
        api_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    print("Waiting for model response", end="", flush=True)
    chunks = []
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            for raw_line in resp:
                line = raw_line.decode("utf-8").strip()
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    delta = json.loads(data)["choices"][0]["delta"].get("content", "")
                    if delta:
                        chunks.append(delta)
                        print(".", end="", flush=True)
                except (KeyError, json.JSONDecodeError):
                    pass
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"\nError: HTTP {exc.code} from {api_url}", file=sys.stderr)
        print(f"  Response: {body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as exc:
        print(f"\nError: could not reach Docker Models at {api_url}", file=sys.stderr)
        print(f"  {exc}", file=sys.stderr)
        print("Make sure Docker Desktop is running and the model is pulled.", file=sys.stderr)
        sys.exit(1)
    print()  # newline after progress dots
    return "".join(chunks)


def print_results(raw: str) -> None:
    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        # Model didn't return clean JSON — print as-is
        print(raw)
        return

    print("\n=== SUMMARY ===")
    print(result.get("summary", "(none)"))

    clips = sorted(result.get("clips", []), key=lambda c: c.get("rank", 999))
    print(f"\n=== TOP CLIPS ({len(clips)} found, best first) ===")
    for clip in clips:
        duration = clip["end"] - clip["start"]
        print(f"\n  #{clip['rank']}  {clip['start']:.1f}s – {clip['end']:.1f}s  ({duration:.0f}s)")
        print(f"      {clip['description']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="highlight-picker",
        description="Rank viral clip moments from a transcription JSON using a local Docker model.",
    )
    parser.add_argument(
        "input",
        metavar="INPUT",
        help="Path to transcription .json file (e.g. output/docker.json)",
    )
    parser.add_argument(
        "--model",
        required=True,
        metavar="MODEL",
        help="Docker model name, e.g. ai/llama3.2 or ai/phi4-mini",
    )
    parser.add_argument(
        "--api-url",
        default=DEFAULT_API_URL,
        metavar="URL",
        help=f"Docker Models API endpoint (default: {DEFAULT_API_URL})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    with input_path.open(encoding="utf-8") as fh:
        segments = json.load(fh)

    transcript = build_transcript(segments)
    raw = call_model(args.api_url, args.model, transcript)
    print_results(raw)


if __name__ == "__main__":
    main()
