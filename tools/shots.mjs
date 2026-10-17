// Captures store/portal images with headless Chrome over the DevTools protocol.
// Usage: node tools/shots.mjs http://localhost:4460/   (serve docs/ first)
import { spawn } from 'node:child_process';
import { writeFileSync, copyFileSync, rmSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const BASE = process.argv[2] || 'http://localhost:4460/';
const OUT = join(ROOT, 'release', 'images');
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PORT = 9333;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

copyFileSync(join(ROOT, 'tools', 'promo.html'), join(ROOT, 'docs', '_promo.html'));
const profile = mkdtempSync(join(tmpdir(), 'yesim-shots-'));
const chrome = spawn(CHROME, ['--headless=new', `--remote-debugging-port=${PORT}`, `--user-data-dir=${profile}`,
  '--hide-scrollbars', '--no-first-run', '--mute-audio', '--force-color-profile=srgb', 'about:blank'], { stdio: 'ignore' });

let page;
for (let i = 0; i < 50 && !page; i++) {
  try { page = (await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json()).find((t) => t.type === 'page'); } catch { await sleep(200); }
}
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener('open', r));
let seq = 0; const waiting = new Map();
ws.addEventListener('message', (m) => { const d = JSON.parse(m.data); if (waiting.has(d.id)) { waiting.get(d.id)(d.result); waiting.delete(d.id); } });
const send = (method, params = {}) => new Promise((r) => { const id = ++seq; waiting.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
const evaluate = (expression) => send('Runtime.evaluate', { expression, awaitPromise: true });

async function seed(level, lang) {
  await send('Page.navigate', { url: BASE }); await sleep(800);
  const prefs = { unlocked: level, lang, sound: false, dim: true, relaxed: false, best: {}, done: {}, stars: {}, streak: { count: 4, last: null } };
  for (let n = 1; n < level; n++) { prefs.done[n] = true; prefs.stars[n] = n % 3 ? 3 : 2; }
  await evaluate(`localStorage.setItem('yesim-mahjong-v1', JSON.stringify({ prefs: ${JSON.stringify(prefs)}, current: null }))`);
}
async function shot(name, { width, height, scale = 1, mobile = false, url, level = 7, lang = 'tr', wait = 2600 }) {
  await send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: scale, mobile });
  await seed(level, lang);
  await send('Page.navigate', { url }); await sleep(wait);
  const { data } = await send('Page.captureScreenshot', { format: 'jpeg', quality: 90 });
  writeFileSync(join(OUT, name), Buffer.from(data, 'base64'));
  console.log('saved', name);
}

await send('Page.enable');
const promo = (layout, lang = 'tr') => `${BASE}_promo.html?layout=${layout}&lang=${lang}`;
await shot('og.jpg', { width: 1200, height: 630, url: promo('landscape'), level: 4 });
await shot('cover-1920x1080.jpg', { width: 1920, height: 1080, url: promo('landscape'), level: 7 });
await shot('cover-1920x1080-en.jpg', { width: 1920, height: 1080, url: promo('landscape', 'en'), level: 7, lang: 'en' });
await shot('cover-800x1200.jpg', { width: 800, height: 1200, url: promo('portrait'), level: 10 });
await shot('cover-800x800.jpg', { width: 800, height: 800, url: promo('square'), level: 3 });
await shot('cover-800x470.jpg', { width: 800, height: 470, url: promo('landscape'), level: 4 });
await shot('screen-desktop-1.jpg', { width: 1440, height: 900, url: BASE, level: 7 });
await shot('screen-desktop-2.jpg', { width: 1440, height: 900, url: BASE, level: 12 });
await shot('screen-phone-1.jpg', { width: 360, height: 780, scale: 3, mobile: true, url: BASE, level: 4 });
await shot('screen-phone-2.jpg', { width: 360, height: 780, scale: 3, mobile: true, url: BASE, level: 10 });
await shot('screen-phone-en.jpg', { width: 360, height: 780, scale: 3, mobile: true, url: BASE, level: 9, lang: 'en' });
await shot('screen-tablet.jpg', { width: 1024, height: 1366, scale: 2, mobile: true, url: BASE, level: 12 });

ws.close(); chrome.kill();
rmSync(join(ROOT, 'docs', '_promo.html'));
copyFileSync(join(OUT, 'og.jpg'), join(ROOT, 'docs', 'og.jpg'));
console.log('done');
