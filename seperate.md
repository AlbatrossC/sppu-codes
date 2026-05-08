Separate Question Papers Website Plan

Objective

Split the current mixed product into two sites inside the same repo:

sppucodes/ for codes only

sppupyqs/ for question papers only

The goal is not just code movement. The goal is to make:

the codes site fully code-focused

the question papers site fully question-paper-focused

URLs simpler

data ownership cleaner

internal links less confusing

Target End State

Website 1: sppucodes

Purpose:

serve subject code pages

serve question-level code pages

serve API/raw answer files if you want to keep them here

Primary routes:

/

/<subject_code>

/<subject_code>/<question_id>

/submit

/contact

/api/... for code-related APIs only

Question paper behavior:

homepage button redirects to new question papers site

subject pages link out to the matching subject page on the new site

no local /question-papers

no local question-paper viewer

no local question-paper list API

Website 2: sppupyqs

Purpose:

serve only question papers

make question-paper discovery and subject pages the core product

Primary routes:

/ instead of current /question-papers

/<subject> instead of current /question-papers/<subject>

Optional future routes:

/branch/<branch>

/semester/<semester>

/search

/sitemap

New URL Structure

Current

/question-papers

/question-papers/<subject>

New

/

/<subject>

Mapping rule

old: https://sppucodes.vercel.app/question-papers

new: https://your-question-paper-domain/

old: https://sppucodes.vercel.app/question-papers/<subject>

new: https://your-question-paper-domain/<subject>

Examples:

/question-papers/database-management-systems-cse -> /database-management-systems-cse

/question-papers/artificial-intelligence-aids -> /artificial-intelligence-aids

Recommended Repo Structure

Current repo root

Keep one repo, but split apps cleanly.

Suggested structure:

sppucodes/

sppupyqs/

shared/ optional, only if you later want shared helpers/data scripts

Suggested app-local structure:

sppucodes/app.py

sppucodes/src/...

sppucodes/templates/...

sppucodes/static/...

sppucodes/questions/...

sppucodes/answers/...

sppucodes/vercel.json

sppupyqs/app.py

sppupyqs/src/...

sppupyqs/templates/...

sppupyqs/static/...

sppupyqs/question-papers/...

sppupyqs/vercel.json

Optional shared root files:

.gitignore

README.md

root workspace notes

What Belongs in the New Question Papers Site

These are the question-paper-specific pieces found in the current codebase.

Data

Move:

