"""Turns a landscape page (English or Arabic) into its 9:16 version for TikTok and Reels.

The page itself switches to the vertical renderer with CFG.vert: a director camera
follows each scene at about 1.4x, and the headline, subtitles and progress strip are
drawn natively at phone size. This script flips that flag and adjusts the page chrome.

Usage: python3 -I make-vertical.py <landscape.html> <vertical.html>
"""
import re
import sys

src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c >= n and (n == 0 or c == n), (c, a[:90])
    s = s.replace(a, b)


rep("/*CFG*/", "/*CFG*/ CFG.vert=true;")
rep(".stage{position:relative;aspect-ratio:16/9;max-width:100%;", ".stage{position:relative;aspect-ratio:9/16;width:min(100%,430px);margin-inline:auto;max-width:100%;")
rep('width="1280" height="720"', 'width="720" height="1280"')
ar = "lang:'ar'" in s
s = re.sub(r"<title>(.*?)</title>", lambda m: "<title>" + m.group(1) + (" عمودي" if ar else " Vertical") + "</title>", s, count=1)
s = s.replace("1920 × 1080", "1080 × 1920")
s = s.replace("'how-glass-is-made-ar.'+r.ext", "'how-glass-is-made-ar-vertical.'+r.ext").replace("'how-glass-is-made.'+r.ext", "'how-glass-is-made-vertical.'+r.ext")
s = s.replace("narrated</p>", "narrated · 9:16</p>").replace("بتعليق عربي</p>", "بتعليق عربي · 9:16</p>")
open(dst, "w", encoding="utf-8").write(s)
print("wrote", dst, len(s))
