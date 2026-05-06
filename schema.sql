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

ALTER TABLE code_submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE contact_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE paper_downloads ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS code_submissions_insert_anon ON code_submissions;
CREATE POLICY code_submissions_insert_anon
ON code_submissions
FOR INSERT
TO public
WITH CHECK (true);

DROP POLICY IF EXISTS contact_messages_insert_anon ON contact_messages;
CREATE POLICY contact_messages_insert_anon
ON contact_messages
FOR INSERT
TO public
WITH CHECK (true);

DROP POLICY IF EXISTS api_requests_insert_anon ON api_requests;
CREATE POLICY api_requests_insert_anon
ON api_requests
FOR INSERT
TO public
WITH CHECK (true);

DROP POLICY IF EXISTS paper_downloads_insert_anon ON paper_downloads;
CREATE POLICY paper_downloads_insert_anon
ON paper_downloads
FOR INSERT
TO public
WITH CHECK (true);
