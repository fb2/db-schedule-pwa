const path = require('path');
const VIZ_DIR = path.resolve(__dirname, '..', 'viz');
const VIZ = 'file://' + VIZ_DIR;
const SHOTS = path.resolve(__dirname, 'shots');
require('fs').mkdirSync(SHOTS, { recursive: true });
const { chromium } = require('playwright');
const DIR = VIZ + '';
const OUT = SHOTS;
const files = ['index.html','01-culture-web.html','02-origin-drill.html','03-thread-flow.html',
               '04-bowl-orbit.html','05-timeline-waves.html','06-confidence-fog.html','07-series-path.html'];

(async () => {
  const fs = require('fs'); fs.mkdirSync(OUT, {recursive:true});
  const browser = await chromium.launch({args:['--no-sandbox','--disable-dev-shm-usage']});
  let bad = 0;
  for (const f of files) {
    const ctx = await browser.newContext({viewport:{width:1280,height:1000}, deviceScaleFactor:1});
    const page = await ctx.newPage();
    const errs = [], warns = [];
    page.on('console', m => {
      if (m.type() !== 'error') return;
      const t = m.text();
      // external CDN + Google Fonts are unreachable in this sandbox; not our bug
      if (/Failed to load resource/i.test(t)) { warns.push(t); return; }
      errs.push(t);
    });
    page.on('pageerror', e => errs.push('PAGEERROR: ' + e.message));
    page.on('requestfailed', r => {
      const u = r.url();
      if (!/fonts\.g|cdnjs/.test(u)) errs.push('REQFAIL: ' + u);
      else warns.push('offline-cdn: ' + u.split('/').pop());
    });
    await page.goto('file://' + path.join(DIR, f));
    // 02 plays a staggered entrance then holds still on purpose (rotating labels
    // are unreadable); sample it while the entrance is still running.
    await page.waitForTimeout(f.startsWith('02') ? 350 : 3200);

    // does the stage actually contain drawn geometry?
    const probe = await page.evaluate(() => {
      const q = s => document.querySelectorAll(s).length;
      const stage = document.querySelector('.viz-stage, .gallery');
      const canv = [...document.querySelectorAll('canvas')].map(c => {
        try {
          const g = c.getContext('2d');
          const d = g.getImageData(0,0,c.width,c.height).data;
          let nz=0; for (let i=3;i<d.length;i+=4*97) if (d[i]>8) nz++;
          return nz;
        } catch(e){ return -1; }
      });
      return {
        d3: typeof window.d3, mee: typeof window.MEE,
        data: window.MEE_GRAPH ? window.MEE_GRAPH.nodes.length : 0,
        svg: q('svg'), circles: q('svg circle'), paths: q('svg path'),
        rects: q('svg rect'), lines: q('svg line'), texts: q('svg text'),
        canvasInk: canv, panels: q('.viz-panel'), cards: q('.g-card'),
        stageH: stage ? Math.round(stage.getBoundingClientRect().height) : 0,
        failNote: !!document.body.textContent.match(/Could not load the graph data/),
      };
    });

    // motion check: sample geometry twice
    const sig = () => page.evaluate(() => {
      // sample every attribute the views actually animate: cx/cy, group transforms,
      // path d, line endpoints, canvas ink
      const grab = sel => [...document.querySelectorAll(sel)].slice(0,60)
        .map(e => (e.getAttribute('cx')||'')+(e.getAttribute('cy')||'')+(e.getAttribute('transform')||'')+
                  (e.getAttribute('x1')||'')+(e.getAttribute('d')||'').slice(0,60)+(e.getAttribute('stroke-dashoffset')||''))
        .join('|');
      const s = grab('svg circle')+grab('svg g')+grab('svg line')+grab('svg path');
      const cv = [...document.querySelectorAll('canvas')].map(x=>{try{
        const g=x.getContext('2d'); const d=g.getImageData(0,0,Math.min(300,x.width),Math.min(300,x.height)).data;
        let h=0; for(let i=0;i<d.length;i+=4*211) h=(h*31+d[i+3])|0; return h;
      }catch(e){return 0}}).join(',');
      return s + '##' + cv;
    });
    const a = await sig(); await page.waitForTimeout(f.startsWith('02') ? 420 : 900); const b = await sig();
    const moving = a !== b;
    const geom = probe.circles+probe.paths+probe.rects+probe.lines;
    const inkOK = probe.canvasInk.length===0 || probe.canvasInk.some(v=>v>0);
    // canvas-only views legitimately have no svg geometry: require ink instead
    const drew = geom > 18 || probe.canvasInk.some(v => v > 40);
    const pass = probe.d3==='object' && probe.data>0 && drew && !probe.failNote && errs.length===0 && inkOK && moving;
    if (!pass) bad++;
    console.log(`\n${pass?'PASS':'FAIL'}  ${f}`);
    console.log(`   d3=${probe.d3} MEE=${probe.mee} nodes=${probe.data} stageH=${probe.stageH}`);
    console.log(`   svg geom: circles=${probe.circles} paths=${probe.paths} rects=${probe.rects} lines=${probe.lines} texts=${probe.texts}`);
    console.log(`   canvasInk=[${probe.canvasInk}] cards=${probe.cards} animating=${moving}`);
    if (warns.length) console.log('   (cdn/font offline: ' + warns.length + ' — expected in sandbox)');
    if (errs.length) errs.slice(0,6).forEach(e=>console.log('   ERR ' + e.slice(0,220)));
    await page.screenshot({path: path.join(OUT, f.replace('.html','.png')), fullPage:false});
    await ctx.close();
  }
  await browser.close();
  console.log(bad ? `\n${bad} file(s) failed` : '\nAll files rendered clean');
  process.exit(bad?1:0);
})();
