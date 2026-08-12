const path = require('path');
const VIZ_DIR = path.resolve(__dirname, '..', 'viz');
const VIZ = 'file://' + VIZ_DIR;
const SHOTS = path.resolve(__dirname, 'shots');
require('fs').mkdirSync(SHOTS, { recursive: true });
const { chromium } = require('playwright');
const D=VIZ + '/';
const files=['01-culture-web','02-origin-drill','03-thread-flow','04-bowl-orbit','05-timeline-waves','06-confidence-fog','07-series-path'];
(async () => {
  const b = await chromium.launch({args:['--no-sandbox']});
  let bad=0;
  for (const f of files) {
    for (const scrolled of [false, true]) {
      const p = await b.newPage({viewport:{width:1440,height:1000}});
      const errs=[]; p.on('pageerror',e=>errs.push(e.message));
      await p.goto(D+f+'.html'); await p.waitForTimeout(2500);
      if (scrolled) { await p.evaluate(()=>window.scrollTo(0,300)); await p.waitForTimeout(400); }
      await p.evaluate(async () => {
        const wait=(ms)=>new Promise(r=>setTimeout(r,ms));
        const open=()=>document.querySelector('.viz-panel').dataset.open==='true';
        for (const sel of ['svg g.n circle.body','.sat circle','.ep circle','.col-node rect','.lane rect','g.dish-dot circle','.arc']) {
          for (const el of [...document.querySelectorAll(sel)].slice(0,14)) {
            el.dispatchEvent(new MouseEvent('click',{bubbles:true})); await wait(70);
            if (open()) return;
          }
        }
        const li=document.querySelector('#dangerlist li'); if(li) li.click();
      });
      await p.waitForTimeout(800);
      const r = await p.evaluate(() => {
        const pa = document.querySelector('.viz-panel');
        const body = pa.querySelector('.p-body');
        const fade = pa.querySelector('.p-fade');
        const pr = pa.getBoundingClientRect(), br = body.getBoundingClientRect(), fr = fade.getBoundingClientRect();
        return {
          // the fade must sit on the panel's bottom edge, not somewhere on the page
          fadeOffBottom: Math.round(pr.bottom - fr.bottom),
          fadeInsidePanel: fr.top >= pr.top - 1 && fr.bottom <= pr.bottom + 1 &&
                           fr.left >= pr.left - 1 && fr.right <= pr.right + 1,
          // the scroll region must not spill past the panel
          bodyOverflowPx: Math.round(Math.max(0, br.bottom - pr.bottom)),
          bodyScrolls: body.scrollHeight > body.clientHeight + 2,
          more: pa.dataset.more,
          atTop: body.scrollTop === 0,
        };
      });
      const ok = r.fadeInsidePanel && Math.abs(r.fadeOffBottom) <= 2 && r.bodyOverflowPx === 0 && r.atTop && !errs.length;
      if (!ok) bad++;
      const why=[];
      if (!r.fadeInsidePanel) why.push('fade outside panel');
      if (Math.abs(r.fadeOffBottom)>2) why.push('fade '+r.fadeOffBottom+'px off the bottom edge');
      if (r.bodyOverflowPx) why.push('body spills '+r.bodyOverflowPx+'px');
      if (!r.atTop) why.push('not scrolled to top');
      if (errs.length) why.push('js: '+errs[0].slice(0,60));
      console.log(`${ok?'PASS':'FAIL'} ${f.padEnd(18)} ${scrolled?'page scrolled':'page at top  '} · scrolls=${r.bodyScrolls} more=${r.more}${why.length?'  << '+why.join(', '):''}`);
      await p.close();
    }
  }
  await b.close();
  console.log(bad? `\n${bad} geometry failure(s)`:'\nPanel geometry correct in all views, scrolled or not');
})();
