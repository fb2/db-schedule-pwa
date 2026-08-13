# Penang Pulse — Editorial Charter

## Purpose

**Penang Pulse = a local’s weekly planning desk for culture and food — owned field notes + curated happenings — not a tourism brochure.**

Two surfaces, one voice:

| Surface | Role |
| --- | --- |
| **Weekly feed** (`feed.json`) | Curated happenings, openings, revisits — what’s useful *this week* |
| **Guides** | Owned field notes — tasted, walked, dated — that compound over time |

Success is primarily *we plan weekends better*. Audience reach and occasional venue access are secondary side effects, not the north star.

## Audience

1. **Self / family first** — English, practical, opinionated, low fuss  
2. **Locals & long-stay visitors** — same need: “what should we do / eat this week?”  
3. Not: TripAdvisor, Visit Penang, or generic destination SEO

## What we publish

| In | Out |
| --- | --- |
| Consumer events (culture, food, family, festivals, markets, movies, music) | Industry / trade / B2B expos and professional conferences |
| New openings & popups (fresh, local) | PR fluff with no practical planning value |
| Worth-revisiting write-ups (reviews, guides) | Hygiene / admin noise, May holiday leftovers as “food” |
| Owned Guides with maps, neighbourhood, date tasted | Thin listicles scraped from elsewhere |
| Honest caveats (queues, sell-outs, cash-only) | Fake completeness (“best of Penang” encyclopedias) |

Feed ranking preferences (family, festival, fair, literary, food, music, culture) live in `scripts/build-penang-feed.py`. Prefer tuning those rules over hand-editing `feed.json`.

## Cadence

| Stream | Cadence |
| --- | --- |
| Weekly feed | Sunday evening MYT refresh (`scripts/penang-weekly-agent.md`) |
| Guides | When tasted / written — no fake weekly Guide quota |
| Series | Episodes when ready; series index pages stay live even at 0–1 posts |

## Canonical URL scheme

