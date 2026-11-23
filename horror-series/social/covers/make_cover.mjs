// COUNTDOWN Season 1 common cover (all languages): 1080x1920 (Reels/series) and 1920x1080 (YouTube).
// Key art: Episode 1 panel e01_p14 rendered at 4K (src_e01_p14_4k.jpg).
// Usage: node make_cover.mjs   (uses the preinstalled Playwright)
import { createRequire } from 'module';
import { dirname } from 'path';
import { fileURLToPath } from 'url';
import { readFileSync } from 'fs';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const here = dirname(fileURLToPath(import.meta.url));
const art = 'data:image/jpeg;base64,' + readFileSync(`${here}/src_e01_p14_4k.jpg`).toString('base64');

const css = (w, h, pos) => `
html,body{margin:0;width:${w}px;height:${h}px;overflow:hidden;background:#05060a}
.art{position:absolute;inset:0;background:url(${art}) ${pos}/cover no-repeat;filter:saturate(.8) contrast(1.08) brightness(.82)}
.grade{position:absolute;inset:0;background:
  radial-gradient(ellipse at 50% 45%,rgba(0,0,0,0) 30%,rgba(0,0,0,.75) 100%),
  linear-gradient(180deg,rgba(5,6,10,.92) 0%,rgba(5,6,10,0) 26%,rgba(5,6,10,0) 58%,rgba(5,6,10,.96) 88%);}
.glow{position:absolute;inset:0;background:radial-gradient(circle at 50% 50%,rgba(127,163,106,.10),transparent 60%)}
.grain{position:absolute;inset:0;opacity:.12;mix-blend-mode:overlay;background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2'/></filter><rect width='200' height='200' filter='url(%23n)'/></svg>")}
.t{position:absolute;left:0;right:0;text-align:center;color:#ece4cf}
.title{font-family:'DejaVu Serif',serif;font-weight:700;letter-spacing:.12em;
  text-shadow:0 0 18px rgba(160,20,20,.85),0 0 46px rgba(160,20,20,.55),0 4px 0 #000}
.title .o{display:inline-block;color:#e9e2d0}
.small{font-family:'DejaVu Sans',sans-serif;letter-spacing:.35em;color:#c9b48a;text-shadow:0 2px 6px #000}
.langs{font-family:'Noto Sans Malayalam','Noto Sans Devanagari','Noto Sans Tamil',sans-serif;color:#ece4cf;text-shadow:0 2px 8px #000}
.red{color:#d23b2f}`;

const vertical = `<!doctype html><html><head><meta charset="utf-8"><style>${css(1080, 1920, '0 0')}
.art{background-size:2000px 1125px;background-position:-560px 400px;background-color:#05060a}
.grade{background:radial-gradient(ellipse at 50% 50%,rgba(0,0,0,0) 35%,rgba(0,0,0,.7) 100%),
  linear-gradient(180deg,#05060a 0%,#05060a 21%,rgba(5,6,10,0) 30%,rgba(5,6,10,0) 66%,#05060a 79%,#05060a 100%)}
</style></head><body>
<div class="art"></div><div class="glow"></div><div class="grade"></div><div class="grain"></div>
<div class="t small" style="top:215px;font-size:28px">kili🦜 AI STORIES PRESENTS</div>
<div class="t title" style="top:255px;font-size:112px;letter-spacing:.06em">COUNTDOWN</div>
<div class="t small" style="top:400px;font-size:32px;color:#ece4cf">SEASON 1 · <span class="red">10</span> CHIMES</div>
<div class="t small" style="top:1545px;font-size:26px;letter-spacing:.25em">IF YOU HEAR IT AT 3 AM… DON'T COUNT</div>
<div class="t langs" style="top:1600px;font-size:46px">മലയാളം · हिंदी · தமிழ்</div>
<div class="t small" style="top:1690px;font-size:26px">🎧 WATCH WITH HEADPHONES</div>
</body></html>`;

const wide = `<!doctype html><html><head><meta charset="utf-8"><style>${css(1920, 1080, '50% 45%')}
.grade{background:radial-gradient(ellipse at 50% 45%,rgba(0,0,0,0) 35%,rgba(0,0,0,.8) 100%),linear-gradient(180deg,rgba(5,6,10,.9) 0%,rgba(5,6,10,0) 30%,rgba(5,6,10,0) 62%,rgba(5,6,10,.95) 92%)}</style></head><body>
<div class="art"></div><div class="glow"></div><div class="grade"></div><div class="grain"></div>
<div class="t small" style="top:40px;font-size:28px">kili🦜 AI STORIES PRESENTS</div>
<div class="t title" style="top:80px;font-size:150px">COUNTDOWN</div>
<div class="t small" style="top:900px;font-size:34px;color:#ece4cf">SEASON 1 · <span class="red">10</span> CHIMES · FULL STORY</div>
<div class="t langs" style="top:960px;font-size:42px">മലയാളം · हिंदी · தமிழ்</div>
</body></html>`;

const browser = await chromium.launch();
for (const [name, html, w, h] of [['COUNTDOWN_S1_cover_9x16', vertical, 1080, 1920], ['COUNTDOWN_S1_cover_16x9', wide, 1920, 1080]]) {
  const page = await browser.newPage({ viewport: { width: w, height: h } });
  await page.setContent(html, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: `${here}/${name}.jpg`, type: 'jpeg', quality: 92 });
  await page.close();
  console.log(name);
}
await browser.close();
