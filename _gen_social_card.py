#!/usr/bin/env python3
"""Generate a placeholder 1200x630 social-share card (images/social-card.png).
Temporary — replace with the real cover art when it exists. Re-run after edits.

    python3 _gen_social_card.py
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

W, H = 1200, 630
BG = (23, 24, 26)        # near-black, matches --text
FG = (244, 244, 242)     # paper --bg
MUTED = (150, 152, 156)
ACCENT = (184, 134, 11)  # the Strand ochre

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

def font(paths, size):
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()

SERIF = ["/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
         "/System/Library/Fonts/Supplemental/Georgia.ttf",
         "/Library/Fonts/Georgia.ttf"]
MONO = ["/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Supplemental/Courier New.ttf"]

f_title = font(SERIF, 92)
f_by = font(MONO, 26)
f_tag = font(SERIF, 30)

def center(text, y, fnt, fill, tracking=0):
    if tracking:
        # manual letter-spacing
        widths = [d.textlength(c, font=fnt) for c in text]
        total = sum(widths) + tracking * (len(text) - 1)
        x = (W - total) / 2
        for c, w in zip(text, widths):
            d.text((x, y), c, font=fnt, fill=fill)
            x += w + tracking
    else:
        w = d.textlength(text, font=fnt)
        d.text(((W - w) / 2, y), text, font=fnt, fill=fill)

# wire mark — a simple bent-wire glyph, scaled from the site's SVG path
cx, top = W / 2, 118
s = 1.9
def P(x, y): return (cx + (x - 60) * s, top + (y - 10) * s)
pts_main = [P(60,134), P(60,96), P(36,74), P(36,50), P(60,30), P(60,10)]
pts_branch = [P(60,96), P(84,74), P(84,44)]
d.line(pts_main, fill=FG, width=5, joint="curve")
d.line(pts_branch, fill=FG, width=5, joint="curve")

center("The Wire Branch", 386, f_title, FG)
center("S.J. BARRETT", 506, f_by, MUTED, tracking=8)
center("Ex Dialogo cum Machina", 556, f_tag, ACCENT)

out = Path(__file__).resolve().parent / "images" / "social-card.png"
out.parent.mkdir(exist_ok=True)
img.save(out, "PNG")
print("wrote", out)
