const path = require('path');
const VIZ_DIR = path.resolve(__dirname, '..', 'viz');
const VIZ = 'file://' + VIZ_DIR;
const SHOTS = path.resolve(__dirname, 'shots');
require('fs').mkdirSync(SHOTS, { recursive: true });
const { chromium } = require('playwright');
const D = VIZ + '/';
const errs = [];
(async () => {
  const b = await chromium.launch({args:['--no-sandbox']});
  const page = await b.newPage({viewport:{width:1280,height:1000}});
  page.on('pageerror', e => errs.push('PAGEERROR ' + e.message));
  page.on('console', m => { if (m.type()==='error' && !/Failed to load resource/.test(m.text())) errs.push('CONSOLE ' + m.text()); });

  const step = async (label, fn) => {
    const before = errs.length;
    try { await fn(); } catch(e) { errs.push(label + ' THREW ' + e.message); }
    await page.waitForTimeout(700);
    console.log((errs.length===before?'  ok  ':' ERR  ') + label);
  };

  // ---- 01 culture web
  await page.goto(D+'01-culture-web.html'); await page.waitForTimeout(2000);
  console.log('01-culture-web');
  await step('switch to Origins mode', () => page.click('[data-mode="origins"]'));
  await step('switch to Noodles mode', () => page.click('[data-mode="noodles"]'));
  await step('back to Communities', () => page.click('[data-mode="communities"]'));
  await step('toggle contested off', () => page.click('#claims'));
  await step('drag gravity slider', () => page.$eval('#gravity', el => { el.value=90; el.dispatchEvent(new Event('input',{bubbles:true})); }));
  await step('expand a hub by click', async () => {
    await page.$eval('svg g.n circle.body', el => el.parentElement.dispatchEvent(new MouseEvent('click',{bubbles:true})));
  });
  await step('panel opened', async () => {
    const open = await page.$eval('.viz-panel', el => el.dataset.open);
    if (open !== 'true') throw new Error('panel did not open');
  });
  await step('collapse all', () => page.click('#reset'));

  // ---- 02 origin drill
  await page.goto(D+'02-origin-drill.html'); await page.waitForTimeout(2200);
  console.log('02-origin-drill');
  await step('zoom into a wedge', () => page.$eval('.arc', el => el.dispatchEvent(new MouseEvent('click',{bubbles:true}))));
  await step('breadcrumb appeared', async () => {
    const n = await page.$$eval('.crumbs button', a => a.length);
    if (n < 1) throw new Error('no breadcrumb after zoom');
  });
  await step('switch hierarchy: place', () => page.click('[data-tree="place"]'));
  await step('switch hierarchy: kitchen', () => page.click('[data-tree="kitchen"]'));
  await step('toggle spin off', () => page.click('#spin'));

  // ---- 03 thread flow
  await page.goto(D+'03-thread-flow.html'); await page.waitForTimeout(2200);
  console.log('03-thread-flow');
  await step('switch to component flow', () => page.click('[data-flow="component"]'));
  await step('back to origin flow', () => page.click('[data-flow="origin"]'));
  await step('pause particles', () => page.click('#pause'));
  await step('follow a thread', async () => {
    const v = await page.$eval('#focus option:nth-child(3)', o => o.value);
    await page.selectOption('#focus', v);
    const dimmed = await page.$$eval('.ribbon.dim', a => a.length);
    if (!dimmed) throw new Error('focus did not dim other ribbons');
  });

  // ---- 04 bowl orbit
  await page.goto(D+'04-bowl-orbit.html'); await page.waitForTimeout(2000);
  console.log('04-bowl-orbit');
  await step('next bowl', () => page.click('#next'));
  await step('threads recomputed', async () => {
    const n = await page.$$eval('.thread-arc', a => a.length);
    if (n < 2) throw new Error('thread ring empty');
  });
  await step('switch to Penang core set', () => page.click('[data-set="core"]'));
  await step('switch to Everything', () => page.click('[data-set="all"]'));
  await step('pick a dish from the rail', () => page.$eval('#rail button:nth-child(4)', el => el.click()));
  await step('hold the orbit still', () => page.click('#spin'));

  // ---- 05 timeline
  await page.goto(D+'05-timeline-waves.html'); await page.waitForTimeout(1600);
  console.log('05-timeline-waves');
  await step('scrub to 1975', () => page.$eval('#scrub', el => { el.value=1975; el.dispatchEvent(new Event('input',{bubbles:true})); }));
  await step('dishes revealed by 1975', async () => {
    const vis = await page.$$eval('g.dish-dot', a => a.filter(e => +getComputedStyle(e).opacity > 0.5).length);
    if (vis < 1) throw new Error('no dish appeared by 1975');
  });
  await step('waves only', () => page.click('[data-layer="waves"]'));
  await step('commodities only', () => page.click('[data-layer="commodity"]'));
  await step('replay', () => page.click('#restart'));

  // ---- 06 fog
  await page.goto(D+'06-confidence-fog.html'); await page.waitForTimeout(2200);
  console.log('06-confidence-fog');
  await step('burn off to 85%', () => page.$eval('#fog', el => { el.value=85; el.dispatchEvent(new Event('input',{bubbles:true})); }));
  await step('few edges remain', async () => {
    const t = await page.$eval('#readout', el => el.textContent);
    const left = parseInt(t.match(/(\d+)of/)?.[1] || t, 10);
    if (!(left > 0 && left < 120)) throw new Error('expected a short list, got: ' + t.slice(0,60));
    console.log('        readout: ' + t.replace(/\s+/g,' ').trim().slice(0,80));
  });
  await step('risk emphasis', () => page.click('[data-em="risk"]'));
  await step('source-quality emphasis', () => page.click('[data-em="tier"]'));
  await step('click a danger-list item', () => page.click('#dangerlist li'));
  await step('auto-sweep', () => page.click('#sweep'));

  // ---- 07 series
  await page.goto(D+'07-series-path.html'); await page.waitForTimeout(2500);
  console.log('07-series-path');
  await step('arrange by noodle', () => page.click('[data-arrange="noodle"]'));
  await step('arrange by venue', () => page.click('[data-arrange="venue"]'));
  await step('arrange by community', () => page.click('[data-arrange="culture"]'));
  await step('hide to-try', () => page.click('#showtodo'));
  await step('scrub to episode 6', () => page.$eval('#scrub', el => { el.value=6; el.dispatchEvent(new Event('input',{bubbles:true})); }));
  await step('six episodes shown', async () => {
    const n = await page.$$eval('g.ep', a => a.length);
    if (n !== 6) throw new Error('expected 6 episodes, got ' + n);
  });
  await step('replay the run', () => page.click('#replay'));

  await b.close();
  console.log('\n' + (errs.length ? errs.length + ' problem(s):\n' + errs.join('\n') : 'All interactions clean'));
  process.exit(errs.length?1:0);
})();
