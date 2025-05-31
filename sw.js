// Service Worker for PDF Caching
// File: sw.js

const CACHE_NAME = 'sppu-pdfs-v1';
const CACHE_EXPIRY_DAYS = 7;
const MAX_CONCURRENT_DOWNLOADS = 3;

const CacheManager = {
    async openCache() {
        return await caches.open(CACHE_NAME);
    },

    async isCached(url) {
        const cache = await this.openCache();
        const response = await cache.match(url);
        return !!response;
    },

    async getCachedUrls(urls) {
        const cache = await this.openCache();
        const cachedUrls = [];
        for (const url of urls) {
            const response = await cache.match(url);
            if (response) {
                const expiryTime = response.headers.get('sw-cache-expiry');
                if (!expiryTime || Date.now() <= parseInt(expiryTime)) {
                    cachedUrls.push(url);
                }
            }
        }
        return cachedUrls;
    },

    async cachePdf(url) {
        const cache = await this.openCache();
        const fileName = this.extractFileName(url);
        const startTime = performance.now();

        try {
            this.postMessage({
                type: 'PDF_DOWNLOAD_START',
                data: { url, fileName }
            });

            const response = await fetch(url, {
                cache: 'no-cache',
                mode: 'cors'
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const responseClone = response.clone();
            const headers = new Headers(responseClone.headers);
            headers.set('sw-cached-at', Date.now().toString());
            headers.set('sw-cache-expiry', (Date.now() + (CACHE_EXPIRY_DAYS * 24 * 60 * 60 * 1000)).toString());

            const cachedResponse = new Response(responseClone.body, {
                status: responseClone.status,
                statusText: responseClone.statusText,
                headers: headers
            });

            await cache.put(url, cachedResponse);

            const loadTime = performance.now() - startTime;
            console.log(`[SW Cache] Cached ${fileName} in ${loadTime.toFixed(2)}ms`);

            this.postMessage({
                type: 'PDF_DOWNLOAD_COMPLETE',
                data: { url, fileName }
            });
        } catch (error) {
            console.error(`[SW Cache] Error caching ${fileName}:`, error);
            this.postMessage({
                type: 'PDF_DOWNLOAD_ERROR',
                data: { url, fileName, error: error.message }
            });
        }
    },

    async cachePdfsInBackground(urls) {
        const queue = urls.slice();
        const activeDownloads = new Set();

        const processNext = async () => {
            if (queue.length === 0 || activeDownloads.size >= MAX_CONCURRENT_DOWNLOADS) return;

            const url = queue.shift();
            activeDownloads.add(url);

            await this.cachePdf(url);
            activeDownloads.delete(url);

            if (queue.length > 0) {
                await processNext();
            }
        };

        await Promise.all(
            Array.from({ length: MAX_CONCURRENT_DOWNLOADS }, processNext)
        );
    },

    async cleanExpiredCache() {
        const cache = await this.openCache();
        const requests = await cache.keys();
        const now = Date.now();

        for (const request of requests) {
            const response = await cache.match(request);
            if (response) {
                const expiryTime = response.headers.get('sw-cache-expiry');
                if (expiryTime && now > parseInt(expiryTime)) {
                    console.log(`[SW Cache] Removing expired: ${request.url}`);
                    await cache.delete(request);
                }
            }
        }
    },

    extractFileName(url) {
        try {
            const urlObj = new URL(url);
            const pathParts = urlObj.pathname.split('/');
            return pathParts[pathParts.length - 1] || 'unknown.pdf';
        } catch {
            return url.split('/').pop() || 'unknown.pdf';
        }
    },

    postMessage(message) {
        self.clients.matchAll().then(clients => {
            clients.forEach(client => client.postMessage(message));
        });
    }
};

self.addEventListener('install', (event) => {
    console.log('[SW] Installing...');
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    console.log('[SW] Activating...');
    event.waitUntil(
        Promise.all([
            caches.keys().then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        if (cacheName !== CACHE_NAME) {
                            console.log('[SW] Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            }),
            CacheManager.cleanExpiredCache(),
            self.clients.claim()
        ])
    );
});

self.addEventListener('fetch', (event) => {
    if (event.request.url.includes('.pdf') || event.request.url.includes('cloudinary.com')) {
        event.respondWith(
            CacheManager.openCache().then(cache => {
                return cache.match(event.request).then(response => {
                    if (response) {
                        const expiryTime = response.headers.get('sw-cache-expiry');
                        if (expiryTime && Date.now() > parseInt(expiryTime)) {
                            return fetch(event.request).then(fetchResponse => {
                                if (fetchResponse.ok) {
                                    const responseClone = fetchResponse.clone();
                                    const headers = new Headers(responseClone.headers);
                                    headers.set('sw-cached-at', Date.now().toString());
                                    headers.set('sw-cache-expiry', (Date.now() + (CACHE_EXPIRY_DAYS * 24 * 60 * 60 * 1000)).toString());
                                    const updatedResponse = new Response(responseClone.body, {
                                        status: responseClone.status,
                                        statusText: responseClone.statusText,
                                        headers: headers
                                    });
                                    cache.put(event.request, updatedResponse);
                                }
                                console.log(`[SW Fetch] Served from network (expired cache): ${event.request.url}`);
                                return fetchResponse;
                            }).catch(() => {
                                console.log(`[SW Fetch] Fallback to expired cache: ${event.request.url}`);
                                return response;
                            });
                        }
                        console.log(`[SW Fetch] Served from cache: ${event.request.url}`);
                        return response;
                    }

                    return fetch(event.request).then(fetchResponse => {
                        if (fetchResponse.ok) {
                            const responseClone = fetchResponse.clone();
                            const headers = new Headers(responseClone.headers);
                            headers.set('sw-cached-at', Date.now().toString());
                            headers.set('sw-cache-expiry', (Date.now() + (CACHE_EXPIRY_DAYS * 24 * 60 * 60 * 1000)).toString());
                            const cachedResponse = new Response(responseClone.body, {
                                status: responseClone.status,
                                statusText: responseClone.statusText,
                                headers: headers
                            });
                            cache.put(event.request, cachedResponse);
                        }
                        console.log(`[SW Fetch] Served from network: ${event.request.url}`);
                        return fetchResponse;
                    });
                });
            })
        );
    }
});

self.addEventListener('message', (event) => {
    const { type, urls } = event.data;
    switch (type) {
        case 'CACHE_PDFS':
            if (Array.isArray(urls)) {
                console.log(`[SW] Starting caching of ${urls.length} PDFs`);
                CacheManager.cachePdfsInBackground(urls);
            }
            break;
        case 'CHECK_CACHED_PDFS':
            if (Array.isArray(urls) && event.ports && event.ports[0]) {
                CacheManager.getCachedUrls(urls).then(cachedUrls => {
                    event.ports[0].postMessage({
                        type: 'PDF_CACHE_CHECK',
                        cachedUrls: cachedUrls
                    });
                });
            }
            break;
        case 'CLEAN_CACHE':
            CacheManager.cleanExpiredCache().then(() => {
                CacheManager.postMessage({
                    type: 'CACHE_CLEANED',
                    data: { success: true }
                });
            }).catch(error => {
                CacheManager.postMessage({
                    type: 'CACHE_CLEANED',
                    data: { success: false, error: error.message }
                });
            });
            break;
        case 'GET_CACHE_INFO':
            CacheManager.openCache().then(async (cache) => {
                const requests = await cache.keys();
                const cacheInfo = {
                    totalFiles: requests.length,
                    cacheSize: 0,
                    files: []
                };
                for (const request of requests) {
                    const response = await cache.match(request);
                    if (response) {
                        const blob = await response.blob();
                        const fileName = CacheManager.extractFileName(request.url);
                        const cachedAt = response.headers.get('sw-cached-at');
                        const expiryTime = response.headers.get('sw-cache-expiry');
                        cacheInfo.cacheSize += blob.size;
                        cacheInfo.files.push({
                            url: request.url,
                            fileName,
                            size: blob.size,
                            cachedAt: cachedAt ? new Date(parseInt(cachedAt)) : null,
                            expiresAt: expiryTime ? new Date(parseInt(expiryTime)) : null
                        });
                    }
                }
                CacheManager.postMessage({
                    type: 'CACHE_INFO',
                    data: cacheInfo
                });
            });
            break;
    }
});

self.addEventListener('periodicsync', (event) => {
    if (event.tag === 'cache-cleanup') {
        event.waitUntil(CacheManager.cleanExpiredCache());
    }
});

self.addEventListener('beforeinstallprompt', (event) => {
    console.log('[SW] Update available');
});