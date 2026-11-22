#!/usr/bin/env bash
# Places the five narration clips on the 61.7 s timeline used by how-glass-is-made-ar.html
# and writes one mono MP3. Part 4 is split at its pause (4.0 s); Arabic is louder, so the mix is lowered 6 dB into shaping and cooling.
# Usage: tools/build-narration.sh <dir with vo1.mp3 … vo5.mp3> <out.mp3>
set -euo pipefail
D="$1"; OUT="$2"
ffmpeg -v error -y -i "$D/vo1.mp3" -i "$D/vo2.mp3" -i "$D/vo3.mp3" -i "$D/vo4.mp3" -i "$D/vo4.mp3" -i "$D/vo5.mp3" -filter_complex "\
[0]atrim=0:8.83,asetpts=PTS-STARTPTS,adelay=450:all=1[a0];\
[1]atrim=0:12.04,asetpts=PTS-STARTPTS,adelay=11550:all=1[a1];\
[2]atrim=0:9.64,asetpts=PTS-STARTPTS,adelay=24600:all=1[a2];\
[3]atrim=0:4.0,asetpts=PTS-STARTPTS,afade=t=out:st=3.85:d=0.15,adelay=35550:all=1[a3];\
[4]atrim=4.0:9.87,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.1,adelay=42000:all=1[a4];\
[5]atrim=0:11.08,asetpts=PTS-STARTPTS,adelay=49750:all=1[a5];\
[a0][a1][a2][a3][a4][a5]amix=inputs=6:normalize=0:dropout_transition=0,volume=-6dB,apad=whole_dur=61.7,atrim=0:61.7[out]" \
  -map "[out]" -ac 1 -ar 44100 -c:a libmp3lame -b:a 160k "$OUT"
