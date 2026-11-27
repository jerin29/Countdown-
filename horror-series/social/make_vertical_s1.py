"""Vertical 9:16 (1080x1920) versions of Season 1 episodes 6-10 (ml/hi/ta) for Instagram Reels.
Same layout as season2/social/make_vertical.py.  Usage: python3 make_vertical_s1.py [lang:ep ...]"""
import os, sys, subprocess
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); S1 = os.path.dirname(HERE)
OUT = os.path.join(S1, 'video', 'vertical'); os.makedirs(OUT, exist_ok=True)
NF = '/usr/share/fonts/truetype/noto/'
FONT = {'ml': NF + 'NotoSansMalayalam-Bold.ttf', 'hi': NF + 'NotoSansDevanagari-Bold.ttf', 'ta': NF + 'NotoSansTamil-Bold.ttf'}
SERIF = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'; SANS = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
EPW = {'ml': 'എപ്പിസോഡ്', 'hi': 'एपिसोड', 'ta': 'எபிசோடு'}
TITLES = {6: {'ml': 'വർക്കി ആൻഡ് സൺസ്', 'hi': 'वर्की एंड संस', 'ta': 'வர்க்கி அண்ட் சன்ஸ்'},
          7: {'ml': 'നഷ്ടപ്പെട്ട സമയം', 'hi': 'खोया हुआ वक़्त', 'ta': 'தொலைந்த நேரம்'},
          8: {'ml': 'ആടുന്ന കസേര', 'hi': 'झूलती कुर्सी', 'ta': 'ஆடும் நாற்காலி'},
          9: {'ml': 'ഗോപുരത്തിനുള്ളിൽ', 'hi': 'घंटाघर के अंदर', 'ta': 'மணிக்கூண்டுக்குள்'},
          10: {'ml': 'അവസാന മണിയൊച്ച', 'hi': 'आख़िरी घंटी', 'ta': 'கடைசி மணியோசை'}}
NEXT = {'ml': 'അടുത്ത എപ്പിസോഡ് നാളെ രാത്രി 9 മണിക്ക്', 'hi': 'अगला एपिसोड कल रात 9:20 बजे', 'ta': 'அடுத்த எபிசோடு நாளை இரவு 9:40'}
FIN = {'ml': 'സീസൺ 1 ഫിനാലെ', 'hi': 'सीज़न 1 फ़िनाले', 'ta': 'சீசன் 1 இறுதி எபிசோடு'}
S2DATE = {'ml': 'SEASON 2  -  9 DEC', 'hi': 'SEASON 2  -  10 DEC', 'ta': 'SEASON 2  -  10 DEC'}
SRC = {'ml': 'COUNTDOWN_ep{:02d}_cinematic_ml.mp4', 'hi': 'hi/COUNTDOWN_ep{:02d}_cinematic_hi.mp4', 'ta': 'ta/COUNTDOWN_ep{:02d}_cinematic_ta.mp4'}


def centred(d, y, text, font, fill, stroke=4):
    w = d.textbbox((0, 0), text, font=font, stroke_width=stroke)[2]
    if w > 1040:
        font = ImageFont.truetype(font.path, int(font.size * 1040 / w)); w = d.textbbox((0, 0), text, font=font, stroke_width=stroke)[2]
    d.text(((1080 - w) // 2, y), text, font=font, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


def overlay(L, n, path):
    im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for y in range(0, 520): d.line([(0, y), (1080, y)], fill=(0, 0, 0, int(150 * (1 - y / 520) + 40)))
    for y in range(1400, 1920): d.line([(0, y), (1080, y)], fill=(0, 0, 0, int(150 * (y - 1400) / 520 + 40)))
    F = lambda s, f=None: ImageFont.truetype(f or FONT[L], s)
    centred(d, 150, 'COUNTDOWN', F(118, SERIF), (236, 228, 210))
    centred(d, 290, f"{EPW[L]} {n}/10", F(56), (210, 40, 30))
    centred(d, 390, TITLES[n][L], F(60), (236, 228, 210))
    if n == 10:
        centred(d, 1430, FIN[L], F(46), (236, 228, 210))
        centred(d, 1500, S2DATE[L], F(40, SANS), (210, 40, 30), 3)
        fy = 1580
    else:
        centred(d, 1440, NEXT[L], F(46), (236, 228, 210)); fy = 1530
    centred(d, fy, 'Follow @kili_poyi_ai', F(44, SANS), (200, 196, 186), 3)
    centred(d, fy + 70, 'Use headphones', F(34, SANS), (160, 156, 150), 2)
    im.save(path)


def make(L, n):
    src = os.path.join(S1, 'video', SRC[L].format(n))
    out = os.path.join(OUT, f'COUNTDOWN_S1_ep{n:02d}_{L}_9x16.mp4')
    png = out[:-4] + '_ov.png'; overlay(L, n, png)
    fc = ('[0:v]split[a][b];[a]scale=-2:1920,crop=1080:1920,boxblur=24:2,eq=brightness=-0.18[bg];'
          '[b]crop=1440:1080:240:0,scale=1080:810[fg];[bg][fg]overlay=0:555[v1];[v1][1:v]overlay=0:0,format=yuv420p[v]')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-i', png, '-filter_complex', fc, '-map', '[v]', '-map', '0:a',
                    '-c:v', 'libx264', '-preset', 'medium', '-crf', '22', '-maxrate', '7000k', '-bufsize', '14000k', '-r', '24',
                    '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', out], check=True)
    os.remove(png); print('wrote', out, os.path.getsize(out) // 1000000, 'MB', flush=True)


if __name__ == '__main__':
    jobs = [a.split(':') for a in sys.argv[1:]] or [(L, n) for L in ('ml', 'hi', 'ta') for n in range(6, 11)]
    for L, n in jobs: make(L, int(n))
