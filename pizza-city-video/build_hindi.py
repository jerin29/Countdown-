# Builds the Hindi version in ../pizza-city-video-hindi from the same scenes, retimed to the Hindi song.
# Every animation time is moved with a piecewise-linear map from German anchor times to Hindi anchor times.
import json, re, pathlib, shutil, subprocess, sys
here = pathlib.Path(__file__).parent
cfg = json.load(open(here / 'hindi.json'))
DE, HI = cfg['anchors_de'], cfg['anchors_hi']
def warp(t):
    for i in range(len(DE) - 1):
        if t <= DE[i + 1] or i == len(DE) - 2:
            a, b, c, d = DE[i], DE[i + 1], HI[i], HI[i + 1]
            return c + (t - a) * (d - c) / (b - a)
DE_HOSTS = [('kitchen', 0, 26.13), ('oven', 26.13, 20.5), ('ride', 46.63, 19.4), ('door', 66.03, 7.85), ('finale', 73.88, 14.86)]
out = here.parent / 'pizza-city-video-hindi'
(out / 'compositions').mkdir(parents=True, exist_ok=True)
(out / 'assets' / 'fonts').mkdir(parents=True, exist_ok=True)
for f in ['hyperframes.json', 'package.json', 'CLAUDE.md', 'AGENTS.md', 'meta.json', '.gitignore']:
    if (here / f).exists(): shutil.copy(here / f, out / f)
for f in (here / 'assets' / 'fonts').glob('*'): shutil.copy(f, out / 'assets' / 'fonts' / f.name)
subprocess.run([sys.executable, str(here / 'build_scenes.py')], cwd=here, check=True, capture_output=True)
total = cfg['duration']
hosts = []
for sid, st, du in DE_HOSTS:
    nst = round(warp(st), 3) if st > 0 else 0
    nend = total if sid == 'finale' else round(warp(st + du), 3)
    hosts.append((sid, nst, round(nend - nst, 3)))
    s = (here / 'compositions' / f'{sid}.html').read_text()
    def fix(m):
        head = m.group(1)
        pos = float(m.group(2)); g = st + pos; ng = warp(g)
        dm = re.search(r'duration: ([\d.]+)', head)
        if dm and float(dm.group(1)) > 3:
            nd = warp(g + float(dm.group(1))) - ng
            head = head.replace(dm.group(0), f'duration: {nd:.2f}', 1)
        return head + f'{max(0, ng - nst):.2f}' + m.group(3)
    s = re.sub(r'^(\s*tl\.fromTo\(.*\}, )([\d.]+)(\);)\s*$', fix, s, flags=re.M)
    if sid == 'finale':
        s = s.replace('heiß &amp; schnell – bis gleich!', cfg['endcard_tag'])
        s = s.replace('<style>', '<style>\n    @font-face { font-family: "Baloo 2"; font-weight: 800; src: url("assets/fonts/baloo2-devanagari.woff2") format("woff2"); unicode-range: U+0900-097F, U+200C-200D, U+25CC; }\n    @font-face { font-family: "Baloo 2"; font-weight: 800; src: url("assets/fonts/baloo2-latin.woff2") format("woff2"); unicode-range: U+0000-00FF, U+2013-2014; }', 1)
        s = s.replace('#f-tag { position: absolute; left: 0; right: 0; top: 590px; text-align: center; font-family: "Nunito", sans-serif; font-weight: 900;',
                      '#f-tag { position: absolute; left: 0; right: 0; top: 580px; text-align: center; font-family: "Baloo 2", sans-serif; font-weight: 800;')
    (out / 'compositions' / f'{sid}.html').write_text(s)
# lyrics
L = cfg['lyrics']
items = ''; tw = ''
for i, (a, b, t, ch) in enumerate(L):
    cls = 'ly-line ly-ch' if ch else 'ly-line'
    items += f'    <div id="ly{i}" class="clip {cls}" data-start="{a}" data-duration="{round(b - a, 2)}" data-track-index="0"><span id="ly{i}t" class="ly-pill">{t}</span></div>\n'
    tw += f'    tl.fromTo("#ly{i}t", {{ y: 50, scale: 0.85, opacity: 0 }}, {{ y: 0, scale: 1, opacity: 1, duration: 0.3, ease: "back.out(2)" }}, {a});\n'
    tw += f'    tl.fromTo("#ly{i}t", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.15, immediateRender: false }}, {round(b - 0.17, 2)});\n'
(out / 'compositions' / 'lyrics.html').write_text(f'''<template>
  <style>
    @font-face {{ font-family: "Baloo 2"; font-weight: 800; src: url("assets/fonts/baloo2-devanagari.woff2") format("woff2"); unicode-range: U+0900-097F, U+1CD0-1CF9, U+200C-200D, U+20A8, U+20B9, U+25CC, U+A830-A839, U+A8E0-A8FF; }}
    @font-face {{ font-family: "Baloo 2"; font-weight: 800; src: url("assets/fonts/baloo2-latin.woff2") format("woff2"); unicode-range: U+0000-00FF, U+2013-2014, U+2018-201E, U+2026; }}
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    .ly-line {{ position: absolute; left: 0; right: 0; bottom: 80px; text-align: center; }}
    .ly-pill {{ display: inline-block; font-family: "Baloo 2", sans-serif; font-weight: 800; font-size: 58px; line-height: 1.25; color: #2B1B17;
      background: #FFF3DC; border: 6px solid #2B1B17; border-radius: 60px; padding: 6px 44px 0; box-shadow: 8px 8px 0 #2B1B17; }}
    .ly-ch .ly-pill {{ background: #E63A2E; color: #FFF3DC; font-size: 62px; }}
  </style>
  <div id="root" data-composition-id="lyrics" data-width="1920" data-height="1080">
{items}  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{tw}    window.__timelines["lyrics"] = tl;
  </script>
</template>
''')
idx = (here / 'index.html').read_text()
idx = idx.replace('lang="de"', 'lang="hi"').replace('data-duration="88.7"', f'data-duration="{total}"')
for sid, st, du in DE_HOSTS:
    n = next(h for h in hosts if h[0] == sid)
    idx = idx.replace(f'id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" data-start="{st}" data-duration="{du}"',
                      f'id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" data-start="{n[1]}" data-duration="{n[2]}"')
(out / 'index.html').write_text(idx)
print(hosts)
