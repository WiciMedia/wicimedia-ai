# Third-party skills

Every skill in this folder except `arabic-subtitles` was copied from a public GitHub repository at the commit below. Each was reviewed before being added, and each copy keeps its upstream license as `LICENSE.third-party`. All eight sources are MIT-licensed.

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

## Review notes

- No prompt-injection text, hidden commands, credential reads, or data exfiltration were found. `promptible-gate.mjs` (in `motion-graphics`) is a local-only state machine that checks file hashes and makes no network calls.
- Some scripts call outside services, and only when used with your own key or token:
  - `youtube`: the YouTube Data API (`YOUTUBE_API_KEY` or OAuth).
  - `nano-banana-image-generator`: Gemini (`GEMINI_API_KEY`).
  - `invisible-threads`: Anthropic and Gemini.
  - `x-posting`: getlate.dev.
  - `motion-design`: 21st.dev (`API_KEY_21ST`), api.svgl.app and Mixkit.
- The motion-graphics skill's reference videos (`assets/references/*.mp4`) are committed on purpose. Its gate verifies their SHA-256 hashes before a build. `.gitignore` allows `*.mp4` under `.claude/skills/` only.
## Local changes to upstream

- **`claude-motion-design`**: renamed from `motion-design`, in both the directory and the `name:` field, so it doesn't clash with claude-motion's own `motion-design` skill. Its description is quoted so the frontmatter is valid YAML.
- **content-os skills**: `seo-content-writer`, `seo-research`, `day-in-the-life`, `invisible-threads`, `memo`, `verified-review` and `vellum-prep` had no frontmatter upstream. Each got a `name` and a one-line `description` taken from its own text. Nothing else was changed.
- **`youtube-scriptwriting`**: every file in it is empty upstream. It now holds a short note and `disable-model-invocation: true` so it is never picked. For scripts, use `yt-script` or `youtube-script-writer`.

## Other notes

- `claude-motion-design` (howseen-ai) was written for its author's own studio, so its paths such as `~/Desktop/Howseen AI/...` and `howseen-video/.venv` do not exist here. On this machine, use `/opt/video-env` and the system ffmpeg.
