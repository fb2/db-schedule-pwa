const path = require('path');
const VIZ_DIR = path.resolve(__dirname, '..', 'viz');
const VIZ = 'file://' + VIZ_DIR;
const SHOTS = path.resolve(__dirname, 'shots');
require('fs').mkdirSync(SHOTS, { recursive: true });
/* The band above the panel's bottom edge must not change when the body scrolls.
   Any glyph showing through a not-quite-opaque fade moves with the text, so
   scroll-invariance catches bleed without caring about corner radii. */
const { chromium } = require('playwright');
const fs = require('fs');
const url = (process.env.VIZ || VIZ) + '/04-bowl-orbit.html';

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1280, height: 1000 }, deviceScaleFactor: 2 });
  const errs = []; p.on('pageerror', e => errs.push(String(e)));
  await p.goto(url); await p.waitForTimeout(1500);

  const dishes = await p.$$eval('#rail button', o => o.map(x => x.dataset.id));
  const setScroll = (frac) => p.evaluate((f) => {
    const bd = document.querySelector('#dossier .p-body');
    bd.scrollTop = Math.round((bd.scrollHeight - bd.clientHeight) * f);
    const pn = bd.closest('.viz-panel'), r = pn.getBoundingClientRect();
    return { more: pn.dataset.more, over: bd.scrollHeight > bd.clientHeight,
             top: bd.scrollTop, x: r.x, y: r.y, w: r.width, h: r.height };
  }, frac);

  const fails = [], rows = [];
  for (const d of dishes) {
    await p.click(`#rail button[data-id="${d}"]`); await p.waitForTimeout(650);
    const a = await setScroll(0.15); await p.waitForTimeout(300);
    if (!a.over) { rows.push({ d, skip: 'fits' }); continue; }
    // The fade is 46px and reaches full opacity at 50%, so the bottom 23px must be
    // completely opaque. Test 22 of them, inset 1px to exclude the border itself.
    const clip = { x: Math.round(a.x + 1), y: Math.round(a.y + a.h - 23),
                   width: Math.round(a.w - 2), height: 22 };
    const s1 = await p.screenshot({ clip });
    const c = await setScroll(0.55); await p.waitForTimeout(300);
    const s2 = await p.screenshot({ clip });
    const same = s1.equals(s2);
    rows.push({ d, more: a.more, scrolls: [a.top, c.top], bandStable: same });
    if (!same) {
      fails.push(d);
      fs.writeFileSync(`${SHOTS}/bleed-${d}-a.png`, s1);
      fs.writeFileSync(`${SHOTS}/bleed-${d}-b.png`, s2);
    }
  }
  console.log(JSON.stringify({ errs, checked: rows.length, bleeding: fails }, null, 1));
  console.log(rows.map(r => `${r.bandStable === true ? 'OK   ' : r.skip ? 'skip ' : 'BLEED'} ${r.d} more=${r.more} scroll ${r.scrolls}`).join('\n'));
  await b.close();
  process.exit(fails.length ? 1 : 0);
})();
