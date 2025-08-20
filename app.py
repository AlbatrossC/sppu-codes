from flask import Flask, render_template, send_from_directory, abort, request, redirect, url_for, flash, jsonify
import os
import psycopg2
import json
import requests
from datetime import datetime
from functools import lru_cache
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'karltos'

# =============================================================================
# CONFIGURATION AND INITIALIZATION
# =============================================================================

# Directory paths
BASE_DIR = os.path.join(os.path.dirname(__file__), 'static')
QUESTIONS_DIR = os.path.join(os.path.dirname(__file__), 'questions')
downloads_folder = os.path.join(app.root_path, 'downloads')

# Database configuration
# For Local Testing
# DATABASE_URL = "postgresql://username:password@localhost:5432/database_name"
DATABASE_URL = os.getenv("DATABASE_URL")

# =============================================================================
# DATABASE UTILITIES
# =============================================================================

def connect_db():
    """Establish database connection with error handling"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

# =============================================================================
# MAIN ROUTES
# =============================================================================

@app.route('/')
def index():
    """Render the home page"""
    return render_template('index.html')

@app.route('/download')
def download():
    """Render the downloads page"""
    return render_template('download.html')

@app.route('/downloads/<filename>')
def download_file(filename):
    """Serve downloadable files from the downloads directory"""
    return send_from_directory(downloads_folder, filename)

# =============================================================================
# FORM HANDLING ROUTES
# =============================================================================

@app.route('/submit', methods=["GET", "POST"])
def submit():
    """Handle code submission form - both display and processing"""
    conn = connect_db()
    if conn is None:
        flash("Database Connection error. Please try again later", "error")
        return render_template("submit.html")

    if request.method == "POST":
        try:
            cur = conn.cursor()
            name = request.form.get("name")
            year = request.form.get("year")
            branch = request.form.get("branch")
            subject = request.form.get("subject")
            question = request.form.get("question")
            answer = request.form.get("answer")

            if name and year and branch and subject and question and answer:
                cur.execute("INSERT INTO codes (name, year, branch, subject, question, answer) VALUES (%s,%s,%s,%s,%s,%s)",
                            (name, year, branch, subject, question, answer))
                conn.commit()
                flash("Code Sent Successfully! Thank you", "success")
                return redirect(url_for('submit'))
            else:
                flash("PLEASE FILL ALL NECESSARY FIELDS", "error")
        except Exception as e:
            conn.rollback()
            flash(f"Error inserting data: {e}", "error")
        finally:
            if 'cur' in locals() and cur:
                cur.close()
            if conn:
                conn.close()
    return render_template("submit.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    """Handle contact form - both display and processing"""
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        if name and email and message:
            conn = None
            try:
                conn = connect_db()
                if conn is None:
                    flash("Database connection error. Please try again later.", "error")
                    return redirect(url_for('contact'))

                cur = conn.cursor()
                cur.execute("INSERT INTO contacts (name, email, message) VALUES (%s, %s, %s)",
                          (name, email, message))
                conn.commit()
                flash("Message sent successfully! Thank you", "success")
            except Exception as e:
                if conn: 
                    conn.rollback()
                flash(f"Error inserting data: {e}", "error")
            finally:
                if 'cur' in locals() and cur: 
                    cur.close()
                if conn: 
                    conn.close()
            return redirect(url_for('contact'))
        else:
            flash("PLEASE FILL ALL NECESSARY FIELDS", "error")
    return render_template("contact.html")

# =============================================================================
# QUESTION PAPER ROUTES
# =============================================================================

# Question paper data initialization

# Question paper data initialization
QUESTION_PAPER_DATA = {}
SEO_DATA = {}
data_json_path = os.path.join(os.path.dirname(__file__), 'static', 'pyqs', 'questionpapers.json')
seo_json_path = os.path.join(os.path.dirname(__file__), 'static', 'pyqs', 'viewerseo.json')

def load_question_paper_data():
    """Load question paper data from JSON file on application startup"""
    global QUESTION_PAPER_DATA
    try:
        with open(data_json_path, 'r') as f:
            QUESTION_PAPER_DATA = json.load(f)
        print("SUCCESS: questionpapers.json loaded successfully.")
    except FileNotFoundError:
        print(f"ERROR: questionpapers.json not found at {data_json_path}")
    except json.JSONDecodeError as e:
        print(f"ERROR: questionpapers.json is not valid JSON! Details: {e}")

def load_seo_data():
    """Load SEO data from JSON file on application startup"""
    global SEO_DATA
    try:
        with open(seo_json_path, 'r') as f:
            seo_list = json.load(f)
            # Convert list to dictionary for faster lookup by link
            SEO_DATA = {item['link']: item for item in seo_list}
        print("SUCCESS: viewerseo.json loaded successfully.")
    except FileNotFoundError:
        print(f"ERROR: viewerseo.json not found at {seo_json_path}")
        SEO_DATA = {}
    except json.JSONDecodeError as e:
        print(f"ERROR: viewerseo.json is not valid JSON! Details: {e}")
        SEO_DATA = {}

# Initialize data on startup
load_question_paper_data()
load_seo_data()

@app.route('/questionpapers')
def select_page():
    # Group data from SEO_DATA
    organized_data = defaultdict(lambda: defaultdict(list))

    for item in SEO_DATA.values():
        branch = item.get("branch", "Unknown Branch")
        sem = f"Semester {item.get('sem', 'Unknown')}"
        organized_data[branch][sem].append(item)

    return render_template('select.html', organized_data=organized_data)

@app.route('/questionpapers/<subject_name>')
def viewer_page(subject_name):
    """Display PDF viewer page for selected subject with all available question papers"""
    raw_pdf_urls = [
        url 
        for branch in QUESTION_PAPER_DATA.values()
        for semester in branch.values()
        for subject, urls in semester.items()
        if subject == subject_name
        for url in urls
    ]
    
    if not raw_pdf_urls:
        abort(404, description=f"No question papers found for subject: {subject_name}")
    
    pdf_data_list = [
        {'filename': url.split('/')[-1].split('?')[0], 'url': url}
        for url in raw_pdf_urls
    ]

    # Get SEO data for current route
    current_route = f"/questionpapers/{subject_name}"
    seo_info = SEO_DATA.get(current_route, {})
    
    # Prepare SEO metadata
    seo_data = {
        'title': f"Sppu {seo_info.get('subjectName', subject_name.replace('_', ' ').title())} Question Papers: Sppu Codes",
        'description': seo_info.get('description', f"SPPU {subject_name.replace('_', ' ').title()} Question Papers - View PDFs for selected subjects"),
        'keywords': ', '.join(seo_info.get('keywords', [])) if seo_info.get('keywords') else f"sppu, {subject_name.replace('_', ' ')}, question papers",
        'subject_name': seo_info.get('subjectName', subject_name.replace('_', ' ').title())
    }

    return render_template('viewer.html', 
                         subject_name=subject_name, 
                         pdf_data_for_js=pdf_data_list,
                         seo_data=seo_data)

    print("hey",pdf_data_list)

# =============================================================================
# SUBJECT AND QUESTION ROUTES
# =============================================================================

@app.route("/<subject_code>")
@app.route("/<subject_code>/<question_id>")
def question(subject_code, question_id=None):
    """Display subject page with questions, optionally highlighting a specific question"""
    json_file_path = os.path.join(QUESTIONS_DIR, f"{subject_code}.json")
    
    if not os.path.exists(json_file_path):
        abort(404, description="Subject not found")

    with open(json_file_path, 'r') as f:
        data = json.load(f)

    subject = data.get("default", {})
    questions = data.get("questions", [])
    question_dict = {q["id"]: q for q in questions}

    # Default metadata
    title = f"SPPU Codes - {subject.get('subject_name', '')}"
    description = subject.get("description", "")
    keywords = subject.get("keywords", [])
    url = subject.get("url", f"https://sppucodes.vercel.app/{subject_code}")
    question_paper_url = subject.get("question_paper_url")

    # Override metadata if specific question selected
    selected_question = question_dict.get(question_id) if question_id else None
    if selected_question:
        title = selected_question["title"]
        description = f"SPPU Codes: {selected_question['question']}"
        keywords = [selected_question["question"], selected_question["title"]] + subject.get("keywords", [])
        url = f"https://sppucodes.vercel.app/{subject_code}/{question_id}"

    # Group questions by category
    groups = {}
    for q in questions:
        groups.setdefault(q["group"], []).append(q)

    return render_template(
        "subject.html",
        title=title,
        description=description,
        keywords=keywords,
        url=url,
        subject_code=subject_code,
        subject_name=subject.get("subject_name", ""),
        groups=groups,
        sorted_groups=sorted(groups.keys()),
        question=selected_question,
        question_paper_url=question_paper_url
    )

# =============================================================================
# FILE SERVING ROUTES
# =============================================================================

@app.route('/answers/<subject>/<filename>')
def get_answer(subject, filename):
    """Serve answer files for specific subjects"""
    try:
        base_dir = os.path.abspath(os.path.dirname(__file__))
        answers_dir = os.path.join(base_dir, 'answers', subject)
        if not os.path.exists(answers_dir): 
            abort(404)
        full_path = os.path.join(answers_dir, filename)
        if not os.path.exists(full_path): 
            abort(404)
        return send_from_directory(answers_dir, filename)
    except Exception: 
        abort(404)

@app.route('/images/<filename>')
def get_image(filename):
    """Serve static image files"""
    base_dir = os.path.abspath(os.path.dirname(__file__))
    images_dir = os.path.join(base_dir, 'images')
    return send_from_directory(images_dir, filename)

@app.route('/sitemap.xml')
def sitemap():
    """Serve sitemap for SEO"""
    return send_from_directory('.', 'sitemap.xml')

@app.route('/robots.txt')
def robots():
    """Serve robots.txt for web crawlers"""
    return send_from_directory('.', 'robots.txt')

@app.route('/sw.js')
def service_worker():
    """Serve the service worker script"""
    return send_from_directory('.', 'sw.js')

@app.route('/ads.txt')
def ads_verify():
    return send_from_directory('.', 'ads.txt')

# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors with custom error page"""
    description = e.description if hasattr(e, 'description') else "Page not found."
    return render_template('error.html', error_code=404, error_message=description), 404

