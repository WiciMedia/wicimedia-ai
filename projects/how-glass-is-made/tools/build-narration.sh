#!/usr/bin/env bash
# Places the five narration clips on the 61 s timeline used by how-glass-is-made.html
# and writes one mono MP3. Part 4 is split at its pause (3.5 s) into shaping and cooling.
# Usage: tools/build-narration.sh <dir with vo1.mp3 … vo5.mp3> <out.mp3>
set -euo pipefail
D="$1"; OUT="$2"
ffmpeg -v error -y -i "$D/vo1.mp3" -i "$D/vo2.mp3" -i "$D/vo3.mp3" -i "$D/vo4.mp3" -i "$D/vo4.mp3" -i "$D/vo5.mp3" -filter_complex "\
[0]atrim=0:10.76,asetpts=PTS-STARTPTS,adelay=450:all=1[a0];\
[1]atrim=0:11.73,asetpts=PTS-STARTPTS,adelay=12600:all=1[a1];\
[2]atrim=0:9.40,asetpts=PTS-STARTPTS,adelay=25250:all=1[a2];\
[3]atrim=0:3.5,asetpts=PTS-STARTPTS,afade=t=out:st=3.35:d=0.15,adelay=35900:all=1[a3];\
[4]atrim=3.5:8.59,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.1,adelay=42750:all=1[a4];\
[5]atrim=0:9.56,asetpts=PTS-STARTPTS,adelay=49950:all=1[a5];\
[a0][a1][a2][a3][a4][a5]amix=inputs=6:normalize=0:dropout_transition=0,apad=whole_dur=61,atrim=0:61[out]" \
  -map "[out]" -ac 1 -ar 44100 -c:a libmp3lame -b:a 160k "$OUT"
