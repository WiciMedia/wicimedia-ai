# WiciMedia AI

AI-powered video and content production for WiciMedia, made with Claude Code and the Higgsfield MCP server. Most content is Arabic (Gulf dialect), for TikTok, Reels, Shorts and YouTube.

## Talking to the user

- The user writes in Gulf Arabic. Reply in Arabic, short and clear. Keep commands, file names and code in English.
- Before spending Higgsfield credits, quote the cost (`estimate_video_cost`, `estimate_image_cost` or `estimate_audio_cost`) and get the user's OK.

## Environment

- Use the cloud environment **`wicimedia-ai`**, not Default. It allows the Hugging Face hosts, and its setup script installs everything below. If the tools are missing, the session is probably on Default.
- **Python video libraries** are in a venv at `/opt/video-env` (moviepy 2.2, faster-whisper, arabic-reshaper, python-bidi, numpy, playwright 1.63, yt-dlp). Run them with `/opt/video-env/bin/python -I`.
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

## Installed skills

Third-party skills are vendored in `.claude/skills/`. `.claude/skills/THIRD_PARTY.md` lists each source, its pinned commit and the review notes. Never update them by pulling blindly: review the diff first.

**Ideas and content**

- YouTube agent: `yt-script`, `yt-package`, `yt-seo`, `yt-shorts`, `yt-chapters`, `yt-edit`, `yt-retention`, `yt-plan`, `yt-audit`, `yt-viral`, `yt-comment`.
- `youtube`: an all-in-one YouTube strategist.
- `youtube-script-writer`.
- content-os: 35 writing, social and video skills, such as `short-form-video`, `video-caption-creation`, `hook-and-headline-writing` and `youtube-title-creator`.

**Motion and directing**

- `studio/claude-motion/` is a complete Remotion project (claude-motion). It carries its own skills (`motion-design`, `sound-design`, `review-loop`, `web-sims`) that apply when working inside that folder. `npm run studio`, `still`, `draft`, `render`, `sfx` and `sheet` are run there.
- `claude-motion-design`: HTML plus Playwright plus ffmpeg, no Remotion. It is renamed from upstream's `motion-design` so it doesn't clash with claude-motion's skill of that name.
- `remotion-motion-graphics` (claude-remotion-skill).
- remotion-motion-graphics-skill: `motion-graphics`, `cinematic-camera`, `terminal-inserts`, `article-highlights`. These ask about the format and background before rendering, and support transparent backgrounds.

Most of these skills were written for English. Write Arabic on-screen text through Remotion/HTML with an Arabic font (Cairo, Tajawal and so on) and `dir="rtl"`, then check frames as usual.

## Remotion

- Point every Remotion render at the preinstalled browser. That is the tested path. Whether Remotion can download its own browser through this network was not tested. In `studio/claude-motion` this is set up through `remotion.config.ts`: run with `REMOTION_BROWSER=/opt/pw-browsers/chromium`. In any other Remotion project, add `--browser-executable=/opt/pw-browsers/chromium_headless_shell` to `remotion render` and `remotion still`. Both paths were tested.
- **Never run `npx playwright install`**, even though `studio/claude-motion/AGENTS.md` says to. Playwright 1.63 already finds its browsers through `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`. For the sims capture, set `CHROMIUM=/opt/pw-browsers/chromium` if a browser path is asked for.
- New Remotion projects install their packages from npm, which is reachable.
- **License:** Remotion is free for individuals and for-profit companies with up to 3 employees. Larger companies need a Remotion company license. Tell the user before relying on Remotion for client work if this may apply.

## Files and storage

- **Never commit media** (`.mp4`, `.mov`, `.wav`, `.mp3` and so on). `.gitignore` blocks them. The one exception is the reference videos that vendored skills ship in `.claude/skills/`, which `.gitignore` allows. Leave them in place, because `motion-graphics` verifies their hashes, and never add produced media there.
- Work in the scratchpad directory. Deliver with SendUserFile or Google Drive.
- The container is ephemeral. Keep code by committing it and media by putting it on Drive.
