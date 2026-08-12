const path = require('path');
const VIZ_DIR = path.resolve(__dirname, '..', 'viz');
const VIZ = 'file://' + VIZ_DIR;
const SHOTS = path.resolve(__dirname, 'shots');
require('fs').mkdirSync(SHOTS, { recursive: true });
/* The hub label must be INSIDE the hub circle: for every text line, the far corner
   of its box must be within the circle's radius. Checking half-width is not enough —
   a wide line sitting low needs more radius than a wide line through the centre. */
const { chromium } = require('playwright');
const url = VIZ + '/04-bowl-orbit.html';

(async () => {
  const b = await chromium.launch();
  const fails = [];
  for (const vp of [{ width: 1440, height: 1080 }, { width: 1180, height: 820 }, { width: 390, height: 844 }]) {
    const p = await b.newPage({ viewport: vp });
    p.on('pageerror', e => fails.push(`${vp.width}: pageerror ${e}`));
    await p.goto(url); await p.waitForTimeout(1400);
    const ids = await p.$$eval('#rail button', o => o.map(x => x.dataset.id));
    console.log(`\n--- ${vp.width}x${vp.height} ---`);
    for (const id of ids) {
      await p.click(`#rail button[data-id="${id}"]`); await p.waitForTimeout(560);
      const r = await p.evaluate(() => {
        // Scope to the hub group itself. querySelectorAll('g') returns ancestors
        // first, so "the first g containing .core-title" is the ROOT group — which
        // is how an earlier version of this test ended up measuring ring labels
        // against the outer thread ring.
        const title = document.querySelector('text.core-title');
        const g = title.parentNode;
        const hubR = Math.max(...[...g.querySelectorAll(':scope > circle')].map(c => +c.getAttribute('r')));
        const items = [];
        for (const t of g.querySelectorAll(':scope > text')) {
          const fs = parseFloat(getComputedStyle(t).fontSize);
          const tsp = t.querySelectorAll('tspan');
          const parts = tsp.length ? [...tsp] : [t];
          for (const el of parts) {
            const f = parseFloat(el.getAttribute('font-size')) || fs;
            const w = el.getComputedTextLength();
            const y = parseFloat(el.getAttribute('y')) || 0;
            const top = y - f * 0.78, bot = y + f * 0.26;
            items.push({ txt: el.textContent, need: Math.round(Math.hypot(w / 2, Math.max(Math.abs(top), Math.abs(bot))) * 10) / 10 });
          }
        }
        const innerRingR = Math.min(...[...document.querySelectorAll('circle.orbit-ring')].map(c => +c.getAttribute('r')));
        return { hubR: Math.round(hubR * 10) / 10, items, innerRingR: Math.round(innerRingR) };
      });
      const worst = r.items.reduce((a, b) => (b.need > a.need ? b : a));
      const over = worst.need - r.hubR;
      const gap = r.innerRingR - r.hubR;
      const ok = over <= 0.5 && gap >= 6;
      if (!ok) fails.push(`${vp.width} ${id}: worst "${worst.txt}" needs ${worst.need} hub ${r.hubR} (over ${over.toFixed(1)}) ringGap ${gap}`);
      console.log(`${ok ? 'ok  ' : 'FAIL'} ${id.replace('d-', '').padEnd(20)} hub=${String(r.hubR).padStart(5)}  widest="${worst.txt}" needs ${worst.need}  slack=${(-over).toFixed(1)}  ringGap=${gap}`);
    }
    await p.close();
  }
  console.log(fails.length ? '\nFAILURES:\n' + fails.join('\n') : '\nEvery hub label fits inside its circle, with clearance to the first orbit');
  await b.close();
  process.exit(fails.length ? 1 : 0);
})();
