const CACHE_NAME = 'sppu-codes-static-v2';

function isStaticAsset(url) {
    return (
        url.pathname.startsWith('/static/') ||
        url.pathname.startsWith('/images/')
    );
}

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
    if (event.request.headers.has('range')) return;

    const url = new URL(event.request.url);
    if (!isStaticAsset(url)) {
        return;
    }

    event.respondWith(
        caches.open(CACHE_NAME).then(cache => {
            return cache.match(event.request).then(cachedResponse => {
                const networkFetch = fetch(event.request).then(networkResponse => {
                    if (networkResponse && networkResponse.ok) {
                        const responseClone = networkResponse.clone();
                        cache.put(event.request, responseClone);
                    }
                    return networkResponse;
                });

                if (cachedResponse) {
                    event.waitUntil(
                        networkFetch.catch(() => undefined)
                    );
                    return cachedResponse;
                }

                return networkFetch;
            });
        }).catch(() => {
            return fetch(event.request);
        })
    );
});

self.addEventListener('message', event => {
    if (!event.data || event.data.type !== 'CLEAR_STATIC_CACHE') {
        return;
    }

    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            return cache.keys().then(requests => {
                return Promise.all(
                    requests.map(request => {
                        const url = new URL(request.url);
                        if (isStaticAsset(url)) {
                            return cache.delete(request);
                        }
                    })
                );
            });
        })
    );
});