**Public host:** [https://penangpulse.com](https://penangpulse.com/)  
Served by Firebase Hosting target `penang-pulse`. Use this host in writing, shares, Maps-adjacent copy, and agent-facing citations.

| Path | What |
| --- | --- |
| [`/`](https://penangpulse.com/) | Home — weekly pulse + Guides strip |
| [`/feed.json`](https://penangpulse.com/feed.json) | Weekly feed data |
| Guides strip on home | Links into posts (no separate public guides landing required) |
| `/guides/<slug>/` | Single Guide post (published only; drafts skipped) |
| [`/guides/series/<series-slug>/`](https://penangpulse.com/guides/series/mee-myself-and-i/) | Series index (episodes in order) — Pulse width (1120); episode Guides stay narrow for reading |
| [`/guides/series/mee-myself-and-i/mee-search/`](https://penangpulse.com/guides/series/mee-myself-and-i/mee-search/) | Mee-Search landing (culture-graph companion; registry `meeSearch: true`) |
| [`/mee-graph/viz/`](https://penangpulse.com/mee-graph/viz/04-bowl-orbit.html) | Mee-Search viz pages (Bowl Orbit ready; others alpha) |
| [`/guides/index.json`](https://penangpulse.com/guides/index.json) | Machine index of guides + series |
| [`/guides/article.css`](https://penangpulse.com/guides/article.css) | Shared Guide stylesheet |

### Registered series (v1)

| Series slug | Title | Notes |
| --- | --- | --- |
| `mee-myself-and-i` | Mee Myself and I | Noodle / hawker field notes |
| `family-matters` | Family Matters | Weekends & evenings with kids |

Add more by editing `guides/posts/_series.json` and rebuilding. Room for future spines (e.g. rainy evenings, island vs mainland) without changing the URL pattern.

### Examples

| Page | Canonical URL |
| --- | --- |
| Home | https://penangpulse.com/ |
| Mee series | https://penangpulse.com/guides/series/mee-myself-and-i/ |
| Family Matters series | https://penangpulse.com/guides/series/family-matters/ |
| Episode (example) | https://penangpulse.com/guides/kolo-mee/ |

GitHub Pages also mirrors under `/db-schedule-pwa/utilities/penang-pulse/` — useful for repo browsing, not the public brand URL.

## Series framework

A **series** is a durable spine of related Guides. Posts remain standalone URLs; the series page is the ordered index.

### How posts relate

- Post front matter may set `series`, `seriesTitle`, `seriesOrder`
- Build emits `/guides/series/<series-slug>/` and links the series badge on the post
- Registry file `guides/posts/_series.json` lists known series (slug, title, dek, status) so empty or single-episode series still get a public index page

### Front matter

```yaml
series: mee-myself-and-i          # kebab slug; must match registry when possible
seriesTitle: Mee Myself and I     # display title
seriesOrder: 1                    # integer; sort ascending on series page
type: series-mee                  # optional type hint (mee episodes)
draft: true                       # optional — CMS only; build skips publishing
fieldNote: Field note · Pulau Tikus · Jul 2026
```

Posts with `draft: true` stay editable in the local guides CMS but are not emitted to public HTML, `index.json`, or series indexes.

### Naming conventions

| Thing | Convention |
| --- | --- |
| Series slug | kebab-case, stable forever (`mee-myself-and-i`) |
| Post slug | kebab-case from venue/topic (set on create; rename in CMS if needed) |
| Series title | Title Case, human voice |
| Episode title | Venue or answer-shaped topic — not “Episode 3” |
| `seriesOrder` | Dense integers starting at 1, **by tasting date** (oldest first); reorder by editing the field |
| `location` | Required for place Guides — `name` + `mapsUrl` power the spot widget |

Standalone Guides omit `series` / `seriesTitle` / `seriesOrder`.

### Mee Myself and I — C-Mee-PO voice

**Mee Myself and I** episodes may feature **C-Mee-PO**, an AI research assistant character (C-3PO + *mee*). Use him to reuse strong dish/ingredient research (e.g. from Grok) almost as-is, framed as a briefing, with light conversational glue from the human narrator.

**Role split**

| Human narrator (you) | C-Mee-PO |
| --- | --- |
| Where, when, queue, cash, “would I go again” | Dish history, ingredients, regional names, “what am I eating” |
| Taste opinion and venue judgment | Corrective / encyclopedic / dry wit |
| Short setup questions in prose | Dense answer (mostly reused research), then at most one catchphrase |

Penang Pulse stays a **field note**. C-Mee-PO is the **lore track**, not the stall review. Do not let him rate the venue or replace tasting notes.

**Tone:** light pedantry + warmth — protocol droid at a hawker table. Accurate, slightly literal, amused by humans. One joke per beat, then useful fact. Avoid constant sci-fi gags, emoji-robot voice, or comedy-sketch density.

**Attribution (markdown → Guides build)**

- Default: prose setup, then a normal paragraph starting with `**C-Mee-PO:**`
- Long lore dump only: optional `### C-Mee-PO briefs the bowl` (or similar) once per article
- **Never** put C-Mee-PO lines in `>` blockquotes — in this pipeline `>` becomes a practical `.tip` (cash-only / go-early). Keep `>` for real caveats
- First mention in a series episode may gloss once: “C-Mee-PO, my AI research assistant…” — then just the name
- When he asks a question (“How are you finding it?”), keep the `**C-Mee-PO:**` label on that line, then answer in plain first person — no `Me:` label. The article voice is already you; only the assistant needs a name tag.
- **Dialogue handoff** — the tasting block must never follow a lore paragraph without an attributed C-Mee-PO cue (e.g. `**C-Mee-PO:** How are you finding it?`) or a clear section break. Readers need a marked transition when the human narrator takes over.

**Examples**

```markdown
I asked C-Mee-PO what I was actually eating.

**C-Mee-PO:** [research summary, mostly as-is]

I’d eat that if I had a mouth!
```

```markdown
“That green tasted like seaweed.”

**C-Mee-PO:** You must be human-hallucinating. That’s *sayur manis*
(mani cai / sweet leaf / Sabah vegetable) — …
```

**Catchphrase bank** (rotate; ~1 per article, 2 only if one is a correction beat)

| Phrase | When |
| --- | --- |
| *I’d eat that if I had a mouth!* | Endorsement / envy after a strong bowl |
| *You must be human-hallucinating.* | Soft correction (wrong ingredient guess, etc.) |
| *Not a dinner bowl — unless you want to dream with the Singularity.* | Heavy / fatty / very spicy — **max every 4th–5th article** |
| *My training data agrees.* | Confirming a classic take |
| *Regional nomenclature incoming.* | Before a names dump (Hokkien / Malay / Mandarin) |
| *Texture confirmed: not a hallucination.* | After chew / springiness notes |
| *Query complete. Now you chew.* | End of a research block |
| *I have no mouth, and I must mee.* | Rare Easter egg — once a series at most |
| *Hmm, intriguing — I wish I had taste buds to acquire this data.* | Taste-envy variant when the bowl is unusual / hard to map |
| *Well, that sounds like a great lunch. Hey — can you top up my tokens? Thanks.* | Rare comic closer after a strong lunch endorsement — **use sparingly** |

One-off custom closers in the same dry-wit register are fine (e.g. bib / grave-error style after a messy bowl). Still ~1 catchphrase beat per article; do not stack bank + custom.

Name alternatives considered and rejected for now: Mee-3PO, C-Mee, Protocol Mee. Prefer **C-Mee-PO**.

## AI / agent notes (GEO)

Agents retrieve clear, quotable pages. Write for citation:

- **Answer-shaped titles** — “Hawker lunch near Common Ground”, not “My noodle journey #1”
- **Maps** — always attach a Google Maps URL + venue name when the Guide is about a place
- **Dates tasted** — put month/year in `fieldNote` and/or body (“Jul 2026”)
- **Neighbourhood + proper nouns** — Pulau Tikus, Hokkien mee, kopitiam names
- **Honesty** — queues, sell-outs, cash; agents and humans both need caveats
- **Stable URLs** — don’t rename slugs after publish; add new episodes instead

You are not replacing ChatGPT — you are becoming a **source it prefers** when someone asks about Penang weekends or a specific bowl.

## Distribution (light-touch)

Proportional effort. No growth theater.

1. **Phase 0** — Build for family planning. No growth OKRs.  
2. **Phase 1** — Compound owned content: Mee Myself and I spine + a few planning Guides; keep the weekly feed honest.  
3. **Phase 2** — Quiet shares only when a Guide is good (one chat group, one FB group). Optional weekly “Week of …” pointer to the site — not daily posting.  
4. **Phase 3** — Soft venue/festival intros only after ~10 solid owned pieces + consistent pulse. Invites follow usefulness.

**Don’t over-invest:** competing with Visit Penang on SEO, viral social as the core, newsletters before content exists, “the app everyone installs.”

## Guides publish cycle (learnings)

Idempotent checklist from Mee Myself and I episodes (C-Mee-PO):

1. **Write in the correct episode slug** — CMS Save always targets the open `/edit?slug=…`. Creating `kolo-mee` then editing another draft (e.g. a sample) pastes content into the wrong folder. Prefer one open editor tab per episode.
2. **Draft → Build → Deploy are three steps** — CMS **Build** only regenerates local `guides/<slug>/` + `index.json`. It does **not** update `https://penangpulse.com`. After unchecking Draft: Save & build → commit → `npx firebase-tools deploy --only hosting:penang-pulse` (see agent handoff for push).
3. **`location` front matter** — set `name` + `mapsUrl` (CMS Maps paste) so the spot widget renders. Place Guides without `location` ship without the Spot block.
4. **Media filenames** — no spaces in `media/orig/` basenames (markdown links break otherwise). CMS uploads are kebab-cased on save. Prefer descriptive names (`kolo-mee-bowl.jpeg`, `kolo-mee-seller.jpeg`).
5. **Photo order & captions** — seller/stall first, then dish (when both exist). Put `_Caption text._` on the line after `![alt](./media/orig/…)`. A blank line between image and caption is OK (build skips it). Underscores become `<figcaption>`; if undetected, `_…_` can leak into body copy.
6. **Photo aspect** — body photos keep natural aspect ratio (no forced 3:2 / landscape crop). Portrait stall shots need faces/menus intact. See `guides/article.css` `.photo-block img`.
7. **C-Mee-PO dialogue** — label only the assistant (`**C-Mee-PO:**`). When he asks a question, keep that label on the question line, then answer in plain first person — no `Me:`. After a lore brief, **dialogue handoff is required** before tasting — attributed cue (`How are you finding it?` / short equivalent), never jump straight from research into first-person bites.
8. **Meal time consistency** — dek, `fieldNote`, and body must agree (breakfast vs lunch vs evening). Don’t call it lunch in the dek and breakfast in the tasting.
9. **Research paste hygiene** — strip accidental multi-dish / multi-venue chat dumps when pasting Grok (or similar) into C-Mee-PO. One dish, one brief.
10. **Sample vs real episodes** — do not keep auto-generated venue samples once real episodes exist; delete the sample post and renumber `seriesOrder` by tasting date.
11. **Series mark (B masthead)** — Mee Myself and I uses `guides/marks/mee-myself-and-i.svg` via the registry `mark` field (series index masthead + episode series row). Other series stay text-only unless they get their own mark. Wireframes: [`wireframes/guides/series-mark-mee.html`](./wireframes/guides/series-mark-mee.html).
12. **Share previews (OG)** — Guide/series HTML gets Open Graph + Twitter Card tags from `scripts/build-penang-guides.py`. `og:image` prefers the first guide photo (absolute `https://penangpulse.com/guides/…/media/….jpg`); otherwise `https://penangpulse.com/og-default.jpg` (JPEG — WhatsApp won’t use SVG). Rebuild after photos change so crawlers see the new image URL.
13. **Caching after publish** — Firebase serves HTML/`index.json`/`feed.json`/`sw.js` with `max-age=0, must-revalidate`. The PWA service worker is **network-first** for navigations, guide HTML, `guides/index.json`, `feed.json`, and Mee-Search `graph-data.js`. Shell assets stay offline-capable. After deploy, returning visitors should see new Mee episodes without hard-refresh fights; bump `CACHE_NAME` + `?v=` on shell changes.
14. **Mee checklist sync** — After publishing a Mee Myself and I episode, update `utilities/penang-pulse/MEE-CHECKLIST.md` from published posts (`series: mee-myself-and-i`, not `draft:true`): tick **Tried** (and **Optional revisits** when it’s a clear style revisit). Use `seriesOrder` / tasting date as source of truth; don’t invent tries. Uncheck or remove the matching planning-list line so the checklist doesn’t claim the bowl is still open.
15. **Mee-Search graph** — Bowl Orbit’s “Tasted so far” rail is **not** a hardcoded filter. It lists unique dishes from tried `episode` nodes in `graph-data.js`. After each Mee publish, update the culture graph (edit `src_*.py`, never the JSON), rebuild, then deploy with the Guide:

    1. `mee-graph/tools/src_dishes.py` — `EP("ep-NN-…", …, "d-dish", date=, venue=, postSlug=, seriesOrder=N)` (default status is `tried`). `V()` if the venue is new. Set the dish’s `tryStatus="tried"`.
    2. `mee-graph/tools/src_edges.py` — add `(ep, dish, venue, revisit_or_None)` to `_EPISODES` (emits `of_dish` + `tasted_at`). Add `reference_stall_for` if the venue is new.
    3. `mee-graph/tools/src_sources.py` — `pp-field-<slug>` community source with the live `https://penangpulse.com/guides/<slug>/` URL; cite it on at least one edge or the dish.
    4. Rebuild: `cd utilities/penang-pulse/mee-graph/tools && python3 build_graph.py` — writes JSON, `viz/graph-data.js`, stamps `graph-data.js?v=YYYYMMDD` on viz HTML, and fails if the episode isn’t linked to a dish.
    5. If source/dish/region counts changed, update the literals in `viz/mee-search.html` (the public landing is generated from `graph-stats.json` on the Guides build).
    6. Rebuild Guides (`scripts/build-penang-guides.py`) so the series-hub Mee-Search teaser counts stay in step.
    7. Verify [Bowl Orbit](https://penangpulse.com/mee-graph/viz/04-bowl-orbit.html) “Tasted so far” includes the new dish (scroll the rail — it’s last). Do **not** invent a Mohinga–laksa (or similar) transmission edge; the graph already records refused links.

    Mohinga (ep.17 / Mingalarpar) is the template for an immigrant/cousin bowl that was already a dish node: add episode + venue, flip `tryStatus`, rebuild.

## Agent handoff / session practices

Quick pickup for a fresh agent context working Mee / Guides:

| Topic | Practice |
| --- | --- |
| **Canonical host** | Cite and verify **only** `https://penangpulse.com` — not the Firebase `*.web.app` fallback. |
| **CMS Build ≠ live** | Local build regenerates files; production needs `npx firebase-tools deploy --only hosting:penang-pulse`. |
| **Git push from agents** | Prefer **not** to `git push` when it stalls on approval (“Working…” / zombie). Firebase deploy alone updates production. If commit is done but push skipped, say **`PUSH_SKIPPED`** in the handoff. |
| **Commit author** | Use env for that commit only: `GIT_AUTHOR_NAME='Balazs Fejes' GIT_AUTHOR_EMAIL='fbalazs@gmail.com'` (and matching `GIT_COMMITTER_*`). **Never** `git config`. |
| **Wrong draft** | Confirm `/edit?slug=…` before pasting a full episode. |
| **Stuck Working** | Orphaned approval card after a finished subagent — Stop does not clear it. Dismiss the approval, or archive the agent / start a new chat. |
| **C-Mee-PO** | Full voice rules above; hard rules also in `.cursor/rules/penang-pulse-mee-cmeepo.mdc`. |
| **Mee checklist** | After a Mee publish: sync `MEE-CHECKLIST.md` from published posts (Tried + clear revisits). Part of the handoff — don’t leave the checklist stale. |
| **Mee-Search graph** | After a Mee publish: add `EP()` / venue / `tryStatus="tried"` in `mee-graph/tools/src_*.py`, run `python3 build_graph.py`, rebuild Guides. Bowl Orbit “Tasted so far” reads tried episodes from `graph-data.js` — there is no separate filter list. |
| **Shell refresh** | Any `index.html` / `sw.js` / CSS/JS shell change → bump `CACHE_NAME` and `?v=` together. |

## Tooling pointers

| Need | Where |
| --- | --- |
| Weekly feed agent | `scripts/penang-weekly-agent.md` |
| Local Guides CMS | `scripts/penang-guides-editor/` → http://127.0.0.1:8765/ |
| Series registry | `utilities/penang-pulse/guides/posts/_series.json` |
| Build Guides | `scripts/build-penang-guides.py` |
| App README | `utilities/penang-pulse/README.md` |
| Series mark wireframes | `utilities/penang-pulse/wireframes/guides/series-mark-mee.html` |
| C-Mee-PO agent rule | `.cursor/rules/penang-pulse-mee-cmeepo.mdc` |
| Mee try checklist | `utilities/penang-pulse/MEE-CHECKLIST.md` (sync after each Mee publish) |
| Mee-Search graph | `utilities/penang-pulse/mee-graph/` — `tools/src_*.py` then `python3 tools/build_graph.py` |
