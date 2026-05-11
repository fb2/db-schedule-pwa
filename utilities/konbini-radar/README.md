# Konbini Radar

Konbini Radar is a static, no-login PWA that reads `feed.json` and presents weekly Japan convenience-store new products for English readers.

The generated feed is English-first for UI fields. Japanese originals are retained only in trace fields such as `nameJa` and source URLs so readers can verify the source material.

## Weekly Refresh

Run the Cursor agent workflow in `scripts/konbini-weekly-agent.md`, or run the deterministic steps directly:

```sh
python3 scripts/fetch-konbini-sources.py
python3 scripts/build-konbini-feed.py
python3 scripts/build-konbini-feed.py --publish
```

Draft scrape artifacts are written to `private/konbini-radar/YYYY-MM-DD/` and should not be committed. The public output is `utilities/konbini-radar/feed.json`.

## Images

Thumbnails in `imageUrl` are taken from official listing HTML when available (FamilyMart and 7-Eleven). They are loaded directly from retailer CDNs and may be blocked by privacy tools.

## Translation rules

See `scripts/konbini_translation_guidance.md` for guarded English wording (especially noodle terminology and café drinks).

## Local Test

```sh
python3 -m http.server 5173
```

Open `http://localhost:5173/utilities/konbini-radar/`.

The app is plain static HTML/CSS/JS and is safe to publish from GitHub Pages.
