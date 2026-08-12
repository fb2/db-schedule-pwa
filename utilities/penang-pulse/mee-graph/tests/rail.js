const path = require('path');
const VIZ_DIR = path.resolve(__dirname, '..', 'viz');
const VIZ = 'file://' + VIZ_DIR;
const SHOTS = path.resolve(__dirname, 'shots');
require('fs').mkdirSync(SHOTS, { recursive: true });
/* The rail's scroll affordance: fades and arrows must reflect which side has more
   content, the arrows must actually move it, and a rail that fits must show neither. */
const { chromium } = require('playwright');
const url = VIZ + '/04-bowl-orbit.html';

const read = (p) => p.evaluate(() => {
  const w = document.getElementById('railwrap'), r = document.getElementById('rail');
  const vis = (sel, pseudo) => {
    const cs = pseudo ? getComputedStyle(w, pseudo) : getComputedStyle(document.querySelector(sel));
    return +cs.opacity > 0.5;
  };
  return { state: w.dataset.scroll,
           max: r.scrollWidth - r.clientWidth,
           left: Math.round(r.scrollLeft),
           fadeL: vis(null, '::before'), fadeR: vis(null, '::after'),
           arrowL: vis('#rail-l'), arrowR: vis('#rail-r'),
           scrollbarH: r.offsetHeight - r.clientHeight };
});

(async () => {
  const b = await chromium.launch();
  const fails = [];
  const t = (c, m) => { if (!c) fails.push(m); console.log(`${c ? 'ok  ' : 'FAIL'} ${m}`); };

  // --- wide desktop: rail overflows ---
  let p = await b.newPage({ viewport: { width: 1440, height: 1000 } });
  p.on('pageerror', e => fails.push('pageerror ' + e));
  await p.goto(url); await p.waitForTimeout(2600);   // past the peek
  let s = await read(p);
  console.log(JSON.stringify(s));
  t(s.max > 20, `rail overflows (max=${s.max})`);
  t(s.state === 'right' || s.state === 'both', `at rest shows a right cue (state=${s.state})`);
  t(s.fadeR && s.arrowR, 'right fade + right arrow visible');

  await p.click('#rail-r'); await p.waitForTimeout(700);
  const s2 = await read(p);
  t(s2.left > s.left + 100, `right arrow scrolls (${s.left} → ${s2.left})`);
  t(s2.fadeL && s2.arrowL, 'left cue appears once scrolled off the start');

  // scroll fully right -> only left cue
  await p.evaluate(() => { const r = document.getElementById('rail'); r.style.scrollBehavior = 'auto'; r.scrollLeft = r.scrollWidth; });
  await p.waitForTimeout(350);
  const s3 = await read(p);
  t(s3.state === 'left', `at the far end state=left (got ${s3.state})`);
  t(!s3.fadeR && !s3.arrowR, 'right cue gone at the far end');

  await p.click('#rail-l'); await p.waitForTimeout(700);
  const s4 = await read(p);
  t(s4.left < s3.left - 100, `left arrow scrolls back (${s3.left} → ${s4.left})`);

  // clicking a pill still works with the arrows overlaying the ends
  await p.click('#rail button[data-id="d-mee-sotong"]'); await p.waitForTimeout(900);
  const sel = await p.$eval('#rail button[data-id="d-mee-sotong"]', e => e.getAttribute('aria-pressed'));
  t(sel === 'true', 'pill under the arrow region is still clickable');
  await p.close();

  // --- narrow: still coherent ---
  p = await b.newPage({ viewport: { width: 390, height: 844 } });
  p.on('pageerror', e => fails.push('mobile pageerror ' + e));
  await p.goto(url); await p.waitForTimeout(2600);
  s = await read(p);
  console.log('mobile', JSON.stringify(s));
  t(s.state !== 'none', `mobile shows a cue (state=${s.state})`);

  await p.close();

  // --- a rail that fits shows nothing ---
  p = await b.newPage({ viewport: { width: 1440, height: 1000 } });
  await p.goto(url); await p.waitForTimeout(1600);
  await p.evaluate(() => {
    const r = document.getElementById('rail');
    [...r.children].slice(3).forEach(c => c.remove());
    r.dispatchEvent(new Event('scroll'));
  });
  await p.waitForTimeout(500);
  s = await read(p);
  t(s.state === 'none', `three pills => state=none (got ${s.state})`);
  t(!s.fadeL && !s.fadeR && !s.arrowL && !s.arrowR, 'no fades or arrows when it fits');
  await p.close();

  // --- the one-time peek actually moves the rail and returns it ---
  p = await b.newPage({ viewport: { width: 1440, height: 1000 } });
  await p.goto(url);
  const samples = await p.evaluate(() => new Promise((res) => {
    const r = document.getElementById('rail'); const out = [];
    const iv = setInterval(() => out.push(r.scrollLeft), 60);
    setTimeout(() => { clearInterval(iv); res(out); }, 2600);
  }));
  const peak = Math.max(...samples), end = samples[samples.length - 1];
  t(peak > 10, `peek moves the rail (peak ${Math.round(peak)}px)`);
  t(end < 3, `peek returns to the start (ended ${Math.round(end)}px)`);
  await p.close();

  /* The always-visible scrollbar CANNOT be verified in headless Chromium — it uses
     overlay scrollbars platform-wide (an unstyled probe reserves 0px too), and
     getComputedStyle on ::-webkit-scrollbar-thumb returns the authored value whether
     or not Chrome is honouring it. So assert the source condition instead: the rail
     must not set scrollbar-width/color outside the Firefox @supports block, because
     either one makes Chrome discard every ::-webkit-scrollbar rule. */
  const css = require('fs').readFileSync(VIZ_DIR + '/04-bowl-orbit.html', 'utf8');
  // strip comments first — an earlier version of this check matched the explanatory
  // comment that names the very properties it is asserting are absent
  const bare = css.replace(/\/\*[\s\S]*?\*\//g, '');
  const railRule = bare.slice(bare.indexOf('.dish-rail {'), bare.indexOf('.dish-rail::-webkit-scrollbar'));
  t(!/scrollbar-(width|color)/.test(railRule), 'no standard scrollbar props in .dish-rail (they would kill the webkit styling)');
  t(/::-webkit-scrollbar-thumb\s*{/.test(bare), '::-webkit-scrollbar-thumb is styled');
  t(/@supports \(-moz-appearance/.test(bare), 'Firefox gets the standard props via @supports');

  console.log(fails.length ? '\nFAILURES:\n' + fails.join('\n') : '\nrail affordance correct');
  await b.close();
  process.exit(fails.length ? 1 : 0);
})();
