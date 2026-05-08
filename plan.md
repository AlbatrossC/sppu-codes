# SSR Pre-rendering Plan for Answer Code

## Problem
Answers are loaded client-side via JavaScript (`loadAnswer()` → `/api/{subject}/{qno}`). Google SEO bots see only question text — no code content. This causes "thin content" penalties and poor keyword indexing.

## Analysis: File Sizes & Server Impact

### Test Subjects — Raw Answer Code Sizes

| Subject | Files | Raw Code | With HTML Wrapping | After Gzip (~75%) |
|---------|-------|----------|--------------------|--------------------|
| **CGL** (light) | 9 × .cpp | **19 KB** | ~22 KB | **~5 KB** |
| **ANN** (.py only) | 10 × .py | **11 KB** | ~13 KB | **~3 KB** |
| **DS** (.py + .md) | 19 text files | **25 KB** | ~28 KB | **~7 KB** |
| **Single question** | 1-2 files | ~1-3 KB | ~1.5-3.5 KB | **~1 KB** |

### Files to SKIP for SSR (too large / non-text)

| Subject | Skipped Files | Size |
|---------|-------------|------|
| ANN | 4 × .ipynb (B5_CNN, C1, C2, C4) | ~130 KB total |
| ANN | 4 × .jpg | Binary |
| DS | BostonHousing.csv, Social_Network_Ads.csv | ~55 KB |
| DS | iris.csv, Data_2.csv, data3.csv | ~4 KB |
| DS | movie_dataset.csv, covid_vaccine_statewise.csv | Large |

### Server Load — NEGLIGIBLE

- `_read_answer_file()` already has `@lru_cache(maxsize=256)` — files cached in RAM
- Memory overhead: ~768 KB for 256 cached files
- Current HTML payload: ~6-8 KB (template + ads + CSS links)
- **Total HTML after SSR: 15-35 KB raw, 5-10 KB gzipped**
- Modern websites routinely serve 100-500 KB HTML pages

**The SEO gain massively outweighs the negligible cost.**

---

## Implementation Plan

### 1. Route: `sppucodes/src/routes/subjects.py`

Add `_get_ssr_answers(subject_link, questions, selected_question=None)`:
- Calls `_read_answer_file()` for each question's files (already cached via lru_cache)
- Skips: .ipynb, .csv, .jpg, .png, .pdf, .gif, .svg, .webp
- Returns dict: `{question_id: [(filename, content), ...]}`
- If `selected_question` set → only pre-renders that question

Import `_read_answer_file` from utils. Pass `ssr_answers` to template.

### 2. Template: `sppucodes/templates/subject.html`

After each question's buttons, add hidden SSR blocks (`style="display:none"`):
```html
{% if ssr_answers and question_item.id in ssr_answers %}
<div class="ssr-answers" style="display:none;" aria-hidden="true">
  {% for fname, content in ssr_answers[question_item.id] %}
  <pre class="ssr-code-block" data-file="{{ fname }}"
       data-question="{{ question_item.id }}" data-index="{{ loop.index }}">
    <code>{{ content }}</code>
  </pre>
  {% endfor %}
</div>
{% endif %}
```

Apply in BOTH: subject listing mode and single question mode.

### 3. JavaScript: `sppucodes/static/js/script.js`

In `loadAnswer()`, SSR-first then API fallback:
```javascript
const questionId = button.closest('.question-item').getAttribute('id');
const ssrBlock = document.querySelector(
    `.ssr-code-block[data-question="${questionId}"][data-file="${fileName}"]`
);
if (ssrBlock) {
    trimmedText = ssrBlock.textContent.trim();
    // render from SSR
} else {
    trimmedText = await fetchAnswerText(subject, questionNo, fileIndex);
}
```

`.question-item` already has `id` attribute matching question ID — no selector changes needed.

### 4. Structured Data: Replace placeholder answer text in ld+json with real code snippets

---

## Files to Modify

| File | Changes |
|------|---------|
| `sppucodes/src/routes/subjects.py` | Add `_get_ssr_answers()`; import `_read_answer_file`; pass `ssr_answers` to template |
| `sppucodes/templates/subject.html` | Add hidden SSR `<pre><code>` blocks; enhance ld+json snippets |
| `sppucodes/static/js/script.js` | `loadAnswer()`: SSR-first with API fallback |

## Verification

1. `/cgl` source → 9 .cpp files in `<pre class="ssr-code-block">` (~25-30 KB total)
2. `/ann` source → 10 .py pre-rendered; .ipynb NOT present (~18 KB)
3. `/ds` source → 19 .py/.md pre-rendered; CSVs NOT present (~32 KB)
4. `/cgl/scan-fill` → only one question's answer pre-rendered
5. Click notebook button (ANN B5) → still fetches via API (no SSR for .ipynb)
