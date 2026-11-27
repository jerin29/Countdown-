"""Build the COUNTDOWN storyboard book: pairs each rendered panel with its script row (Malayalam) and lays out
6 panels per landscape page. Writes storyboard/COUNTDOWN_storyboard_ml.html, then (via render_pages.mjs) a PDF and PNG pages.
Usage: python3 build_storyboard.py"""
import html, json, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SB = os.path.join(ROOT, "art", "storyboard")
SCRIPT = os.path.join(ROOT, "malayalam", "02-scripts-ml.md")

TITLES = {}
rows = {}
text = open(SCRIPT, encoding="utf-8").read()
parts = re.split(r"\n## എപ്പിസോഡ് (\d+): \"([^\"]+)\" \(എണ്ണം: (\d+)\)", text)
for i in range(1, len(parts), 4):
    ep, title, count, body = int(parts[i]), parts[i + 1], parts[i + 2], parts[i + 3].split("\n## ")[0]
    TITLES[ep] = (title, count)
    rows[ep] = []
    for line in body.splitlines():
        m = re.match(r"\|\s*(\d:\d\d)\s*\|(.*)\|(.*)\|\s*$", line)
        if m:
            rows[ep].append([c.strip() for c in m.groups()])


def md(s):
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\*(.+?)\*", r"<i>\1</i>", s)
    return s


panels = json.load(open(os.path.join(SB, "panels", "index.json"), encoding="utf-8"))
by_ep = {}
for p in panels:
    by_ep.setdefault(p["ep"], []).append(p)

pages = []
for ep in sorted(by_ep):
    ps, rs = by_ep[ep], rows[ep]
    assert len(ps) == len(rs), f"episode {ep}: {len(ps)} panels vs {len(rs)} script rows"
    for k in range(0, len(ps), 6):
        cards = []
        for p, (tc, vis, aud) in zip(ps[k:k + 6], rs[k:k + 6]):
            assert p["tc"] == tc, (ep, p["tc"], tc)
            cards.append(f"""<div class="card"><img src="panels/{p['file']}"><div class="meta"><span class="tc">{tc}</span>
<p class="vis">{md(vis)}</p><p class="aud">🔊 {md(aud)}</p></div></div>""")
        title, count = TITLES[ep]
        n, total = k // 6 + 1, (len(ps) + 5) // 6
        pages.append(f"""<section class="page"><header><span class="big">{count}</span><div><h1>കൗണ്ട്ഡൗൺ · എപ്പിസോഡ് {ep}: “{html.escape(title)}”</h1>
<h2>സ്റ്റോറിബോർഡ് · 1:30 · പേജ് {n}/{total}</h2></div></header><div class="grid">{''.join(cards)}</div></section>""")

cover = """<section class="page cover"><img src="../characters/06_cast.jpg"><div class="ct"><h1>കൗണ്ട്ഡൗൺ</h1><h2>COUNTDOWN · സ്റ്റോറിബോർഡ് · 10 എപ്പിസോഡുകൾ × 1:30</h2>
<p>ഓരോ പാനലും സ്ക്രിപ്റ്റിലെ ഒരു വരി. സമയം = എപ്പിസോഡിലെ സമയം (audio/episodes ട്രാക്കുമായി ഒത്തുപോകും).</p></div></section>"""

doc = f"""<!doctype html><html lang="ml"><head><meta charset="utf-8"><title>COUNTDOWN storyboard</title><style>
@page {{ size: 1600px 1000px; margin: 0; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: #1a1a1f; font-family: "Noto Sans Malayalam", sans-serif; color: #1c1820; }}
.page {{ width: 1600px; height: 1000px; background: #ece6da; padding: 28px 34px; page-break-after: always; overflow: hidden; }}
header {{ display: flex; align-items: center; gap: 22px; border-bottom: 3px solid #1c1820; padding-bottom: 10px; margin-bottom: 18px; }}
.big {{ font: 64px Georgia, serif; color: #b33a3a; width: 90px; text-align: center; }}
h1 {{ font-size: 30px; margin: 0; }} h2 {{ font-size: 18px; margin: 2px 0 0; font-weight: 400; color: #555; }}
.grid {{ display: grid; grid-template-columns: repeat(3, 1fr); grid-template-rows: repeat(2, 1fr); gap: 18px; height: 840px; }}
.card {{ background: #f7f3ea; border: 2px solid #1c1820; display: flex; flex-direction: column; overflow: hidden; }}
.card img {{ width: 100%; aspect-ratio: 16/9; display: block; border-bottom: 2px solid #1c1820; }}
.meta {{ padding: 8px 12px; font-size: 14.5px; line-height: 1.4; overflow: hidden; }}
.tc {{ display: inline-block; background: #1c1820; color: #ece6da; font: 15px monospace; padding: 2px 8px; border-radius: 3px; }}
.vis {{ margin: 6px 0 4px; }} .aud {{ margin: 0; color: #5a3a3a; }}
.cover {{ position: relative; padding: 0; }} .cover img {{ width: 100%; height: 100%; object-fit: cover; }}
.ct {{ position: absolute; left: 0; right: 0; bottom: 0; background: rgba(20,18,24,.88); color: #ece6da; padding: 26px 40px; }}
.ct h1 {{ font-size: 64px; }} .ct h2 {{ color: #c9b48a; font-size: 24px; }} .ct p {{ font-size: 18px; }}
</style></head><body>{cover}{''.join(pages)}</body></html>"""
out = os.path.join(SB, "COUNTDOWN_storyboard_ml.html")
open(out, "w", encoding="utf-8").write(doc)
print("wrote", out, len(pages) + 1, "pages")
subprocess.run(["node", os.path.join(HERE, "render_pages.mjs"), out], check=True)
