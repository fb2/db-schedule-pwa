# Mee-Search — where Penang's noodles come from

Animated views over the Penang noodle culture graph: 75 noodle dishes, 26 communities,
62 towns and regions, 1,020 traced connections, 138 cited sources.

Vanilla HTML, CSS and JS plus **d3 v7**. No build step, no framework, no bundler. Open any
file by double-clicking it — `graph-data.js` sets `window.MEE_GRAPH`, so every view works on
`file://` without a server.

`mee-search.html` is the section landing page: four cards, four counts, and live animated
thumbnails (same previews as the gallery) via `mee-search-thumbs.js`. Counts are still
literals; `tests/landing.js` fails if they drift from `data/graph-stats.json`. The public
port is emitted by the guides build. `index.html` is the development gallery of all seven
views and shares the four Mee-Search thumbs from that module.

```
mee-graph/
├── data/
│   ├── noodle-graph.json      362 nodes, 1020 edges, 138 sources
│   ├── graph-stats.json       counts per type, per confidence level
│   └── SCHEMA.md              node and edge types, field by field
├── narrative/                 seven essay chapters, ~24.5k words
├── tools/
│   ├── src_nodes.py  src_dishes.py  src_edges.py  src_sources.py
│   └── build_graph.py         validates, then emits all three outputs
├── tests/                     browser tests, see "Tests" below
└── viz/
    ├── mee-search.html        section landing page — no JS, no data load
    ├── index.html             development gallery of all seven views
    ├── 01-culture-web.html    force-directed drill-down: communities ↔ dishes
    ├── 02-origin-drill.html   radial hierarchy: thread → community → place → dish
    ├── 03-thread-flow.html    particle flow: place → community → noodle → dish
    ├── 04-bowl-orbit.html     one dish deconstructed into orbiting components
    ├── 05-timeline-waves.html 1786 → now, with an undated band
    ├── 06-confidence-fog.html evidence threshold, dissolving the weak claims
    ├── 07-series-path.html    every tasted bowl as a route across the map
    ├── mee-viz.css            shared chrome, inheriting the site's tokens and type
    ├── mee-viz.js             shared helpers
    └── graph-data.js          generated — do not edit
```

## The views

| # | View | Question it answers | Technique |
| --- | --- | --- | --- |
| 01 | Culture Web | Whose dish is this, and who else claims it? | `d3-force`, expand/collapse hubs, perpetual drift |
| 02 | Origin Drill | From "Chinese" to Zhangzhou in three clicks | `d3-partition` sunburst, arc-tween zoom, slow rotation |
| 03 | Thread Flow | Which noodle crossed every community boundary? | hand-rolled 4-column ribbon layout, canvas particles |
| 04 | Bowl Orbit | Which kitchens are actually in this bowl? | orbital `d3.timer`, arc-tween thread ring, dossier column |
| 05 | Timeline Waves | What can be dated, and what can't? | animated playhead and scrubber, reveal-on-pass |
| 06 | Confidence Fog | Which claims would break the narrative if wrong? | canvas force graph, evidence-threshold dissolve |
| 07 | Series Path | Where has the eating been, and what is missing? | animated path draw, regroups by community/noodle/venue |

Four of these carry the Mee-Search section: **02 Origin Drill**, **04 Bowl Orbit**,
**03 Thread Flow** and **05 Timeline Waves**. Each owns its own control row, matched to its
own question — a breadcrumb for the drill, a bowl stepper for the orbit, a thread picker for
the flow, time for the waves. The shared chrome is a topbar with the four view tabs and a
route back to the landing page, and nothing else. Continuity between views runs through the
dossier: click a dish anywhere and it offers a route into Bowl Orbit for that dish.

01 and 06 are method views, useful for editing the dataset and for prose about how it was
built. 07 belongs on the series index.

## Shared helpers

`mee-viz.js` exposes one global, `MEE`:

