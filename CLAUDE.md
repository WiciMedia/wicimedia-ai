# WiciMedia AI

AI-powered video and content production for WiciMedia, made with Claude Code and the Higgsfield MCP server. Most content is Arabic (Gulf dialect), for TikTok, Reels, Shorts and YouTube.

## Talking to the user

- The user writes in Gulf Arabic. Reply in Arabic, short and clear. Keep commands, file names and code in English.
- Before spending Higgsfield credits, quote the cost (`estimate_video_cost`, `estimate_image_cost` or `estimate_audio_cost`) and get the user's OK.

## Environment

- Use the cloud environment **`wicimedia-ai`**, not Default. It allows the Hugging Face hosts, and its setup script installs everything below. If the tools are missing, the session is probably on Default.
- **Python video libraries** are in a venv at `/opt/video-env` (moviepy 2.2, faster-whisper, arabic-reshaper, python-bidi). Run them with `/opt/video-env/bin/python -I`.
  - `av` is pinned `<16`. av 16+ breaks faster-whisper (`metadata_errors` TypeError).
  - Do not pip-install moviepy into the system Python. It downgrades Pillow below 12, which breaks other installed skills.
- **Whisper model**: `large-v3-turbo` in `/opt/whisper-models`. It runs on CPU int8 at about 0.7× real time. Downloading it needs `HF_HUB_DISABLE_XET=1`.
- **Arabic fonts** are in `/usr/local/share/fonts/arabic`: Cairo-VF, Tajawal, Almarai, Changa-VF, ElMessiri-VF, ReemKufi-VF. apt also installs Noto Sans/Naskh/Kufi Arabic, Amiri and KACST.
- **ffmpeg** is version 6.1 with libass. There is no GPU.
- The **Workflow tool is not available in cloud sessions**. The `claude-security` plugin's scans have to run from the local CLI or the Desktop app, with Dynamic workflows turned on in `/config`.

## Arabic text on video

These rules come from testing. Breaking them produces broken letters.

- Use the **`arabic-subtitles` skill** (`.claude/skills/arabic-subtitles/`) for any subtitles or captions.
- **Never** use ffmpeg `drawtext` for Arabic. With `text_shaping=1` glyphs go missing, and with `0` the letters come out disconnected and reversed.
- **Never** burn an `.srt` with `subtitles=file.srt`, because glyphs go missing.
- **Always** follow this path: SRT → ASS (`PlayResX/PlayResY` = the real video size, style `Encoding` = **-1** for RTL auto-direction) → `ass=file.ass:fontsdir=/usr/local/share/fonts/arabic`.
- Put titles and other on-screen text in the same ASS file as their own styles and events, positioned with `{\pos(x,y)}`.
- Font filenames containing `[` `]` break ffmpeg filter arguments. Keep the renamed `*-VF.ttf` files.
- After every render, pull a frame (`ffmpeg -ss T -i out.mp4 -frames:v 1 frame.png`) and look at it before delivering.

## Video defaults

- Vertical **1080×1920** for TikTok, Reels and Shorts. Horizontal **1920×1080** for YouTube.
- H.264 `yuv420p`, CRF 18–20, AAC audio, `-movflags +faststart`.

## Generation

- Higgsfield MCP covers video, image, voice/TTS, music, SFX, lipsync, upscale and reframe. Follow its server instructions, and check `models_explore` for model options.
- For prompts, use the `video-prompt-builder` skill for new scenes and `seedance-footage-vfx` for transforming existing footage.

## Files and storage

- **Never commit media** (`.mp4`, `.mov`, `.wav`, `.mp3` and so on). `.gitignore` blocks them.
- Work in the scratchpad directory. Deliver with SendUserFile or Google Drive.
- The container is ephemeral. Keep code by committing it and media by putting it on Drive.
