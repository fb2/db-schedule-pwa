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
  await p.goto(VIZ + '/04-bowl-orbit.html');
  await p.waitForTimeout(2400);
  await p.evaluate(()=>{const btn=[...document.querySelectorAll('#rail button')].find(x=>/Sotong/i.test(x.textContent)); btn.click();});
  await p.waitForTimeout(1200);
  const r = await p.evaluate(()=>{
    const body = document.querySelector('.p-body');
    return { asterisks: (body.textContent.match(/\*\*/g)||[]).length,
             strongs: [...body.querySelectorAll('strong')].map(s=>s.textContent),
             // make sure no raw html leaked through from the data
             hasScript: /<script/i.test(body.innerHTML) };
  });
  console.log('literal ** left in the dossier:', r.asterisks);
  console.log('rendered bold spans:', JSON.stringify(r.strongs));
  console.log('raw html injected from data:', r.hasScript);
  console.log(errs.length?'ERRORS '+errs.join(' | '):'no console errors');
  await b.close();
})();