| Call | Gives you |
| --- | --- |
| `MEE.load()` | the graph, indexed; throws if `graph-data.js` is missing |
| `MEE.index(g)` | `byId`, `byType`, `out`, `in`, `degree`, `neighbours`, `threadsOf` |
| `MEE.tooltip()` | one shared hover tooltip — **one per page** |
| `MEE.panel(stage, onNav, opts)` | the detail panel, floating or fixed |
| `MEE.legend(el, items)` | the colour key |
| `MEE.colour(n)` / `MEE.tone(n)` | the two colour scales, below |
| `MEE.rich(str)` | escapes, then re-introduces `**bold**` only |
| `MEE.esc(str)` / `MEE.short(str, n)` | escaping and truncation |
| `MEE.size(el)` / `MEE.onResize(fn)` | measured stage size, debounced resize |
| `MEE.reducedMotion()` | `prefers-reduced-motion` |

`threadsOf(dishId)` walks `carried_by` at weight 2.2, `attributed_to` at 1.1, then
`uses_noodle` / `uses_ingredient` / `uses_technique` out to each component and
`contributed_by` back to a community. No dish label is read at any point, which is why a
bowl can come out as five kitchens.

Several prose fields in the dataset contain `**bold**`, because the narrative chapters read
the same fields. Any view rendering those fields must use `MEE.rich()`, or the asterisks
show up literally.

## Colour model

Two scales, and they answer different questions.

- **`node.colour`** is the node *type* — dish red, community terracotta, noodle ochre, region
  blue, technique teal. Use it when the question is what kind of thing this is.
- **`node.tone`** is the *individual community* — Hokkien terracotta, Teochew deeper red,
  Cantonese lighter, Peranakan rose, Tamil Muslim violet, Malay/Javanese green, Siamese teal.
  Use it wherever one bowl receives several kitchens at once, which is the point of views 03,
  04 and 07.

Both are emitted by `tools/build_graph.py` and live in the data, so no renderer hardcodes a
taxonomy. `build_graph.py` refuses to write if any culture lacks a tone.

## Inherited styling

`mee-viz.css` re-declares the same tokens as `styles.css` and `guides/article.css` —
`--bg #fafaf8`, `--text #1c1c1a`, `--muted #6b6b66`, `--line #e6e6e2`, `--accent #0f6e6e` —
and reuses the site's existing patterns: Fraunces 560/650 for headings, Source Sans 3
400/500/600 for body, the uppercase letterspaced kicker, 1px borders, no shadows, and the
`.view-switch` pill toggle taken verbatim.

When embedding for real, delete the `:root` block and the `body` / `button` / `a` rules from
`mee-viz.css` and let the host stylesheet provide them. They exist so these files stand alone.

## Embedding

An iframe is enough, since each view is self-contained and responsive:

```html
<iframe src="/mee-graph/viz/04-bowl-orbit.html"
        title="What is in a bowl of Penang curry mee"
        loading="lazy" style="width:100%;height:820px;border:0"></iframe>
```

Inline suits a template better. Copy the `<style>` block, the stage markup and the view's
`<script>`, and include `mee-viz.js` once per page. Three things to watch:

1. **The detail panel has two modes.** `MEE.panel(stage, onNav)` floats it over the view.
   `MEE.panel(stage, onNav, { host: el })` renders it into an element you supply, as a fixed
   column beside the stage, with no fade-in, no close button, and no overlap. Use the fixed
   mode whenever the subject is centred and its labels sit outside it — an overlay in view 04
   covers the thread labels it is describing.
2. **`MEE.onResize` assumes the stage has a height from CSS.** The default stage is
   `height: min(70vh, 660px)`. Inside a flex or grid parent, give it an explicit height or it
   collapses to `min-height: 520px`.
3. **One `MEE.tooltip()` per page.** It appends a fixed-position div to `<body>`.

For deep-linking a dish into view 04, read `location.search` and pass it to `select()`, which
is already the entry point.

## Integrating the four section views

Each view is a single self-contained page: its own `<style>` block, its own stage markup, its
own `<script>`, and a shared dependency on `mee-viz.css`, `mee-viz.js`, `graph-data.js` and d3.
An iframe needs nothing changed. Inline, copy those three parts and include `mee-viz.js` once
per page.

Common to all four:

- **`graph-data.js` before `mee-viz.js` before the view's script.** The first sets
  `window.MEE_GRAPH`, and `MEE.load()` reads it.
- **The stage needs a height from CSS.** Each view sets its own; see the table.
- **One `MEE.tooltip()` per page.** Two views on one page means one tooltip between them.
- **`aria-pressed` toggles are wired by `data-` attribute, not by id**, so a template can
  re-render the control row as long as it keeps the attributes.

