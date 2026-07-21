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
3. **Editor** — series picker, field note, Maps paste + spot preview, media upload, sibling episodes in the sidebar.
4. Set `seriesOrder` to reorder (lower first), then **Save & build**.
5. Preview: `python3 -m http.server 5173` → `/utilities/penang-pulse/`.
6. Deploy production (after commit/push — not done by the editor):

   ```sh
   npx firebase-tools deploy --only hosting:penang-pulse,hosting:main
   ```

Registered by default: **Mee Myself and I**, **Family Matters** (empty OK — build still emits the series index).

Standalone guides: **New standalone guide** on the desk (series = None).

Built output (safe to commit): `guides/index.json`, `guides/<slug>/`, `guides/series/<slug>/`, `guides/article.css`.

Source posts under `guides/posts/` are ignored by Firebase Hosting (including `_series.json` — source only).

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
fieldNote: Field note · George Town · Jul 2026
location:
  name: Lean Huat Hokkien Mee
  mapsUrl: https://maps.app.goo.gl/...
  address: optional
  lat: optional
  lng: optional
```

Add or edit series metadata in `utilities/penang-pulse/guides/posts/_series.json`.
