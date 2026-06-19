---
name: utility-pwa-scaffold
description: Scaffold and maintain static utility PWAs in the DBTravel repo. Use when creating a new utility app, adding a Firebase-backed private utility, updating utility links, adding a PWA shell, or changing Firebase Hosting deploy surfaces.
---

# Utility PWA Scaffold

Use this skill for any new app or utility in this repo.

## First Decisions

Confirm or infer these choices before editing:

- URL placement: root path like `travel/`, nested path like `utilities/name/`, or separate Firebase Hosting target.
- Visibility: listed on `utilities/index.html`, listed in the DB Ferry footer, hidden, or dedicated URL only.
- Access: public read-only, Google-auth private, Firestore-backed private, Storage-backed private, or imported static data.
- Offline behavior: installable PWA shell only, or public data cached too. Never cache private Firestore data in a service worker.

Default to `utilities/name/` for public utilities and root path only when the user explicitly wants a short URL such as `/travel/`.

## Required Files

Every installable utility should have:

- `index.html`
- `app.js`
- `styles.css`
- `manifest.webmanifest`
- `icon.svg`
- `sw.js` when a PWA/offline shell is useful

Keep paths relative, for example `./app.js`, `./styles.css`, and `./icon.svg`.

For app shell changes, bump:

- script/style query strings in `index.html`
- `CACHE_NAME` in `sw.js`
- cached asset URLs in `sw.js`

## Firebase Patterns

For private or DB-backed utilities:

- Load config with `fetch("/__/firebase/init.json", { cache: "no-store" })`.
- Use Google Auth with `GoogleAuthProvider`.
- Put allowlisted emails and access checks in `firestore.rules`, not front-end JS.
- Use narrow Firestore collections/rules for the utility.
- Deploy Firebase Hosting for DB-backed utilities; GitHub Pages is not enough.

Avoid storing private data in service worker caches, localStorage, or IndexedDB unless the user explicitly accepts the risk.

## Mandatory Updates

When adding, removing, renaming, or moving a utility:

1. Update `utilities/index.html` with the app link, description, and public/private badges.
2. Update `scripts/check_firebase_hosting_surface.py` so Firebase deploys fail if the app shell is missing.
3. Update `firebase.json` / `.firebaserc` only if a new hosting target is needed.
4. Update `firestore.rules` only if the app needs Firestore access.
5. Do not add hidden/private data files to hosting. Respect `private/**`, `scripts/**`, and secret ignores.
6. Commit and push tracked source files after deploy when the user asks to save or publish changes.

## Verification

Run these before deploying:

```sh
python3 scripts/check_firebase_hosting_surface.py
node --check path/to/app.js
```

For Firebase-backed apps, deploy and verify live URLs:

```sh
npx firebase-tools deploy --only hosting
npx firebase-tools deploy --only firestore:rules
curl -I https://fb-personal-utilities.web.app/<path>/
```

Only deploy Firestore rules when rules changed.

## Current Utility Surface

- Root DB Ferry app: `/`
- Utility index: `/utilities/`
- Travel Plans: `/travel/`
- Recipe Book: `/utilities/recipe-book/`
- KCRW Tracklists: `/utilities/kcrw-tracklists/`
- Expense Helper: `/utilities/expense-helper/`
- Reciprocity Timer: `/utilities/reciprocity-timer/`
- Konbini Radar: `/utilities/konbini-radar/` and `https://fb-konbini-radar.web.app/`
