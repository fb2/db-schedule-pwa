# Agent playbook — new Firebase Hosting site (same Google account)

Use this when you need to deploy a **separate Hosting site** under Balazs’s Firebase account, **not** into the default `fb-personal-utilities` (“main” / utilities) site.

This repo already uses multi-site Hosting. Copy that pattern. Do **not** dump a new app into `public: "."` on target `main` unless the user explicitly asks.

## Account & project facts

| Item | Value |
| --- | --- |
| Google / Firebase login | `fbalazs@gmail.com` (same account as existing deploys) |
| Existing Firebase project | `fb-personal-utilities` |
| CLI config in this repo | `firebase.json`, `.firebaserc` at repo root |
| Deploy tool | `npx firebase-tools …` (preferred) or a local `firebase` binary |

### Existing Hosting sites (do not overwrite)

| Deploy target | Hosting site id | Local `public` dir | Default URL |
| --- | --- | --- | --- |
| `main` | `fb-personal-utilities` | `.` (repo root) | `https://fb-personal-utilities.web.app/` |
| `konbini-radar` | `fb-konbini-radar` | `utilities/konbini-radar` | `https://fb-konbini-radar.web.app/` |
| `penang-pulse` | `fb-penang-pulse` | `utilities/penang-pulse` | `https://fb-penang-pulse.web.app/` (+ custom domain) |

**Rule:** a new product gets a **new Hosting site id** + **new deploy target** + **its own local directory**. Never deploy a new product with `--only hosting` (all targets) unless intentional.

---

## 0) Decide the shape (ask if unclear)

Pick one:

**A — New virtual site in the existing project (default)**  
Same project `fb-personal-utilities`, new Hosting site (like Penang Pulse).  
Use when the app is related personal utilities / same billing / shared Firebase Auth/Firestore is OK.

**B — Brand-new Firebase project under the same Google login**  
Use when the user wants isolation (separate billing, rules, or zero risk to existing sites).  
Still log in as `fbalazs@gmail.com`, then `firebase projects:create` / Console create, then Hosting setup.

This playbook focuses on **A**. Section 7 covers **B** briefly.

Collect from the user (or infer carefully):

- Local folder to publish (example: `utilities/my-new-app` or a path outside this repo)
- Deploy target name (kebab-case, example: `my-new-app`)
- Hosting site id (example: `fb-my-new-app` — must be globally unique in Firebase)
- Whether a custom domain is needed later (optional; do after first successful deploy)

---

## 1) Auth — same account, human-in-the-loop

Credentials live on the **Mac user**, not in the agent process. Agents cannot complete browser OAuth alone.

### Check current login

```sh
npx firebase-tools login:list
```

Expect something like: logged in as `fbalazs@gmail.com`.

### Reauth when deploy says credentials are invalid

Ask the **human** to run in their own terminal:

```sh
firebase login --reauth
# or
npx firebase-tools login --reauth
```

Then retry deploy from the agent. Do not invent tokens or commit anything under `~/.config/configstore/`.

### CI / headless (only if user asks)

```sh
npx firebase-tools login:ci
```

Store the token in a secret manager / env (`FIREBASE_TOKEN`). Prefer interactive reauth on this laptop for personal utilities.

### Common friction

- `Authentication Error: Your credentials are no longer valid` → human reauth, then retry.
- `firebase-tools update check failed` / `~/.config` ownership warnings → usually non-fatal; fix with `sudo chown -R "$USER" ~/.config` only if the human agrees.
- Node engine warnings from `npx firebase-tools` on Node 26+ are usually OK if deploy still exits 0.

---

## 2) Create the Hosting site (virtual site)

From the **repo root** (or the project that owns `.firebaserc`):

```sh
npx firebase-tools use fb-personal-utilities
npx firebase-tools hosting:sites:list
```

Create a new site id (must be unique; prefer `fb-<slug>` to match existing naming):

```sh
npx firebase-tools hosting:sites:create fb-my-new-app
```

If create fails because the id is taken, pick another id with the user.

