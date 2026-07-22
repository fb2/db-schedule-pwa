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

## Series workflow

1. **Desk** (`/`) — registered series from `guides/posts/_series.json` with episode counts; open a series card.
2. **Series page** (`/series?slug=…`) — episodes in `seriesOrder`; **New episode in this series** pre-fills series fields + template.
3. **Create** — title derives a kebab slug preview (`guides/posts/<slug>/` → live `/guides/<slug>/`); edit the slug before Create.
4. **Editor** — series picker, draft toggle, editable slug (rename), field note, Maps paste + spot preview, media upload, sibling episodes in the sidebar.
5. Set `seriesOrder` to reorder (lower first), then **Save & build**.
6. Preview: `python3 -m http.server 5173` → `/utilities/penang-pulse/`.
7. Deploy production (after commit/push — **not** done by Build):

   ```sh
   npx firebase-tools deploy --only hosting:penang-pulse,hosting:main
   ```

   Verify `https://penangpulse.com/guides/<slug>/`. See [`EDITORIAL.md` → Guides publish cycle](../../utilities/penang-pulse/EDITORIAL.md#guides-publish-cycle-learnings).

Registered by default: **Mee Myself and I**, **Family Matters** (empty OK — build still emits the series index).

Standalone guides: **New standalone guide** on the desk (series = None).

Built output (safe to commit): `guides/index.json`, `guides/<slug>/`, `guides/series/<slug>/`, `guides/article.css`.

Source posts under `guides/posts/` are ignored by Firebase Hosting (including `_series.json` — source only).

## Drafts, rename, delete

- **Draft** — check **Draft** on the editor (writes `draft: true` in front matter). `build-penang-guides.py` skips drafts: no `guides/<slug>/`, not in `index.json`, not on the public series page. CMS still lists them (with a draft badge) so you can copy structure or promote later.
- **Reuse a draft as a writing basis** — open the draft in the CMS, keep it drafted, and create new episodes for real venues (set their slugs on create). Or rename the draft slug when you’re ready to publish that bowl under the correct URL, then uncheck Draft → Save & build.
- **Rename slug** — edit the Slug field and Save. Moves `guides/posts/<old>/` → `guides/posts/<new>/` (lowercase kebab only). Run build to refresh public paths.
- **Delete episode** — danger zone at the bottom of the editor; confirm removes `guides/posts/<slug>/`. Run build afterward to clear stale public HTML.

## Maps URL paste behaviour

On paste or blur of the Maps URL field (also re-checked on save):

| URL shape | Behaviour |
| --- | --- |
| `maps.app.goo.gl/…` or `goo.gl/maps/…` | Stored as-is. No name/coords extracted — fill **Venue name** yourself. |
| `google.com/maps/place/Name/@lat,lng…` | Stores URL; may fill name + lat/lng when present in the string. |
| `google.com/maps/?q=…` / `query=` | Stores URL; may fill name or coords from the query. |

No API keys and no short-link resolution — parsing is URL-string only. Name stays editable after auto-fill.

## Front matter extras

```yaml
series: mee-myself-and-i
seriesTitle: Mee Myself and I
seriesOrder: 1
type: series-mee
draft: true   # optional — CMS only until you uncheck Draft
fieldNote: Field note · George Town · Jul 2026
location:
  name: Venue name
  mapsUrl: https://maps.app.goo.gl/...
  address: optional
  lat: optional
  lng: optional
```

Add or edit series metadata in `utilities/penang-pulse/guides/posts/_series.json`.

## Media tips

- Uploads land in `guides/posts/<slug>/media/orig/` and are renamed to kebab-case (spaces removed).
- In the body: `![Alt](./media/orig/filename.jpeg)` then optional `_Caption._` (blank line between is fine).
- Body photos render at natural aspect ratio after build — shoot portrait when the scene needs it.