| | File | Stage height | Panel | Controls it owns | d3 modules |
| --- | --- | --- | --- | --- | --- |
| 02 | `02-origin-drill.html` | `min(96vh, 940px)`, min 560 | floating | `[data-tree]` ×3, `[data-depth]` ×3, `#up`, `#top`, `#spin`, `#crumbs` | `partition`, `interpolate`, `select`, `timer` |
| 03 | `03-thread-flow.html` | default `min(70vh, 660px)` | floating | `#focus` select, `#pause`, `#speed`, `#particles` | `select`, `timer`, `scale` |
| 04 | `04-bowl-orbit.html` | `--orbit-h: min(74vh, 660px)`, min 520 | fixed, in `#dossier` | `#railwrap` (`#rail`, `#rail-l`, `#rail-r`), `#spin`, `#next`, `[data-set]` ×3 | `arc`, `interpolate`, `select`, `timer` |
| 05 | `05-timeline-waves.html` | `min(76vh, 720px)`, inline on the element | floating | `#scrub`, `#play`, `#restart`, `#speed`, `#year` | `scaleLinear`, `group`, `select`, `timer` |

### 02 Origin Drill

Entry state is the `people` hierarchy at 3 rings. `relayout()` rebuilds after any hierarchy or
depth change and always animates, because a collapsed instant redraw leaves the arcs at zero
width with `pointer-events: none` and the drill stops responding.

Five exit routes back up the hierarchy, all of which need to survive a port: clicking the
centre, `#up`, `#top`, any crumb in `#crumbs`, and the `Esc` / `Backspace` / `Home` keys.
`back02.js` covers all five.

This view uses the full stage width and wants a near-square container. The default landscape
stage caps its radius at half the height and wastes the width.

### 03 Thread Flow

`layout()` builds the four columns and is called on entry, on `#focus` change, and on resize.
Particles are drawn to a `<canvas>` sized by `devicePixelRatio` and layered under the SVG, so a
host stylesheet that changes stacking context needs to leave `#svg` above the canvas.

`#focus` holds one community or one noodle. Passing a community id or noodle id into it is the
deep-link hook.

### 04 Bowl Orbit

`select(dishId)` is the single entry point and is called once on load with
`d-curry-mee-penang`. For a deep link, read `location.search` and pass the id through.

This is the only view of the four with a per-dish selection, and the only one using the fixed
panel mode — it renders into `#dossier` in the right-hand grid column. An overlay panel here
covers the thread labels it describes. The `.orbit-grid` is
`minmax(0, 1fr) 312px`; below 760px it folds to one column and `.dossier` takes a fixed 380px
height.

The dish rail is a horizontal scroll container. Its known problem, and the alternative, are in
Known limitations below.

### 05 Timeline Waves

The span is `YEAR0 = 1786` to `YEAR1 = 2026`, hardcoded, with `#scrub` bounded to match. The
playhead advances on a `d3.timer` and wraps at `YEAR1`. Auto-play is suppressed under
`prefers-reduced-motion`, so a host must not assume motion has started.

Left margin is responsive in script rather than CSS — `M.left` is 118 below 640px wide and 172
above — because the era labels sit in it.

Dishes with no defensible date appear in a band below the axis rather than being placed at a
guessed year. Any reworking of this view needs to keep that band, or the view starts asserting
dates the sources do not support.

## Porting the landing page

`mee-search.html` is built to be lifted into a site template. It is one `<style>` block and
one `<main>`, with inline SVG thumbnails, no JavaScript and no data load. Every class is
prefixed `.ms-`, so the block drops into an existing stylesheet without collisions.

What to change on the way in:

- **Drop the Google Fonts links** and the token declarations. The site already loads Fraunces
  and Source Sans 3 and already declares `--bg`, `--text`, `--muted`, `--line`, `--accent`,
  `--surface`, `--line-soft` and `--stage-bg`. The page reads those names and nothing else.
- **Confirm six URLs.** The topbar back link, the "the diary" link in the dek, and the four
  card `href`s. The card links currently point at sibling files
  (`./02-origin-drill.html` and so on) and need to point at wherever the views are served.
