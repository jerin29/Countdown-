"""AGAIN poster: anime art + a huge "23" behind, AGAIN title, Malayalam subtitle and tagline.
Usage: python3 poster.py ART.jpg OUT.jpg [top|bottom]   (where the title block goes)
Makes OUT (1080x1920) and OUT with _4x5 (1080x1350 feed crop).
"""
import sys, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, '/home/user/Countdown-/love-story/tools')
import ep01 as E

W, H = 1080, 1920
font, mlfont = E.font, E.mlfont
RED, GOLD, CREAM = (214, 40, 52), (246, 196, 92), (250, 244, 232)


def make(art, out, where='bottom'):
    im = cv2.imread(art); im = cv2.resize(im, (W, H), interpolation=cv2.INTER_CUBIC)
    base = Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).convert('RGBA')
    # big translucent 23 behind everything in the title zone
    big = Image.new('RGBA', (W, H)); bd = ImageDraw.Draw(big)
    y23 = 1180 if where == 'bottom' else 420
    bd.text((W / 2, y23), '23', font=font('Bold', 760), fill=(255, 255, 255, 46), anchor='mm')
    base.alpha_composite(big)
    # gradient for legibility
    g = np.zeros((H, W, 4), np.uint8); ys = np.arange(H)[:, None]
    if where == 'bottom': a = np.clip((ys - 1000) / 600, 0, 1) * 235
    else: a = np.clip((560 - ys) / 520, 0, 1) * 215 + np.clip((ys - 1480) / 380, 0, 1) * 220
    g[..., 3] = a.astype(np.uint8); base.alpha_composite(Image.fromarray(g, 'RGBA'))
    # title block
    ty = 1330 if where == 'bottom' else 210
    sub_y = ty + 290 if where == 'bottom' else H - 300     # tagline: under the title (bottom) or near the foot (top)
    sh = Image.new('RGBA', (W, H)); sd = ImageDraw.Draw(sh)
    items = [((W / 2, ty), 'AGAIN', font('Bold', 230), CREAM),
             ((W / 2, ty + 170), 'വീണ്ടും', mlfont('Bold', 74), GOLD),
             ((W / 2, sub_y), 'ഇത് അവസാനമല്ല… എല്ലാത്തിനും തുടക്കമാണ്', mlfont('Regular', 44), (235, 228, 214))]
    for xy, t, f, c in items: sd.text((xy[0] + 4, xy[1] + 6), t, font=f, fill=(0, 0, 0, 210), anchor='mm')
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(9)))
    d = ImageDraw.Draw(base)
    for xy, t, f, c in items: d.text(xy, t, font=f, fill=c + (255,), anchor='mm')
    # red bar with 23 badge
    by = sub_y + 70
    d.rectangle([W / 2 - 170, by, W / 2 + 170, by + 6], fill=RED + (255,))
    d.text((W / 2, by + 60), 'A TRUE STORY  ·  #23', font=font('SemiBold', 36), fill=(255, 255, 255, 230), anchor='mm')
    d.text((W / 2, H - 60), 'Story: Jerin Joseph Sebastian  ·  @kili_poyi_ai', font=font('Regular', 30), fill=(210, 205, 195, 220), anchor='mm')
    base.convert('RGB').save(out, quality=94)
    # 4:5 feed crop around the centre
    c = base.convert('RGB').crop((0, 285, W, 285 + 1350)); c.save(out.replace('.jpg', '_4x5.jpg'), quality=94)
    print(out)


if __name__ == '__main__':
    make(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else 'bottom')