Optional Console path: [Firebase Console](https://console.firebase.google.com/project/fb-personal-utilities/hosting) → add site.

---

## 3) Wire a deploy target (do not use `main`)

### Apply target mapping

```sh
npx firebase-tools target:apply hosting my-new-app fb-my-new-app
```

This updates `.firebaserc` under:

```json
"targets": {
  "fb-personal-utilities": {
    "hosting": {
      "my-new-app": ["fb-my-new-app"]
    }
  }
}
```

Keep existing `main`, `konbini-radar`, and `penang-pulse` entries intact.

### Add a hosting block in `firebase.json`

Append a new object to the `hosting` **array** (this repo uses a list of targets):

```json
{
  "target": "my-new-app",
  "public": "utilities/my-new-app",
  "ignore": [
    "firebase.json",
    ".firebaserc",
    "firestore.rules",
    "**/.*",
    "**/node_modules/**",
    "private/**",
    "scripts/**",
    "**/*.private.json"
  ],
  "headers": [
    {
      "source": "**/*.@(html|webmanifest|js|json|css|svg)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "no-cache"
        }
      ]
    }
  ]
}
```

Notes:

- `public` is the **local directory** uploaded as that site’s `/`. It is not a URL path under `fb-personal-utilities.web.app`.
- If this app lives in **another repo/folder**, either:
  - run Firebase config from that folder, or
  - set `public` to a path relative to this repo’s root after copying/building artifacts here.
- Do **not** point a new target at `public: "."` unless the user wants a full-repo snapshot site.

### Surface check (this repo only)

If the new site’s files live in this DBTravel checkout, update `scripts/check_firebase_hosting_surface.py`:

1. Add required shell files under `REQUIRED_PATHS`.
2. Extend `check_hosting_config` / `check_targets` so the new target + site id are asserted.
3. Run: `python3 scripts/check_firebase_hosting_surface.py`

If the new site is **outside** this repo’s deploy surface, do not weaken the existing check; use a separate Firebase config in that project instead.

---

## 4) Prepare the local directory

Minimum static site:

```text
utilities/my-new-app/
  index.html
  …assets…
```

For PWAs in this monorepo, also follow `.cursor/skills/utility-pwa-scaffold/SKILL.md` (manifest, icon, relative paths, optional SW).

Never host:

- `private/**`
- secrets, tokens, service-account JSON
- raw `media/orig/**` or other gitignored originals unless the user explicitly wants them public

---

## 5) Deploy only the new site

Always scope deploy:

```sh
npx firebase-tools deploy --only hosting:my-new-app
```

Verify:

```sh
curl -I "https://fb-my-new-app.web.app/"
curl -sL "https://fb-my-new-app.web.app/" | head
```

Cite the new site URL to the user. Do **not** tell them to check `fb-personal-utilities.web.app` for this app (that is the other site).

### Safe vs unsafe deploy selectors

| Command | Effect |
| --- | --- |
| `--only hosting:my-new-app` | Deploys **only** the new site (preferred) |
| `--only hosting:penang-pulse` | Only Penang Pulse — leave alone |
| `--only hosting` | Deploys **all** hosting targets in `firebase.json` — avoid unless asked |

---

## 6) Optional custom domain

After the `*.web.app` URL works:

```sh
npx firebase-tools hosting:channel:list   # optional; not required for domains
```

Prefer Console for first-time domain connect:  
Hosting → select **the new site** (not `fb-personal-utilities`) → add custom domain → set DNS as instructed.

Document the canonical public host for the user/agents the same way Penang Pulse uses `https://penangpulse.com/` rather than the `*.web.app` fallback.

---

## 7) Alternative — new Firebase project (same login)

Only when the user wants isolation from `fb-personal-utilities`:

1. Human: ensure `firebase login` / `--reauth` as `fbalazs@gmail.com`.
2. Create project (CLI or Console), example id `fb-something-else`.
3. In the **new app’s repo/folder**:

```sh
npx firebase-tools login:list
npx firebase-tools projects:list
npx firebase-tools use fb-something-else
npx firebase-tools init hosting
# or hand-write firebase.json + .firebaserc
npx firebase-tools deploy --only hosting
```

4. Do **not** point that new project’s config at this repo’s existing `.firebaserc` default without an explicit `firebase use` / project alias. Mixing projects in one checkout is error-prone; prefer a dedicated folder/repo.

---

## 8) Agent checklist (copy/paste)

```text
[ ] Confirmed: new virtual site (not main / not fb-personal-utilities web.app root)
[ ] Human login OK: npx firebase-tools login:list → fbalazs@gmail.com
[ ] firebase use fb-personal-utilities
[ ] hosting:sites:create fb-<slug>
[ ] target:apply hosting <target> fb-<slug>
[ ] firebase.json hosting entry: target + public dir + ignores
[ ] .firebaserc keeps existing targets untouched
[ ] Local public dir has index.html (and app shell if PWA)
[ ] Updated check_firebase_hosting_surface.py if inside this repo
[ ] Deploy: npx firebase-tools deploy --only hosting:<target>
[ ] Verified https://fb-<slug>.web.app/
[ ] Told user the new site URL (and custom domain plan if any)
[ ] Did not deploy --only hosting (all targets) by accident
```

---

## 9) Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Auth errors on deploy | Expired CLI session | Human: `firebase login --reauth` |
| Deploy updated the wrong URL | Used `main` or bare `--only hosting` | Deploy `--only hosting:<target>`; check `.firebaserc` mapping |
| Site create fails | Site id taken / invalid | Choose another `fb-…` id |
| Predeploy script fails | `check_firebase_hosting_surface.py` | Fix missing files or config assertions |
| Files missing on site | Wrong `public` path / ignore rules | Confirm relative path from repo root; check `ignore` |
| “Logged in” but deploy still auth-fails | Stale token despite login:list | Human reauth again; retry deploy immediately after |

---

## 10) What not to do

- Do not change `main` → `public` away from `.` unless explicitly requested.
- Do not remap `penang-pulse` / `konbini-radar` site ids.
- Do not commit Firebase refresh tokens or `login:ci` tokens.
- Do not run `firebase login --reauth` as a non-interactive agent step and pretend it succeeded.
- Do not use GitHub Pages as a substitute when the user asked for a Firebase Hosting site with its own `*.web.app` (or custom) host.
