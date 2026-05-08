/**
 * sppucodes-db — Cloudflare Worker for SPPU Codes analytics
 *
 * Endpoints:
 *   POST /api/submit   — code_submissions
 *   POST /api/contact  — contact_messages
 *   POST /api/log      — api_requests
 *   POST /api/download — paper_downloads (upsert)
 *
 * All endpoints require header: X-API-Key: <DB_API_KEY>
 */

export interface Env {
  DB: D1Database;
  DB_API_KEY: string;
}

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, X-API-Key",
  "Access-Control-Max-Age": "86400",
};

function corsPreflight(): Response {
  return new Response(null, { status: 204, headers: CORS_HEADERS });
}

function json(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { ...CORS_HEADERS, "Content-Type": "application/json" },
  });
}

function validateApiKey(request: Request, env: Env): boolean {
  const key = request.headers.get("X-API-Key");
  return key === env.DB_API_KEY;
}

async function readBody(request: Request): Promise<Record<string, unknown> | null> {
  try {
    return await request.json() as Record<string, unknown>;
  } catch {
    return null;
  }
}

// ─── Handlers ────────────────────────────────────────────────────────

async function handleSubmit(env: Env, request: Request, ctx: ExecutionContext): Promise<Response> {
  const body = await readBody(request);
  if (!body) return json({ error: "invalid json" }, 400);

  const name = String(body.name || "").slice(0, 100).trim();
  const email = String(body.email || "").slice(0, 150).trim();
  const subject = String(body.subject || "").slice(0, 200).trim();
  const question = String(body.question || "").slice(0, 2000).trim();
  const code = String(body.code || "").trim();

  if (!name || !subject || !code) {
    return json({ error: "missing required fields: name, subject, code" }, 400);
  }

  ctx.waitUntil(
    env.DB.prepare(
      `INSERT INTO code_submissions (name, email, subject, question, code)
       VALUES (?1, ?2, ?3, ?4, ?5)`
    )
      .bind(name, email || null, subject, question || null, code)
      .run()
      .catch((e) => console.error("submit insert failed:", e))
  );

  return json({ ok: true });
}

async function handleContact(env: Env, request: Request, ctx: ExecutionContext): Promise<Response> {
  const body = await readBody(request);
  if (!body) return json({ error: "invalid json" }, 400);

  const name = String(body.name || "").slice(0, 100).trim();
  const email = String(body.email || "").slice(0, 150).trim();
  const message = String(body.message || "").trim();

  if (!name || !email || !message) {
    return json({ error: "missing required fields: name, email, message" }, 400);
  }

  ctx.waitUntil(
    env.DB.prepare(
      `INSERT INTO contact_messages (name, email, message)
       VALUES (?1, ?2, ?3)`
    )
      .bind(name, email, message)
      .run()
      .catch((e) => console.error("contact insert failed:", e))
  );

  return json({ ok: true });
}

async function handleLog(env: Env, request: Request, ctx: ExecutionContext): Promise<Response> {
  const body = await readBody(request);
  if (!body) return json({ error: "invalid json" }, 400);

  const subject = String(body.subject || "").slice(0, 100).trim();
  const question_no = String(body.question_no || "").slice(0, 50).trim();
  const status = String(body.status || "").trim();

  if (!subject || !question_no || !status) {
    return json({ error: "missing required fields: subject, question_no, status" }, 400);
  }
  if (!["success", "not_found"].includes(status)) {
    return json({ error: "status must be 'success' or 'not_found'" }, 400);
  }

  ctx.waitUntil(
    env.DB.prepare(
      `INSERT INTO api_requests (subject, question_no, status)
       VALUES (?1, ?2, ?3)`
    )
      .bind(subject, question_no, status)
      .run()
      .catch((e) => console.error("log insert failed:", e))
  );

  return json({ ok: true });
}

async function handleDownload(env: Env, request: Request, ctx: ExecutionContext): Promise<Response> {
  const body = await readBody(request);
  if (!body) return json({ error: "invalid json" }, 400);

  const fingerprint_id = String(body.fingerprint_id || "").slice(0, 255).trim();
  const subject = String(body.subject || "").slice(0, 100).trim();

  if (!fingerprint_id || !subject) {
    return json({ error: "missing required fields: fingerprint_id, subject" }, 400);
  }

  ctx.waitUntil(
    env.DB.prepare(
      `INSERT INTO paper_downloads (fingerprint_id, subject, download_count)
       VALUES (?1, ?2, 1)
       ON CONFLICT(fingerprint_id, subject)
       DO UPDATE SET download_count = download_count + 1,
                     created_at = datetime('now')`
    )
      .bind(fingerprint_id, subject)
      .run()
      .catch((e) => console.error("download insert failed:", e))
  );

  return json({ ok: true });
}

// ─── Router ──────────────────────────────────────────────────────────

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    if (request.method === "OPTIONS") return corsPreflight();

    if (!validateApiKey(request, env)) {
      return json({ error: "unauthorized" }, 401);
    }

    const url = new URL(request.url);

    if (request.method !== "POST") {
      return json({ error: "method not allowed" }, 405);
    }

    switch (url.pathname) {
      case "/api/submit":
        return handleSubmit(env, request, ctx);
      case "/api/contact":
        return handleContact(env, request, ctx);
      case "/api/log":
        return handleLog(env, request, ctx);
      case "/api/download":
        return handleDownload(env, request, ctx);
      default:
        return json({ error: "not found" }, 404);
    }
  },
};
