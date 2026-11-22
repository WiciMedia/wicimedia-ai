# How Glass Is Made

A 61-second narrated explainer in a paper cut-out infographic style, 1920 × 1080, 30 fps. Everything is drawn in JavaScript on one canvas: the illustrations, labels, subtitles and sound effects.

- Live page: https://claude.ai/artifact/5etrR86CntFJyizteaCdpG
- Storyboard: https://claude.ai/artifact/EKSYPRk79ediKj8FcUKN86

## Files

| File | What it is |
|---|---|
| `how-glass-is-made.html` | The player page (artifact source). Loads `narration.mp3` next to it, or `window.__NARR_DATA` if set. |
| `storyboard.html` | Stage 1 storyboard with the five rendered frames. |
| `how-glass-is-made.srt` | English subtitles, timed to the narration. |
| `arabic-script.md` | Arabic narration script (Modern Standard Arabic) for the Arabic version. |
| `tools/transcribe.py` | Whisper word timings for `vo1.mp3` … `vo5.mp3`. |
| `tools/build-narration.sh` | Places the five narration clips on the 61 s timeline. |
| `tools/render-mp4.js` | Renders the final MP4 (H.264 CRF 18 + AAC) from the page. |

Media is not committed. The narration MP3, the rendered MP4s and the narration source clips live on Drive or with the user.

## Timeline

| Scene | Starts | Narration part |
|---|---|---|
| Hook: how does sand become glass? | 0.0 s | 1 (at 0.45 s) |
| Batch: three key ingredients | 12.1 s | 2 (at 12.6 s) |
| Melt: about 1,500 °C | 24.7 s | 3 (at 25.25 s) |
| Forming: float or blow | 35.4 s | 4, first sentence (at 35.9 s) |
| Annealing: cool slowly | 42.4 s | 4, second sentence (at 42.75 s, file offset 3.5 s) |
| Recycling: old glass, new life | 49.4 s | 5 (at 49.95 s) |

The constants live in `how-glass-is-made.html`: `SCN`, `PANS`, `WIPE`, `VO_PLACE`, `SPEECH` and `CAPS`. Each scene's beat times are inside its `sceneX` function.

## Rebuild

```bash
/opt/video-env/bin/python -I tools/transcribe.py <dir with vo1.mp3 … vo5.mp3>
```

```bash
tools/build-narration.sh <dir with vo1.mp3 … vo5.mp3> narration.mp3
```

```bash
node tools/render-mp4.js how-glass-is-made.html narration.mp3 <path>/mediabunny.min.mjs out.mp4
```

`render-mp4.js` needs the Mediabunny 1.65.2 bundle on disk because the CDN is not reachable from the container (`npm pack mediabunny@1.65.2`, then `package/dist/bundles/mediabunny.min.mjs`). It uses the preinstalled Playwright Chromium. A render takes about 3 minutes.
