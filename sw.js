const CACHE_NAME = 'sppu-codes-cache-v1';

self.addEventListener('install', event => {
    self.skipWaiting();
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', event => {
    if (event.request.method !== 'GET') return;

    // Cache-first strategy for static assets and PDFs
    event.respondWith(
        caches.match(event.request).then(cachedResponse => {
            if (cachedResponse) {
                return cachedResponse; // Return from cache
            }
            return fetch(event.request).then(networkResponse => {
                // Determine if we should cache this response implicitly
                const url = new URL(event.request.url);
                if (
                    url.pathname.startsWith('/static/') || 
                    url.pathname.startsWith('/images/') ||
                    url.pathname.includes('/pdfjs/') 
                ) {
                    const responseClone = networkResponse.clone();
                    caches.open(CACHE_NAME).then(cache => {
                        cache.put(event.request, responseClone);
                    });
                }
                return networkResponse;
            });
        }).catch(() => {
            // Offline fallback could go here
        })
    );
});

self.addEventListener('message', event => {
    if (event.data && event.data.type === 'CACHE_PDFS') {
        const urls = event.data.urls;
        event.waitUntil(
            caches.open(CACHE_NAME).then(cache => {
                return Promise.all(
                    urls.map(url => {
                        return fetch(url).then(response => {
                            if (response.ok) {
                                return cache.put(url, response);
                            }
                        }).catch(err => console.error('SW manual cache error:', err));
                    })
                );
            })
        );
    }
});
