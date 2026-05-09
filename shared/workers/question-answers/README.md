# Question Answers Worker

Cloudflare Worker for the SPPU PYQ platform that generates exam-oriented answers with Groq, streams them to the frontend, and caches completed answers in Cloudflare D1 using `question_id` as the unique cache key.

## Architecture Overview

The flow is:

1. Flask SSR page renders questions and metadata into `viewer.html`.
2. User clicks `Generate Answer` on a question card.
3. Frontend sends the question payload to this worker at `POST /api/answers/stream`.
4. Worker checks D1 for `question_id`.
5. If cached, the answer is streamed back immediately and cache counters are updated.
6. If not cached, the worker streams Groq output token-by-token to the browser while accumulating the final answer.
7. When generation completes, the worker stores the answer and analytics metadata in D1.

## Folder Structure

```text
shared/workers/question-answers/
├── src/
│   ├── index.ts
│   ├── routes/
│   │   └── answer.ts
│   ├── services/
│   │   └── groq.ts
│   ├── db/
│   │   └── question-answer-repo.ts
│   ├── prompts/
│   │   └── answer-prompt.ts
│   ├── utils/
│   │   ├── cors.ts
│   │   ├── hash.ts
│   │   ├── json.ts
│   │   └── request.ts
│   ├── types/
│   │   └── env.ts
│   ├── streaming/
│   │   └── text.ts
│   └── constants/
│       └── config.ts
├── schema.sql
├── wrangler.toml
├── package.json
├── tsconfig.json
├── .dev.vars
└── README.md
```

## D1 Schema

Only one table is used: `question_answers`.

Fields included:

- `id`
- `question_id`
- `pdf_id`
- `pdf_url`
- `subject_slug`
- `semester`
- `branch`
- `question_text`
- `generated_answer`
- `model_used`
- `answer_hash`
- `cache_hit_count`
- `generate_button_clicks`
- `worker_response_time_ms`
- `prompt_version`
- `generation_status`
- `generation_error`
- `created_at`
- `updated_at`
- `last_accessed_at`

`question_id` is unique and acts as the cache key.

## Local Development Setup

### 1. Install dependencies

```bash
cd shared/workers/question-answers
npm install
```

### 2. Configure `.dev.vars`

Set your Groq key:

```env
GROQ_API_KEY=your-groq-api-key
```

### 3. Create the D1 database

```bash
npm run db:create
```

Copy the returned `database_id` into `wrangler.toml`.

### 4. Run the schema migration

```bash
npm run db:execute
```

### 5. Run local worker development

```bash
npm run dev
```

For remote D1 preview:

```bash
npm run dev:remote
```

## Wrangler Commands

```bash
npm run dev
npm run dev:remote
npm run deploy
npm run typecheck
```

## D1 Migration Commands

```bash
npm run db:create
npm run db:execute
npm run db:migrate
```

You can also run ad hoc queries:

```bash
wrangler d1 execute question-answers-db --command="SELECT question_id, generation_status, cache_hit_count FROM question_answers ORDER BY updated_at DESC LIMIT 20"
```

## Deployment Commands

```bash
npm run deploy
```

Before first deployment, set the Groq secret:

```bash
npm run secret:groq
```

## Environment Variables

Worker env:

- `GROQ_API_KEY`: required
- `GROQ_MODEL`: optional, defaults to `llama-3.3-70b-versatile`
- `PROMPT_VERSION`: optional prompt version tag persisted in D1
- `ALLOWED_ORIGIN`: optional CORS origin, defaults to `*`

Flask env:

- `QUESTION_ANSWER_WORKER_URL=https://your-worker-subdomain.workers.dev`

## Streaming Behavior

The worker exposes `POST /api/answers/stream` and returns a plain text stream.

- Cached response: returns the stored answer immediately as a stream.
- Miss response: forwards Groq tokens to the client as they arrive.
- Frontend behavior: reads `ReadableStream` chunks, accumulates markdown, and re-renders the answer panel live.
- Cancellation: the browser uses `AbortController`; the UI stops reading immediately.

## Cache Flow

### Cache hit

1. Find row by `question_id`
2. If `generation_status = complete` and answer exists:
3. Increment `cache_hit_count`
4. Increment `generate_button_clicks`
5. Update timestamps
6. Stream cached answer

### Cache miss

1. Upsert row with `generation_status = generating`
2. Increment `generate_button_clicks`
3. Stream Groq output
4. Save final answer, hash, model, and response time
5. Mark row as `complete`

### Failure

1. Persist `generation_status = failed`
2. Store error text in `generation_error`
3. Keep timestamps updated for debugging

## Frontend Integration

The Flask viewer sends this payload:

```json
{
  "questionId": "7dbf9c1ee1b1_q1_a",
  "pdfId": "7dbf9c1ee1b1",
  "pdfUrl": "https://...",
  "subjectSlug": "human-computer-interface-ele-i-aids",
  "subjectName": "Human Computer Interface Ele I",
  "semester": "sem-5",
  "branch": "aids",
  "questionNumber": "Q1",
  "subquestion": "a",
  "marks": "6",
  "paperLabel": "2024 May Jun Endsem",
  "questionText": "What is meant by design?"
}
```

## Troubleshooting

- `HTTP 400 invalid request payload`
  Missing required question fields from the frontend.

- `Groq request failed`
  Verify `GROQ_API_KEY`, model name, and Groq account limits.

- `D1 updates not visible`
  Re-run `npm run db:execute` and confirm the worker is bound to the correct D1 database id.

- `CORS errors`
  Set `ALLOWED_ORIGIN` to your site origin instead of `*` if you want a stricter policy.

- `No answer generation from Flask`
  Verify `QUESTION_ANSWER_WORKER_URL` is set in the Flask app environment and points to the deployed worker.
