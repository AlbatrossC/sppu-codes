import os

def generate_sw_js():
    # Define the directories
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates', 'subjects')
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    answers_dir = os.path.join(os.path.dirname(__file__), 'answers')

    # List to hold all file paths
    files_to_cache = []

    # Add index.html
    files_to_cache.append('/')

    # Add all subject HTML files
    for subject_file in os.listdir(templates_dir):
        if subject_file.endswith('.html'):
            files_to_cache.append(f'/{subject_file[:-5]}')

    # Add all static files (JS, CSS) with proper path formatting
    for root, dirs, files in os.walk(static_dir):
        for file in files:
            if file.endswith('.js') or file.endswith('.css'):
                # Get the path relative to the project root
                rel_path = os.path.relpath(os.path.join(root, file), os.path.dirname(__file__))
                # Convert backslashes to forward slashes and ensure leading slash
                formatted_path = '/' + rel_path.replace(os.sep, '/')
                files_to_cache.append(formatted_path)

    # Add all answer files (.cpp, .py, .c++)
    for root, dirs, files in os.walk(answers_dir):
        for file in files:
            if file.endswith('.cpp') or file.endswith('.py') or file.endswith('.c++'):
                # Remove the 'answers' directory from the path
                relative_path = os.path.relpath(os.path.join(root, file), answers_dir)
                files_to_cache.append(f'/{relative_path.replace(os.sep, "/")}')

    # Define core assets
    core_assets = ['/', '/static/css/index.css', '/static/js/index.js']

    # Generate the sw.js content
    sw_js_content = f"""
const CACHE_NAME = 'my-site-cache-v1';
const urlsToCache = {files_to_cache};

// Core assets to cache immediately (critical for offline use)
const CORE_ASSETS = {core_assets};

// Install event: Cache only core assets initially
self.addEventListener('install', (event) => {{
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {{
        console.log('Opened cache');
        return cache.addAll(CORE_ASSETS); // Cache only critical files
      }})
      .then(() => self.skipWaiting()) // Activate SW immediately
      .catch((err) => console.error('Install failed:', err))
  );
}});

// Activate event: Clean old caches and pre-cache remaining files in the background
self.addEventListener('activate', (event) => {{
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then((cacheNames) => {{
      return Promise.all(
        cacheNames.map((cacheName) => {{
          if (!cacheWhitelist.includes(cacheName)) {{
            return caches.delete(cacheName);
          }}
        }})
      );
    }}).then(() => {{
      // Pre-cache remaining files in the background
      return caches.open(CACHE_NAME).then((cache) => {{
        const filesToCache = urlsToCache.filter((url) => !CORE_ASSETS.includes(url));
        return Promise.allSettled(
          filesToCache.map((url) => {{
            return cache.add(url).catch((err) => {{
              console.warn(`Failed to cache ${{url}}: ${{err}}`);
            }});
          }})
        );
      }});
    }}).then(() => self.clients.claim()) // Take control of pages immediately
  );
}});

// Fetch event: Cache dynamically and serve from cache
self.addEventListener('fetch', (event) => {{
  let requestUrl = new URL(event.request.url);

  // Normalize requests by removing query parameters for CSS, JS, and other static files
  if (requestUrl.pathname.startsWith('/static/')) {{
    requestUrl.search = ''; // Strip query params
  }}

  event.respondWith(
    caches.match(requestUrl.pathname).then((cachedResponse) => {{
      if (cachedResponse) {{
        return cachedResponse;
      }}

      return fetch(event.request).then((networkResponse) => {{
        if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic') {{
          return networkResponse; // Don't cache errors or cross-origin responses
        }}

        const responseToCache = networkResponse.clone();
        caches.open(CACHE_NAME).then((cache) => {{
          cache.put(requestUrl.pathname, responseToCache);
        }});

        return networkResponse;
      }}).catch(() => caches.match('/')); // Fallback
    }})
  );
}});
"""

    # Write the sw.js file
    with open(os.path.join(os.path.dirname(__file__), 'sw.js'), 'w') as f:
        f.write(sw_js_content)

if __name__ == '__main__':
    generate_sw_js()
