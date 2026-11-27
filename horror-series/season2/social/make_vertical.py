"""Vertical 9:16 (1080x1920) versions of the 48 Season 2 posts for Instagram Reels.
Centre 4:3 of the 16:9 frame shown large (1080x810), blurred copy of the video behind, title on top, follow line below.
Usage: python3 make_vertical.py [index ...]   (indices into captions.json; default all)"""
import json, os, sys, subprocess
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); S2 = os.path.dirname(HERE)
OUT = os.path.join(S2, 'video', 'vertical'); os.makedirs(OUT, exist_ok=True)
NF = '/usr/share/fonts/truetype/noto/'
FONT = {'ml': NF + 'NotoSansMalayalam-Bold.ttf', 'hi': NF + 'NotoSansDevanagari-Bold.ttf', 'ta': NF + 'NotoSansTamil-Bold.ttf'}
SERIF = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'; SANS = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
sys.path.insert(0, HERE)
from make_captions import TITLES, LI
EPW = {'ml': 'എപ്പിസോഡ്', 'hi': 'एपिसोड', 'ta': 'எபிசோட்'}
SONGT = {'ml': 'ടൈറ്റിൽ സോങ്', 'hi': 'टाइटल सॉन्ग', 'ta': 'டைட்டில் பாடல்'}
NEXT = {'ml': 'അടുത്ത എപ്പിസോഡ് നാളെ രാത്രി 9 മണിക്ക്', 'hi': 'अगला एपिसोड कल रात 9:20 बजे', 'ta': 'அடுத்த எபிசோட் நாளை இரவு 9:40'}
FIN = {'ml': 'സീസൺ 2 ഫിനാലെ', 'hi': 'सीज़न 2 फ़िनाले', 'ta': 'சீசன் 2 இறுதி எபிசோட்'}
START = {'ml': 'എപ്പിസോഡ് 1 നാളെ രാത്രി 9 മണിക്ക്', 'hi': 'एपिसोड 1 कल रात 9:20 बजे', 'ta': 'எபிசோட் 1 நாளை இரவு 9:40'}


def centred(d, y, text, font, fill, stroke=4):
    w = d.textbbox((0, 0), text, font=font, stroke_width=stroke)[2]
    if w > 1040:   # shrink to fit
        font = ImageFont.truetype(font.path, int(font.size * 1040 / w)); w = d.textbbox((0, 0), text, font=font, stroke_width=stroke)[2]
    d.text(((1080 - w) // 2, y), text, font=font, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


def overlay(p, path):
    im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    # dark bands so text reads over the blurred background
    for y in range(0, 520): d.line([(0, y), (1080, y)], fill=(0, 0, 0, int(150 * (1 - y / 520) + 40)))
    for y in range(1400, 1920): d.line([(0, y), (1080, y)], fill=(0, 0, 0, int(150 * (y - 1400) / 520 + 40)))
    L = p['lang']; F = lambda s, f=None: ImageFont.truetype(f or FONT[L], s)
    centred(d, 150, 'COUNTDOWN', F(118, SERIF), (236, 228, 210))
    centred(d, 285, 'SEASON 2', F(40, SANS), (190, 186, 176), 2)
    if p['kind'] == 'song':
        centred(d, 370, SONGT[L], F(62), (210, 40, 30))
        centred(d, 1440, START[L], F(46), (236, 228, 210))
    else:
        n = p['ep']
        centred(d, 350, f"{EPW[L]} {n}/15", F(52), (210, 40, 30))
        centred(d, 430, TITLES[n][LI[L]], F(56), (236, 228, 210))
        centred(d, 1440, FIN[L] if n == 15 else NEXT[L], F(46), (236, 228, 210))
    centred(d, 1530, 'Follow @kili_poyi_ai', F(44, SANS), (200, 196, 186), 3)
    centred(d, 1600, 'Use headphones', F(34, SANS), (160, 156, 150), 2)
    im.save(path)


def make(i, p):
    src = os.path.join(S2, p['file'])
    out = os.path.join(OUT, os.path.basename(src).replace('.mp4', '_9x16.mp4'))
    png = out[:-4] + '_ov.png'; overlay(p, png)
    fc = ('[0:v]split[a][b];[a]scale=-2:1920,crop=1080:1920,boxblur=24:2,eq=brightness=-0.18[bg];'
          '[b]crop=1440:1080:240:0,scale=1080:810[fg];[bg][fg]overlay=0:555[v1];[v1][1:v]overlay=0:0,format=yuv420p[v]')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-i', png, '-filter_complex', fc, '-map', '[v]', '-map', '0:a',
                    '-c:v', 'libx264', '-preset', 'medium', '-crf', '22', '-maxrate', '7000k', '-bufsize', '14000k', '-r', '24',
                    '-c:a', 'copy', '-movflags', '+faststart', out], check=True)
    os.remove(png); print('wrote', out, os.path.getsize(out) // 1000000, 'MB')


if __name__ == '__main__':
    P = json.load(open(os.path.join(HERE, 'captions.json')))
    idx = [int(a) for a in sys.argv[1:]] or range(len(P))
    for i in idx: make(i, P[i])
