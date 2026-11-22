# Third-party skills

Every skill in this folder except `arabic-subtitles` was copied from a public GitHub repository at the commit below. Each was reviewed before being added, and each copy keeps its upstream license as `LICENSE.third-party`. All nine sources are MIT-licensed.

To update one, clone the repository at the new commit, review the diff (scripts, network calls, instructions), copy it over, and change the commit here. Do not pull updates blindly: a skill's text becomes instructions Claude follows.

| # | Source | Commit | Installed as |
|---|---|---|---|
| 01 | [Jakeschincariol/youtube-agent-skill](https://github.com/Jakeschincariol/youtube-agent-skill) | `a2feb2104981` (2026-09-16) | `yt-audit`, `yt-chapters`, `yt-comment`, `yt-edit`, `yt-package`, `yt-plan`, `yt-retention`, `yt-script`, `yt-seo`, `yt-shorts`, `yt-viral` |
| 02 | [AgriciDaniel/claude-youtube](https://github.com/AgriciDaniel/claude-youtube) | `84c3fa680520` (2026-04-10) | `youtube` |
| 03 | [mohitagw15856/pm-claude-skills](https://github.com/mohitagw15856/pm-claude-skills), only `skills/youtube-script-writer` | `c4679f94f256` (2026-11-16) | `youtube-script-writer` |
| 04 | [cdeistopened/content-os](https://github.com/cdeistopened/content-os) | `16e080f04186` (2026-02-12) | the other 35 folders: `ai-tells` … `youtube-title-creator`. `research/notebooklm` was skipped because it has no SKILL.md |
| 05 | [whaleyxbt/claude-motion](https://github.com/whaleyxbt/claude-motion) | `6f80380b9185` (2026-11-08) | the whole Remotion project, in `studio/claude-motion/` with `media/` left out. Its own skills (`motion-design`, `sound-design`, `review-loop`, `web-sims`) live in `studio/claude-motion/.claude/skills/` and apply when working in that folder |
| 06 | [howseen-ai/claude-motion-design](https://github.com/howseen-ai/claude-motion-design) | `3d90d349ef3f` (2026-10-02) | `claude-motion-design` (renamed from upstream's `motion-design`) |
| 07 | [haidrrrry/claude-remotion-skill](https://github.com/haidrrrry/claude-remotion-skill) | `1dcbe5e3fc6c` (2026-08-12) | `remotion-motion-graphics` |
| 08 | [Liamrjohnston/remotion-motion-graphics-skill](https://github.com/Liamrjohnston/remotion-motion-graphics-skill) | `b860c7921f22` (2026-07-23) | `motion-graphics`, `cinematic-camera`, `terminal-inserts`, `article-highlights` |
| 09 | [Melvynx/video-agent-skills](https://github.com/Melvynx/video-agent-skills), only `skills/` | `f4542923f7f7` (2026-11-06) | `editing`, `studio-setup`, `studio-script`, `short-editing`, `steal`, `broll`, `clips`, `short-translate`, `insta-audit`, `outliers`, `publish`, `codex-images`, `vox` |

## Review notes

- No prompt-injection text, hidden commands, credential reads, or data exfiltration were found. `promptible-gate.mjs` (in `motion-graphics`) is a local-only state machine that checks file hashes and makes no network calls.
- Some scripts call outside services, and only when used with your own key or token:
  - `youtube`: the YouTube Data API (`YOUTUBE_API_KEY` or OAuth).
  - `nano-banana-image-generator`: Gemini (`GEMINI_API_KEY`).
  - `invisible-threads`: Anthropic and Gemini.
  - `x-posting`: getlate.dev.
  - `claude-motion-design`: 21st.dev (`API_KEY_21ST`), api.svgl.app and Mixkit.
  - video-agent-skills: ElevenLabs (`ELEVENLABS_API_KEY`: transcription, dubbing, audio isolation), OpenAI or Gemini images (`OPENAI_API_KEY`, `GEMINI_API_KEY`), the Codex CLI, and Treg (treg.to). Keys are read from `video-agent/.env` or `~/.short-editing/.env` and sent only to their own API. Without a key the engine stays local: whisper.cpp, Chrome and ffmpeg. Its setup downloads the whisper model from Hugging Face, the MediaPipe face models from storage.googleapis.com and the Noto icons from api.iconify.design. `broll` asks nominatim.openstreetmap.org for place names when clips carry GPS.
- video-agent-skills (reviewed 2026-11-22: every SKILL.md read in full, the engine grepped for processes, network calls and key reads):
  - **Treg** is a third-party service. `insta-audit`, `outliers`, `steal` and `publish` use it, and `publish` posts to Instagram, TikTok and YouTube through it. Its install is `curl -fsSL https://treg.to/install.sh | sh`, and it was not reviewed. The skills ask before installing, say the price before paid calls, and post only after an explicit yes.
  - Several skills pre-approve broad commands in their `allowed-tools` while they run: `Bash(node *)` in `studio-setup`, `short-editing`, `clips` and `vox`, and `Bash(node -e *)` in `broll`. Left as upstream.
  - `short-editing` shows a feedback link (codelynx.dev) once, after the first finished video. The README promotes the author's paid course. Neither does anything else.
  - The one zero-width joiner in `studio-script/references/humanize.md` sits inside its own explanation of invisible characters. It is harmless.
- The motion-graphics skill's reference videos (`assets/references/*.mp4`) are committed on purpose. Its gate verifies their SHA-256 hashes before a build. `.gitignore` allows `*.mp4` under `.claude/skills/` only.
## Local changes to upstream

- **`claude-motion-design`**: renamed from `motion-design`, in both the directory and the `name:` field, so it doesn't clash with claude-motion's own `motion-design` skill. Its description is quoted so the frontmatter is valid YAML.
- **content-os skills**: `seo-content-writer`, `seo-research`, `day-in-the-life`, `invisible-threads`, `memo`, `verified-review` and `vellum-prep` had no frontmatter upstream. Each got a `name` and a one-line `description` taken from its own text. Nothing else was changed.
- **`short-editing`**: the prebuilt macOS binaries `engine/bin/darwin/faces` and `matte` were left out because compiled code can't be reviewed. Their Swift sources (`faces.swift`, `matte.swift`) are included. On a Mac with Xcode tools the engine compiles them once. Otherwise, as on Linux, it uses MediaPipe inside Chrome (`vision-web.mjs`).
- **`youtube-scriptwriting`**: every file in it is empty upstream. It now holds a short note and `disable-model-invocation: true` so it is never picked. For scripts, use `yt-script` or `youtube-script-writer`.

## Other notes

- `claude-motion-design` (howseen-ai) was written for its author's own studio, so its paths such as `~/Desktop/Howseen AI/...` and `howseen-video/.venv` do not exist here. On this machine, use `/opt/video-env` and the system ffmpeg.
- video-agent-skills in a cloud session: run the engine with `CHROME_PATH=/opt/pw-browsers/chromium`, so its setup finds this browser and never runs `playwright install`. There is no whisper.cpp here, so `short-editing words` needs `ELEVENLABS_API_KEY`, or a `whisper-cli` built from source and set as `WHISPER_CLI`. Everything else in setup (npm packages, music beds, icons) works. The skills that only write (`studio-script`, `outliers`' scripts) need nothing.
