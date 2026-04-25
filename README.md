# DB Ferry

A tiny static PWA for quickly checking Discovery Bay ferry departures.

## What It Does

- Opens on `Discovery Bay -> Central` by default.
- Shows the next ferry that is still catchable after the selected walk buffer.
- Uses a `10 min` walk buffer by default.
- Supports flipping direction and switching to Mui Wo or Peng Chau.
- Works offline after first load through a service worker.

## Run Locally

```sh
python3 -m http.server 5173
```

Then open `http://localhost:5173`.

For testing on a phone on the same Wi-Fi, use your Mac's local IP address instead of `localhost`. For daily use as an installed PWA, deploy it to an HTTPS static host such as GitHub Pages, Netlify, or Cloudflare Pages, then use "Add to Home Screen" on the phone.

## Schedule Sources

- Central / Discovery Bay: Transport Department Data.gov XLSX, last updated 22 Aug 2025.
- Discovery Bay / Mui Wo: Peng Chau Kai To online timetable, effective date shown as 1 Jul 2022.
- Discovery Bay / Peng Chau: Blue Sea Ferry / Transport Department timetable.

Public holidays are currently included for 2026 from GovHK general holidays. The app has a manual day-type override for unusual service days or missing future holiday data.
