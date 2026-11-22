"""Convert an SRT file into a styled ASS file that renders Arabic correctly.

Run with any Python 3 (stdlib only):
    python3 srt_to_ass.py INPUT.srt OUTPUT.ass --video VIDEO.mp4 [options]

Why: ffmpeg's `subtitles=file.srt` path and `drawtext` both break Arabic
letters (missing glyphs / disconnected letters). An ASS file with PlayRes set
to the real video size, burned with the `ass=` filter, shapes Arabic properly.
"""
import argparse
import json
import re
import subprocess
import sys

POSITIONS = {"bottom": 2, "middle": 5, "top": 8}

TIME_RE = re.compile(r"(\d+):(\d{2}):(\d{2})[,.](\d{1,3})")


def probe_size(video: str):
    """Displayed frame size: swaps width/height for 90/270-degree rotated video
    (phone footage), because ffmpeg auto-rotates before the ass= filter."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height:stream_tags=rotate:stream_side_data=rotation",
         "-of", "json", video],
        capture_output=True, text=True, check=True,
    ).stdout
    s = json.loads(out)["streams"][0]
    w, h = int(s["width"]), int(s["height"])
    rotation = s.get("tags", {}).get("rotate")
    for sd in s.get("side_data_list", []):
        if "rotation" in sd:
            rotation = sd["rotation"]
    if rotation is not None and int(float(rotation)) % 180 != 0:
        w, h = h, w
    return w, h


def ass_time(srt_time: str) -> str:
    m = TIME_RE.search(srt_time)
    if not m:
        raise ValueError(f"bad timestamp: {srt_time!r}")
    h, mi, s, ms = m.groups()
    cs = int(ms.ljust(3, "0")) // 10
    return f"{int(h)}:{mi}:{s}.{cs:02}"


def ass_color(hex_rgb: str, alpha: int = 0) -> str:
    """'#RRGGBB' -> '&HAABBGGRR' (ASS uses BGR with alpha first)."""
    h = hex_rgb.lstrip("#")
    if not re.fullmatch(r"[0-9A-Fa-f]{6}", h):
        raise ValueError(f"colour must be #RRGGBB, got {hex_rgb!r}")
    r, g, b = h[0:2], h[2:4], h[4:6]
    return f"&H{alpha:02X}{b}{g}{r}".upper()


def parse_srt(text: str):
    blocks = re.split(r"\n\s*\n", text.replace("\r\n", "\n").replace("﻿", "").strip())
    for b in blocks:
        lines = [l for l in b.split("\n") if l.strip() != ""]
        idx = next((i for i, l in enumerate(lines) if "-->" in l), None)
        if idx is None:
            continue
        start, end = [p.strip() for p in lines[idx].split("-->")]
        body = lines[idx + 1:]
        if body:
            yield start, end, body


def escape(text: str) -> str:
    # ASS has no escape for a backslash; swap it for a look-alike (U+29F5) so
    # text like "C:\new" is not read as a \n line break.
    return text.replace("\\", "\u29f5").replace("{", "\\{").replace("}", "\\}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("srt")
    ap.add_argument("ass")
    size = ap.add_mutually_exclusive_group(required=True)
    size.add_argument("--video", help="video the subtitles will be burned into (reads its size)")
    size.add_argument("--res", help="WIDTHxHEIGHT, e.g. 1080x1920")
    ap.add_argument("--font", default="Cairo", help="font family (Cairo, Tajawal, Almarai, Noto Sans Arabic ...)")
    ap.add_argument("--size", type=int, default=None, help="font size in video pixels (default: by frame size)")
    ap.add_argument("--position", choices=POSITIONS, default="bottom")
    ap.add_argument("--margin", type=int, default=None, help="distance from the edge in pixels")
    ap.add_argument("--color", default="#FFFFFF", help="text colour #RRGGBB")
    ap.add_argument("--outline-color", default="#000000")
    ap.add_argument("--outline", type=float, default=None, help="outline width in pixels")
    ap.add_argument("--box", action="store_true", help="draw a semi-transparent box behind each line")
    ap.add_argument("--box-color", default="#000000")
    ap.add_argument("--box-opacity", type=float, default=0.6, help="0..1")
    ap.add_argument("--regular", action="store_true", help="regular weight instead of bold")
    args = ap.parse_args()

    if not 0 <= args.box_opacity <= 1:
        ap.error("--box-opacity must be between 0 and 1")

    if args.video:
        w, h = probe_size(args.video)
    else:
        w, h = (int(x) for x in args.res.lower().split("x"))

    vertical = h > w
    short_side = min(w, h)
    size = args.size or round(short_side * (0.058 if vertical else 0.05))
    margin = args.margin if args.margin is not None else round(h * (0.13 if vertical else 0.07))
    outline = args.outline if args.outline is not None else max(2, round(size * 0.06))

    if args.box:
        border_style = 3  # opaque box
        back = ass_color(args.box_color, round((1 - args.box_opacity) * 255))
        outline_col = back  # with BorderStyle 3 the box uses OutlineColour
        outline = max(outline, round(size * 0.25))  # box padding
    else:
        border_style = 1
        back = ass_color("#000000", 0x80)
        outline_col = ass_color(args.outline_color)

    # Encoding -1 makes libass detect each line's base direction (RTL for Arabic).
    # With any other value the base direction is LTR, which misplaces brackets,
    # punctuation (؟ !), numbers and English words inside Arabic lines.
    style = (
        f"Style: Sub,{args.font},{size},{ass_color(args.color)},{ass_color(args.color)},"
        f"{outline_col},{back},{0 if args.regular else -1},0,0,0,100,100,0,0,"
        f"{border_style},{outline},0,{POSITIONS[args.position]},"
        f"{round(w * 0.06)},{round(w * 0.06)},{margin},-1"
    )

    out = [
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {w}",
        f"PlayResY: {h}",
        "WrapStyle: 0",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, "
        "Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        style,
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]

    n = 0
    with open(args.srt, encoding="utf-8") as f:
        for start, end, body in parse_srt(f.read()):
            text = "\\N".join(escape(l.strip()) for l in body)
            out.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Sub,,0,0,0,,{text}")
            n += 1

    if n == 0:
        print(f"no subtitle entries found in {args.srt}", file=sys.stderr)
        return 1

    with open(args.ass, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print(f"wrote {n} lines to {args.ass} ({w}x{h}, font {args.font} {size}px, "
          f"{args.position}{', box' if args.box else ''})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