@app.errorhandler(500)
def internal_server_error(e):
    """Handle 500 errors with custom error page"""
    description = e.description if hasattr(e, 'description') else "An internal server error occurred."
    return render_template('error.html', error_code=500, error_message=description), 500

# =============================================================================
# REQUEST PROCESSING
# =============================================================================

@app.after_request
def finalize_markup(response):
    """Inject analytics scripts into HTML responses before sending to client"""
    if response.content_type.startswith('text/html'):
        snippet_a = """
        <script>
        (function(w,d,x,s,i,e,t){
            w[x]=w[x]||function(){(w[x].q=w[x].q||[]).push(arguments)};
            e=d.createElement(s); e.async=1;
            e.src="https://www.clarity.ms/tag/"+i;
            t=d.getElementsByTagName("head")[0] || d.getElementsByTagName(s)[0];
            t.parentNode.insertBefore(e,t);
        })(window,document,"clarity","script","qnqi8o9y94");
        </script>
        """

        snippet_b = """
        <script defer src="https://cloud.umami.is/script.js" data-website-id="52ac9be0-a82e-4e1b-a1eb-38a1036db726"></script>
        """

        payload = snippet_a + snippet_b
        response.direct_passthrough = False
        try:
            response.set_data(response.get_data().replace(
                b'</body>',
                payload.encode('utf-8') + b'</body>'
            ))
        except Exception:
            pass
    return response

# =============================================================================
# APPLICATION ENTRY POINT
# =============================================================================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int("3000"), debug=True)