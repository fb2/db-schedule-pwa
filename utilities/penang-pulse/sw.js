const CACHE_NAME = "penang-pulse-v19";
const SHELL_ASSETS = [
  "./",
  "./index.html",
  "./styles.css?v=19",
  "./app.js?v=19",
  "./manifest.webmanifest",
  "./icon.svg",
  "./apple-touch-icon.png",
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(SHELL_ASSETS)));
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

function isFreshContent(request, url) {
  // Daily guides + indexes must not stick in cache-first forever.
  if (request.mode === "navigate") return true;
  const path = url.pathname;
  if (path.endsWith(".html") || path.endsWith("/")) return true;
  if (path.endsWith("/feed.json") || path.endsWith("/guides/index.json")) return true;
  if (path.endsWith("/index.json")) return true;
  // Mee-Search graph changes with each episode; do not pin graph-data.js.
  if (path.endsWith("/graph-data.js") || path.endsWith("/noodle-graph.json") || path.endsWith("/graph-stats.json")) {
    return true;
  }
  return false;
}

function networkFirst(request) {
  return fetch(request)
    .then((response) => {
      if (response && response.ok) {
        const copy = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
      }
      return response;
    })
    .catch(() => caches.match(request));
}

function cacheFirst(request) {
  return caches.match(request).then(
    (cached) =>
      cached ||
      fetch(request).then((response) => {
        if (response && response.ok) {
          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
        }
        return response;
      })
  );
}

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;
  const url = new URL(event.request.url);

  if (url.origin !== self.location.origin) {
    return;
  }

  // Never let the SW pin sw.js itself — browser must see updates.
  if (url.pathname.endsWith("/sw.js")) {
    event.respondWith(fetch(event.request));
    return;
  }

  if (isFreshContent(event.request, url)) {
    event.respondWith(networkFirst(event.request));
    return;
  }

  event.respondWith(cacheFirst(event.request));
});