- **Keep the four counts and `graph-stats.json` in step.** They are literals in the markup,
  each tagged `data-count="dish|culture|region|sources"`. `tests/landing.js` reads the stats
  file and fails on any mismatch, so a data rebuild that changes a count will fail the test
  rather than ship a wrong number.

Three details in the markup that are deliberate:

- **The four calls to action differ** — `Start drilling`, `Open a bowl`, `Follow a thread`,
  `Walk the timeline`. Four identical links give a screen-reader user four indistinguishable
  items in a link list.
- **The "Start here" badge is absolutely positioned.** In the flow it pushes Bowl Orbit's
  thumbnail out of line with the card beside it. Any further badges want the same treatment.
- **Thumbnails are `aria-hidden` with `role="presentation"`.** They carry no information the
  heading and copy do not.

Breakpoints are 760px, where the counts fold to two columns, and 460px, where the cards go to
one. Hover transitions are named individually and collapse under `prefers-reduced-motion`.

## Invariants the code depends on

Each of these is silent when broken: the view still renders, and the output is wrong.

### Radial angles

`d3.arc()` measures angles from 12 o'clock, clockwise. `Math.cos` and `Math.sin` measure from
3 o'clock, counter-clockwise. Mixing them puts every label 90° away from the arc it names,
which presents as a hover highlighting the wrong item. For a d3 angle `t`, the screen offset
from the centre is:

```js
x =  Math.sin(t) * r;
y = -Math.cos(t) * r;
```

The bearing in the other direction, which the tests use, is `Math.atan2(x - cx, -(y - cy))`.

Both radial views start their rings at 12 o'clock and read clockwise, matching the order of
the chips in the dossier.

### Labels in radial views

**Never rotate label text to follow an arc.** Tangential text reads vertically at the sides of
a circle. View 04 places thread names outside the ring as horizontal text with the breakdown
in a list beside the stage. View 02 uses horizontal text where a wedge is wide enough, and
radial text — outward along the radius, one consistent direction — only where nothing else fits.

**Wrap rather than truncate.** An orbit has vertical room when it has no horizontal room, so
view 04's satellite labels break onto two lines. "Coagulated pig's / blood" is a label;
"Coagulated pig's blo…" is not. Only long technique names are cut, and the tooltip carries the
full text.

So the radius is the box minus the width of the labels outside the ring, not a circle
inscribed in the box:

```js
SIDE = W < 620 ? Math.max(56, W * 0.17) : 116;
R = Math.min(W / 2 - SIDE, H / 2 - 42);
```

`SIDE` scales down on narrow screens, and thread labels truncate harder to match. A flat 116px
reserve at 390px wide gives `R = 79`, a circle smaller than its own caption.

Every thread is labelled, down to a 2% share, so neighbouring small slices are decluttered:
each side's labels are pushed apart vertically by at least 15px, then the column is pulled
back inside the stage.

### The hub is sized to its text

View 04's centre circle is measured, not fixed. `fitCore()` wraps the title with
`getComputedTextLength`, tries font sizes 17 down to 11 and three lengths of the subtitle, and
takes the first combination that fits. The hub radius is the text's requirement plus 6px,
clamped to `R * 0.3`.

A line's requirement is the far corner of its box, not its half-width. A wide line sitting low
in the circle needs more radius than the same line through the centre:

```js
needR = Math.hypot(w / 2, Math.max(Math.abs(top), Math.abs(bottom)));
```

Because the hub can grow, the orbits derive from it. The first ring sits a constant `0.11 R`
outside the hub and the rest spread to `0.88`. At the smallest hub this gives
`0.34 / 0.62 / 0.88`, so short names look unchanged.

### Absolute positioning inside the panel

`.viz-panel` sets `top: 12px; right: 12px` for the floating mode. Under `position: relative`
those become relative offsets and push the panel 12px down and 12px left of its grid cell, so
`.viz-panel--fixed` resets `inset: auto`. It keeps `position: relative` rather than `static`,
because `.p-fade` is absolutely positioned and needs it as a containing block.

`.p-body` is the scrolling region and needs `flex: 1 1 auto; min-height: 0`, or it sizes to its
content and spills out of the panel. `show()` writes into `.p-body`, never into the panel
element, which would destroy the fade overlay.

