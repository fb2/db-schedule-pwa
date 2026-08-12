const path = require('path');
const VIZ_DIR = path.resolve(__dirname, '..', 'viz');
const VIZ = 'file://' + VIZ_DIR;
const SHOTS = path.resolve(__dirname, 'shots');
require('fs').mkdirSync(SHOTS, { recursive: true });
/* Two more things the band test does not cover:
   1. how legible text still is inside the ramp (it should be a ghost, not words)
   2. at full scroll the fade must clear and the last line must be fully visible */
const { chromium } = require('playwright');
const fs = require('fs');
const url = VIZ + '/04-bowl-orbit.html';

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1280, height: 1000 }, deviceScaleFactor: 2 });
  const errs = []; p.on('pageerror', e => errs.push(String(e)));
  await p.goto(url); await p.waitForTimeout(1500);
  await p.click('#rail button[data-id="d-mee-sotong"]'); await p.waitForTimeout(700);

  const geo = await p.evaluate(() => {
    const bd = document.querySelector('#dossier .p-body');
    bd.scrollTop = Math.round((bd.scrollHeight - bd.clientHeight) * 0.4);
    const pn = bd.closest('.viz-panel'), r = pn.getBoundingClientRect();
    return { x: r.x, y: r.y, w: r.width, h: r.height };
  });
  await p.waitForTimeout(350);
  // the whole fade, as the user cropped it
  fs.writeFileSync(path.join(SHOTS, 'ramp.png'), await p.screenshot({
    clip: { x: Math.round(geo.x + 1), y: Math.round(geo.y + geo.h - 47),
            width: Math.round(geo.w - 2), height: 46 } }));

  const bottom = await p.evaluate(async () => {
    const bd = document.querySelector('#dossier .p-body');
    bd.scrollTop = bd.scrollHeight;
    await new Promise(r => setTimeout(r, 350));
    const pn = bd.closest('.viz-panel');
    const kids = [...bd.children];
    const last = kids[kids.length - 1];
    const lr = last.getBoundingClientRect(), br = bd.getBoundingClientRect();
    return { more: pn.dataset.more,
             fadeOpacity: getComputedStyle(pn.querySelector('.p-fade')).opacity,
             lastEl: last.tagName + '.' + last.className,
             gapBelowLastLine: Math.round(br.bottom - lr.bottom) };
  });
  console.log(JSON.stringify({ errs, bottom }, null, 1));
  await b.close();
})();
