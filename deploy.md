# Deploy Guide

## App layout

- `sppucodes/` deploys the code-focused site.
- `sppupyqs/` deploys the question-paper-focused site.

## Recommended Vercel setup

Create two separate Vercel projects from the same Git repo.

### Project 1: `sppucodes`

- Root Directory: `sppucodes`
- Build command: none
- Output directory: none
- Install command: default

### Project 2: `sppupyqs`

- Root Directory: `sppupyqs`
- Build command: none
- Output directory: none
- Install command: default

## Environment variables

Set these in both Vercel projects unless noted otherwise.

- `SPPUCODES_SITE_URL=https://sppucodes.vercel.app`
- `SPPUPYQS_SITE_URL=https://sppupyqs.vercel.app`
- `SECRET_KEY=...`
- `MAINTENANCE_MODE=false`
- `PDF_SOURCE=r2` or `supabase`
- `DEFAULT_EXAM_TYPE=endsem`

If you use the existing Cloudflare Worker + D1 logging setup, also set:

- `CF_WORKER_DB_URL=...`
- `DB_API_KEY=...`
- `DISCORD_WEBHOOK_URL=...`

## What each app serves

### `sppucodes`

- `/`
- `/<subject_code>`
- `/<subject_code>/<question_id>`
- `/submit`
- `/contact`
- `/api/<subject>/<question_no>`
- `/raw-answers/...`

Legacy routes redirect out:

- `/question-papers`
- `/question-papers/<subject>`
- `/questionpapers`
- `/questionpapers/<subject>`

### `sppupyqs`

- `/`
- `/<subject>`
- `/api/question-papers/list`
- `/api/notify-download`
- `/api/pdf-proxy`

## Local run

### Codes site

```powershell
cd sppucodes
python app.py
```

### Question papers site

```powershell
cd sppupyqs
python app.py
```

## Post-deploy checks

1. Open the codes homepage and confirm the Question Papers button goes to the new site.
2. Open an old codes URL like `/question-papers/artificial-intelligence-aids` and confirm it redirects to `https://sppupyqs.vercel.app/artificial-intelligence-aids`.
3. Open the question papers homepage and confirm subject cards route to `/<subject>` without the old `/question-papers/` prefix.
4. Open a subject page on the question papers site and verify the PDF viewer loads through `/api/pdf-proxy`.
5. Check both `/sitemap.xml` files after deployment.

## Notes

- The default subject-to-paper links now point to the AIDS slugs for the overlapping code subjects.
- If you later move to custom domains, update `SPPUCODES_SITE_URL` and `SPPUPYQS_SITE_URL` in both projects.