`.p-fade` is inset `0`, not `1px`. An absolutely-positioned child is already laid out inside
the border box, and insetting to "clear the border" leaves a 1px strip of live, unfaded text
below the gradient. The gradient must also reach alpha 1: at 0.97 a whole line of text stays
readable through it. The current ramp is 46px tall and opaque by 50%, with a matching 46px
`padding-bottom` on `.p-body` so the last line clears the band at full scroll.

### One animation channel per element

Every highlight eases. An instant opacity swap on mouseover reads as a flinch, especially
where things are already drifting. Two mechanisms, and the wrong one causes bugs:

- **CSS transitions** for hover states nothing else animates, listed explicitly in
  `mee-viz.css` under "hover easing". Never `all`, and never `transform` — the orbit, force and
  particle loops rewrite transform every frame, and a transition fights them into a rubber-band.
- **Named d3 transitions** — `.transition("hot")`, `.transition("hi")` — wherever d3 already
  tweens the same property on the same selection. An unnamed transition cancels the enter/exit
  tween it collides with, so the shape animation breaks the first time the mouse moves. See
  `hotThread()` in 04 and `highlight()` in 01.

Drive one channel per element. `style.opacity` and the `fill-opacity` attribute both apply and
multiply, so 0.9 in each leaves an element at 0.81.

### The dish rail

The rail overflows at every realistic width, so four cues say so:

1. **Edge fades and arrows**, driven by one `data-scroll` attribute on the wrapper — `right`,
   `both`, `left` or `none`, so the visual logic is entirely CSS. `none` hides everything, and
   a rail that fits looks like a row of pills.
2. **A one-time peek**, 26px out and back on a sine hump about a second after load. Skipped
   under `prefers-reduced-motion`.
3. **Arrow buttons** scrolling 75% of the visible width. They overlay the ends, so the rail
   gains matching horizontal padding while scrollable, keeping the first and last pill clickable.
4. **A permanently visible scrollbar** via `::-webkit-scrollbar`.

Chrome discards every `::-webkit-scrollbar` rule the moment either standard property —
`scrollbar-width` or `scrollbar-color` — is present on the element, and falls back to the macOS
overlay scrollbar, which stays invisible until you are already scrolling. The standard
properties are therefore confined to an `@supports (-moz-appearance: none)` block for Firefox.

### d3-force

`d3.forceLink` **mutates** `link.source` and `link.target` from ids into node objects. Code
that looks up `byId[link.source]` after the simulation starts gets `undefined`. Keep your own
node references, and pass ids back explicitly when handing an edge to the panel.

A force layout whose nodes all start at `(0, 0)` cannot recover before alpha runs out. Seed
positions on a golden-angle spiral and call `sim.alpha(1).restart()`.

### Counts come from the data

16 episodes cover 14 distinct dishes: Pan Mee and Koay Teow Th'ng were each eaten twice. Any
control derived from one number and applied to the other silently loses an episode, so scrubber
maxima and button labels read from the dataset rather than from a literal.

## Tests

Headless Chromium via Playwright, in `mee-graph/tests`. Every one of these guards a failure
mode that a render test — one that counts elements and checks for console errors — reports as
a pass.

```bash
cd mee-graph/tests
npm install          # playwright
npx playwright install chromium
npm run all
```

| File | What it asserts |
| --- | --- |
| `landing.js` | `mee-search.html`: counts match `graph-stats.json`, four cards linking to files that exist, distinct calls to action, heading order, keyboard order, no overflow at 390px |
| `check.js` | all 8 pages: no console or page errors, real geometry or canvas ink, still animating after 1s |
| `mob.js` | 390×844: no horizontal overflow, every view draws |
| `interact.js` | 40 control interactions across the views — mode switches, scrubbers, sliders, expand/collapse, replay |
| `panelgeom.js` | the "more" fade sits within 2px of the panel's bottom edge, with the page scrolled and unscrolled |
| `fadebleed2.js` | the bottom 22px of the panel is pixel-identical at two scroll positions |
| `faderamp.js` | the gradient row by row: only the top ~8px lets ink through, at ~30% contrast |
| `align.js` | stage frame and dossier frame agree on all four edges within 1px, at three widths |
| `corefit.js` | every hub text line fits inside the hub circle, with 6px clearance to the first orbit, 14 dishes × 3 widths |
| `ringall.js` | one ring label per thread, each within 40° of its arc's mid-angle, all inside the stage |
| `rail.js` | fades and arrows match scroll position at both ends, arrows move the rail, pills under the arrows stay clickable, a short rail shows no chrome, the peek returns to zero |
| `rich.js` | no literal `**` in rendered prose, and no HTML injection from data fields |
| `ease.js` | hover opacity sampled mid-tween, proving the transition rather than a jump |
| `back02.js` | all five exit routes out of the Origin Drill: centre click, up a level, breadcrumb, back to top, Esc |
| `ep16.js` | the series scrubber reaches the last episode |

