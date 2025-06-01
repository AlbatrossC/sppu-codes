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

    // Problem 3 Fix: Parallel cache checking instead of sequential
    async getCachedUrls(urls) {
        const cache = await this.openCache();
        const now = Date.now();
        
        // Use Promise.all for parallel processing
        const cacheChecks = urls.map(async (url) => {
            const response = await cache.match(url);
            if (response) {
                const expiryTime = response.headers.get('sw-cache-expiry');
                if (!expiryTime || now <= parseInt(expiryTime)) {
                    return url;
                }
            }
            return null;
        });

        const results = await Promise.all(cacheChecks);
        return results.filter(url => url !== null);
    },

    // Helper function to create cached response with proper headers
    createCachedResponse(originalResponse) {
        const headers = new Headers(originalResponse.headers);
        headers.set('sw-cached-at', Date.now().toString());
        headers.set('sw-cache-expiry', (Date.now() + (CACHE_EXPIRY_DAYS * 24 * 60 * 60 * 1000)).toString());

        return new Response(originalResponse.body, {
            status: originalResponse.status,
            statusText: originalResponse.statusText,
            headers: headers
        });
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
            const cachedResponse = this.createCachedResponse(responseClone);

            await cache.put(url, cachedResponse);

            const loadTime = performance.now() - startTime;
            console.log(`[SW Cache] Cached ${fileName} in ${loadTime.toFixed(2)}ms`);

            this.postMessage({
                type: 'PDF_DOWNLOAD_COMPLETE',
                data: { url, fileName }
            });

            return true;
        } catch (error) {
            console.error(`[SW Cache] Error caching ${fileName}:`, error);
            this.postMessage({
                type: 'PDF_DOWNLOAD_ERROR',
                data: { url, fileName, error: error.message }
            });
            return false;
        }
    },

    // Problem 1 Fix: Fixed race condition in background caching
    async cachePdfsInBackground(urls) {
        const queue = [...urls]; // Create a proper copy
        const activeDownloads = new Set();
        const completedDownloads = new Set();
        
        const processNext = async () => {
            while (queue.length > 0 && activeDownloads.size < MAX_CONCURRENT_DOWNLOADS) {
                const url = queue.shift();
                if (!url || completedDownloads.has(url)) continue;
                
                activeDownloads.add(url);
                
                try {
                    await this.cachePdf(url);
                } catch (error) {
                    console.error(`[SW Cache] Failed to cache ${url}:`, error);
                } finally {
                    activeDownloads.delete(url);
                    completedDownloads.add(url);
                }
            }
        };

        // Start multiple concurrent processors
        const processors = Array.from(
            { length: Math.min(MAX_CONCURRENT_DOWNLOADS, urls.length) }, 
            () => processNext()
        );

        await Promise.all(processors);
        
        // Ensure all downloads are complete
        while (activeDownloads.size > 0) {
            await new Promise(resolve => setTimeout(resolve, 100));
        }
    },

    async cleanExpiredCache() {
        const cache = await this.openCache();
        const requests = await cache.keys();
        const now = Date.now();

        const cleanupPromises = requests.map(async (request) => {
            const response = await cache.match(request);
            if (response) {
                const expiryTime = response.headers.get('sw-cache-expiry');
                if (expiryTime && now > parseInt(expiryTime)) {
                    console.log(`[SW Cache] Removing expired: ${request.url}`);
                    await cache.delete(request);
                }
            }
        });

        await Promise.all(cleanupPromises);
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
    },

    // Problem 6 Fix: Extracted common fetch logic to reduce duplication
    async handlePdfFetch(request) {
        const cache = await this.openCache();
        const cachedResponse = await cache.match(request);

        if (cachedResponse) {
            const expiryTime = cachedResponse.headers.get('sw-cache-expiry');
            
            // Check if cached response is still valid
            if (!expiryTime || Date.now() <= parseInt(expiryTime)) {
                console.log(`[SW Fetch] Served from cache: ${request.url}`);
                return cachedResponse;
            }

            // Cache expired, try to fetch new version
            try {
                const fetchResponse = await fetch(request);
                if (fetchResponse.ok) {
                    const responseClone = fetchResponse.clone();
                    const newCachedResponse = this.createCachedResponse(responseClone);
                    await cache.put(request, newCachedResponse);
                    console.log(`[SW Fetch] Served from network (expired cache updated): ${request.url}`);
                    return fetchResponse;
                }
            } catch (error) {
                console.log(`[SW Fetch] Network failed, serving expired cache: ${request.url}`);
                return cachedResponse;
            }
        }

        // No cached response, fetch from network
        try {
            const fetchResponse = await fetch(request);
            if (fetchResponse.ok) {
                const responseClone = fetchResponse.clone();
                const cachedResponse = this.createCachedResponse(responseClone);
                await cache.put(request, cachedResponse);
                console.log(`[SW Fetch] Served from network (cached): ${request.url}`);
            }
            return fetchResponse;
        } catch (error) {
            console.error(`[SW Fetch] Network request failed: ${request.url}`, error);
            throw error;
        }
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

// Problem 6 Fix: Simplified fetch handler using extracted method
self.addEventListener('fetch', (event) => {
    if (event.request.url.includes('.pdf') || event.request.url.includes('cloudinary.com')) {
        event.respondWith(CacheManager.handlePdfFetch(event.request));
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
            
        // Problem 2 Fix: Memory leak prevention in cache info
        case 'GET_CACHE_INFO':
            CacheManager.openCache().then(async (cache) => {
                const requests = await cache.keys();
                const cacheInfo = {
                    totalFiles: requests.length,
                    cacheSize: 0,
                    files: []
                };
                
                // Process files in batches to prevent memory overload
                const BATCH_SIZE = 10;
                for (let i = 0; i < requests.length; i += BATCH_SIZE) {
                    const batch = requests.slice(i, i + BATCH_SIZE);
                    
                    const batchPromises = batch.map(async (request) => {
                        const response = await cache.match(request);
                        if (response) {
                            const fileName = CacheManager.extractFileName(request.url);
                            const cachedAt = response.headers.get('sw-cached-at');
                            const expiryTime = response.headers.get('sw-cache-expiry');
                            
                            // Get size from Content-Length header instead of loading blob
                            let size = 0;
                            const contentLength = response.headers.get('content-length');
                            if (contentLength) {
                                size = parseInt(contentLength);
                            } else {
                                // Only load blob if Content-Length is not available
                                const blob = await response.blob();
                                size = blob.size;
                            }
                            
                            return {
                                url: request.url,
                                fileName,
                                size,
                                cachedAt: cachedAt ? new Date(parseInt(cachedAt)) : null,
                                expiresAt: expiryTime ? new Date(parseInt(expiryTime)) : null
                            };
                        }
                        return null;
                    });
                    
                    const batchResults = await Promise.all(batchPromises);
                    const validResults = batchResults.filter(result => result !== null);
                    
                    cacheInfo.files.push(...validResults);
                    cacheInfo.cacheSize += validResults.reduce((sum, file) => sum + file.size, 0);
                }
                
                CacheManager.postMessage({
                    type: 'CACHE_INFO',
                    data: cacheInfo
                });
            }).catch(error => {
                console.error('[SW] Error getting cache info:', error);
                CacheManager.postMessage({
                    type: 'CACHE_INFO',
                    data: { error: error.message }
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