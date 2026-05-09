CREATE TABLE IF NOT EXISTS question_answers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  question_id TEXT NOT NULL UNIQUE,
  pdf_id TEXT NOT NULL,
  pdf_url TEXT NOT NULL,
  subject_slug TEXT NOT NULL,
  semester TEXT NOT NULL,
  branch TEXT NOT NULL,
  question_text TEXT NOT NULL,
  generated_answer TEXT,
  model_used TEXT,
  answer_hash TEXT,
  cache_hit_count INTEGER NOT NULL DEFAULT 0,
  generate_button_clicks INTEGER NOT NULL DEFAULT 0,
  worker_response_time_ms INTEGER,
  prompt_version TEXT NOT NULL,
  generation_status TEXT NOT NULL DEFAULT 'pending',
  generation_error TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_accessed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_question_answers_subject_slug
  ON question_answers(subject_slug);

CREATE INDEX IF NOT EXISTS idx_question_answers_pdf_id
  ON question_answers(pdf_id);

CREATE INDEX IF NOT EXISTS idx_question_answers_generation_status
  ON question_answers(generation_status);
