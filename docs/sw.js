// Freyr Match: offline cache. The game page comes from the network first (so updates arrive), everything else from the cache.
const VERSION = 'd9787319fc';
const CACHE = 'freyr-match-' + VERSION;
const CORE = ["./", "manifest.webmanifest", "icons/icon-192.png", "icons/icon-512.png", "icons/icon-maskable-512.png", "icons/apple-touch-icon.png", "icons/favicon-64.png", "fonts/lilita-one-latin-400-normal.woff2", "fonts/nunito-latin-700-normal.woff2", "fonts/nunito-latin-800-normal.woff2", "fonts/nunito-latin-900-normal.woff2", "fonts/m-plus-rounded-1c-latin-700-normal.woff2", "fonts/m-plus-rounded-1c-latin-800-normal.woff2"];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k.startsWith('freyr-match-') && k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
const fresh = async req => {
  const c = await caches.open(CACHE);
  try {
    const res = await fetch(req, { cache: 'no-cache' });
    if (res && res.ok) c.put(req.mode === 'navigate' ? './' : req, res.clone());
    return res;
  } catch (e) {
    return (await c.match(req, { ignoreSearch: true })) || (await c.match('./')) || Response.error();
  }
};
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;
  if (req.mode === 'navigate' || url.pathname.endsWith('/') || url.pathname.endsWith('/index.html')) { e.respondWith(fresh(req)); return; }
  e.respondWith(caches.match(req, { ignoreSearch: true }).then(hit => hit || fetch(req).then(res => {
    if (res && res.ok) caches.open(CACHE).then(c => c.put(req, res.clone()));
    return res;
  })));
});
