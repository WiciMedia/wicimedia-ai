"""Transcribe Arabic speech from a video or audio file into an SRT file.

Run with the video venv:
    /opt/video-env/bin/python -I transcribe.py INPUT OUTPUT.srt [--max-chars 42] [--prompt "..."]

Uses faster-whisper (large-v3-turbo, CPU int8) from /opt/whisper-models.
Long segments are split into subtitle lines of at most --max-chars characters
using word timestamps, so each line stays readable on screen.
"""
import argparse
import os
import sys
import time

os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")

from faster_whisper import WhisperModel  # noqa: E402

MODEL_DIR = "/opt/whisper-models"


def ts(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def split_segment(seg, max_chars: int):
    """Yield (start, end, text) chunks of at most max_chars, cut on word boundaries."""
    words = list(seg.words or [])
    if not words:
        yield seg.start, seg.end, seg.text.strip()
        return
    line, start = [], None
    for w in words:
        token = w.word.strip()
        if not token:
            continue
        candidate = " ".join(line + [token])
        if line and len(candidate) > max_chars:
            yield start, prev_end, " ".join(line)
            line, start = [], None
        if start is None:
            start = w.start
        line.append(token)
        prev_end = w.end
    if line:
        yield start, prev_end, " ".join(line)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="video or audio file")
    ap.add_argument("output", help="output .srt path")
    ap.add_argument("--language", default="ar")
    ap.add_argument("--model", default="large-v3-turbo")
    ap.add_argument("--max-chars", type=int, default=42, help="max characters per subtitle line")
    ap.add_argument("--prompt", default=None,
                    help="initial prompt: names, brand words, dialect hints to improve accuracy")
    args = ap.parse_args()

    if not os.path.exists(args.input):
        print(f"input not found: {args.input}", file=sys.stderr)
        return 1

    model = WhisperModel(args.model, device="cpu", compute_type="int8", download_root=MODEL_DIR)
    t0 = time.time()
    segments, info = model.transcribe(
        args.input,
        language=args.language,
        vad_filter=True,
        word_timestamps=True,
        initial_prompt=args.prompt,
    )

    n = 0
    with open(args.output, "w", encoding="utf-8") as f:
        for seg in segments:
            for start, end, text in split_segment(seg, args.max_chars):
                if not text:
                    continue
                n += 1
                f.write(f"{n}\n{ts(start)} --> {ts(end)}\n{text}\n\n")

    print(f"wrote {n} subtitle lines to {args.output} "
          f"(audio {info.duration:.1f}s, transcribed in {time.time() - t0:.1f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
