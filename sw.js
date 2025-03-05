
const CACHE_NAME = 'my-site-cache-v1';
const urlsToCache = ['/', '/cgl', '/dsal', '/dsl', '/iotl', '/oop', '/osl', '/static/css/answerbox.css', '/static/css/download_styles.css', '/static/css/error_styles.css', '/static/css/footer.css', '/static/css/header.css', '/static/css/index.css', '/static/css/subjectlayout.css', '/static/js/index.js', '/static/js/script.js', '/cgl/grpA_1.cpp', '/cgl/grpA_2.cpp', '/cgl/grpA_3a.cpp', '/cgl/grpB_4a.cpp', '/cgl/grpB_5b.cpp', '/cgl/grpC_6b.cpp', '/dsal/13_graph_dfs_bfs.cpp', '/dsal/14_flight_graph.cpp', '/dsal/1_telephonebook.py', '/dsal/4_set_adt.py', '/dsal/5_book_tree.cpp', '/dsal/6_binary_search_tree.cpp', '/dsal/9_threaded_binary_tree.cpp', '/dsl/grpA_1.py', '/dsl/grpA_2.py', '/dsl/grpA_4.py', '/dsl/grpB_11a.py', '/dsl/grpB_11b.py', '/dsl/grpB_14.py', '/dsl/grpB_15.py', '/dsl/grpB_18.py', '/dsl/grpC_19.cpp', '/dsl/grpC_23.cpp', '/dsl/grpD_25.cpp', '/dsl/grpD_27.cpp', '/dsl/grpE_29.cpp', '/dsl/grpE_30.cpp', '/dsl/grpE_31.cpp', '/iotl/blinking.c++', '/iotl/counter.c++', '/iotl/led_control.c++', '/iotl/square_number.cpp', '/iotl/temperature.cpp', '/oop/grpA_1.c++', '/oop/grpA_2.c++', '/oop/grpA_3.c++', '/oop/grpB_4.c++', '/oop/grpB_5.c++', '/oop/grpC_6.c++', '/oop/grpD_7.c++'];

// Install event: Cache all files upfront
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Opened cache and caching all files');
        return cache.addAll(urlsToCache); // Cache everything
      })
      .then(() => self.skipWaiting())
      .catch((err) => console.error('Install failed:', err))
  );
});

// Activate event: Clean up old caches
self.addEventListener('activate', (event) => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (!cacheWhitelist.includes(cacheName)) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event: Stale-while-revalidate strategy
self.addEventListener('fetch', (event) => {
  let requestUrl = new URL(event.request.url);

  // Normalize requests for static files by removing query params
  if (requestUrl.pathname.startsWith('/static/')) {
    requestUrl.search = '';
  }

  event.respondWith(
    caches.match(requestUrl.pathname).then((cachedResponse) => {
      // Return cached response if available
      if (cachedResponse) {
        // Update cache in the background
        event.waitUntil(
          fetch(event.request).then((networkResponse) => {
            if (networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
              return caches.open(CACHE_NAME).then((cache) => {
                cache.put(requestUrl.pathname, networkResponse.clone());
              });
            }
          }).catch((err) => console.warn('Background update failed:', err))
        );
        return cachedResponse;
      }

      // If not in cache, fetch from network and cache it
      return fetch(event.request).then((networkResponse) => {
        if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic') {
          return networkResponse;
        }

        const responseToCache = networkResponse.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(requestUrl.pathname, responseToCache);
        });

        return networkResponse;
      }).catch(() => caches.match('/')); // Fallback to root
    })
  );
});
