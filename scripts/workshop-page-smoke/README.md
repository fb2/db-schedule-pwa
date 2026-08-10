# Workshop page smoke test

Headless check that `utilities/penang-pulse/workshops/epam-apac-pods-2026/` renders and
behaves on desktop and mobile — including the illustrated map's pins, side POI list, and
popovers.

## Run

```bash
cd scripts/workshop-page-smoke
./run.sh
```

The first run creates `.venv` and downloads Playwright's Chromium + WebKit builds into
`.browsers/` (~850 MB, one time). Both directories are gitignored.

The script starts its own `python3 -m http.server` on a free port with
`utilities/penang-pulse` as the document root, runs the checks, and stops the server
again — nothing needs to be running beforehand.

Screenshots of each viewport:

```bash
./run.sh --keep-screenshots   # writes screenshots/<label>-full.png
```

Exit code is `0` when every check passes, `1` otherwise, so it drops into CI or a
pre-deploy step as-is.

## Coverage

| Viewport | Browser | Size |
| --- | --- | --- |
| `desktop-chromium` | Chromium | 1280×800 |
| `mobile-chromium` | Chromium (mobile emulation, touch) | 390×844 |
| `mobile-webkit` | WebKit | 390×844 |

Each viewport checks:

- Page responds `200`, and `robots` is still `noindex,nofollow` (the page is unlisted).
- Penang Pulse brand links home; the workshop sub-head is the `h1`.
- Hero photo and EPAM logo actually decode (not just present in the DOM).
- Every section renders: welcome, map, tips, what to see, food, team moments, events.
- Practical tips include the auto-gates line and an MDAC link pointing at
  `https://imigresen-online.imi.gov.my/mdac/main`.
- The Mee Myself and I series link is present, and nothing links to `feed.json` /
  `guides/index.json` (the page must stay unlisted).
- Map SVG renders with all 7 pins, the POI list mirrors them, the legend shows, and the
  hotel popover is open on load.
- Clicking each pin opens its popover, with exactly one popover open at a time.
- Clicking each POI list item opens the *matching* popover and marks the item current.
- `Escape` and the popover close button dismiss popovers.
- No horizontal overflow, no broken images, no failed requests, no console errors.

## Notes

- Adding or renaming a map pin means updating `PIN_KEYS` in `smoke.py`.
- The MDAC URL is asserted exactly; if Malaysian Immigration moves the form, update both
  the page and `MDAC_URL`.
