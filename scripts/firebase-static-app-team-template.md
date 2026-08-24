# Firebase static app template

Shareable reference architecture for a static web app or PWA hosted on Firebase, with optional Google sign-in and Firestore data.

## Architecture

```text
Browser
  ├─ Firebase Hosting: HTML, CSS, JavaScript, icons, public JSON
  ├─ Firebase Authentication: Google sign-in and user identity
  └─ Cloud Firestore: protected application data
       └─ Security Rules: the real authorization boundary
```

Firebase Hosting serves static files only. Application logic runs in the browser. Firestore is the data service; Authentication identifies the user; Security Rules decide which reads and writes are allowed.

We use two app shapes:

1. **Public static app** — Hosting serves the app and public data files. No login or database is required.
2. **Authenticated data app** — Hosting serves the same kind of static shell, but browser JavaScript signs the user in and reads/writes Firestore.

There is no traditional application server in either shape.

## What belongs where

| Concern | Location |
| --- | --- |
| HTML, CSS, browser JavaScript, icons | Firebase Hosting |
| Public generated feeds or catalogs | Hosting as static JSON |
| User or private application data | Firestore |
| User identity | Firebase Authentication |
| Authorization and allowlists | Firestore Security Rules |
| Offline app shell | Service worker cache |
| Secrets and privileged operations | A trusted backend or secret manager, never the static app |

Do not place private data, service-account files, API secrets, raw imports, or Firebase CLI tokens in the Hosting directory.

## Important security model

The Firebase web configuration is not a secret. Values such as `apiKey`, `projectId`, and `authDomain` identify the Firebase project; they do not authorize Firestore access.

Security must be enforced by:

- Firebase Authentication
- Firestore Security Rules
- App Check where abuse protection is warranted
- A trusted backend for operations that require secrets or Admin SDK privileges

Hiding a button or checking an email in front-end JavaScript is not authorization. A user can bypass the UI and call Firebase directly.

## Project and Hosting layout

One Firebase project may contain multiple Hosting sites:

```text
Firebase project: <project-id>
  ├─ Hosting site: <main-site-id>
  ├─ Hosting site: <public-app-site-id>
  ├─ Hosting site: <another-app-site-id>
  ├─ Authentication
  └─ Firestore
```

This is useful when apps can share billing, Authentication, and Firestore rules. Create a separate Firebase project when the product needs stronger isolation, separate billing, independent administrators, or unrelated security rules.

Map each Hosting site to a named deploy target:

```sh
npx firebase-tools target:apply hosting <target-name> <hosting-site-id>
npx firebase-tools deploy --only hosting:<target-name>
```

Always deploy a named target. A bare `--only hosting` deploys every configured Hosting target.

Example `.firebaserc`:

```json
{
  "projects": {
    "default": "<project-id>"
  },
  "targets": {
    "<project-id>": {
      "hosting": {
        "main": ["<main-site-id>"],
        "my-app": ["<my-app-site-id>"]
      }
    }
  }
}
```

Example `firebase.json`:

```json
{
  "hosting": [
    {
      "target": "my-app",
      "public": "path/to/static-app",
      "ignore": [
        "firebase.json",
        ".firebaserc",
        "**/.*",
        "**/node_modules/**",
        "private/**",
        "scripts/**",
        "**/*.private.json"
      ],
      "headers": [
        {
          "source": "**/*.@(html|js|css|json|webmanifest|svg)",
          "headers": [
            {
              "key": "Cache-Control",
              "value": "no-cache"
            }
          ]
        }
      ]
    }
  ],
  "firestore": {
    "rules": "firestore.rules"
  }
}
```

## Loading Firebase in a static app

When the app runs on Firebase Hosting, load the project configuration from the reserved Hosting endpoint:

```js
import { initializeApp } from "https://www.gstatic.com/firebasejs/<version>/firebase-app.js";

const response = await fetch("/__/firebase/init.json", { cache: "no-store" });
if (!response.ok) {
  throw new Error("Firebase configuration is unavailable.");
}

const firebaseConfig = await response.json();
const app = initializeApp(firebaseConfig);
```

The `/__/firebase/init.json` endpoint is provided by Firebase Hosting. Apps that depend on it must be served from Firebase Hosting; a different static host will not provide that endpoint unless configuration is supplied another way.

