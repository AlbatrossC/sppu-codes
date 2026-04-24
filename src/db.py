import os
import psycopg2
from .config import BASE_DIR, DATABASE_URL


SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")

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
    conn = get_db_connection()
    if not conn:
        print("Warning: DATABASE_URL not set. Database features disabled.")
        return

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
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()


def save_submission(name, email, subject, code):
    """Saves a code submission to the database."""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO code_submissions (name, email, subject, code)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (name, email, subject, code)
                )
        return True
    except Exception as e:
        print(f"Submit Error: {e}")
        return False
    finally:
        conn.close()


def save_contact(name, email, message):
    """Saves a contact message to the database."""
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
