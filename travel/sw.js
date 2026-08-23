const CACHE_NAME = "travel-plans-v4";
const ASSETS = [
  "./",
  "./index.html",
  "./styles.css?v=4",
  "./app.js?v=4",
  "./plan-view.js?v=4",
  "./manifest.webmanifest",
  "./icon.svg"
];
const FIREBASE_ASSETS = [
  "https://www.gstatic.com/firebasejs/10.14.1/firebase-app.js",
  "https://www.gstatic.com/firebasejs/10.14.1/firebase-auth.js",
  "https://www.gstatic.com/firebasejs/10.14.1/firebase-firestore.js"
];

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
  const scopeUrl = new URL(self.registration.scope);
  const isFirebase = FIREBASE_ASSETS.includes(requestUrl.href);
  const isAsset = ASSETS.some((asset) => new URL(asset, scopeUrl).href === requestUrl.href);

  if (!isFirebase && !isAsset) return;

  event.respondWith((async () => {
    const cached = await caches.match(event.request);
    if (cached && isFirebase) return cached;
    try {
      const response = await fetch(event.request);
      const cache = await caches.open(CACHE_NAME);
      cache.put(event.request, response.clone());
      return response;
    } catch (error) {
      if (cached) return cached;
      throw error;
    }
  })());
});
