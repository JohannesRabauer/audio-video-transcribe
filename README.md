# audio-video-transcribe

A local-first tool that transcribes video files into text with sentence-level timestamps using [Whisper](https://github.com/openai/whisper). Runs entirely offline inside Docker — no API keys required.

---

## What it does

1. Extracts audio from any video file (mp4, mkv, mov, …) using **FFmpeg**.
2. Transcribes the audio with **OpenAI Whisper** (runs locally).
3. Produces two output files:
   - **JSON** — segments with `start`, `end`, and `text`.
   - **SRT** — subtitle file with proper timestamps.

---

## One-command usage

```bash
docker compose run --rm transcriber input.mp4
```

Place `input.mp4` in the current directory before running the command. Output files will be written to `./output/` by default.

---

## Example command

```bash
# Transcribe with the default (base) model
docker compose run --rm transcriber lecture.mp4

# Use a larger model for higher accuracy
docker compose run --rm transcriber lecture.mp4 --model medium

# Choose a custom output directory
docker compose run --rm transcriber lecture.mp4 --output-dir ./transcripts
```

---

## Example output

**`output/lecture.json`**
```json
[
  { "start": 0.0,  "end": 4.32, "text": "Welcome to today's lecture on machine learning." },
  { "start": 4.32, "end": 9.10, "text": "We will start by discussing supervised learning." }
]
```

**`output/lecture.srt`**
```
1
00:00:00,000 --> 00:00:04,320
Welcome to today's lecture on machine learning.

2
00:00:04,320 --> 00:00:09,100
We will start by discussing supervised learning.
```

---

## Options

| Flag | Default | Description |
|---|---|---|
| `--model` | `base` | Whisper model size (see table below) |
| `--output-dir` | `./output` | Directory for JSON and SRT output files |
| `--device` | `cpu` | Compute device: `cpu` or `cuda` |

---

## Model size vs. performance

| Model  | Parameters | Relative speed | Accuracy |
|--------|-----------|----------------|----------|
| tiny   | 39 M      | ~32×            | lowest   |
| base   | 74 M      | ~16×            | good     |
| small  | 244 M     | ~6×             | better   |
| medium | 769 M     | ~2×             | great    |
| large  | 1550 M    | 1×              | best     |

> **Tip:** Start with `base` for quick results. Switch to `medium` or `large` when accuracy matters most.

---

## Project structure

```
.
├── app/
│   ├── main.py          # CLI entrypoint
│   ├── transcriber.py   # Whisper transcription logic
│   ├── ffmpeg_utils.py  # Audio extraction via FFmpeg
│   └── exporters.py     # JSON + SRT output writers
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Requirements (for local / non-Docker usage)

- Python 3.10+
- FFmpeg installed and on PATH
- `pip install -r requirements.txt`

Then run directly:
```bash
python app/main.py input.mp4
```
