"""Timed lyric lines for the Season 2 title song videos.
Word timings come from ElevenLabs speech-to-text (song/stt/*.json); each sung phrase is matched to the
official lyric line (song/*-lyrics.md) so the screen shows the correct spelling, plus an English line."""
import json, os, re, difflib, sys
SONG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = {'ml': ('naalpathu-ml-v2_master', 'naalpathu-ml-lyrics.md'),
         'hi': ('chaalis-hi_master', 'chaalis-hi-lyrics.md'),
         'ta': ('naarpathu-ta_master', 'naarpathu-ta-lyrics.md')}
EN = {
 'city': "The city sleeps, the clock has stopped", 'three': "At three in the night, someone is calling",
 'notten': "Not ten anymore: forty chimes", 'name': "And every one of them says your name",
 'turned': "Wasn't it you who turned it back?", 'woke': "Wasn't it you who woke her?",
 'wake': "Forty chimes... no one will wake again", 'return': "Forty chimes... no one will come back",
 'close': "Close your eyes, and she is beside you", 'open': "Open your eyes, and you are gone",
 'forty': "Forty... forty...", 'mirror': "The shadow in the mirror lags one moment behind",
 'gears': "Gears are turning under the skin", 'faces': "Clock-faced figures standing in the street",
 'blink': "They come closer only when you blink", 'lullaby': "It isn't a lullaby, it's her call",
 'breath': "It isn't sleep, it's the last breath", 'look': "Don't look back... don't look back...",
 'count': "Forty... thirty-nine... thirty-eight...", 'sings': "She sings... you count...",
 'behind': "She is behind you...", 'zero': "Zero.",
}
# official line order in each lyrics file (first occurrences, parentheses removed) -> meaning key
ORDER = ['city', 'three', 'notten', 'name', 'turned', 'woke', 'wake', 'return', 'close', 'open', 'forty',
         'mirror', 'gears', 'faces', 'blink', 'lullaby', 'breath', 'look', 'count', 'sings']
EXTRA = {'ml': {'behind': 'അവൾ നിന്റെ പുറകിലുണ്ട്', 'zero': 'പൂജ്യം'},
         'hi': {'behind': 'वो तुम्हारे पीछे है', 'zero': 'शून्य'},
         'ta': {'behind': 'அவள் உன் பின்னால் இருக்கிறாள்', 'zero': 'பூஜ்ஜியம்'}}


def official(lang):
    out, seen = [], set()
    for ln in open(os.path.join(SONG, FILES[lang][1]), encoding='utf-8'):
        ln = ln.strip()
        if not ln or ln.startswith(('#', '[')) or re.fullmatch(r'[A-Za-z].*', ln): continue
        txt = re.sub(r'[()]', '', ln).strip(' …')
        if re.fullmatch(r'(टिक|டிக்|ടിക്|ही|ஹி)[\s…]*.*', txt) and len(set(txt.split())) <= 2: continue
        if txt in seen: continue
        seen.add(txt); out.append(txt)
    lines = {k: out[i] for i, k in enumerate(ORDER)}
    lines.update(EXTRA[lang]); return lines


FORTY = ('നാല്പതു', 'നാൽപത്', 'चालीस', 'चालिश', 'நாற்பது')
is_forty = lambda ws: all(norm(w['text']) in FORTY for w in ws)
norm = lambda s: re.sub(r'[\s.,?!।…\-]', '', s)


def timed(lang):
    d = json.load(open(os.path.join(SONG, 'stt', FILES[lang][0] + '.json'), encoding='utf-8'))
    words = [w for w in d['words'] if w.get('type') == 'word']
    segs, cur = [], []
    for w in words:
        if cur and (w['start'] - cur[-1]['end'] > .6): segs.append(cur); cur = []
        cur.append(w)
        if re.search(r'[.?!।,]$', w['text']): segs.append(cur); cur = []
    if cur: segs.append(cur)
    m = []                                 # glue very short phrases onto the next one
    for s in segs:
        if m and len(m[-1]) <= 2 and s[0]['start'] - m[-1][-1]['end'] < .8 and not is_forty(m[-1]): m[-1] = m[-1] + s
        else: m.append(s)
    L = official(lang)
    def best(ws):
        txt = norm(' '.join(w['text'] for w in ws))
        if is_forty(ws): return 'forty', 1.0
        k = max(L, key=lambda k: difflib.SequenceMatcher(None, txt, norm(L[k])).ratio())
        return k, difflib.SequenceMatcher(None, txt, norm(L[k])).ratio()
    def split(ws):
        k, r = best(ws)
        if len(ws) >= 4:
            cands = []
            for i in range(2, len(ws) - 1):
                (ka, ra), (kb, rb) = best(ws[:i]), best(ws[i:])
                if min(ra, rb) > max(.55, r + .05): cands.append((ra + rb, i))
            if cands:
                i = max(cands)[1]; return split(ws[:i]) + split(ws[i:])
        return [(ws, k, r)]
    out = []
    for s in m:
        for ws, k, r in split(s):
            txt = ' '.join(w['text'] for w in ws)
            if r < .5: print('  skip', lang, f"{ws[0]['start']:.1f}", txt, k, round(r, 2), file=sys.stderr); continue
            if out and out[-1]['key'] == k and ws[0]['start'] - out[-1]['t1'] < 1.5 and k != 'forty':
                out[-1]['t1'] = ws[-1]['end']; continue
            out.append({'t0': ws[0]['start'], 't1': ws[-1]['end'], 'key': k, 'text': L[k], 'en': EN[k]})
    for i, o in enumerate(out):   # hold each line until the next one (max +1.8 s)
        nxt = out[i + 1]['t0'] - .25 if i + 1 < len(out) else o['t1'] + 2
        o['t1'] = min(nxt - .1, o['t1'] + 1.8); o['t0'] = max(0, o['t0'] - .25)
    return out


if __name__ == '__main__':
    for lang in sys.argv[1:] or ['ml', 'hi', 'ta']:
        print('==', lang)
        for o in timed(lang): print(f"{o['t0']:6.1f}-{o['t1']:6.1f} {o['key']:8s} {o['text']}")
