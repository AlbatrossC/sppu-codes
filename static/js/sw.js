const CACHE_NAME = 'offline-pages-v1';
const OFFLINE_PAGES = [
    '/offline/offline_index',
    '/offline/offline_cgl',
    '/offline/offline_oop',
    '/offline/offline_dsal',
    '/offline/offline_dsl',
    '/offline/offline_iotl',
    
    // Add more offline pages here as needed
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                return cache.addAll(OFFLINE_PAGES);
            })
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                return response || fetch(event.request);
            })
            .catch(() => caches.match('/offline/offline_index')) // Fallback to offline index
    );
});
