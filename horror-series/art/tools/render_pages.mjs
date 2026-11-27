// Print the storyboard HTML to a PDF and to one PNG per page (for phones). Uses the preinstalled Playwright.
import { createRequire } from 'module';
import { mkdirSync } from 'fs';
import { dirname, join } from 'path';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const src = process.argv[2], dir = dirname(src);
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } });
await page.goto('file://' + src, { waitUntil: 'networkidle' });
await page.evaluate(() => document.fonts.ready);
await page.pdf({ path: join(dir, 'COUNTDOWN_storyboard_ml.pdf'), width: '1600px', height: '1000px', printBackground: true });
mkdirSync(join(dir, 'pages'), { recursive: true });
const n = await page.locator('section.page').count();
for (let i = 0; i < n; i++) {
  await page.locator('section.page').nth(i).screenshot({ path: join(dir, 'pages', `page_${String(i).padStart(2, '0')}.jpg`), type: 'jpeg', quality: 82 });
}
console.log(`pdf + ${n} pages`);
await browser.close();
