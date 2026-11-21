// Render COUNTDOWN storyboard panels and character sheets to JPEGs.
//   node render_boards.mjs --out=../horror-series/art/storyboard/panels [--only=1,2] [--workers=4] [--soft-gl]
//   node render_boards.mjs --sheets --out=../horror-series/art/characters
import puppeteer from 'puppeteer-core';
import { existsSync, mkdirSync, writeFileSync, readdirSync } from 'fs';
import { resolve } from 'path';
import { pathToFileURL } from 'url';
import { homedir } from 'os';

const args = Object.fromEntries(process.argv.slice(2).map(a => { const [k, v] = a.replace(/^--/, '').split('='); return [k, v ?? true]; }));
const pw = `${homedir()}/.cache/ms-playwright`;
const CHROME = [process.env.CHROME_PATH, '/opt/pw-browsers/chromium', '/usr/bin/chromium',
  ...(existsSync(pw) ? readdirSync(pw).filter(n => /^chromium-\d+$/.test(n)).map(n => `${pw}/${n}/chrome-linux64/chrome`) : []),
  ...(existsSync('/opt/pw-browsers') ? readdirSync('/opt/pw-browsers').filter(n => /^chromium-\d+$/.test(n)).map(n => `/opt/pw-browsers/${n}/chrome-linux64/chrome`) : [])]
  .find(p => p && existsSync(p) && !p.endsWith('/chromium') || (p === '/usr/bin/chromium' && existsSync(p)));
const out = resolve(args.out || 'out/boards'); mkdirSync(out, { recursive: true });
const browser = await puppeteer.launch({ executablePath: CHROME, headless: true, protocolTimeout: 0,
  args: ['--no-sandbox', '--allow-file-access-from-files', '--ignore-gpu-blocklist', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--window-size=1920,1080'] });

async function openPage() {
  const page = await browser.newPage();
  page.on('pageerror', e => console.log('[page error]', e.message));
  await page.goto(pathToFileURL(resolve('countdown.html')).href + '?render', { waitUntil: 'networkidle0' });
  await page.waitForFunction('window.ready === true', { timeout: 60000 });
  await page.evaluate(() => document.fonts.load('40px "Noto Sans Malayalam"'));
  return page;
}
const grab = (page, w, h) => page.evaluate(async (w, h) => {
  await window.renderAt(.5);
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  c.getContext('2d').drawImage(document.getElementById('out'), 0, 0, w, h);
  return c.toDataURL('image/jpeg', w > 1280 ? .93 : .88);
}, w, h);
const save = (f, url) => writeFileSync(f, Buffer.from(url.slice(url.indexOf(',') + 1), 'base64'));

const probe = await openPage();
let jobs;
if (args.sheets) {
  jobs = (await probe.evaluate(() => Object.keys(LOOPS).filter(k => k.startsWith('sheet_')))).map(k => ({ loop: k, file: `${out}/${k.slice(6)}.jpg`, w: 1920, h: 1080 }));
} else {
  const panels = await probe.evaluate(() => PANELS.map(p => [p.ep, p.tc]));
  const only = args.only ? String(args.only).split(',').map(Number) : null;
  const count = {};
  const all = panels.map(([ep, tc], i) => { count[ep] = (count[ep] || 0) + 1; return { i, ep, tc, file: `${out}/e${String(ep).padStart(2, '0')}_p${String(count[ep]).padStart(2, '0')}.jpg`, w: +(args.w || 1280), h: +(args.h || 720) }; });
  writeFileSync(`${out}/index.json`, JSON.stringify(all.map(({ ep, tc, file }) => ({ ep, tc, file: file.split('/').pop() })), null, 1));
  jobs = all.filter(j => !only || only.includes(j.ep));
}
await probe.close();
const workers = +(args.workers || 4); let next = 0; const t0 = Date.now();
await Promise.all(Array.from({ length: workers }, async () => {
  const page = await openPage();
  while (next < jobs.length) {
    const j = jobs[next++];
    if (j.loop) await page.evaluate(n => { window.LOOP = LOOPS[n]; }, j.loop);
    else await page.evaluate(i => { window.PANEL = i; window.LOOP = LOOPS.panel; }, j.i);
    save(j.file, await grab(page, j.w, j.h));
    console.log(j.file.split('/').pop(), j.tc || '');
  }
}));
console.log(`${jobs.length} images in ${((Date.now() - t0) / 1000).toFixed(0)} s`);
await browser.close();
