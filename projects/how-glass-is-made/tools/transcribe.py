import sys, json, glob, os
from faster_whisper import WhisperModel
m = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", download_root="/opt/whisper-models")
out = {}
for i in range(1, 6):
    p = os.path.join(sys.argv[1], f"vo{i}.mp3")
    segs, info = m.transcribe(p, language="en", word_timestamps=True, beam_size=5, vad_filter=False)
    words = []; text = []
    for s in segs:
        text.append(s.text.strip())
        for w in s.words: words.append([round(w.start, 2), round(w.end, 2), w.word])
    out[i] = {"text": " ".join(text), "words": words}
    print(f"--- {i}: {out[i]['text']}")
    print(" ".join(f"{w[2].strip()}@{w[0]:.2f}" for w in words))
json.dump(out, open(os.path.join(sys.argv[1], "words.json"), "w"), indent=1)
