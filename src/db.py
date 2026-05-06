import os
import threading
import psycopg2
import requests
from .config import BASE_DIR, DATABASE_URL, SUPABASE_KEY, SUPABASE_URL


SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")
_db_init_lock = threading.Lock()
_db_initialized = False
_http = requests.Session()


def _has_supabase_rest():
    return bool(SUPABASE_URL and SUPABASE_KEY)


def _supabase_headers(prefer="return=minimal"):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }
    if prefer:
        headers["Prefer"] = prefer
    return headers


def _supabase_table_url(table_name):
    return f"{SUPABASE_URL}/rest/v1/{table_name}"


def _insert_row(table_name, payload):
    if not _has_supabase_rest():
        return False

    try:
        response = _http.post(
            _supabase_table_url(table_name),
            json=payload,
            headers=_supabase_headers(),
            timeout=2.5,
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Supabase insert error for {table_name}: {e}")
        if getattr(e, "response", None) is not None:
            print(f"Supabase response: {e.response.text}")
        return False

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    if not DATABASE_URL:
        return None
    try:
        return psycopg2.connect(DATABASE_URL, sslmode='require')
    except Exception as e:
        print(f"Database connection error: {e}")
        return None


def init_db():
    """Creates necessary tables if they don't exist."""
    global _db_initialized
    if _db_initialized:
        return

    with _db_init_lock:
        if _db_initialized:
            return

        if _init_db_once():
            _db_initialized = True


def _init_db_once():
    """Creates necessary tables if they don't exist."""
    conn = get_db_connection()
    if not conn:
        print("Warning: DATABASE_URL not set. Schema auto-migration skipped.")
        return False

    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as schema_file:
            schema_sql = schema_file.read()

        with conn:
            with conn.cursor() as cur:
                cur.execute(schema_sql)
                cur.execute(
                    """
                    ALTER TABLE paper_downloads
                    ADD COLUMN IF NOT EXISTS download_count INTEGER
                    """
                )
                cur.execute(
                    """
                    UPDATE paper_downloads
                    SET download_count = 1
                    WHERE download_count IS NULL
                    """
                )
                cur.execute(
                    """
                    ALTER TABLE paper_downloads
                    ALTER COLUMN download_count SET NOT NULL
                    """
                )
                cur.execute(
                    """
                    ALTER TABLE code_submissions
                    ADD COLUMN IF NOT EXISTS question TEXT
                    """
                )
        print("Database initialized successfully.")
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False
    finally:
        conn.close()


def save_submission(name, email, subject, question, code):
    """Saves a code submission to the database."""
    payload = {
        "name": name,
        "email": email,
        "subject": subject,
        "question": question,
        "code": code,
    }
    if _has_supabase_rest():
        if _insert_row("code_submissions", payload):
            return True

    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO code_submissions (name, email, subject, question, code)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (name, email, subject, question, code)
                )
        return True
    except Exception as e:
        print(f"Submit Error: {e}")
        return False
    finally:
        conn.close()


def save_contact(name, email, message):
    """Saves a contact message to the database."""
    payload = {
        "name": name,
        "email": email,
        "message": message,
    }
    if _has_supabase_rest():
        if _insert_row("contact_messages", payload):
            return True

    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO contact_messages (name, email, message)
                    VALUES (%s, %s, %s)
                    """,
                    (name, email, message)
                )
        return True
    except Exception as e:
        print(f"Contact Error: {e}")
        return False
    finally:
        conn.close()


def save_api_request(subject_link, question_no, status):
    """Saves an API request log entry."""
    payload = {
        "subject": subject_link,
        "question_no": str(question_no),
        "status": status,
    }
    if _has_supabase_rest():
        if _insert_row("api_requests", payload):
            return True

    conn = get_db_connection()
    if not conn:
        return False

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO api_requests (subject, question_no, status)
                    VALUES (%s, %s, %s)
                    """,
                    (subject_link, str(question_no), status),
                )
        return True
    except Exception as e:
        print(f"API log error: {e}")
        return False
    finally:
        conn.close()


def save_paper_download(fingerprint_id, subject):
    """Saves a paper download log entry."""
    payload = {
        "fingerprint_id": fingerprint_id,
        "subject": subject,
        "download_count": 1,
    }
    if _has_supabase_rest():
        if _insert_row("paper_downloads", payload):
            return True

    conn = get_db_connection()
    if not conn:
        return False

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO paper_downloads (fingerprint_id, subject, download_count)
                    SELECT
                        %s,
                        %s,
                        COALESCE(MAX(download_count), 0) + 1
                    FROM paper_downloads
                    WHERE fingerprint_id = %s
                    """,
                    (fingerprint_id, subject, fingerprint_id),
                )
        return True
    except Exception as e:
        print(f"Paper download log error: {e}")
        return False
    finally:
        conn.close()
