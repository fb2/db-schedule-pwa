const path = require('path');
const VIZ_DIR = path.resolve(__dirname, '..', 'viz');
const VIZ = 'file://' + VIZ_DIR;
const SHOTS = path.resolve(__dirname, 'shots');
require('fs').mkdirSync(SHOTS, { recursive: true });
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({args:['--no-sandbox']});
  const p = await b.newPage({viewport:{width:1440,height:1100}});
  const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  await p.goto(VIZ + '/07-series-path.html');
  await p.waitForTimeout(2200);
  // jump straight to the end of the run
  await p.$eval('#scrub', el => { el.value = el.max; el.dispatchEvent(new Event('input',{bubbles:true})); });
  await p.waitForTimeout(1400);
  const r = await p.evaluate(() => ({
    progress: document.getElementById('pcount').textContent.replace(/\s+/g,' ').trim(),
    eps: [...document.querySelectorAll('.ep text')].map(t=>t.textContent),
    caption: document.getElementById('caption').textContent.replace(/\s+/g,' ').trim(),
  }));
  console.log('progress:', r.progress);
  console.log('episodes drawn:', r.eps.length);
  console.log('ep 16:', r.eps.filter(l=>/^16/.test(l)));
  console.log('caption:', r.caption);
  // and grouped by community, is there now a Tamil Muslim zone?
  await p.click('[data-arrange="culture"]'); await p.waitForTimeout(1500);
  console.log('community zones:', (await p.$$eval('.zone-label', a=>a.map(t=>t.textContent))).join(' | '));
  await p.screenshot({path:path.join(SHOTS, '07-with-sotong.png')});
  console.log(errs.length?'ERRORS '+errs.join('|'):'no errors');
  await b.close();
})();
