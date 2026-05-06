-- sppucodes-db D1 Schema (SQLite-compatible)
-- Run: wrangler d1 execute sppucodes-db --file=schema.sql

CREATE TABLE IF NOT EXISTS code_submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    subject TEXT NOT NULL,
    question TEXT,
    code TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS contact_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS api_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT NOT NULL,
    question_no TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('success', 'not_found')),
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS paper_downloads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fingerprint_id TEXT NOT NULL,
    subject TEXT NOT NULL,
    download_count INTEGER NOT NULL DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(fingerprint_id, subject)
);

CREATE INDEX IF NOT EXISTS idx_code_submissions_created_at
ON code_submissions (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_contact_messages_created_at
ON contact_messages (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_api_requests_subject_question
ON api_requests (subject, question_no, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_paper_downloads_subject
ON paper_downloads (subject, created_at DESC);
