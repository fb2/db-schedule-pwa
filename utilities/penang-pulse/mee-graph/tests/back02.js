const path = require('path');
const VIZ_DIR = path.resolve(__dirname, '..', 'viz');
const VIZ = 'file://' + VIZ_DIR;
const SHOTS = path.resolve(__dirname, 'shots');
require('fs').mkdirSync(SHOTS, { recursive: true });
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({args:['--no-sandbox']});
  const p = await b.newPage({viewport:{width:1440,height:1300}});
  const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  p.on('console',m=>{if(m.type()==='error'&&!/Failed to load resource/.test(m.text()))errs.push(m.text())});
  await p.goto(VIZ + '/02-origin-drill.html');
  await p.waitForTimeout(2600);

  const where = () => p.$eval('#crumbs .here', e => e.textContent.trim());
  const depth = () => p.$$eval('#crumbs button', a => a.length);
  const drill = (lab) => p.evaluate((l) => {
    const ls=[...document.querySelectorAll('.arc-label')];
    const t=ls.find(x=>x.textContent.startsWith(l)); if(!t) return false;
    document.querySelectorAll('.arc')[ls.indexOf(t)].dispatchEvent(new MouseEvent('click',{bubbles:true})); return true;
  }, lab);

  const check = async (label, expect) => {
    const w = await where();
    const ok = w.startsWith(expect);
    console.log((ok?'  ok  ':' FAIL ') + label + '  → "' + w + '"');
    return ok;
  };

  let fails = 0;
  console.log('entrance animation on load:');
  const a1 = await p.$$eval('.arc', a => a.slice(0,20).map(x=>x.getAttribute('d')).join('').length);
  await p.waitForTimeout(300);
  console.log('  ok  arcs have geometry (' + a1 + ' path chars)');

  console.log('\ndrill down two levels:');
  await drill('Chinese dialect'); await p.waitForTimeout(1300);
  if (!await check('level 1', 'Chinese dialect')) fails++;
  await drill('Hokkien'); await p.waitForTimeout(1500);
  if (!await check('level 2', 'Hokkien')) fails++;
  console.log('  breadcrumb steps available: ' + await depth());

  console.log('\nexit route 1 — click the centre of the circle:');
  await p.evaluate(() => document.querySelector('.hitcentre').dispatchEvent(new MouseEvent('click',{bubbles:true})));
  await p.waitForTimeout(1300);
  if (!await check('centre click went up', 'Chinese dialect')) fails++;

  console.log('\nexit route 2 — the "Up a level" button:');
  await p.click('#up'); await p.waitForTimeout(1300);
  if (!await check('up button went to root', 'Penang noodles')) fails++;
  const dis = await p.$eval('#up', e => e.disabled);
  console.log((dis?'  ok  ':' FAIL ') + 'up button disabled at root: ' + dis);
  if (!dis) fails++;

  console.log('\nexit route 3 — Escape key:');
  await drill('Chinese dialect'); await p.waitForTimeout(1200);
  await drill('Teochew'); await p.waitForTimeout(1300);
  await check('drilled to Teochew', 'Teochew');
  await p.keyboard.press('Escape'); await p.waitForTimeout(1300);
  if (!await check('Esc went up one', 'Chinese dialect')) fails++;

  console.log('\nexit route 4 — breadcrumb:');
  await drill('Hokkien'); await p.waitForTimeout(1300);
  await p.click('#crumbs button'); await p.waitForTimeout(1300);
  if (!await check('breadcrumb jumped to root', 'Penang noodles')) fails++;

  console.log('\nexit route 5 — "Back to the top" from depth 2:');
  await drill('Chinese dialect'); await p.waitForTimeout(1100);
  await drill('Hakka'); await p.waitForTimeout(1300);
  await p.click('#top'); await p.waitForTimeout(1300);
  if (!await check('top button', 'Penang noodles')) fails++;

  console.log('\n' + (errs.length ? 'ERRORS: '+errs.join(' | ') : 'no console errors'));
  console.log(fails ? fails + ' navigation failure(s)' : 'All five exit routes work');
  await p.screenshot({path:path.join(SHOTS, '02-final.png'), clip:{x:150,y:255,width:1150,height:1040}});
  await b.close();
})();
