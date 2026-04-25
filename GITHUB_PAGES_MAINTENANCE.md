# Maintaining GitHub Pages

This app is a static PWA hosted on GitHub Pages. There is no server build step and no database. The deployed site is just these files:

- `index.html`
- `styles.css`
- `app.js`
- `schedules.js`
- `manifest.webmanifest`
- `sw.js`
- `icon.svg`

## Normal Update Flow

Yes, you can keep iterating on the project files here in Cursor.

For most changes, edit the files locally, test them, commit, and push to `main`:

```sh
python3 -m http.server 5173
```

Open `http://localhost:5173` and check the app.

When it looks good:

```sh
git status
git add .
git commit -m "Describe the change"
git push
```

The GitHub Actions workflow in `.github/workflows/deploy.yml` runs automatically after every push to `main`. When it finishes, GitHub Pages updates the live site:

```text
https://fb2.github.io/db-schedule-pwa/
```

## Updating Schedules

Most timetable maintenance should happen in `schedules.js`.

After editing schedules:

1. Run the local server.
2. Check each route and direction you changed.
3. Check weekday, Saturday, and Sunday / public holiday views if relevant.
4. Commit and push.
5. Wait for the GitHub Pages action to finish.

Because this is a PWA with a service worker, your phone may briefly keep an older cached version. If the live site looks stale, close and reopen the app, refresh the browser page, or remove and reinstall the home screen app.

## Updating App Behavior

Use these files for typical changes:

- `app.js`: app logic, route switching, countdown behavior, local storage, rendering.
- `schedules.js`: ferry routes, timetable data, source links, public holidays.
- `styles.css`: visual design.
- `index.html`: page structure and metadata.
- `manifest.webmanifest`: installed PWA name, icon, colors, start URL, scope.
- `sw.js`: offline caching behavior.

If you add a new public file that must be deployed, also add it to the copy command in `.github/workflows/deploy.yml`.

If the file should work offline, also add it to the `ASSETS` list in `sw.js`.

## Checking Deployments

To see deployment progress, open the GitHub repo and go to:

```text
Actions -> Deploy to GitHub Pages
```

You can also open the repo from the terminal:

```sh
gh repo view --web
```

If a deployment fails, check the failed workflow log first. For this app, failures are most likely caused by a missing file listed in `.github/workflows/deploy.yml`.

## Ways to Use GitHub Pages

GitHub Pages can publish a site in a few ways:

- GitHub Actions workflow: this repo uses this. It is flexible and explicit.
- Deploy from a branch: GitHub can publish files directly from a branch, often `main` or `gh-pages`.
- User site repo: a special repo named `fb2.github.io` publishes at `https://fb2.github.io/`.
- Project site repo: this repo publishes at `https://fb2.github.io/db-schedule-pwa/`.
- Custom domain: you can point your own domain at the Pages site later.

For this PWA, the current GitHub Actions setup is the right fit.

## Limitations

GitHub Pages only hosts static files. It cannot run backend code, scheduled jobs, server-side APIs, private databases, or scripts that execute on GitHub's servers after deployment.

That means this app is a good fit because all schedule data lives in `schedules.js` and all logic runs in the browser.

If you later want live data, user accounts, push notifications from a server, or automatic schedule scraping, you would need another service such as Supabase, Firebase, Cloudflare Workers, Netlify, Vercel, or a separate API.

## PWA Notes

GitHub Pages provides HTTPS, which is required for service workers and installable PWAs.

The app is deployed under `/db-schedule-pwa/`, so paths should stay relative, like `./app.js` and `./icon.svg`. Avoid hard-coding root paths like `/app.js` unless you also change the deployment setup.

The service worker controls caching. If you change cached files and want to force installed apps to refresh more reliably, update `CACHE_NAME` in `sw.js`, for example from `db-ferry-v1` to `db-ferry-v2`.