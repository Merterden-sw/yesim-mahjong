"""Draws the app icons: an ivory tile with a red 中 on the jade table."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = os.path.join(os.path.dirname(__file__), '..', 'docs', 'icons')
os.makedirs(OUT, exist_ok=True)
FELT, FELT_LIGHT, IVORY, SHADE, JADE, JADE_DARK, RED = '#0f3b35', '#17564d', '#f6f0df', '#d9cba5', '#2a7a5e', '#1b5843', '#c23a2b'


def font(size):
    for path, idx in [('/System/Library/Fonts/Supplemental/Songti.ttc', 1), ('/System/Library/Fonts/Supplemental/Songti.ttc', 0),
                      ('/System/Library/Fonts/STHeiti Medium.ttc', 0)]:
        try:
            return ImageFont.truetype(path, size, index=idx)
        except OSError:
            continue
    raise SystemExit('no CJK font found')


def draw(size, maskable=False, rounded=True):
    S = 1024
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    bg = Image.new('RGBA', (S, S), FELT)
    glow = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((-150, -200, S + 150, S + 50), fill=FELT_LIGHT)
    bg = Image.alpha_composite(bg, glow.filter(ImageFilter.GaussianBlur(160)))
    mask = Image.new('L', (S, S), 0)
    if rounded and not maskable:
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, S, S), radius=220, fill=255)
    else:
        mask.paste(255, (0, 0, S, S))
    img.paste(bg, (0, 0), mask)
    # Tile size: maskable icons keep the art inside the central safe zone.
    tw = 420 if maskable else 520
    th = int(tw * 4 / 3)
    x0, y0 = (S - tw) // 2 - 14, (S - th) // 2 - 18
    d = ImageDraw.Draw(img)
    depth = 34
    shadow = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((x0 + depth + 10, y0 + depth + 24, x0 + tw + depth + 10, y0 + th + depth + 24), 60, fill=(0, 0, 0, 120))
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(28)))
    for i in range(depth, 0, -1):
        col = JADE_DARK if i > depth * .8 else JADE if i > depth * .45 else SHADE
        d.rounded_rectangle((x0 + i, y0 + i, x0 + tw + i, y0 + th + i), 56, fill=col)
    d.rounded_rectangle((x0, y0, x0 + tw, y0 + th), 56, fill=IVORY)
    f = font(int(tw * .78))
    bb = d.textbbox((0, 0), '中', font=f)
    d.text((x0 + (tw - (bb[2] - bb[0])) / 2 - bb[0], y0 + (th - (bb[3] - bb[1])) / 2 - bb[1]), '中', font=f, fill=RED)
    return img.resize((size, size), Image.LANCZOS)


draw(512).save(f'{OUT}/icon-512.png')
draw(192).save(f'{OUT}/icon-192.png')
draw(512, maskable=True).save(f'{OUT}/icon-maskable-512.png')
draw(180, rounded=False).convert('RGB').save(f'{OUT}/apple-touch-icon.png')
draw(32).save(f'{OUT}/favicon-32.png')
draw(1024).save(f'{OUT}/icon-1024.png')
print('icons written to', os.path.abspath(OUT))
