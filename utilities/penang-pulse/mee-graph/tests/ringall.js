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
  await p.waitForTimeout(2500);

  const probe = () => p.evaluate(() => {
    const svg = document.querySelector('#stage svg');
    const st = svg.getBoundingClientRect();
    const cx = st.left + st.width/2, cy = st.top + st.height/2;
    const bearing = (x,y) => (Math.atan2(x-cx, -(y-cy)) * 180/Math.PI + 360) % 360;
    const arcs = Object.fromEntries([...document.querySelectorAll('.thread-arc')].map(a=>{
      const d = d3.select(a).datum();
      return [d.culture.id, ((d.mid*180/Math.PI)%360+360)%360];
    }));
    const labels = [...document.querySelectorAll('.thread-tick')].map(t=>{
      const d = d3.select(t).datum(); const r = t.getBoundingClientRect();
      const an = t.getAttribute('text-anchor');
      const lx = an==='start' ? r.left+2 : an==='end' ? r.right-2 : (r.left+r.right)/2;
      return { id: d.culture.id, deg: bearing(lx,(r.top+r.bottom)/2), inside: r.left>=st.left && r.right<=st.right && r.top>=st.top && r.bottom<=st.bottom };
    });
    return { dish: document.querySelector('.core-title').textContent,
             nArcs: Object.keys(arcs).length, nLabels: labels.length,
             worst: Math.max(0, ...labels.map(l=>{
               const s=(((l.deg-arcs[l.id]+180)%360)+360)%360-180; return Math.abs(s); })),
             chips: document.querySelectorAll('.thread-chip').length,
             allInside: labels.every(l=>l.inside) };
  });

  let bad = 0;
  // walk every unique tasted dish (derived from tried episodes — do not hardcode)
  const nTried = await p.evaluate(() =>
    new Set(
      (window.MEE_GRAPH.nodes || [])
        .filter((n) => n.type === "episode" && n.status === "tried")
        .map((e) => e.dish)
    ).size
  );
  for (let i = 0; i < nTried; i++) {
    const r = await probe();
    const ok = r.nLabels === r.nArcs && r.worst <= 40 && r.allInside && r.chips === r.nArcs;
    if (!ok) bad++;
    console.log(`${ok?'ok  ':'BAD '} ${String(r.dish).replace(/\s+/g,' ').slice(0,26).padEnd(27)} arcs=${r.nArcs} labels=${r.nLabels} chips=${r.chips} worstOffset=${Math.round(r.worst)}° insideStage=${r.allInside}`);
    await p.click('#next'); await p.waitForTimeout(1000);
  }
  console.log(bad ? `\n${bad} dish(es) with a ring/label mismatch` : '\nRing labels correct for every tasted dish: one label per thread, all aligned, all inside the stage');
  console.log(errs.length?'ERRORS '+errs.join(' | '):'no console errors');
  await b.close();
})();
