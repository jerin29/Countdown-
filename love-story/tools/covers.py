"""Reel cover images for ഒരു റിപ്ലൈ (1080x1920). Text sits inside the centre 1080x1350 band so the
profile grid (3:4 crop) still shows the title. Usage: python3 covers.py [key ...]  -> love-story/covers/*.jpg
"""
import os, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ep01 as E

AN = '/home/user/Countdown-/love-story/anime_test'
OUT = '/home/user/Countdown-/love-story/covers'
W, H = 1080, 1920
GOLD, CREAM = (240, 205, 150), (246, 236, 220)

# key: (image, focus y 0..1, badge, title, hook)
COVERS = {
    'song': ('manjusha_sunrise', .45, 'ടൈറ്റിൽ സോങ്', 'ഒരു റിപ്ലൈ', 'ഒരു റിപ്ലൈക്കായി കാത്തിരുന്ന ഒരാൾ'),
    'ep01': ('aadhi_214am', .5, 'എപ്പിസോഡ് 1', '2:14 AM', 'ഉറക്കം വരാത്ത രാത്രി… ഒരു റീൽ'),
    'ep02': ('e2_busstop', .5, 'എപ്പിസോഡ് 2', 'ചുവര്', 'അവൾക്ക് എന്റെ മെസ്സേജ് എത്തുന്നില്ല'),
    'ep03': ('e3_buzz', .55, 'എപ്പിസോഡ് 3', 'കൊളാബ് പേജ്', 'അവസാനം… ആ മെസ്സേജ് അയച്ചു'),
    'ep04': ('e4_call', .5, 'എപ്പിസോഡ് 4', 'ഒരു റിപ്ലൈ', 'അവൾ എനിക്ക് റിപ്ലൈ ചെയ്തു!'),
    'ep05': ('e5_gift', .55, 'എപ്പിസോഡ് 5', 'അടുത്തേക്ക്', 'ഗിഫ്റ്റ് അയക്കണം… പക്ഷേ എവിടേക്ക്?'),
    'ep06': ('e6_fade', .45, 'എപ്പിസോഡ് 6', 'സമ്മാനം', 'ഇവന് എന്റെ വീട് എങ്ങനെ അറിയാം?'),
}


def fit(d, text, f, size, maxw):
    while d.textlength(text, font=f(size)) > maxw and size > 30: size -= 4
    return f(size)


def make(key):
    img, fy, badge, title, hook = COVERS[key]
    im = cv2.imread(os.path.join(AN, img + '.jpg'))
    h, w = im.shape[:2]; s = max(W / w, H / h)
    im = cv2.resize(im, (round(w * s), round(h * s)), interpolation=cv2.INTER_AREA)
    y0 = int(np.clip(fy * im.shape[0] - H / 2, 0, im.shape[0] - H)); x0 = (im.shape[1] - W) // 2
    im = im[y0:y0 + H, x0:x0 + W]
    base = Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).convert('RGBA')
    # dark gradient from mid to the bottom of the safe band, light one at the top
    g = np.zeros((H, W, 4), np.uint8)
    ys = np.arange(H)[:, None]
    a = np.clip((ys - 950) / 650, 0, 1) * 225 + np.clip((420 - ys) / 420, 0, 1) * 120
    g[..., 3] = a.astype(np.uint8)
    base.alpha_composite(Image.fromarray(g, 'RGBA'))
    d = ImageDraw.Draw(base)
    ml = E.mlfont
    # badge pill (top of the safe band)
    bf = ml('Bold', 44); bw = d.textlength(badge, font=bf) + 70
    d.rounded_rectangle([(W - bw) / 2, 330, (W + bw) / 2, 410], 40, fill=(200, 60, 90, 235))
    d.text((W / 2, 370), badge, font=bf, fill=(255, 255, 255, 255), anchor='mm')
    # series name, heart, episode title, hook line — stacked above the bottom of the safe band
    sh = Image.new('RGBA', (W, H)); sd = ImageDraw.Draw(sh)
    tf = fit(d, title, (lambda z: E.font('Bold', z)) if title.isascii() else (lambda z: ml('Bold', z)), 150, W - 120)
    items = [((W / 2, 1180), 'ഒരു റിപ്ലൈ' if key != 'song' else '', ml('Bold', 64), GOLD),
             ((W / 2, 1360), title, tf, CREAM),
             ((W / 2, 1530), hook, fit(d, hook, lambda z: ml('Regular', z), 50, W - 120), (225, 220, 210))]
    for xy, t, f, c in items:
        if t: sd.text((xy[0] + 3, xy[1] + 5), t, font=f, fill=(0, 0, 0, 200), anchor='mm')
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    d = ImageDraw.Draw(base)
    for xy, t, f, c in items:
        if t: d.text(xy, t, font=f, fill=c + (255,), anchor='mm')
    E.heart(d, W / 2, 1260 if key != 'song' else 1250, 22, fill=(237, 120, 140, 255), outline=(237, 120, 140, 255), w=2)
    os.makedirs(OUT, exist_ok=True)
    p = f'{OUT}/ONE_REPLY_cover_{key}.jpg'
    base.convert('RGB').save(p, quality=93); print(p)


if __name__ == '__main__':
    for k in (sys.argv[1:] or COVERS): make(k)
