// COUNTDOWN Season 1 title song promo cover (all languages): 1080x1920 (Reels) and 1080x1080 (square / music).
// Key art: Episode 1 panel e01_p12 (the clock tower) rendered at 4K.
// Usage: node make_song_cover.mjs
import { createRequire } from 'module';
import { dirname } from 'path';
import { fileURLToPath } from 'url';
import { readFileSync } from 'fs';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const here = dirname(fileURLToPath(import.meta.url));
const art = 'data:image/jpeg;base64,' + readFileSync(`${here}/src_e01_p12_4k.jpg`).toString('base64');

const base = (w, h, bg) => `
html,body{margin:0;width:${w}px;height:${h}px;overflow:hidden;background:#05060a}
.art{position:absolute;inset:0;background:url(${art}) no-repeat;${bg};filter:saturate(.85) contrast(1.1) brightness(.85)}
.moon{position:absolute;inset:0;background:radial-gradient(circle at 50% 34%,rgba(240,230,200,.22),transparent 38%)}
.grade{position:absolute;inset:0}
.grain{position:absolute;inset:0;opacity:.12;mix-blend-mode:overlay;background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2'/></filter><rect width='200' height='200' filter='url(%23n)'/></svg>")}
.t{position:absolute;left:0;right:0;text-align:center;color:#ece4cf}
.small{font-family:'DejaVu Sans',sans-serif;letter-spacing:.3em;color:#c9b48a;text-shadow:0 2px 6px #000}
.title{font-family:'DejaVu Serif',serif;font-weight:700;letter-spacing:.06em;text-shadow:0 0 18px rgba(160,20,20,.85),0 0 46px rgba(160,20,20,.55),0 4px 0 #000}
.song{font-family:'Noto Sans Malayalam','Noto Sans Devanagari','Noto Sans Tamil',sans-serif;font-weight:700;color:#ece4cf;text-shadow:0 0 14px rgba(0,0,0,.9),0 3px 0 #000;line-height:1.25}
.song span{display:block}
.note{font-size:1.1em;color:#d23b2f}
.badge{display:inline-block;border:2px solid #c9b48a;border-radius:40px;padding:10px 30px}`;

const songs = `<span>പത്തു മണിയൊച്ച</span><span>दस घंटियाँ</span><span>பத்து மணியோசை</span>`;

const vertical = `<!doctype html><html><head><meta charset="utf-8"><style>${base(1080, 1920, 'background-size:3413px 1920px;background-position:-1166px 0')}
.grade{background:radial-gradient(ellipse at 50% 40%,rgba(0,0,0,0) 30%,rgba(0,0,0,.65) 100%),linear-gradient(180deg,rgba(5,6,10,.85) 0%,rgba(5,6,10,0) 22%,rgba(5,6,10,0) 50%,rgba(5,6,10,.97) 76%)}
</style></head><body>
<div class="art"></div><div class="moon"></div><div class="grade"></div><div class="grain"></div>
<div class="t small" style="top:230px;font-size:30px"><span class="badge">🎵 OFFICIAL TITLE SONG</span></div>
<div class="t title" style="top:320px;font-size:112px">COUNTDOWN</div>
<div class="t small" style="top:465px;font-size:30px;color:#ece4cf">SEASON 1</div>
<div class="t song" style="top:1270px;font-size:66px">${songs}</div>
<div class="t small" style="top:1560px;font-size:26px">THE LULLABY THAT COUNTS DOWN… 10 · 9 · 8 …</div>
<div class="t small" style="top:1620px;font-size:26px">🎧 LISTEN WITH HEADPHONES · kili🦜 AI STORIES</div>
</body></html>`;

const square = `<!doctype html><html><head><meta charset="utf-8"><style>${base(1080, 1080, 'background-size:1920px 1080px;background-position:-420px 0')}
.grade{background:radial-gradient(ellipse at 50% 40%,rgba(0,0,0,0) 30%,rgba(0,0,0,.7) 100%),linear-gradient(180deg,rgba(5,6,10,.85) 0%,rgba(5,6,10,0) 25%,rgba(5,6,10,0) 45%,rgba(5,6,10,.97) 72%)}
</style></head><body>
<div class="art"></div><div class="moon"></div><div class="grade"></div><div class="grain"></div>
<div class="t small" style="top:40px;font-size:24px"><span class="badge">🎵 OFFICIAL TITLE SONG</span></div>
<div class="t title" style="top:110px;font-size:96px">COUNTDOWN</div>
<div class="t song" style="top:740px;font-size:50px">${songs}</div>
</body></html>`;

const browser = await chromium.launch();
for (const [name, html, w, h] of [['COUNTDOWN_S1_song_cover_9x16', vertical, 1080, 1920], ['COUNTDOWN_S1_song_cover_1x1', square, 1080, 1080]]) {
  const page = await browser.newPage({ viewport: { width: w, height: h } });
  await page.setContent(html, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: `${here}/${name}.jpg`, type: 'jpeg', quality: 92 });
  await page.close();
  console.log(name);
}
await browser.close();
