#!/usr/bin/env python3
"""Build the web cover + social share card from the canonical cover art.

Outputs:
  images/cover.jpg        web-optimised cover for the home hero
  images/social-card.png  1200x630 OG card: cover art + title beside it

Re-run if the cover art changes:  python3 _gen_social_card.py
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path

SITE = Path(__file__).resolve().parent
COVER_SRC = Path("/Users/lgnd/Documents/cowork/fiction/the_wire_branch/"
                 "cover/the_wire_branch_cover_canonical_v1.png")
IMAGES = SITE / "images"
IMAGES.mkdir(exist_ok=True)

cover = Image.open(COVER_SRC).convert("RGB")

# ── 1. web cover (hero) ──
web_w = 900
web = cover.resize((web_w, round(web_w * cover.height / cover.width)), Image.LANCZOS)
web.save(IMAGES / "cover.jpg", "JPEG", quality=90, optimize=True, progressive=True)

# ── 2. social card ──
W, H = 1200, 630

def sample(box):
    return Image.open(COVER_SRC).convert("RGB").crop(box).resize((1, 1), Image.LANCZOS).getpixel((0, 0))

bg = sample((820, 140, 1000, 320))   # open background, upper right — warm taupe
DARK, MUTED, COPPER = (55, 46, 38), (110, 98, 84), (160, 104, 58)

def font(paths, size):
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()

SERIF_B = ["/System/Library/Fonts/Supplemental/Georgia Bold.ttf"]
SERIF_I = ["/System/Library/Fonts/Supplemental/Georgia Italic.ttf"]
MONO = ["/System/Library/Fonts/Menlo.ttc"]
f_title = font(SERIF_B, 66)
f_author = font(MONO, 27)
f_tag = font(SERIF_I, 30)

# cover placed left, fit to height
margin = 84
ch = H - 2 * margin
cw = round(ch * cover.width / cover.height)
cx, cy = margin, margin
cover_fit = cover.resize((cw, ch), Image.LANCZOS)

card = Image.new("RGBA", (W, H), bg + (255,))
shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(shadow).rounded_rectangle(
    [cx - 10, cy + 6, cx + cw + 12, cy + ch + 16], radius=10, fill=(45, 35, 26, 120))
card = Image.alpha_composite(card, shadow.filter(ImageFilter.GaussianBlur(18)))
card.paste(cover_fit, (cx, cy))
ImageDraw.Draw(card).rectangle([cx, cy, cx + cw - 1, cy + ch - 1], outline=(255, 255, 255, 70), width=1)

d = ImageDraw.Draw(card)
tx = cx + cw + 70

def text_w(s, fnt, tr=0):
    return d.textlength(s, font=fnt) + tr * (len(s) - 1)

def draw_tracked(x, y, s, fnt, fill, tr=0):
    for c in s:
        d.text((x, y), c, font=fnt, fill=fill)
        x += d.textlength(c, font=fnt) + tr

# title, wrapped to fit the right column
avail = W - tx - 70
words, lines, cur = "The Wire Branch".split(), [], ""
for w in words:
    t = (cur + " " + w).strip()
    if text_w(t, f_title) <= avail:
        cur = t
    else:
        lines.append(cur); cur = w
if cur:
    lines.append(cur)

title_lh = 74
block_h = len(lines) * title_lh + 30 + 34 + 26 + 40
y = (H - block_h) // 2
for ln in lines:
    d.text((tx, y), ln, font=f_title, fill=DARK)
    y += title_lh
y += 24
draw_tracked(tx, y, "S.J. BARRETT", f_author, MUTED, tr=6)
y += 52
d.text((tx, y), "Ex Dialogo cum Machina", font=f_tag, fill=COPPER)

card.convert("RGB").save(IMAGES / "social-card.png", "PNG")
print("wrote", IMAGES / "cover.jpg", "and", IMAGES / "social-card.png", "; bg", bg)