## Google Authentication

Enable Google as a sign-in provider in:

```text
Firebase Console → Authentication → Sign-in method → Google
```

Add every production and preview hostname under:

```text
Firebase Console → Authentication → Settings → Authorized domains
```

Browser example:

```js
import {
  GoogleAuthProvider,
  getAuth,
  onAuthStateChanged,
  signInWithPopup,
  signOut,
} from "https://www.gstatic.com/firebasejs/<version>/firebase-auth.js";

const auth = getAuth(app);
const provider = new GoogleAuthProvider();

await signInWithPopup(auth, provider);

onAuthStateChanged(auth, (user) => {
  if (!user) {
    // Show signed-out state.
    return;
  }

  // Load data. Firestore Rules still decide whether access is allowed.
});
```

Handle popup cancellation and blocked popups gracefully. Sign-out should call `signOut(auth)` and clear private data from the rendered UI.

## Firestore authorization templates

Default-deny all collections that are not explicitly listed.

### Small internal allowlist

Suitable for a private team utility with a small, stable membership:

```text
rules_version = '2';

service cloud.firestore {
  match /databases/{database}/documents {
    function isAllowedUser() {
      return request.auth != null
        && request.auth.token.email_verified == true
        && request.auth.token.email in [
          'person-one@example.com',
          'person-two@example.com'
        ];
    }

    match /appData/{document=**} {
      allow read, write: if isAllowedUser();
    }

    match /{document=**} {
      allow read, write: if false;
    }
  }
}
```

### Per-user data

```text
rules_version = '2';

service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId}/{document=**} {
      allow read, write: if request.auth != null
        && request.auth.uid == userId;
    }

    match /{document=**} {
      allow read, write: if false;
    }
  }
}
```

For larger teams, prefer custom claims or a membership collection managed by trusted administration rather than maintaining a long email list in rules.

Deploy rules separately:

```sh
npx firebase-tools deploy --only firestore:rules
```

Hosting deployment does not deploy Firestore rules.

## Data handling

- Keep public, non-sensitive generated data as static JSON when it changes only during deployments.
- Put private, user-generated, or frequently changing data in Firestore.
- Scope documents by user or tenant when possible.
- Validate document fields, types, ownership, and immutable fields in Security Rules.
- Do not cache private Firestore responses in a service worker.
- Avoid storing sensitive private data in `localStorage` or IndexedDB unless the threat model explicitly permits it.
- Use the Firebase Emulator Suite to test deny and allow cases before changing production rules.

## PWA caching

Cache only the public app shell:

```text
index.html
app.js
styles.css
manifest.webmanifest
icon assets
```

Do not service-worker-cache Authentication responses, Firestore traffic, `/__/firebase/init.json`, or private user data.

When changing cached shell files:

1. Bump the service-worker cache name.
2. Bump script and stylesheet version query strings.
3. Deploy the Hosting target.
4. Verify a returning browser receives the new shell.

## Deployment checklist

```text
[ ] Correct Firebase project selected
[ ] Correct named Hosting target selected
[ ] Public directory contains only deployable static files
[ ] No secrets, private exports, tokens, or service-account files
[ ] Google provider enabled if required
[ ] Production domain added to Authorized domains
[ ] Firestore rules default-deny unspecified collections
[ ] Rules tested for signed-out, allowed, and disallowed users
[ ] Static app tested locally
[ ] App shell cache/version bumped when required
[ ] Hosting deployed with --only hosting:<target>
[ ] Firestore rules deployed separately if changed
[ ] Live URL, authentication, reads, writes, and sign-out verified
```

## CI/CD

For team automation, use a dedicated CI identity with the minimum required IAM roles. Store credentials in the CI platform's secret store, or prefer workload identity federation where supported.

Do not commit:

- service-account JSON
- Firebase refresh tokens
- `.env` files containing secrets
- exported private Firestore data

Production deployment should require protected-branch or environment approval appropriate to the team's risk level.

## When this architecture is not enough

Add a trusted backend—such as Cloud Functions or Cloud Run—when the app needs:

- third-party API secrets
- payment processing
- privileged Admin SDK operations
- server-side validation beyond Security Rules
- scheduled jobs
- email or webhook delivery
- content transformation that must not be controlled by the browser

The browser should call that backend; secrets must never be shipped in static JavaScript.
