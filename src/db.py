import psycopg2
from .config import DATABASE_URL

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
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS submissions (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100),
                        year VARCHAR(10),
                        branch VARCHAR(50),
                        subject VARCHAR(200),
                        question TEXT,
                        answer TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS contacts (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100),
                        email VARCHAR(150),
                        message TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()


def save_submission(name, year, branch, subject, question, answer):
    """Saves a code submission to the database."""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO submissions (name, year, branch, subject, question, answer) VALUES (%s, %s, %s, %s, %s, %s)",
                    (name, year, branch, subject, question, answer)
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
                    "INSERT INTO contacts (name, email, message) VALUES (%s, %s, %s)",
                    (name, email, message)
                )
        return True
    except Exception as e:
        print(f"Contact Error: {e}")
        return False
    finally:
        conn.close()
