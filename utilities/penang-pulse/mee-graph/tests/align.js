const path = require('path');
const VIZ_DIR = path.resolve(__dirname, '..', 'viz');
const VIZ = 'file://' + VIZ_DIR;
const SHOTS = path.resolve(__dirname, 'shots');
require('fs').mkdirSync(SHOTS, { recursive: true });
/* The stage frame and the dossier frame are two separate bordered boxes side by
   side, so their top and bottom edges must agree to the pixel. */
const { chromium } = require('playwright');
const url = VIZ + '/04-bowl-orbit.html';
const TOL = 1;

(async () => {
  const b = await chromium.launch();
  const fails = [];
  for (const vp of [{ width: 1440, height: 1100 }, { width: 1280, height: 900 }, { width: 1100, height: 800 }]) {
    const p = await b.newPage({ viewport: vp });
    p.on('pageerror', e => fails.push(`${vp.width}: pageerror ${e}`));
    await p.goto(url); await p.waitForTimeout(1400);
    const r = await p.evaluate(() => {
      const q = (s) => { const e = document.querySelector(s); const r = e.getBoundingClientRect();
        return { top: Math.round(r.top), bottom: Math.round(r.bottom), left: Math.round(r.left),
                 right: Math.round(r.right), h: Math.round(r.height) }; };
      return { stage: q('#stage'), dossier: q('#dossier'), side: q('.orbit-side'), grid: q('.orbit-grid') };
    });
    const dTop = r.dossier.top - r.stage.top, dBot = r.dossier.bottom - r.stage.bottom;
    const dRight = r.dossier.right - r.side.right, dLeft = r.dossier.left - r.side.left;
    const ok = Math.abs(dTop) <= TOL && Math.abs(dBot) <= TOL && Math.abs(dRight) <= TOL && Math.abs(dLeft) <= TOL;
    if (!ok) fails.push(`${vp.width}x${vp.height}: top${dTop >= 0 ? '+' : ''}${dTop} bottom${dBot >= 0 ? '+' : ''}${dBot} left${dLeft >= 0 ? '+' : ''}${dLeft} right${dRight >= 0 ? '+' : ''}${dRight}`);
    console.log(`${ok ? 'OK   ' : 'FAIL '} ${vp.width}x${vp.height}  stage ${r.stage.top}–${r.stage.bottom} (h${r.stage.h})  dossier ${r.dossier.top}–${r.dossier.bottom} (h${r.dossier.h})  Δtop=${dTop} Δbottom=${dBot} Δleft=${dLeft} Δright=${dRight}`);
    await p.close();
  }
  console.log(fails.length ? '\nFAILURES:\n' + fails.join('\n') : '\nall frames flush');
  await b.close();
  process.exit(fails.length ? 1 : 0);
})();
