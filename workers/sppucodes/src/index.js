export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Strip leading slash to get R2 object key
    // e.g. /fy/sem-1/basic-electrical.../file.pdf → fy/sem-1/.../file.pdf
    const key = url.pathname.slice(1);

    if (!key) {
      return new Response("Not found", { status: 404 });
    }

    const cache = caches.default;

    // ==============================
    // 1. Check Cloudflare Edge Cache
    // ==============================
    const cachedResponse = await cache.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }

    // ==============================
    // 2. Cache miss — fetch from R2
    // ==============================
    const object = await env.BUCKET.get(key);

    if (!object) {
      return new Response("Not found", { status: 404 });
    }

    const filename = key.split("/").pop();

    const response = new Response(object.body, {
      headers: {
        "Content-Type": "application/pdf",
        "Cache-Control": "public, max-age=31536000, s-maxage=31536000, immutable",
        "Content-Disposition": `inline; filename="${filename}"`,
        "X-Cache": "MISS", // helpful for debugging — will show HIT once cached
      },
    });

    // ==============================
    // 3. Store in Cloudflare Edge Cache
    // waitUntil = don't block response, cache async in background
    // ==============================
    ctx.waitUntil(cache.put(request, response.clone()));

    return response;
  },
};