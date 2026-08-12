const path = require('path');
const VIZ_DIR = path.resolve(__dirname, '..', 'viz');
const VIZ = 'file://' + VIZ_DIR;
const SHOTS = path.resolve(__dirname, 'shots');
require('fs').mkdirSync(SHOTS, { recursive: true });
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({args:['--no-sandbox']});
  const p = await b.newPage({viewport:{width:1440,height:1050}});
  const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  p.on('console',m=>{if(m.type()==='error'&&!/Failed to load resource/.test(m.text()))errs.push(m.text())});
  await p.goto(VIZ + '/04-bowl-orbit.html');
  await p.waitForTimeout(2600);

  const layout = await p.evaluate(() => {
    const side = document.querySelector('.orbit-side').getBoundingClientRect();
    const dos = document.querySelector('.dossier').getBoundingClientRect();
    return { sideH: Math.round(side.height), dossierH: Math.round(dos.height),
             fillsColumn: Math.abs(side.height - dos.height) < 3,
             threadBox: !!document.querySelector('.thread-list'),
             chips: document.querySelectorAll('.thread-chip').length,
             firstText: document.querySelector('.dossier .p-type').textContent,
             chipsBelowProse: (() => {
               const pr = document.querySelector('.dossier .p-blurb');
               const ch = document.querySelector('.dossier .p-threads');
               return pr && ch ? ch.getBoundingClientRect().top > pr.getBoundingClientRect().top : null;
             })() };
  });
  console.log('dossier fills column:', layout.fillsColumn, '(' + layout.dossierH + ' of ' + layout.sideH + ')');
  console.log('separate threads box gone:', !layout.threadBox, '· chips inside dossier:', layout.chips);
  console.log('dossier starts with:', JSON.stringify(layout.firstText), '· chips after prose:', layout.chipsBelowProse);

  // easing: sample opacity mid-transition — an instant swap lands on the end value
  const mid = await p.evaluate(async () => {
    const wait=(ms)=>new Promise(r=>setTimeout(r,ms));
    const arcs = () => [...document.querySelectorAll('.thread-arc')].map(a=>+(a.style.opacity||getComputedStyle(a).opacity));
    const before = arcs();
    document.querySelector('.thread-chip').dispatchEvent(new MouseEvent('mouseenter',{bubbles:true}));
    await wait(70);                     // a third of the way through a 220ms tween
    const during = arcs();
    await wait(400);
    const after = arcs();
    document.querySelector('.thread-chip').dispatchEvent(new MouseEvent('mouseleave',{bubbles:true}));
    await wait(500);
    const rest = arcs();
    return { before, during, after, rest };
  });
  const moved = mid.during.some((v,i) => Math.abs(v - mid.before[i]) > 0.01 && Math.abs(v - mid.after[i]) > 0.01);
  console.log('\nopacity sampled 70ms into a 220ms hover tween:');
  console.log('  before:', mid.before.map(v=>v.toFixed(2)).join(' '));
  console.log('  during:', mid.during.map(v=>v.toFixed(2)).join(' '));
  console.log('  after :', mid.after.map(v=>v.toFixed(2)).join(' '));
  console.log('  rest  :', mid.rest.map(v=>v.toFixed(2)).join(' '));
  console.log(moved ? '  → intermediate values present: the hover is EASED' : '  → snapped straight to the end value: NOT eased');
  const restOK = mid.rest.every(v => Math.abs(v - 0.9) < 0.02);
  console.log(restOK ? '  → returns cleanly to 0.90 on mouseleave' : '  → does NOT return to 0.90: ' + mid.rest.join(','));
  await p.screenshot({path:path.join(SHOTS, '04-dossier-full.png'), clip:{x:150,y:250,width:1160,height:790}});
  console.log(errs.length?'ERRORS '+errs.join(' | '):'no console errors');
  await b.close();
})();
