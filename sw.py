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

    # Generate the sw.js content with optimized logic
    sw_js_content = f"""
const CACHE_NAME = 'my-site-cache-v1';
const urlsToCache = {files_to_cache};

// Install event: Cache all files upfront
self.addEventListener('install', (event) => {{
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {{
        console.log('Opened cache and caching all files');
        return cache.addAll(urlsToCache); // Cache everything
      }})
      .then(() => self.skipWaiting())
      .catch((err) => console.error('Install failed:', err))
  );
}});

// Activate event: Clean up old caches
self.addEventListener('activate', (event) => {{
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then((cacheNames) => {{
      return Promise.all(
        cacheNames.map((cacheName) => {{
          if (!cacheWhitelist.includes(cacheName)) {{
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }}
        }})
      );
    }}).then(() => self.clients.claim())
  );
}});

// Fetch event: Stale-while-revalidate strategy
self.addEventListener('fetch', (event) => {{
  let requestUrl = new URL(event.request.url);

  // Normalize requests for static files by removing query params
  if (requestUrl.pathname.startsWith('/static/')) {{
    requestUrl.search = '';
  }}

  event.respondWith(
    caches.match(requestUrl.pathname).then((cachedResponse) => {{
      // Return cached response if available
      if (cachedResponse) {{
        // Update cache in the background
        event.waitUntil(
          fetch(event.request).then((networkResponse) => {{
            if (networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {{
              return caches.open(CACHE_NAME).then((cache) => {{
                cache.put(requestUrl.pathname, networkResponse.clone());
              }});
            }}
          }}).catch((err) => console.warn('Background update failed:', err))
        );
        return cachedResponse;
      }}

      // If not in cache, fetch from network and cache it
      return fetch(event.request).then((networkResponse) => {{
        if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic') {{
          return networkResponse;
        }}

        const responseToCache = networkResponse.clone();
        caches.open(CACHE_NAME).then((cache) => {{
          cache.put(requestUrl.pathname, responseToCache);
        }});

        return networkResponse;
      }}).catch(() => caches.match('/')); // Fallback to root
    }})
  );
}});
"""

    # Write the sw.js file
    with open(os.path.join(os.path.dirname(__file__), 'sw.js'), 'w') as f:
        f.write(sw_js_content)

if __name__ == '__main__':
    generate_sw_js()