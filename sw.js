const CACHE_NAME = 'offline-pages-v3';
const OFFLINE_PAGES = [
    '/offline/offline_index',
    '/offline/offline_cgl',
    '/offline/offline_oop',
    '/offline/offline_dsal',
    '/offline/offline_dsl',
    '/offline/offline_iotl',
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('Caching offline pages:', OFFLINE_PAGES);
                return cache.addAll(OFFLINE_PAGES);
            })
            .catch((error) => {
                console.error('Caching failed:', error);
            })
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                // Return cached response if available, otherwise fetch from network
                return response || fetch(event.request).catch(() => {
                    // Fallback to offline index page if network fails
                    return caches.match('/offline/offline_index');
                });
            })
    );
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((name) => {
                    if (name !== CACHE_NAME) {
                        return caches.delete(name); // Clean up old caches
                    }
                })
            );
        })
    );
});