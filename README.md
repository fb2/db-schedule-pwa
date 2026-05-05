# DB Ferry

A tiny static website with PWAs for Discovery Bay ferry departures and film photography utilities.

## Apps

- `./`: DB Ferry schedule PWA.
- `./utilities/reciprocity-timer/`: film reciprocity calculator and countdown timer PWA.

## Ferry App

- Opens on `Discovery Bay -> Central` by default.
- Shows the next ferry that is still catchable after the selected walk buffer.
- Uses a `10 min` walk buffer by default.
- Supports flipping direction and switching to Mui Wo or Peng Chau.
- Works offline after first load through a service worker.

## Reciprocity Timer

- Select a film stock and enter the metered long-exposure shutter time.
- Shows corrected exposure time, multiplier, and stop compensation.
- Starts a countdown timer for the corrected exposure.
- Uses local static film data from `utilities/reciprocity-timer/films.json`.
- Includes data-quality notes because many color negative films do not have manufacturer-published fixed reciprocity tables.

## Run Locally

```sh
python3 -m http.server 5173
```

Then open `http://localhost:5173`.

For testing on a phone on the same Wi-Fi, use your Mac's local IP address instead of `localhost`. For daily use as an installed PWA, deploy it to an HTTPS static host such as GitHub Pages, Netlify, or Cloudflare Pages, then use "Add to Home Screen" on the phone.

The reciprocity app is available locally at `http://localhost:5173/utilities/reciprocity-timer/`.

## Deploy to GitHub Pages

This repo includes a GitHub Actions workflow that publishes the static app to GitHub Pages whenever `main` is pushed.

After authenticating with GitHub CLI, enable Pages for workflow deployments:

```sh
gh api --method POST /repos/fb2/db-schedule-pwa/pages -f build_type=workflow
```

If Pages is already enabled, update it instead:

```sh
gh api --method PUT /repos/fb2/db-schedule-pwa/pages -f build_type=workflow
```

Then push `main`. The deployed app will be available at `https://fb2.github.io/db-schedule-pwa/` once the workflow finishes.

For ongoing maintenance notes, see `GITHUB_PAGES_MAINTENANCE.md`.

## Schedule Sources

- Central / Discovery Bay: Transport Department Data.gov XLSX, last updated 22 Aug 2025.
- Discovery Bay / Mui Wo: Peng Chau Kai To online timetable, effective date shown as 1 Jul 2022.
- Discovery Bay / Peng Chau: Blue Sea Ferry / Transport Department timetable.

Public holidays are currently included for 2026 from GovHK general holidays. The app has a manual day-type override for unusual service days or missing future holiday data.
