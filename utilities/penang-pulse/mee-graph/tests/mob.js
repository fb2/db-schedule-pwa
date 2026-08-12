const path = require('path');
const VIZ_DIR = path.resolve(__dirname, '..', 'viz');
const VIZ = 'file://' + VIZ_DIR;
const SHOTS = path.resolve(__dirname, 'shots');
require('fs').mkdirSync(SHOTS, { recursive: true });
const { chromium } = require('playwright');
const D = VIZ + '/';
const files = ['index.html','01-culture-web.html','02-origin-drill.html','03-thread-flow.html','04-bowl-orbit.html','05-timeline-waves.html','06-confidence-fog.html','07-series-path.html'];
(async () => {
  const b = await chromium.launch({args:['--no-sandbox']});
  let bad = 0;
  for (const f of files) {
    const ctx = await b.newContext({viewport:{width:390,height:844}, deviceScaleFactor:2, isMobile:true, hasTouch:true});
    const p = await ctx.newPage();
    const errs = [];
    p.on('pageerror', e => errs.push(e.message));
    await p.goto(D+f); await p.waitForTimeout(2600);
    const r = await p.evaluate(() => {
      const overflow = document.documentElement.scrollWidth - document.documentElement.clientWidth;
      const stage = document.querySelector('.viz-stage');
      const geom = document.querySelectorAll('svg circle,svg path,svg rect,svg line').length;
      const ink = [...document.querySelectorAll('canvas')].map(c=>{try{const g=c.getContext('2d');const d=g.getImageData(0,0,c.width,c.height).data;let n=0;for(let i=3;i<d.length;i+=4*97)if(d[i]>8)n++;return n}catch(e){return -1}});
      return {overflow, stageH: stage?Math.round(stage.getBoundingClientRect().height):0, geom, ink};
    });
    const ok = r.overflow <= 2 && (r.geom > 15 || r.ink.some(v=>v>40)) && errs.length===0;
    if (!ok) bad++;
    console.log(`${ok?'PASS':'FAIL'}  ${f}  hOverflow=${r.overflow}px stage=${r.stageH} geom=${r.geom} ink=[${r.ink}]${errs.length?' ERR '+errs[0].slice(0,90):''}`);
    await p.screenshot({path:path.join(SHOTS, 'mob-')+f.replace('.html','.png')});
    await ctx.close();
  }
  await b.close();
  console.log(bad? `\n${bad} mobile issue(s)` : '\nMobile clean: no horizontal overflow, all views draw');
})();
