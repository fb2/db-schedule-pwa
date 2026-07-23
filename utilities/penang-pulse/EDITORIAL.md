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
| [`/guides/series/<series-slug>/`](https://penangpulse.com/guides/series/mee-myself-and-i/) | Series index (episodes in order) |
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
| `seriesOrder` | Dense integers starting at 1; reorder by editing the field |

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

Idempotent checklist from the first Mee Myself and I episode (Kolo Mee / C-Mee-PO):

1. **Write in the correct episode slug** — CMS Save always targets the open `/edit?slug=…`. Creating `kolo-mee` then editing another draft (e.g. a sample) pastes content into the wrong folder. Prefer one open editor tab per episode.
2. **Draft → Build → Deploy are three steps** — CMS **Build** only regenerates local `guides/<slug>/` + `index.json`. It does **not** update `https://penangpulse.com`. After unchecking Draft: Save & build → commit → `npx firebase-tools deploy --only hosting:penang-pulse`.
3. **Media filenames** — no spaces in `media/orig/` basenames (markdown links break otherwise). CMS uploads are kebab-cased on save. Prefer descriptive names (`kolo-mee-bowl.jpeg`, `kolo-mee-seller.jpeg`).
4. **Captions** — put `_Caption text._` on the line after `![alt](./media/orig/…)`. A blank line between image and caption is OK (build skips it). Underscores are stripped into `<figcaption>`; if the caption is not detected, `_…_` can leak into body copy.
5. **Photo aspect** — body photos keep natural aspect ratio (no forced landscape crop). Portrait stall shots need faces/menus intact; dish crops tolerate 3:2 less often. See `guides/article.css` `.photo-block img`.
6. **C-Mee-PO dialogue** — label only the assistant (`**C-Mee-PO:**`). When he asks a question, keep that label on the question line, then answer in plain first person — no `Me:` and no extra `### First bites` heading unless the section truly needs one. After a lore brief, never jump straight into tasting — end with an attributed cue (`How are you finding it?` / short equivalent) so the handoff is visible.
7. **Sample vs real episodes** — do not keep auto-generated venue samples once real episodes exist; delete the sample post and renumber `seriesOrder`.
8. **Series mark (B masthead)** — Mee Myself and I uses `guides/marks/mee-myself-and-i.svg` via the registry `mark` field (series index masthead + episode series row). Other series stay text-only unless they get their own mark. Wireframes: [`wireframes/guides/series-mark-mee.html`](./wireframes/guides/series-mark-mee.html).
9. **Share previews (OG)** — Guide/series HTML gets Open Graph + Twitter Card tags from `scripts/build-penang-guides.py`. `og:image` prefers the first guide photo (absolute `https://penangpulse.com/guides/…/media/….jpg`); otherwise `https://penangpulse.com/og-default.jpg` (JPEG — WhatsApp won’t use SVG). Rebuild after photos change so crawlers see the new image URL.
10. **Caching after publish** — Firebase serves HTML/`index.json`/`feed.json`/`sw.js` with `max-age=0, must-revalidate`. The PWA service worker is **network-first** for navigations, guide HTML, `guides/index.json`, and `feed.json` (shell assets stay offline-capable). After deploy, returning visitors should see new Mee episodes without hard-refresh fights; bump `CACHE_NAME` + `?v=` on shell changes.

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
