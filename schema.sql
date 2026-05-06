-- Schema definitions for Cloudflare D1 (pending migration)
-- These table definitions are ready for D1 SQL dialect.
-- Note: D1 uses SQLite-compatible syntax; BIGSERIAL should be changed to INTEGER PRIMARY KEY AUTOINCREMENT.

CREATE TABLE IF NOT EXISTS code_submissions (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150),
    subject VARCHAR(200) NOT NULL,
    question TEXT,
    code TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS contact_messages (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS api_requests (
    id BIGSERIAL PRIMARY KEY,
    subject VARCHAR(100) NOT NULL,
    question_no VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('success', 'not_found')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS paper_downloads (
    id BIGSERIAL PRIMARY KEY,
    fingerprint_id VARCHAR(255) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    download_count INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_code_submissions_created_at
ON code_submissions (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_contact_messages_created_at
ON contact_messages (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_api_requests_subject_question
ON api_requests (subject, question_no, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_paper_downloads_subject
ON paper_downloads (subject, created_at DESC);
