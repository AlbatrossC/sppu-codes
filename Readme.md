# `question-papers`

> This branch is the central registry for SPPU question paper PDFs and their delivery manifests.
> It is maintained separately from the main application code.

All PDF files tracked here are available for direct download via GitHub. Since GitHub applies IP-based rate limiting on file downloads, it acts as a resilient fallback delivery layer alongside the primary CDN. The web application itself delivers PDFs through **Supabase Storage** or **Cloudflare R2** — the JSON manifests in this branch are what the app reads to resolve PDF links per subject.

---

## Table of Contents

- [Source](#source)
- [Workflow](#workflow)
- [Folder Structure](#folder-structure)
- [JSON Structure](#json-structure)
- [Upload Scripts](#upload-scripts)
- [CDN Delivery](#cdn-delivery)
- [Cloudflare Worker](#cloudflare-worker)
- [Self Hosting](#self-hosting)

---

## Source

Question papers are sourced from **[Google Drive](https://drive.google.com/drive/folders/0Bz9C0ysJZ7PnMGZKeWcybUpXWGM)** maintained by Zeal Education.

**Source:** Zeal Education — `unipunepaper@zealeducation.com`

> Only **2019 Pattern (PAT 2019)** papers are included in this repository.

---

## Workflow

```
Download from Drive  →  Organise  →  Rename Folders  →  Rename Files  →  Verify  →  Upload  →  Merge
```

### 1 · Download from Google Drive

Files are manually downloaded from the Google Drive. The drive organises files as:

```
Branch/
└── Year/
    └── Pattern/        ← only 2019 pattern is considered
        └── Subject/
```

After downloading, files are manually reorganised into the local working structure by cross-referencing the official SPPU syllabus:

```
branch/
└── sem-n/
    └── subject-name/
        └── raw-file.pdf
```

---

### 2 · Rename Subject Folders — `rename-folders.py`

Normalises subject folder names, then appends the branch suffix so every subject folder is uniquely identifiable across branches.

| Action | Example |
|---|---|
| Strips special characters | `Engineering Mathematics-I!` → `engineering-mathematics-i` |
| Spaces to hyphens | `basic electrical` → `basic-electrical` |
| Appends branch suffix to subjects folder | `engineering-mathematics-i` → `engineering-mathematics-i-fy` |
| Skips already correct | `basic-electrical-fy` → untouched |
| Skips name conflicts | logs warning, no overwrite |

---

### 3 · Rename PDF Files — `rename.py`

Renames each PDF using metadata extracted from the filename and the PDF text content. The output format is:

```
{exam_type}-{exam_month}-{exam_year}-pat{pattern_year}-{scheme}.pdf
```

**Examples:**
```
endsem-may-jun-2023-pat2019-emif.pdf
insem-oct-2022-pat2019-beef.pdf
other-nov-dec-2021-pat2019-cga.pdf
```

**How each field is detected:**

| Field | Source | Logic |
|---|---|---|
| `exam_type` | PDF text | `insem` if max marks = 30, `endsem` if 50 or 70 |
| `exam_month` | Filename | Extracted from prefix before the year |
| `exam_year` | Filename → PDF text | 4-digit year, falls back to PDF scan |
| `pattern_year` | PDF text | Matches `YYYY pattern` or `YYYY credit pattern` |
| `scheme` | Subject folder name | Initials with Roman numerals preserved |

Files that already match the final format are skipped. Files where any field cannot be determined are logged to `rename_update.txt` for manual review.

---

### 4 · Manual Verification

After renaming, all filenames are manually checked against the expected pattern before upload.

---

### 5 · Upload

Upload scripts push PDFs to the configured storage provider and generate or update the JSON manifest files. See [Upload Scripts](#upload-scripts).

---

### 6 · Merge to Main Branch

Once the upload is complete, the generated JSON manifests from `question-papers/r2/` or `question-papers/supabase/` are moved to the main branch for the web application to consume.

---

## Folder Structure

```
sppu-codes/
│
├── aids/                            ← Raw PDFs · AI & Data Science
│   └── sem-3/
│       └── computer-graphics-aids/
│           └── endsem-nov-dec-2023-pat2019-cga.pdf
│
├── cse/                             ← Raw PDFs · Computer Science
│   └── sem-3/
│       └── subject-name-cse/
│           └── ...pdf
│
├── fy/                              ← Raw PDFs · First Year Engineering
│   └── sem-1/
│       └── subject-name-fy/
│           └── ...pdf
│
├── it/                              ← Raw PDFs · Information Technology
│   └── sem-3/
│       └── subject-name-it/
│           └── ...pdf
│
├── question-papers/
│   │
│   ├── supabase/                    ← JSON manifests · Supabase public URLs
│   │   ├── aids.json
│   │   ├── cse.json
│   │   ├── fy.json
│   │   └── it.json
│   │
│   ├── r2/                          ← JSON manifests · Cloudflare Worker URLs
│   │   ├── aids.json
│   │   ├── cse.json
│   │   ├── fy.json
│   │   └── it.json
│   │
│   └── seo/                         ← SEO metadata · separate from PDF data
│       ├── aids.json
│       ├── cse.json
│       ├── fy.json
│       └── it.json
│
├── workers/
│   └── sppucodes/
│       ├── src/
│       │   └── index.js             ← Cloudflare Worker · R2 PDF delivery
│       └── wrangler.jsonc
│
├── rename-folders.py
├── rename.py
├── upload-supabase.py
├── upload-r2.py
├── list.py
├── remove.py
└── .env
```

---

## JSON Structure

### Delivery Manifests — `question-papers/supabase/{branch}.json` · `question-papers/r2/{branch}.json`

Both files share the exact same structure. The only difference is the base URL in `pdf_links` — Supabase manifests point to Supabase public storage URLs, R2 manifests point to the Cloudflare Worker URL.

```json
{
    "branch_name": "First Year Engineering",
    "branch_code": "F.E",
    "sem-1": {
        "basic-electrical-engineering-fy": {
            "subject_name": "Basic Electrical Engineering",
            "pdf_links": [
                "https://sppucodes.albatrossc.workers.dev/fy/sem-1/basic-electrical-engineering-fy/endsem-may-jun-2023-pat2019-beef.pdf",
                "https://sppucodes.albatrossc.workers.dev/fy/sem-1/basic-electrical-engineering-fy/insem-oct-2022-pat2019-beef.pdf"
            ]
        }
    }
}
```

---

### SEO Manifest — `question-papers/seo/{branch}.json`

Stored separately from delivery data to keep the main manifests lean. Consumed by the web app to populate `<title>` and `<meta>` tags on each subject page.

```json
{
    "branch_name": "Artificial Intelligence and Data Science",
    "branch_code": "AI & DS",
    "sems": {
        "sem-3": {
            "computer-graphics-aids": {
                "subject_name": "Computer Graphics",
                "seo_data": {
                    "title": "SPPU Computer Graphics | AI & DS Question Papers | Sppu Codes",
                    "description": "Computer Graphics in the AI & DS branch at SPPU...",
                    "keywords": "computer graphics question papers sppu, sppu aids graphics insem, ..."
                }
            }
        }
    }
}
```

`seo_data` always contains three fields: `title`, `description`, and `keywords`.

---

## Upload Scripts

### `upload-supabase.py`

Uploads PDFs to Supabase Storage via the S3-compatible API using `boto3`.

- Prompts for branch names to process (`fy`, `aids`, `cse`, `it`)
- Walks the `{branch}/sem-n/subject/` folder structure
- Skips files already tracked in the JSON — **incremental, no re-uploads**
- Constructs a full Supabase public URL per uploaded file
- Writes or updates `question-papers/supabase/{branch}.json`
- Cache header: `public, max-age=31536000`

---

### `upload-r2.py`

Uploads PDFs to Cloudflare R2 via the S3-compatible API using `boto3`. Behaviour is identical to the Supabase script with these differences:

- Uses R2 credentials with endpoint `https://{account_id}.r2.cloudflarestorage.com`
- Constructs delivery URLs using `CF_WORKER_URL` — the R2 bucket is **private** and never directly exposed
- Writes or updates `question-papers/r2/{branch}.json`
- Cache header: `public, max-age=31536000, s-maxage=31536000, immutable`

**Why these cache directives:**

| Directive | Scope | Effect |
|---|---|---|
| `max-age=31536000` | Browser | Cache locally for 1 year |
| `s-maxage=31536000` | CDN edge | Cache at Cloudflare edge nodes for 1 year |
| `immutable` | Browser | Never revalidate — question papers never change once uploaded |

---

## CDN Delivery

### Supabase — Legacy

PDFs were originally served directly from Supabase Storage public URLs. This worked reliably until early 2026, when the platform became inaccessible across India.

> **As of 1 March 2026**, Supabase is blocked on most Indian networks following a government blocking order.
> Source: [India disrupts access to popular developer platform Supabase with blocking order — TechCrunch, Feb 27 2026](https://techcrunch.com/2026/02/27/india-disrupts-access-to-popular-developer-platform-supabase-with-blocking-order/)

Since SPPU Codes serves students primarily in India, Supabase delivery became non-functional for the majority of users overnight. A full transition to Cloudflare R2 was made as a result. The Supabase upload script and manifests are retained for reference and as a fallback for non-Indian traffic.

---

### Cloudflare R2 — Current

PDFs are stored in a **private** R2 bucket (`sppucodes-files`). The bucket has no public URL — all delivery is routed through a Cloudflare Worker which authenticates with R2 internally.

---

## Cloudflare Worker

**Location:** `workers/sppucodes/src/index.js`
**Deployed at:** `https://sppucodes.albatrossc.workers.dev`

### Request Flow

```
1st request  →  Cloudflare Worker  →  R2 bucket  →  response sent + stored at edge
2nd request  →  Cloudflare Edge Cache  →  response returned instantly
               (Worker and R2 are never contacted again)
```

### What the Worker Does

1. Extracts the R2 object key from the request URL path (strips the leading `/`)
2. Checks `caches.default` — if a cached response exists, returns it immediately
3. On a cache miss, fetches the object from the private R2 bucket
4. Streams the PDF back to the user with full cache headers and `Content-Disposition: inline`
5. Calls `ctx.waitUntil(cache.put(...))` to store the response at the Cloudflare edge **asynchronously** — the user's response is not delayed

The `X-Cache: MISS` header is present on the first response to any given file. From the second request onward, the Worker is bypassed entirely — requests are served straight from the nearest Cloudflare data center.

### Recommended Cloudflare Dashboard Rule

To ensure Cloudflare respects aggressive caching for Worker responses, create a Cache Rule in the dashboard:

```
URL match  : cdn.sppucodes.in/*
Cache level: Cache Everything
Edge TTL   : 1 year
```

Without this rule Cloudflare may not cache Worker-originated responses at the edge regardless of the headers sent.

---

## Self Hosting

To run this pipeline yourself, clone the repository and follow the steps below.

### Install Dependencies

```bash
pip install boto3 python-dotenv pymupdf
```

### `.env` Reference

| Variable | Used In | Description |
|---|---|---|
| `SUPABASE_S3_ENDPOINT` | `upload-supabase.py` | Supabase S3-compatible endpoint URL |
| `SUPABASE_S3_BUCKET` | `upload-supabase.py` | Supabase storage bucket name |
| `SUPABASE_S3_ACCESS_KEY` | `upload-supabase.py` | Supabase S3 access key |
| `SUPABASE_S3_SECRET_KEY` | `upload-supabase.py` | Supabase S3 secret key |
| `SUPABASE_PROJECT_ID` | `upload-supabase.py` | Project ID — used to construct public URLs |
| `CF_ACCOUNT_ID` | `upload-r2.py` | Cloudflare account ID |
| `CF_R2_BUCKET` | `upload-r2.py` | R2 bucket name |
| `CF_R2_ACCESS_KEY` | `upload-r2.py` | R2 API token — Access Key ID |
| `CF_R2_SECRET_KEY` | `upload-r2.py` | R2 API token — Secret Access Key |
| `CF_WORKER_URL` | `upload-r2.py` | Base URL of the deployed Cloudflare Worker |

### Run Order

```bash
# 1. Normalise subject folder names
python rename-folders.py

# 2. Rename PDF files using extracted metadata
python rename.py

# 3. Upload PDFs and generate JSON manifests
python upload-r2.py

# 4. Move generated JSONs from question-papers/r2/ to the main branch
```

---

<sub>Maintained as part of the [SPPU Codes](https://sppucodes.vercel.app) project.</sub>