question-papers/question-papers-r2/*.json

question-papers/question-papers-supabase/*.json

question-papers/pyqs-seo/*.json

Maybe keep or move depending on workflow:

static/pyqs/upload.py

static/pyqs/validator.py

static/pyqs/rename.py

static/pyqs/comparison_report.txt

These are operationally question-paper tooling, so they belong with the new site.

Backend logic

Move:

src/routes/question_papers.py

question-paper parts of src/utils.py

_extract_semesters_from_data

_load_seo_index

load_question_papers

question-paper config from src/config.py

QUESTION_PAPERS_DIR

PDF_SOURCE

QP_PDF_DIR

QP_SEO_DIR

DEFAULT_EXAM_TYPE

Move question-paper API endpoints from src/routes/api.py:

/api/question-papers/list

/api/notify-download

/api/pdf-proxy

Templates

Move:

templates/select.html

templates/viewer.html

Maybe recreate instead of directly moving:

templates/sitemap.html

Reason:

current sitemap mixes codes + question papers

new site should have its own clean sitemap page

Static assets

Move:

static/css/select.css

static/css/viewer.css

static/js/download-paper.js

static/pdfjs/**

Likely copy/shared:

static/js/analytics.js

static/images/logo.png

static/images/logo.webp

static/images/favicon.ico

If the new site gets its own branding, replace these rather than sharing forever.

What Should Stay in sppucodes

Data

Keep:

questions/*.json

answers/**

Backend logic

Keep:

src/routes/subjects.py

src/routes/main.py

code-related parts of src/routes/api.py

load_subject_data

answer loading helpers

Templates

Keep:

templates/index.html

templates/subject.html

templates/submit.html

templates/contact.html

templates/error.html

But update them so they no longer assume local question-paper routes exist.

Changes Needed in sppucodes

1. Homepage question papers button

Current:

homepage links to local /questionpapers

Change to:

direct absolute link to new domain homepage

Examples:

https://sppupyqs.vercel.app/

your custom domain if you set one later

Also update:

desktop nav button

mobile nav button

any footer/sitewide mentions

2. Subject JSON question_paper_url

Current:

questions/*.json contain local question_paper_url

many are outdated or incorrect

Change all of them to the new site:

https://new-domain/<subject>

This needs to be updated for:

questions/ai.json

questions/ann.json

questions/cgl.json

questions/cnl.json

questions/cs.json

questions/dbms.json

questions/ds.json

questions/dsal.json

questions/dsl.json

questions/iotl.json

questions/nlp.json

questions/oop.json

3. Subject page button behavior

Current:

templates/subject.html renders a Question Papers button from question_paper_url

Keep this behavior, but point it to the new domain.

4. Remove local question-paper routes

Remove from sppucodes:

src/routes/question_papers.py

registration of that blueprint in src/__init__.py

local redirect logic for /questionpapers if no longer needed

Decision:

either remove old paths fully

or keep a thin redirect route that sends users to the new domain

Recommended:

keep redirects for old public URLs for user continuity

5. Remove question-paper APIs from codes site

Remove or externalize:

/api/question-papers/list

/api/notify-download

/api/pdf-proxy

Because after the split they belong to the question-paper site.

6. Clean homepage search behavior

Current static/js/index.js loads question papers into the mixed search experience.

Decide one of these:

Option A: remove question papers from search completely

Option B: keep them, but results open the new site

Recommended:

remove them from sppucodes homepage search to keep site identity clean

7. Update error page

Current templates/error.html includes question-paper discovery and fetches /api/question-papers/list.

Change it so:

sppucodes error page only shows code subjects

optionally include one external button: Go to Question Papers Site

8. Update sitemap

Current sitemap includes question-paper URLs.

After split:

remove all question-paper URLs from sppucodes sitemap

keep only code-related pages here

Changes Needed in sppupyqs

1. Homepage becomes current question-papers root

Map:

old templates/select.html -> new homepage template

Need updates:

canonical should be /

titles/descriptions should reference the new brand

links should point to /<subject>

2. Subject viewer page route changes

Map:

old /question-papers/<subject> -> new /<subject>

Need updates in backend:

route definition

canonical

OG URL

breadcrumb schema

back button behavior

JS URL parsing in download-paper.js

Important:

static/js/download-paper.js currently assumes path contains question-papers.

That logic must be rewritten for the new root-level subject paths.

3. API route review

Keep:

/api/question-papers/list

/api/notify-download

/api/pdf-proxy

But all URLs, metadata, and JS fetches should now belong to the new site.

4. Branding changes

Replace old SPPU Codes mentions in:

titles

descriptions

schema

visible body copy

logo alt text

footer/about sections

Current viewer.html repeatedly says SPPU Codes.

That must become the new site’s brand everywhere.

5. Sitemap and robots

New site should have:

its own robots.txt

its own sitemap.xml

optional HTML sitemap

The new sitemap should include:

/

every /<subject>

optional branch/semester pages if added

Inventory of Current Code Touchpoints

These are the main places that will need edits or removal.

sppucodes app side

templates/index.html

templates/subject.html

templates/error.html

templates/sitemap.html

static/js/index.js

src/routes/api.py

src/__init__.py

src/config.py

src/utils.py

questions/*.json

vercel.json

robots.txt

sitemap.xml

sppupyqs side

templates/select.html

templates/viewer.html

static/css/select.css

static/css/viewer.css

static/js/download-paper.js

static/pdfjs/**

src/routes/question_papers.py

question-paper parts of src/utils.py

question-paper config in src/config.py

question-paper endpoints in src/routes/api.py

question-papers/**

vercel.json

robots.txt

sitemap.xml

URL Rewrite and Redirect Plan

In old sppucodes

Recommended redirects:

/question-papers -> https://new-domain/

/question-papers/<subject> -> https://new-domain/<subject>

/questionpapers -> https://new-domain/

/questionpapers/<subject> -> https://new-domain/<subject>

This is important even if you said migration is not the main concern, because:

existing users may have saved links

some URLs may already be in Google

internal stale links may exist for some time

In new site

No extra prefix needed.

Keep it simple:

homepage = discovery page

subject page = root-level slug

Data and Mapping Checklist

Subject slug mapping

Before moving, confirm that every code subject’s question_paper_url points to the exact target slug on the new site.

Examples needing confirmation:

object-oriented-programming vs object-oriented-programming-aids

database-management-system vs database-management-systems-cse or ...-aids

computer-networks vs computer-network-and-security-cse or computer-networks-aids

This is important because current mappings are inconsistent.

Branch ambiguity

Some code subjects may map to one branch-specific paper subject, but some may not be one-to-one.

You need a rule for each code page:

if only one matching paper subject exists, link directly

if multiple branch-specific paper subjects exist, decide:

pick one default branch

or link to a mini chooser page on the new site

This is one of the most important product decisions in the split.

Practical Sequencing Plan

Phase 1: Create the new app shell

create sppupyqs/

copy/move question-paper templates, routes, config, static assets, and data

make homepage route /

make subject route /<subject>

Phase 2: Make the new site self-contained

update branding

update canonical/OG/schema URLs

update download-paper.js path assumptions

add new robots.txt

add new sitemap.xml

Phase 3: Disconnect question papers from sppucodes

remove question-paper route blueprint

remove question-paper APIs

remove question-paper search integration

remove question-paper section from sitemap.xml

update homepage button to new domain

update error page to stop calling question-paper APIs

Phase 4: Rewire code subject links

fix every question_paper_url in questions/*.json

verify button behavior on all subject pages

Phase 5: Clean deployment setup

create separate Vercel project for sppucodes/

create separate Vercel project for sppupyqs/

set correct root directories

give each app its own vercel.json

New Site SEO Checklist

Homepage /

unique title

unique meta description

canonical to /

visible HTML links to all subject pages

branch/semester grouping

not JS-only navigation

Subject pages /<subject>

unique title

unique meta description

canonical to self

visible HTML list of available papers

paper years in body text

branch and semester in body text

back links to homepage and related subjects

Technical

own sitemap

own robots

no mixed SPPU Codes branding

no references to old /question-papers/... route

Codes Site Cleanup Checklist

remove local question-paper routes

remove local question-paper templates

remove question-paper APIs

remove question-paper search results from homepage

remove question-paper URLs from sitemap

change nav/homepage question papers button to external new site

update all question_paper_url fields

update error page to not fetch question-paper data

Question Papers Site Build Checklist

create app folder

move question-paper data JSONs

move viewer/select templates

move viewer/select CSS

move download-paper.js

move pdfjs assets

move question-paper route code

move question-paper utility loaders

move question-paper API endpoints

update route structure from /question-papers/<subject> to /<subject>

update JS path parsing

update all canonicals/schema/OG URLs

add branding

add sitemap/robots

Risks to Watch

1. Broken subject-to-paper mapping

Current mappings are already inconsistent.

If not cleaned first, the split will preserve confusion.

2. Hidden route assumptions in JS

download-paper.js definitely assumes /question-papers/<subject>.

There may be a few more assumptions in templates and button handlers.

3. Shared config contamination

If both apps continue sharing one config module, it will get messy fast.

Prefer app-local config for each site.

4. Mixed branding leftovers

The new question-paper site should not keep saying SPPU Codes in schema, titles, and footer copy.

Recommended Decision Rules

Keep in sppucodes only if it serves code users directly

Keep:

code answers

code APIs

subject pages

Move out if it exists only for question papers:

viewer UI

paper list APIs

paper analytics

paper JSON stores

paper sitemap entries

Final Recommendation

Treat this as a full product separation, not just a folder move.

The cleanest result is:

sppucodes becomes lean and code-focused

sppupyqs becomes the question-paper authority

URLs become simpler on the new site

internal linking becomes less confusing

data ownership becomes much easier to reason about

If you execute this cleanly, the split can improve both maintainability and topical clarity.