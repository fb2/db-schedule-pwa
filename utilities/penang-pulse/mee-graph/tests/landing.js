const path = require('path');
const fs = require('fs');
const VIZ_DIR = path.resolve(__dirname, '..', 'viz');
const VIZ = 'file://' + VIZ_DIR;
const SHOTS = path.resolve(__dirname, 'shots');
fs.mkdirSync(SHOTS, { recursive: true });
const { chromium } = require('playwright');

const stats = JSON.parse(fs.readFileSync(path.resolve(__dirname, '..', 'data', 'graph-stats.json'), 'utf8'));
const EXPECT = {
  dish: stats.nodesByType.dish,
  culture: stats.nodesByType.culture,
  region: stats.nodesByType.region,
  sources: stats.sources,
};

(async () => {
  const b = await chromium.launch();
  const fails = [];
  const t = (c, m) => { if (!c) fails.push(m); console.log(`${c ? 'ok  ' : 'FAIL'} ${m}`); };

  for (const vp of [{ width: 1280, height: 1000 }, { width: 390, height: 844 }]) {
    const p = await b.newPage({ viewport: vp });
    const errs = [];
    p.on('pageerror', e => errs.push(String(e)));
    p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
    await p.goto(VIZ + '/mee-search.html');
    await p.waitForTimeout(700);
    console.log(`\n--- ${vp.width}x${vp.height} ---`);
    t(errs.length === 0, `no console or page errors${errs.length ? ' — ' + errs[0] : ''}`);

    const r = await p.evaluate(() => {
      const counts = {};
      document.querySelectorAll('[data-count]').forEach(e => (counts[e.dataset.count] = e.textContent.trim()));
      const cards = [...document.querySelectorAll('.ms-card')].map(a => ({
        href: a.getAttribute('href'),
        heading: a.querySelector('h2') ? a.querySelector('h2').textContent.trim() : null,
        cta: a.querySelector('.ms-more') ? a.querySelector('.ms-more').textContent.trim() : null,
      }));
      return {
        counts, cards,
        h1: (document.querySelector('h1') || {}).textContent,
        title: document.title,
        headingOrder: [...document.querySelectorAll('h1,h2,h3')].map(h => h.tagName),
        overflow: Math.max(0, document.documentElement.scrollWidth - window.innerWidth),
        thumbsHidden: [...document.querySelectorAll('.ms-thumb')].every(e => e.getAttribute('aria-hidden') === 'true'),
      };
    });

    for (const [k, want] of Object.entries(EXPECT)) {
      t(r.counts[k] === String(want), `${k} count on the page (${r.counts[k]}) matches graph-stats.json (${want})`);
    }
    t(r.cards.length === 4, `four cards (${r.cards.length})`);
    t(r.h1.trim() === 'Mee-Search', `h1 is "Mee-Search" (got "${(r.h1 || '').trim()}")`);
    t(/^Mee-Search — where Penang's noodles come from/.test(r.title), 'page title carries the plain-language half');
    t(r.headingOrder[0] === 'H1' && r.headingOrder.slice(1).every(h => h === 'H2'), `heading order is h1 then h2s (${r.headingOrder.join(',')})`);
    t(r.overflow === 0, `no horizontal overflow (${r.overflow}px)`);
    t(r.thumbsHidden, 'decorative thumbnails are aria-hidden');

    for (const c of r.cards) {
      const target = path.join(VIZ_DIR, c.href.replace('./', ''));
      t(fs.existsSync(target), `${c.heading} links to a file that exists (${c.href})`);
      t(!!c.cta && c.cta.length > 3, `${c.heading} has a distinct call to action ("${c.cta}")`);
    }

    const ctas = r.cards.map(c => c.cta);
    t(new Set(ctas).size === ctas.length, `calls to action are all different (${ctas.join(' / ')})`);

    await p.screenshot({ path: path.join(SHOTS, `landing-${vp.width}.png`), fullPage: true });
    await p.close();
  }

  // keyboard: every card reachable by tab, in document order
  const p = await b.newPage({ viewport: { width: 1280, height: 1000 } });
  await p.goto(VIZ + '/mee-search.html');
  await p.waitForTimeout(400);
  const order = [];
  for (let i = 0; i < 10; i++) {
    await p.keyboard.press('Tab');
    const h = await p.evaluate(() => {
      const a = document.activeElement;
      return a && a.classList.contains('ms-card') ? a.querySelector('h2').textContent.trim() : null;
    });
    if (h) order.push(h);
  }
  t(order.length === 4, `all four cards reachable by keyboard (${order.length})`);
  t(order.join('|') === 'Origin drill|Bowl orbit|Thread flow|Arrivals', `tab order follows the page (${order.join(', ')})`);
  await p.close();

  console.log(fails.length ? '\nFAILURES:\n' + fails.join('\n') : '\nlanding page correct');
  await b.close();
  process.exit(fails.length ? 1 : 0);
})();
