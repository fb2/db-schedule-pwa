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

**Canonical host:** [https://penangpulse.com](https://penangpulse.com/)

**Alternate host** (same Firebase target; use when corp filters block `.com`):  
[https://fb-penang-pulse.web.app](https://fb-penang-pulse.web.app/)

Pathnames are identical on both hosts. Prefer `.com` in writing, shares, and agent-facing citations.

| Path | What |
| --- | --- |
| [`/`](https://penangpulse.com/) | Home — weekly pulse + Guides strip |
| [`/feed.json`](https://penangpulse.com/feed.json) | Weekly feed data |
| Guides strip on home | Links into posts (no separate public guides landing required) |
| [`/guides/<slug>/`](https://penangpulse.com/guides/lean-huat-hokkien-mee/) | Single Guide post |
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
| Example episode | https://penangpulse.com/guides/lean-huat-hokkien-mee/ |
| fb- home fallback | https://fb-penang-pulse.web.app/ |
| fb- Mee series fallback | https://fb-penang-pulse.web.app/guides/series/mee-myself-and-i/ |

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
fieldNote: Field note · Pulau Tikus · Jul 2026
```

### Naming conventions

| Thing | Convention |
| --- | --- |
| Series slug | kebab-case, stable forever (`mee-myself-and-i`) |
| Post slug | kebab-case from venue/topic (`lean-huat-hokkien-mee`) |
| Series title | Title Case, human voice |
| Episode title | Venue or answer-shaped topic — not “Episode 3” |
| `seriesOrder` | Dense integers starting at 1; reorder by editing the field |

Standalone Guides omit `series` / `seriesTitle` / `seriesOrder`.

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

## Tooling pointers

| Need | Where |
| --- | --- |
| Weekly feed agent | `scripts/penang-weekly-agent.md` |
| Local Guides CMS | `scripts/penang-guides-editor/` → http://127.0.0.1:8765/ |
| Series registry | `utilities/penang-pulse/guides/posts/_series.json` |
| Build Guides | `scripts/build-penang-guides.py` |
| App README | `utilities/penang-pulse/README.md` |
