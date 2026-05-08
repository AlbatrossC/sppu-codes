# SPPU Platform

Monorepo containing two separate SPPU student resource websites + shared Cloudflare Worker infrastructure.

---

## Folder Structure

### `sppucodes/`
**SPPU Codes** — Code-focused website deployed at `https://sppucodes.vercel.app`

Serves programming lab codes and answers for SPPU engineering subjects.

**Routes:** `/`, `/<subject_code>`, `/<subject_code>/<question_id>`, `/submit`, `/contact`, `/sitemap`, `/api/<subject>/<question_no>`, `/raw-answers/...`

**Contents:**
```
sppucodes/
├── app.py              # Flask entry point
├── vercel.json         # Vercel deployment config
├── requirements.txt
├── robots.txt
├── sitemap.xml
├── sw.js               # Service worker
├── ads.txt
├── src/
│   ├── __init__.py     # App factory, blueprint registration
│   ├── config.py       # Site config, env vars
│   ├── db.py           # DB client → Cloudflare Worker
│   ├── utils.py        # Subject/answer data loaders
│   ├── async_logger.py # API request logging
│   ├── notifications.py# Discord webhook notifications
│   ├── terminal_beautify.py
│   └── routes/
│       ├── main.py     # Homepage, submit, contact, static files, sitemap
│       ├── subjects.py # Subject/answer pages
│       └── api.py      # Code answer API + raw file serving
├── templates/          # Jinja2 HTML (index, subject, submit, contact, error, sitemap, maintenance)
├── static/             # CSS, JS, fonts, images, SVG
├── questions/          # Subject JSON data (ai.json, dbms.json, oop.json, ...)
└── answers/            # Answer files by subject code (ai/, dbms/, oop/, ...)
```

**What it does NOT contain:** Question paper routes, viewer UI, paper list APIs, paper data. Old `/question-papers/*` and `/questionpapers/*` URLs 301 redirect to `sppupyqs`.

---

### `sppupyqs/`
**SPPU PYQs** — Question-paper-focused website deployed at `https://sppupyqs.vercel.app`

Serves discoverable, browsable previous year question papers with an embedded PDF.js viewer.

**Routes:** `/`, `/<subject>`, `/sitemap`, `/api/question-papers/list`, `/api/notify-download`, `/api/pdf-proxy`

**Contents:**
```
sppupyqs/
├── app.py              # Flask entry point
├── vercel.json         # Vercel deployment config
├── requirements.txt
├── robots.txt
├── sitemap.xml
├── ads.txt
├── src/
│   ├── __init__.py     # App factory, blueprint registration
│   ├── config.py       # Site config, PDF source, proxy allowlist
│   ├── db.py           # DB client → Cloudflare Worker
│   ├── utils.py        # Question paper data loaders
│   ├── async_logger.py # Paper download logging
│   └── routes/
│       ├── main.py            # Static files, robots, sitemap, ads
│       ├── question_papers.py # Homepage (select) + subject viewer pages
│       └── api.py             # Paper list, download notify, PDF proxy
├── templates/          # Jinja2 HTML (select, viewer, error, sitemap, maintenance)
├── static/
│   ├── css/
│   │   ├── select.css  # Homepage/branch picker styles
│   │   └── viewer.css  # Subject viewer styles
│   ├── js/
│   │   ├── analytics.js       # Placeholder — replace with QP-specific analytics
│   │   └── download-paper.js  # PDF viewer + download tracking
│   ├── images/         # favicon.ico, logo.png, logo.webp
│   ├── fonts/          # JetBrainsMono (used in viewer)
│   ├── pdfjs/          # PDF.js library for embedded viewer
│   ├── pdfviewer/      # Custom PDF viewer HTML/CSS
│   └── pyqs/           # Question paper upload/validation tooling
└── question-papers/    # Paper data (R2 JSONs, Supabase JSONs, SEO metadata)
```

**What it does NOT contain:** Code subject routes, answer files, code submission forms, terminal-related assets.

---

### `shared/`
**Shared resources** used by both deployed sites.

