# sppucodes-db Worker

**Status**: ✅ Deployed · `https://sppucodes-db.albatrossc.workers.dev` · D1 `dbde5970` · All endpoints verified.

Cloudflare Worker that handles all database analytics operations for SPPU Codes via **Cloudflare D1** (SQLite-compatible edge database). Designed to be **non-blocking and fast** — the worker responds immediately, and DB writes happen in the background via `ctx.waitUntil()`.

## Architecture

```
Flask Server (sppucodes.in)
       │
       │  POST /api/download   X-API-Key: <secret>
       │  POST /api/submit
       │  POST /api/contact
       │  POST /api/log
       ▼
┌─────────────────────────────┐
│   sppucodes-db Worker       │
│   (Cloudflare Edge)         │
│                             │
│  1. Validate X-API-Key      │
│  2. Parse JSON body         │
│  3. ctx.waitUntil(          │
│       D1 insert/upsert      │────►  Cloudflare D1
│     )                       │      (SQLite at edge)
│  4. Return { ok: true }     │
└─────────────────────────────┘
```

## Endpoints

| Method | Path | Table | Description |
|--------|------|-------|-------------|
| POST | `/api/submit` | `code_submissions` | Code submission from users |
| POST | `/api/contact` | `contact_messages` | Contact form messages |
| POST | `/api/log` | `api_requests` | API request analytics (success/not_found) |
| POST | `/api/download` | `paper_downloads` | Paper download tracking (upsert) |

**Headers required:**
- `Content-Type: application/json`
- `X-API-Key: <DB_API_KEY>` — shared secret between server and worker

## Setup (First Time)

### 1. Install dependencies

```bash
cd workers/sppucodes-db
npm install
```

### 2. Login to Cloudflare

```bash
npx wrangler login
```

### 3. Create D1 database

```bash
npm run db:create
```

This outputs a `database_id`. Copy it and update `wrangler.toml`:

```toml
[[d1_databases]]
binding = "DB"
database_name = "sppucodes-db"
database_id = "your-database-id-here"   # ← paste here
```

### 4. Run schema migration

```bash
npm run db:execute
```

### 5. Set the shared API key secret

Generate a strong random key:

```bash
# Generate a random 64-char hex key
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

Set it securely in the worker (never hardcode in files):

```bash
npx wrangler secret put DB_API_KEY
# Paste the generated key when prompted
```

### 6. Deploy the worker

```bash
npm run deploy
```

Note the deployed URL (e.g., `https://sppucodes-db.your-subdomain.workers.dev`).

### 7. Set DB_API_KEY on the Flask server

Add the same API key to the server's `.env`:

```env
CF_WORKER_DB_URL=https://sppucodes-db.your-subdomain.workers.dev
DB_API_KEY=your-generated-key-here
```

## Deploy to Production

```bash
npm run deploy
```

After deploying, update `wrangler.toml` with the production D1 database ID if using a separate production database.

## Local Development

```bash
npm run dev
```

This starts a local wrangler dev server. Note: D1 requires a remote preview — local SQLite is not available without `--remote`:

```bash
npx wrangler dev --remote
```

## DB Operations Pattern (Python Side)

On the Flask server, call the worker with a **fire-and-forget** pattern:

```python
import threading, requests

_CF_WORKER_DB_URL = os.getenv("CF_WORKER_DB_URL")
_DB_API_KEY = os.getenv("DB_API_KEY")

def _db_post(endpoint, payload):
    """Fire-and-forget POST to the DB worker."""
    def _send():
        try:
            requests.post(
                f"{_CF_WORKER_DB_URL}{endpoint}",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": _DB_API_KEY,
                },
                timeout=3,
            )
        except Exception:
            pass  # Worker unreachable — silently ignore analytics loss

    threading.Thread(target=_send, daemon=True).start()

# Usage
_db_post("/api/download", {"fingerprint_id": fid, "subject": subj})
```

## Schema

See [schema.sql](./schema.sql) — SQLite-compatible D1 schema with 4 tables, indexes, and an upsert for download tracking.

## Quick Test Queries

```bash
npx wrangler d1 execute sppucodes-db --remote --command="SELECT id, name, email, subject, question, created_at FROM code_submissions ORDER BY id DESC LIMIT 20"
npx wrangler d1 execute sppucodes-db --remote --command="SELECT id, name, email, message, created_at FROM contact_messages ORDER BY id DESC LIMIT 20"
npx wrangler d1 execute sppucodes-db --remote --command="SELECT id, subject, question_no, status, created_at FROM api_requests ORDER BY id DESC LIMIT 20"
npx wrangler d1 execute sppucodes-db --remote --command="SELECT id, fingerprint_id, subject, download_count, created_at FROM paper_downloads ORDER BY id DESC LIMIT 20"
```

## Security

- `DB_API_KEY` is stored as a **Cloudflare Secret** — never committed to git
- All endpoints require `X-API-Key` header matching the secret
- Requests without a valid key return `401 Unauthorized`
- Input is sanitized (length-limited strings, trimmed whitespace)

## Commands Reference

| Command | Description |
|---------|-------------|
| `npm install` | Install dependencies |
| `npm run dev` | Start local dev server |
| `npm run deploy` | Deploy to Cloudflare |
| `npm run db:create` | Create D1 database |
| `npm run db:execute` | Run schema.sql against D1 |
| `npm run db:migrate` | List D1 tables |
| `npm run secret:set` | Set DB_API_KEY secret |
