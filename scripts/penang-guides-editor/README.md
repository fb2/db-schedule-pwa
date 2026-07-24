# Penang Pulse Guides Editor (local only)

Series-aware mini CMS for editorial Guides. **Not deployed** to Firebase or GitHub Pages.

Charter + public URL scheme: [`utilities/penang-pulse/EDITORIAL.md`](../../utilities/penang-pulse/EDITORIAL.md).

## Setup (once)

Pillow is required for the image build step:

```sh
python3 -m venv scripts/penang-guides-editor/.venv
scripts/penang-guides-editor/.venv/bin/pip install Pillow
# optional HEIC support:
# scripts/penang-guides-editor/.venv/bin/pip install pillow-heif
```

## Run

From the repo root:

```sh
python3 scripts/penang-guides-editor/server.py
```

Open [http://127.0.0.1:8765/](http://127.0.0.1:8765/).

Restart the process after pulling CMS changes (stdlib server — no auto-reload).

## Save vs Save & build vs Publish

| Action | What it does |
| --- | --- |
| **Save** | Writes `post.md` + media locally. Syncs tasting date → `fieldNote` / `updated` / series order. |
| **Save & build** | Save, then runs `scripts/build-penang-guides.py` for **all** guides + series indexes + `index.json` (local only — not selective per slug). |
| **Publish** | Confirm → full guides build → `git add` guide paths → commit (env author) → `git push origin main` (best-effort) → `npx firebase-tools deploy --only hosting:penang-pulse` (**entire** penangpulse.com app surface, not a single-article CDN publish). |

**Strategy in one line:** Save & build is local and rebuilds everything; Publish commits pending guide paths and deploys all of [penangpulse.com](https://penangpulse.com/).

- Refuses Publish while the anchor episode is `draft: true`.
- UI: series page has one quiet **Publish to penangpulse.com** (actions bar); episode editor has Publish after writing. No per-row Publish buttons.
- Commit author via env only (never `git config`): `Balazs Fejes` / `fbalazs@gmail.com`.
- If push fails (auth / approval), deploy still runs and the result page notes **`PUSH_SKIPPED`**.
- Live URL shown as `https://penangpulse.com/guides/<slug>/` (not `*.web.app`).

## Series workflow

1. **Desk** (`/`) — registered series from `guides/posts/_series.json`; open a series card.
2. **Series page** — clean episode rows (`#order`, tasting date, Edit); one series-level Publish when a non-draft episode exists.
3. **Create** — title → kebab slug preview; set **Tasting date**; Create.
4. **Editor** — tasting date, series picker, draft, slug rename, Maps paste, photo intake with roles, sibling sidebar; Publish for that slug when not draft.
5. Write → **Save** / **Save & build** locally → uncheck Draft → **Publish** when ready.
6. Optional local preview: `python3 -m http.server 5173` → `/utilities/penang-pulse/`.

Registered by default: **Mee Myself and I**, **Family Matters**.

Built output (safe to commit): `guides/index.json`, `guides/<slug>/`, `guides/series/<slug>/`, `guides/article.css`.

Source posts under `guides/posts/` are ignored by Firebase Hosting (including `_series.json` — source only).

## 1) Tasting date → seriesOrder

- Editor/create **Tasting date** (`type=date`) persists as front matter `tasted: YYYY-MM-DD`.
- On save/create, syncs:
  - `fieldNote` → `Field note · {neighbourhood} · 23 Jul 2026` (neighbourhood omitted from the middle when empty)
  - `updated` → tasting date when set
- For posts in a series, **all episodes** get dense integer `seriesOrder` recomputed:
  - Sort by tasting date ascending (oldest = 1)
  - Same-day tie-break: existing `seriesOrder`, then slug
- Order is auto-only in the UI (shown as computed; not manually edited).
- Old posts without `tasted`: inferred when opened/saved from day-precise `fieldNote`, else `updated`, else month-only `fieldNote` (day 1).

## 2) Smart photo intake

On upload, pick a role per file:

| Role | Filename |
| --- | --- |
| Hawker / seller | `{slug}-seller.jpeg` |
| Dish / bowl | `{slug}-bowl.jpeg` |
| Author | `{slug}-author.jpeg` |
| Other (freeform) | `{slug}-{label}.jpeg` |

- Collisions get `-2`, `-3`, …
- Appends into `## Photos` (creates the section if missing) in editorial order: seller → bowl → author → other
- Markdown shape: `![Alt](./media/orig/…)` + `_Caption._` stub (matches EDITORIAL.md)
- Skips append if that `./media/orig/…` link already exists in the body

## 3) Publish handoff

Server endpoint `POST /publish` (editor, or series actions bar with `intent=series`):

1. Refuse if the anchor slug is draft
2. Sync tasting / series order, run **full** guides builder (all guides)
3. `git add` guide-related paths (`guides/posts/<touched>`, built `guides/<slug>/`, `guides/index.json`, `guides/series/…`)
4. Commit with `Publish <title> guide.` (or `Publish <series> series guides.` from the series page); skip if nothing staged
5. `git push origin main` — continue on failure (`PUSH_SKIPPED`)
6. `npx firebase-tools deploy --only hosting:penang-pulse` — whole host target
7. Result page with step logs + live URL

Requires local git credentials for push and Firebase CLI login for deploy. This CMS is trusted/local-only and shells out from the repo root.

## Drafts, rename, delete

- **Draft** — `draft: true`; build skips public HTML / index / series listing. CMS still lists them.
- **Rename slug** — edit Slug + Save. Moves `guides/posts/<old>/` → `guides/posts/<new>/`.
- **Delete episode** — danger zone; confirm removes the posts folder.

## Maps URL paste behaviour

| URL shape | Behaviour |
| --- | --- |
| `maps.app.goo.gl/…` or `goo.gl/maps/…` | Stored as-is. Fill **Venue name** yourself. |
| `google.com/maps/place/Name/@lat,lng…` | May fill name + lat/lng from the string. |
| `google.com/maps/?q=…` / `query=` | May fill name or coords from the query. |

No API keys / no short-link resolution.

## Front matter extras

```yaml
tasted: 2026-07-23
series: mee-myself-and-i
seriesTitle: Mee Myself and I
seriesOrder: 1          # auto from tasting date
type: series-mee
draft: true             # optional — CMS only
fieldNote: Field note · George Town · 23 Jul 2026
location:
  name: Venue name
  mapsUrl: https://maps.app.goo.gl/...
  address: optional
  lat: optional
  lng: optional
```

Add or edit series metadata in `utilities/penang-pulse/guides/posts/_series.json`.

## Media tips

- Prefer seller/stall shot first, then dish (CMS role order does this).
- Captions: `_Caption text._` on the line after the image (blank line OK).
- Body photos keep natural aspect ratio after build — no forced 3:2.
- Confirm the open editor slug before pasting a full episode.
