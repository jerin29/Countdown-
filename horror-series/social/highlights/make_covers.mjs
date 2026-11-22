// Instagram highlight covers for COUNTDOWN (1080x1920, icon centred in the safe circle).
// Usage: node make_covers.mjs   (uses the preinstalled Playwright)
import { createRequire } from 'module';
import { dirname } from 'path';
import { fileURLToPath } from 'url';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const here = dirname(fileURLToPath(import.meta.url));

const ticks = Array.from({ length: 12 }, (_, i) => {
  const a = i / 12 * Math.PI * 2, r1 = i % 3 === 0 ? 212 : 228, r2 = 250;
  return `<line x1="${Math.sin(a) * r1}" y1="${-Math.cos(a) * r1}" x2="${Math.sin(a) * r2}" y2="${-Math.cos(a) * r2}" stroke="#2a2420" stroke-width="${i % 3 === 0 ? 14 : 7}" stroke-linecap="round"/>`;
}).join('');
const cracks = `<path d="M-40 -265 L-12 -150 L-62 -60 L-18 40" fill="none" stroke="#2a2420" stroke-width="7" stroke-linejoin="round"/>
<path d="M255 70 L140 58 L100 140" fill="none" stroke="#2a2420" stroke-width="6" stroke-linejoin="round"/>`;

function cover({ label, font, size = 230, face = true, dy = 0 }) {
  return `<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;width:1080px;height:1920px;background:#07080c;overflow:hidden}
.bg{position:absolute;inset:0;background:radial-gradient(circle at 50% 50%,#1d2a24 0,#0c1110 34%,#07080c 62%)}
svg{position:absolute;left:0;top:0}
</style></head><body><div class="bg"></div>
<svg width="1080" height="1920" viewBox="-540 -960 1080 1920">
<defs><radialGradient id="g"><stop offset="0" stop-color="#7FA36A" stop-opacity=".45"/><stop offset="1" stop-color="#7FA36A" stop-opacity="0"/></radialGradient>
<radialGradient id="f" cx="45%" cy="40%"><stop offset="0" stop-color="#efe8d6"/><stop offset="1" stop-color="#c9bfa6"/></radialGradient>
<linearGradient id="rim" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#d6b06a"/><stop offset=".5" stop-color="#8a6a32"/><stop offset="1" stop-color="#5a4320"/></linearGradient></defs>
<circle r="420" fill="url(#g)"/>
<circle r="292" fill="url(#rim)" stroke="#1a1512" stroke-width="10"/>
<circle r="262" fill="${face ? 'url(#f)' : '#101614'}" stroke="#1a1512" stroke-width="8"/>
${face ? ticks + cracks : ticks.replaceAll('#2a2420', '#c9b48a')}
${label ? `<text x="0" y="${dy}" text-anchor="middle" dominant-baseline="central" font-family='${font}' font-size="${size}" font-weight="700" fill="#e9e2d0" stroke="#07080c" stroke-width="6" paint-order="stroke">${label}</text>` : ''}
</svg></body></html>`;
}

const covers = [
  ['01_countdown', cover({})],
  ['02_malayalam', cover({ label: 'മ', font: 'Noto Sans Malayalam', size: 260, face: false })],
  ['03_hindi', cover({ label: 'हि', font: 'Noto Sans Devanagari', size: 250, face: false })],
  ['04_tamil', cover({ label: 'த', font: 'Noto Sans Tamil', size: 260, face: false })],
  ['05_season2', cover({ label: '40', font: 'Georgia, serif', size: 250, face: false })],
];
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
for (const [name, html] of covers) {
  await page.setContent(html, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: `${here}/${name}.jpg`, type: 'jpeg', quality: 92 });
  console.log(name);
}
await browser.close();
