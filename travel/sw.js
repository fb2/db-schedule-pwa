const CACHE_NAME = "travel-plans-v8";
const ASSETS = [
  "./",
  "./index.html",
  "./styles.css?v=8",
  "./app.js?v=8",
  "./plan-view.js?v=8",
  "./experience-view.js?v=8",
  "./manifest.webmanifest",
  "./icon.svg"
];
const FIREBASE_ASSETS = [
  "https://www.gstatic.com/firebasejs/10.14.1/firebase-app.js",
  "https://www.gstatic.com/firebasejs/10.14.1/firebase-auth.js",
  "https://www.gstatic.com/firebasejs/10.14.1/firebase-firestore.js"
];
const BACKGROUND_REFRESH_MS = 8000;

function scopeUrl() {
  return new URL(self.registration.scope);
}

function assetHref(asset) {
  return new URL(asset, scopeUrl()).href;
}

function isShellAsset(url) {
  return ASSETS.some((asset) => assetHref(asset) === url.href);
}

function isInitJson(url) {
  return url.origin === self.location.origin && url.pathname === "/__/firebase/init.json";
}

function isTravelNavigation(url) {
  const scope = scopeUrl();
  if (url.origin !== scope.origin) return false;
  const scopePath = scope.pathname.replace(/\/$/, "");
  return url.pathname === scopePath || url.pathname.startsWith(`${scopePath}/`);
}

function canStore(response) {
  return Boolean(response && response.ok && response.type !== "opaque" && response.type !== "opaqueredirect");
}

async function storeResponse(request, response) {
  if (!canStore(response)) return;
  try {
    const cache = await caches.open(CACHE_NAME);
    await cache.put(new Request(request.url), response.clone());
  } catch {
    /* Ignore quota errors and bodies that cannot be stored. */
  }
}

function refreshInBackground(request) {
  if (!self.navigator.onLine) return Promise.resolve();
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), BACKGROUND_REFRESH_MS);
  return fetch(request, { signal: controller.signal })
    .then((response) => storeResponse(request, response))
    .catch(() => {})
    .finally(() => clearTimeout(timer));
}

async function shellFallback() {
  return (await caches.match(assetHref("./"))) || (await caches.match(assetHref("./index.html")));
}

self.addEventListener("install", (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);
    await cache.addAll(ASSETS);
    await Promise.allSettled(FIREBASE_ASSETS.map((url) => cache.add(url)));
  })());
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;
  const requestUrl = new URL(event.request.url);
  const isFirebase = FIREBASE_ASSETS.includes(requestUrl.href);
  const isAsset = isShellAsset(requestUrl);
  const initJson = isInitJson(requestUrl);
  const navigate = event.request.mode === "navigate" && isTravelNavigation(requestUrl);

  if (!navigate && !isFirebase && !isAsset && !initJson) return;

  event.respondWith((async () => {
    const cached = navigate
      ? (await caches.match(event.request)) || (await shellFallback())
      : await caches.match(event.request);
    if (cached) {
      event.waitUntil(refreshInBackground(event.request));
      return cached;
    }
    try {
      const response = await fetch(event.request);
      await storeResponse(event.request, response);
      return response;
    } catch (error) {
      const fallback = navigate ? await shellFallback() : null;
      if (fallback) return fallback;
      throw error;
    }
  })());
});
