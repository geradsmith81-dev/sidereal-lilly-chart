// The Sidereal Oracle (siderealoracle.com): a small helper that keeps the welcome page and an
// "you are offline" page on the device. It never stores anything from the app itself (/app/),
// and it never sees anything you type into the app.
var CACHE = "oracle-site-v1";
var FILES = ["/", "/index.html", "/offline.html", "/privacy.html", "/manifest.webmanifest",
  "/icons/icon-192.png", "/icons/icon-512.png", "/icons/icon-maskable-512.png",
  "/icons/apple-touch-icon.png", "/icons/favicon-32.png"];

self.addEventListener("install", function (e) {
  e.waitUntil(caches.open(CACHE).then(function (c) { return c.addAll(FILES); }));
  self.skipWaiting();
});
self.addEventListener("activate", function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k !== CACHE; })
                           .map(function (k) { return caches.delete(k); }));
  }));
  self.clients.claim();
});
self.addEventListener("fetch", function (e) {
  var req = e.request, url = new URL(req.url);
  if (req.method !== "GET" || url.origin !== self.location.origin) return;
  if (url.pathname === "/app" || url.pathname.indexOf("/app/") === 0) {
    // The app: always straight from the internet. Only if the phone is offline when the app is
    // opened, show the friendly offline page instead of the browser's error.
    if (req.mode === "navigate") {
      e.respondWith(fetch(req).catch(function () { return caches.match("/offline.html"); }));
    }
    return;
  }
  // The welcome page and icons: fresh when online, saved copy when offline.
  e.respondWith(fetch(req).then(function (r) {
    var copy = r.clone();
    caches.open(CACHE).then(function (c) { c.put(req, copy); });
    return r;
  }).catch(function () {
    return caches.match(req, { ignoreSearch: true }).then(function (m) {
      return m || caches.match("/offline.html");
    });
  }));
});
