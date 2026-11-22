---
name: arabic-subtitles
description: Add Arabic subtitles to a video. Transcribes the speech with Whisper into SRT, has the user review the text, converts it to a styled ASS file, and burns it in with ffmpeg so Arabic letters, punctuation and mixed English/numbers render correctly. Use when the user asks for ترجمة, subtitles, captions, كابشن, or the text of what is said in a video.
---

# Arabic subtitles

Pipeline: **video → `transcribe.py` → SRT → user review → `srt_to_ass.py` → ASS → ffmpeg `ass=` → check frames → deliver.**

Scripts live next to this file in `scripts/`. Below, `SK` means that directory:
`SK=/home/user/wicimedia-ai/.claude/skills/arabic-subtitles/scripts` (adjust if the repo is elsewhere).

Work in the scratchpad directory, never in the repo: media files must not be committed.

## 0. Preflight

```bash
ls /opt/video-env/bin/python /opt/whisper-models >/dev/null && fc-list | grep -qi cairo && echo ready
```

If this fails, the session is not on the `wicimedia-ai` cloud environment (its setup script installs the venv, the Whisper model and the fonts). Tell the user, in Arabic, to start the session on that environment.

## 1. Transcribe

```bash
/opt/video-env/bin/python -I "$SK/transcribe.py" input.mp4 subs.srt --max-chars 42 \
  --prompt "ويكيميديا، <brand names, people, dialect words that appear in the video>"
```

- Accepts video or audio. Runs on CPU at roughly 0.7× real time. For anything longer than a few minutes, run it in the background.
- `--max-chars`: 42 is good for 16:9. Use about 30 for 9:16 so lines stay short.
- `--prompt` noticeably improves names and brand words. Fill it from what the user told you about the video.
- If the user already has the script or text of what is said, still transcribe for the timings, then replace the wording with theirs.

## 2. Review with the user (do not skip)

Whisper makes mistakes with Gulf dialect, names and brand words. Show the SRT text to the user and ask for corrections before burning. Keep the timings and fix only the words. Skip this step only if the user explicitly says to.

## 3. SRT → ASS

```bash
python3 -I "$SK/srt_to_ass.py" subs.srt subs.ass --video input.mp4 [options]
```

| Option | Default | Notes |
|---|---|---|
| `--font` | `Cairo` | Also: `Tajawal`, `Almarai`, `Changa`, `El Messiri`, `Reem Kufi`, `Noto Sans Arabic`, `Amiri` |
| `--size` | ~5.8% (9:16) or 5% (16:9) of the short side | Pixels at the video's real size |
| `--position` | `bottom` | `bottom`, `middle` or `top` |
| `--margin` | 13% of height (9:16), 7% (16:9) | The 9:16 default keeps captions above TikTok/Reels UI |
| `--color` / `--outline-color` | `#FFFFFF` / `#000000` | `#RRGGBB` |
| `--box` | off | Semi-transparent box behind each line (`--box-color`, `--box-opacity`) |
| `--regular` | bold | Regular weight |

Use `--res 1080x1920` instead of `--video` when the video does not exist yet.

## 4. Burn in

```bash
ffmpeg -y -i input.mp4 -vf "ass=subs.ass:fontsdir=/usr/local/share/fonts/arabic" \
  -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p -c:a copy -movflags +faststart output.mp4
```

Keep file names simple (no `:` `,` `'` or spaces), because they sit inside an ffmpeg filter argument.

To give YouTube a separate caption file instead of (or as well as) burning in, deliver the reviewed `.srt` and the user uploads it there. TikTok and Reels need burned-in captions.

## 5. Check before delivering

Pull 2–3 frames at times when a subtitle is on screen, then Read the PNGs and look at them:

```bash
ffmpeg -v error -y -ss 3 -i output.mp4 -frames:v 1 -vf scale=540:-1 -update 1 check1.png
```

Check that the letters are connected (no boxes), brackets, `؟`, `!`, numbers and English words sit where they should in right-to-left order, no line is cut off at the frame edge, and the captions are not hidden behind platform UI.

## 6. Deliver

Send the video with SendUserFile, or upload it to Google Drive if the user wants it there. Never commit the media.

## Rules that must not be broken

- **Never** use ffmpeg `drawtext` for Arabic. With `text_shaping=1` glyphs go missing, and with `0` the letters come out disconnected and reversed.
- **Never** burn an `.srt` directly with `subtitles=file.srt`, because glyphs go missing. Always convert to ASS first.
- The ASS style's `Encoding` must stay `-1` (`srt_to_ass.py` sets it). That lets libass detect right-to-left direction. Any other value misplaces brackets, punctuation, numbers and English inside Arabic lines.
- Font files whose names contain `[` `]` break ffmpeg filter parsing. The installed variable fonts are already renamed (`Cairo-VF.ttf` and so on).
