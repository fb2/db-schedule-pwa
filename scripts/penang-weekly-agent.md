# Penang Pulse Weekly Agent

Use this runbook in Cursor once a week (Sunday evening MYT) to refresh the public Penang Pulse feed. Fetch/build scripts are deterministic; the agentic part is source-grounded editorial review and publication.

## Goal

Create `utilities/penang-pulse/feed.json` from configured Penang web sources: events for the next ~2 weeks, new food/popup openings, and worth-revisiting restaurant write-ups.

## Feed schema (`kind`)

Items use a single `kind` field (no separate bucket/tag):

| `kind` | UI section | Meaning |
|--------|------------|---------|
| `event` | Happening soon / Upcoming later | Dated happenings |
| `food` | Food & popups | New openings / popups (freshness: **≤ ~2 months**) |
| `revisit` | Worth revisiting | Reviews / guides / interesting restaurants (older OK) |

Parsers map openings → `food` and review-like pieces → `revisit` via title/summary hints. Build drops stale `food` items older than ~62 days using `startDate` / `publishedAt` / date text; `revisit` is not age-gated. The app also safety-filters Food & popups the same way.

### Event ranking (Happening soon)

Build tags consumer `topics` / `interest` from title+summary keywords (EN + common MS/ZH): family, festival, fair, literary, food, music, culture, movies, books, gaming. Each event gets an `interestScore`; feed sort for `kind=event` is **score desc, then startDate, then title** so the app’s Happening soon list (feed order) surfaces those priorities first.

Industry / trade / B2B / corporate expos (e.g. Halal industry, PIHEX, professional conferences) are **hard-dropped** from the public feed or **soft-demoted** (−45 score) when expo/summit language pairs with industry/trade context. Consumer travel/food/culture fairs are not demoted. Prefer tuning keyword rules in `build-penang-feed.py` over hand-editing `feed.json`.

Header fields:

- `weekLabel`: human date like `Week of 19 Jul` (not ISO)
- `intro`: short count summary **without** repeating “Week of …” (e.g. `24 events and 15 food picks.`)

## Constraints

- No login, API keys, or Meta (Instagram/Facebook) scraping in v1.
- Do not publish raw scrape artifacts. They belong under `private/penang-pulse/` (gitignored).
- Prefer parser/config fixes over hand-editing `feed.json`.
- Keep summaries short and source-grounded. Link to the original post.
- Fail closed on `--publish` unless sanity checks pass (or `--force-publish` after manual inspection).
- Prefer keeping the previous public feed when a new draft fails quality gates.
- Images: prefer usable hotlinkable URLs. PenangToday RSS `/wp-content/uploads/` often soft-404s — build enriches from article `og:image` (`/ipsostuh/`). UI uses `<img referrerPolicy="no-referrer">` (same pattern as Konbini Radar). SW must not cache opaque cross-origin images.

## Weekly Steps

1. Fetch sources:

   ```sh
   python3 scripts/fetch-penang-sources.py
   ```

   Optional sources fail soft (non-blocking). Required failures are warned but do not abort fetch.

2. Build a draft feed:

   ```sh
   python3 scripts/build-penang-feed.py
   ```

3. Review the newest `private/penang-pulse/YYYY-MM-DD/` folder:

   - `fetch-manifest.json` for failed/tiny fetches
   - `feed.draft.json` warnings and item quality
   - Dates/labels look sane; Food & popups are openings (not May holiday leftovers / hygiene noise)
   - Worth revisiting holds reviews/guides
   - Intro summarizes the week without invented claims
   - Many items should have working `imageUrl`s

4. If needed, fix parsers or `scripts/penang_sources.json` and rebuild.

5. Publish:

   ```sh
   python3 scripts/build-penang-feed.py --publish
   ```

6. Local check:

   ```sh
   python3 -m http.server 5173
   ```

   Open `http://localhost:5173/utilities/penang-pulse/`.

7. Commit public app/feed/script changes only (never `private/`). Push `main` for GitHub Pages.

8. Publish the production custom domain. GitHub Pages deploys `https://fb2.github.io/db-schedule-pwa/utilities/penang-pulse/`, but `https://penangpulse.com/` and `https://fb-penang-pulse.web.app/` are served by Firebase Hosting target `penang-pulse`.

   ```sh
   npx firebase-tools deploy --only hosting:penang-pulse
   ```

9. Verify both live Firebase surfaces serve the new feed metadata:

   ```sh
   python3 - <<'PY'
   import json, urllib.request
   for url in [
       "https://fb-penang-pulse.web.app/feed.json",
       "https://penangpulse.com/feed.json",
   ]:
       with urllib.request.urlopen(url, timeout=20) as resp:
           feed = json.load(resp)
       print(url, resp.status, feed["weekLabel"], feed["generatedAt"], len(feed["items"]))
   PY
   ```

## Source tiers

Configured in `scripts/penang_sources.json` (`tier`: A/B). Optional sources may fail without blocking publish if sanity still passes.

### Tier A (primary)

- PenangToday Events / Food (RSS)
- Hin Bus Depot (HTML)
- The Smart Local new cafes (HTML)
- George Town Festival (HTML, optional)
- China Press Penang 吃喝玩乐 (HTML → mostly `revisit`)
- myPenang Events (HTML)
- Penang Foodie home (HTML; `/feed/` often 403 → openings `food`, guides `revisit`)

### Tier B (optional / variety)

- SmartDory (HTML → mostly `revisit`)
- Penang Hyperlocal (RSS)
- Buletin Mutiara (RSS)

### Manual scout only

- **Common Ground Penang** (Moulmein Rise / Pulau Tikus coworking): no public scrapable event calendar on their site. Member events go through the CG app; venue hire is enquire-only. Third-party events (e.g. mixers) appear on Eventbrite/AllEvents under the venue name — do not automate Instagram/Facebook. Scout manually when relevant.

## Editorial Guides (separate from weekly feed)

Guides are hand-written posts, not scrape output. They appear as a quiet strip under the home header and open at `/guides/<slug>/` on **https://penangpulse.com**.

Full charter + URL scheme: `utilities/penang-pulse/EDITORIAL.md`.

### Layout

- Source (not hosted): `utilities/penang-pulse/guides/posts/<slug>/post.md` + `media/orig/` (gitignored) + `_series.json` registry
- Built (deployed): `utilities/penang-pulse/guides/index.json`, `guides/<slug>/index.html`, `guides/series/<series-slug>/`

### Edit → build → deploy

1. Local series-aware editor (not on Firebase):

   ```sh
   python3 scripts/penang-guides-editor/server.py
   ```

   Open `http://127.0.0.1:8765/` — Series desk → series detail → New episode. Setup: `scripts/penang-guides-editor/README.md` (Pillow venv).

2. Build static pages + strip index (emits registered series even with 0 posts):

   ```sh
   scripts/penang-guides-editor/.venv/bin/python scripts/build-penang-guides.py
   ```

3. Local preview: `python3 -m http.server 5173` → `/utilities/penang-pulse/`.

4. Deploy production custom domain:

   ```sh
   npx firebase-tools deploy --only hosting:penang-pulse,hosting:main
   ```

   Firebase ignores `guides/posts/**`. Commit built `guides/<slug>/`, `guides/series/`, + `guides/index.json` with the app when saving.

Stars stay on feed cards only — guide pages have no star toggle.