Screenshots land in `tests/shots`, which is gitignored.

Two assertions cannot be made in this environment. Headless Chromium uses overlay scrollbars
platform-wide, so an unstyled probe reserves 0px and layout reservation is unmeasurable; and
`getComputedStyle(el, '::-webkit-scrollbar-thumb')` returns the authored value whether or not
Chrome honours it. `rail.js` therefore asserts the source condition — no standard scrollbar
properties on `.dish-rail` — and the rendered scrollbar wants an eyeball on a real Mac.

## Regenerating the data

```bash
cd mee-graph/tools && python3 build_graph.py
```

Writes `../data/noodle-graph.json`, `../data/graph-stats.json` and `../viz/graph-data.js`, and
stamps `graph-data.js?v=YYYYMMDD` on viz HTML. It refuses to write anything if an edge dangles,
an edge type is unknown, a source id is wrong, a dish has no noodle, an episode is not linked to
a dish, a culture has no tone, or a node ends up with no edges.

Bowl Orbit’s **Tasted so far** set is unique dishes from tried episode nodes — not a hardcoded
list. After a Mee publish, add the episode in `tools/src_*.py` and rebuild (charter:
`utilities/penang-pulse/EDITORIAL.md` item 15).

## Accessibility and motion

`prefers-reduced-motion` is honoured throughout: CSS transitions collapse to near zero, the
orbit and the spin stop, the timeline does not auto-play, the rail skips its peek, and the
series path draws instantly. Controls are real `<button>` and `<select>` elements with
`aria-pressed` and labels, and the detail panel is `aria-live="polite"`.

Two things a public page would need, neither built: keyboard movement through the graph itself
(tab between nodes, arrow between neighbours) and a tabular fallback. The data supports both —
`graph-stats.json` plus a table of dishes and their threads covers it.

## Known limitations

- **Horizontal overscroll on the dish rail triggers browser back navigation.** A trackpad swipe
  past the end of the rail chains to the page. `overscroll-behavior-x: contain` on the scroller
  fixes it without affecting back navigation anywhere else on the page; Chrome honours it
  reliably, Safari less so. Replacing the rail with a transform-driven reel removes the scroll
  container altogether and with it the whole class of problem.
- **d3 is vendored** as `./d3.v7.min.js` (see Production notes).
- **`graph-data.js` is 388 KB unminified.**

## Production notes

d3 is vendored as `./d3.v7.min.js` (~280 KB). A custom bundle can reach roughly 90 KB later:
views 01, 06 and 07 need `d3-force`, `d3-selection`, `d3-transition`, `d3-timer` and
`d3-shape`; view 02 needs `d3-hierarchy` and `d3-interpolate`; views 03, 04 and 05 need
`d3-scale`, `d3-shape` and `d3-timer`.

The public Mee-Search landing is emitted by `scripts/build-penang-guides.py` to
`/guides/series/mee-myself-and-i/mee-search/` when the series registry has `"meeSearch": true`.
`mee-search.html` in this folder remains the local/prototype copy (sibling card hrefs for tests).

For `graph-data.js`, in order of preference: gzip it at the CDN, where it compresses to about
90 KB and Firebase Hosting does this automatically; or emit a trimmed build dropping
`contested`, `penangVariation` and the long prose fields the views do not render, which halves
it; or `fetch` `../data/noodle-graph.json` and let the service worker cache it separately from
the page. Bump `CACHE_NAME` and the `?v=` query when you do, following the rest of the shell.
