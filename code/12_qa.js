// QA: open index.html at 1280 px and 390 px, collect console errors, take screenshots, exercise the controls.
const { chromium } = require('playwright');
const path = require('path');
const LF = process.env.LEAFLET_DIR || '/tmp/claude-0/qa/node_modules/leaflet/dist';  // local Leaflet 1.9.4 (the CDN is not reachable from the build container)
const ROOT = path.resolve(__dirname, '..');
(async () => {
  const b = await chromium.launch();
  for (const [w, h, tag] of [[1280, 900, 'desktop'], [390, 844, 'phone']]) {
    const p = await b.newPage({ viewport: { width: w, height: h } });
    const errs = [];
    p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
    p.on('pageerror', e => errs.push('PAGEERROR ' + e.message));
    await p.route(/arcgisonline|googleapis|gstatic/, r => r.abort());
    await p.route(/leaflet.min.js/, r => r.fulfill({ path: LF + '/leaflet.js' }));
    await p.route(/leaflet.min.css/, r => r.fulfill({ path: LF + '/leaflet.css' }));
    await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'load' });
    await p.waitForTimeout(1500);
    await p.screenshot({ path: `${ROOT}/qa/${tag}_top.png` });
    await p.evaluate(() => document.getElementById('atlas').scrollIntoView());
    await p.evaluate(() => { setYear(1348); });
    await p.waitForTimeout(500);
    await p.screenshot({ path: `${ROOT}/qa/${tag}_map_1348.png` });
    await p.evaluate(() => { setYear(1665); });
    await p.waitForTimeout(400);
    await p.screenshot({ path: `${ROOT}/qa/${tag}_map_1665.png` });
    for (const m of ['wave', 'last', 'often']) { await p.evaluate(m => setMode(m), m); await p.waitForTimeout(400); await p.screenshot({ path: `${ROOT}/qa/${tag}_map_${m}.png` }); }
    await p.evaluate(() => pickTown(TN.find(t => t.n === 'London'), true)); await p.waitForTimeout(500);
    await p.screenshot({ path: `${ROOT}/qa/${tag}_london.png` });
    await p.fill('#q', 'Vienn'); await p.waitForTimeout(200);
    const sug = await p.$eval('#sug', e => e.textContent);
    await p.evaluate(() => setMode('year')); await p.click('#play'); await p.waitForTimeout(1200); await p.click('#play');
    const yr = await p.$eval('#yr', e => e.value);
    for (const id of ['waveChart', 'decChart', 'endChart', 'topChart', 'ivChart', 'ctab']) {
      await p.evaluate(id => document.getElementById(id).scrollIntoView({ block: 'center' }), id); await p.waitForTimeout(150);
      await p.screenshot({ path: `${ROOT}/qa/${tag}_${id}.png` });
    }
    const fs = await p.$$eval('.mfs-btn', e => e.length);
    const sw = await p.evaluate(() => document.documentElement.scrollWidth);
    console.log(tag, 'fullscreen buttons', fs, 'scrollWidth', sw, 'year after play', yr, 'search:', sug.slice(0, 80));
    console.log(tag, 'errors', errs.filter(e => !/ERR_|net::|Failed to load resource/.test(e)), 'network errors', errs.filter(e => /ERR_|net::|Failed to load resource/.test(e)).length);
    await p.close();
  }
  await b.close();
})();