#### `shared/workers/sppucodes-db/`
**Cloudflare Worker + D1** — the analytics/logging backend for both sites. Deployed at `https://sppucodes-db.albatrossc.workers.dev`.

```
shared/workers/sppucodes-db/
├── wrangler.toml       # Worker + D1 binding config
├── package.json        # Dependencies + wrangler scripts
├── tsconfig.json
├── schema.sql          # D1 table definitions
└── src/
    └── index.ts        # Worker entry point
```

**D1 Tables:**
| Table | Used By | Purpose |
|-------|---------|---------|
| `code_submissions` | sppucodes | User code submissions |
| `contact_messages` | sppucodes | Contact form messages |
| `api_requests` | sppucodes | API usage logs (success/not_found) |
| `paper_downloads` | sppupyqs | Paper download tracking (upsert by fingerprint) |

**API Endpoints (all POST, require `X-API-Key` header):**
| Endpoint | Payload | Table |
|----------|---------|-------|
| `/api/submit` | `name, email, subject, question, code` | `code_submissions` |
| `/api/contact` | `name, email, message` | `contact_messages` |
| `/api/log` | `subject, question_no, status` | `api_requests` |
| `/api/download` | `fingerprint_id, subject` | `paper_downloads` (upsert) |

**Both `sppucodes` and `sppupyqs` call this worker** via their `src/db.py` modules using `CF_WORKER_DB_URL` + `DB_API_KEY` environment variables. The worker uses `ctx.waitUntil()` so responses return immediately while D1 inserts happen in the background.

**Deploy:**
```bash
cd shared/workers/sppucodes-db
npm run deploy          # wrangler deploy
npm run db:execute      # apply schema.sql to D1
npm run secret:set      # set DB_API_KEY secret
```

---

## Deployment

Each app deploys independently on Vercel from the same Git repo using different **Root Directory** settings:

| Project | Root Directory | URL |
|---------|---------------|-----|
| sppucodes | `sppucodes` | `https://sppucodes.vercel.app` |
| sppupyqs | `sppupyqs` | `https://sppupyqs.vercel.app` |

The Cloudflare Worker deploys separately via `wrangler deploy`.

See `deploy.md` for detailed Vercel setup and post-deploy checks.

---

## Local Development

```powershell
# Codes site
cd sppucodes
pip install -r requirements.txt
python app.py

# Question papers site
cd sppupyqs
pip install -r requirements.txt
python app.py

# Worker (requires wrangler)
cd shared/workers/sppucodes-db
npm install
npm run dev
```

Set required env vars or use the root `.env` file (loaded via `python-dotenv`).

---

## Environment Variables

Both Flask apps look for a `.env` file at the **repo root** (loaded by `python-dotenv`). In production, set these in each Vercel project.

### Cross-site linking (why both URLs are needed)

Both `SPPUCODES_SITE_URL` and `SPPUPYQS_SITE_URL` are required by **both** apps for bidirectional linking:

- **sppucodes** uses `QUESTION_PAPERS_SITE_URL` to 301-redirect legacy `/question-papers/*` URLs and to generate the "Question Papers" button link.
- **sppupyqs** uses `CODES_SITE_URL` for the "Home" / "Go to SPPU Codes" buttons and backlinks.

Without these, the two sites can't reference each other, and old bookmarked URLs break.

| Variable | Used By | Purpose |
|----------|---------|---------|
| `SPPUCODES_SITE_URL` | Both | Codes site URL for cross-linking |
| `SPPUPYQS_SITE_URL` | Both | QP site URL for cross-linking + redirects |
| `CF_WORKER_DB_URL` | Both | sppucodes-db Worker endpoint |
| `DB_API_KEY` | Both | Auth key for DB worker |
| `DISCORD_WEBHOOK_URL` | Both | Discord notifications |
| `MAINTENANCE_MODE` | Both | Toggle maintenance page |
| `SECRET_KEY` | Both | Flask session secret |

**QP-site-specific:** `PDF_SOURCE` (r2/supabase), `DEFAULT_EXAM_TYPE` (endsem/insem), `PDF_PROXY_ALLOWED_HOSTS`
