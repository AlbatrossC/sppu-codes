
const CACHE_NAME = 'my-site-cache-v1';
const urlsToCache = ['/', '/cgl', '/dsal', '/dsl', '/iotl', '/oop', '/osl', '/static/css/answerbox.css', '/static/css/download_styles.css', '/static/css/error_styles.css', '/static/css/footer.css', '/static/css/header.css', '/static/css/index.css', '/static/css/subjectlayout.css', '/static/js/index.js', '/static/js/script.js', '/cgl/grpA_1.cpp', '/cgl/grpA_2.cpp', '/cgl/grpA_3a.cpp', '/cgl/grpB_4a.cpp', '/cgl/grpB_5b.cpp', '/cgl/grpC_6b.cpp', '/dsal/13_graph_dfs_bfs.cpp', '/dsal/14_flight_graph.cpp', '/dsal/1_telephonebook.py', '/dsal/4_set_adt.py', '/dsal/5_book_tree.cpp', '/dsal/6_binary_search_tree.cpp', '/dsal/9_threaded_binary_tree.cpp', '/dsl/grpA_1.py', '/dsl/grpA_2.py', '/dsl/grpA_4.py', '/dsl/grpB_11a.py', '/dsl/grpB_11b.py', '/dsl/grpB_14.py', '/dsl/grpB_15.py', '/dsl/grpB_18.py', '/dsl/grpC_19.cpp', '/dsl/grpC_23.cpp', '/dsl/grpD_25.cpp', '/dsl/grpD_27.cpp', '/dsl/grpE_29.cpp', '/dsl/grpE_30.cpp', '/dsl/grpE_31.cpp', '/iotl/blinking.c++', '/iotl/counter.c++', '/iotl/led_control.c++', '/iotl/square_number.cpp', '/iotl/temperature.cpp', '/oop/grpA_1.c++', '/oop/grpA_2.c++', '/oop/grpA_3.c++', '/oop/grpB_4.c++', '/oop/grpB_5.c++', '/oop/grpC_6.c++', '/oop/grpD_7.c++'];

// Core assets to cache immediately (critical for offline use)
const CORE_ASSETS = ['/', '/static/css/index.css', '/static/js/index.js'];

// Install event: Cache only core assets initially
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Opened cache');
        return cache.addAll(CORE_ASSETS); // Cache only critical files
      })
      .then(() => self.skipWaiting()) // Activate SW immediately
      .catch((err) => console.error('Install failed:', err))
  );
});

// Activate event: Clean old caches and pre-cache remaining files in the background
self.addEventListener('activate', (event) => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (!cacheWhitelist.includes(cacheName)) {
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      // Pre-cache remaining files in the background
      return caches.open(CACHE_NAME).then((cache) => {
        const filesToCache = urlsToCache.filter((url) => !CORE_ASSETS.includes(url));
        return Promise.allSettled(
          filesToCache.map((url) => {
            return cache.add(url).catch((err) => {
              console.warn(`Failed to cache ${url}: ${err}`);
            });
          })
        );
      });
    }).then(() => self.clients.claim()) // Take control of pages immediately
  );
});

// Fetch event: Cache dynamically and serve from cache
self.addEventListener('fetch', (event) => {
  let requestUrl = new URL(event.request.url);

  // Normalize requests by removing query parameters for CSS, JS, and other static files
  if (requestUrl.pathname.startsWith('/static/')) {
    requestUrl.search = ''; // Strip query params
  }

  event.respondWith(
    caches.match(requestUrl.pathname).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }

      return fetch(event.request).then((networkResponse) => {
        if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic') {
          return networkResponse; // Don't cache errors or cross-origin responses
        }

        const responseToCache = networkResponse.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(requestUrl.pathname, responseToCache);
        });

        return networkResponse;
      }).catch(() => caches.match('/')); // Fallback
    })
  );
});
