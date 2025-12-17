from flask import Flask, render_template, send_from_directory, abort, request, redirect, url_for, flash, jsonify
import os
import psycopg2
import json
import requests
from datetime import datetime
from functools import lru_cache
from collections import defaultdict
from flask import render_template
from werkzeug.exceptions import HTTPException
import glob



app = Flask(__name__)
app.secret_key = 'karltos'
MAINTENANCE_MODE = os.getenv("MAINTENANCE_MODE", "false").lower() == "true"
MAINTENANCE_BYPASS_IP = os.getenv("MAINTENANCE_BYPASS_IP")


@app.before_request
def maintenance():
    if MAINTENANCE_MODE:
        # Allow bypass for your IP (optional)
        if MAINTENANCE_BYPASS_IP and request.remote_addr == MAINTENANCE_BYPASS_IP:
            return  # let you access normally
        
        # Allow static files so your maintenance page loads properly
        if request.path.startswith("/static"):
            return
        
        # Show maintenance page for everyone else
        return render_template("maintenance.html"), 503


# --- BEGIN: Local fallback redirect for /questionpapers to /question-papers ---
@app.before_request
def questionpapers_redirect():
    # Only redirect if path starts with /questionpapers (not /question-papers)
    # and not already at /question-papers
    path = request.path
    if path == "/questionpapers":
        return redirect("/question-papers", code=301)
    elif path.startswith("/questionpapers/"):
        return redirect("/question-papers" + path[len("/questionpapers"):], code=301)
# --- END: Local fallback redirect ---

# =============================================================================
# CONFIGURATION AND INITIALIZATION
# =============================================================================

# Directory paths
BASE_DIR = os.path.join(os.path.dirname(__file__), 'static')
QUESTIONS_DIR = os.path.join(os.path.dirname(__file__), 'questions')

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


# =============================================================================
# FORM HANDLING ROUTES
# =============================================================================

@app.route('/submit', methods=["GET", "POST"])
def submit():
    """Handle code submission form - both display and processing"""
    if request.method == "POST":
        # Get form data
        name = request.form.get("name", "").strip()
        year = request.form.get("year", "").strip()
        branch = request.form.get("branch", "").strip()
        subject = request.form.get("subject", "").strip()
        question = request.form.get("question", "").strip()
        answer = request.form.get("answer", "").strip()

        # Validate required fields
        if not all([year, branch, subject, question, answer]):
            flash("Please fill all required fields", "error")
            return render_template("submit.html")

        # Set default name if empty
        if not name:
            name = "Anonymous"

        conn = None
        cur = None
        try:
            conn = connect_db()
            if conn is None:
                flash("Database connection error. Please try again later.", "error")
                return render_template("submit.html")

            cur = conn.cursor()
            cur.execute(
                "INSERT INTO codes (name, year, branch, subject, question, answer) VALUES (%s, %s, %s, %s, %s, %s)",
                (name, year, branch, subject, question, answer)
            )
            conn.commit()
            flash("Code submitted successfully! Thank you for your contribution.", "success")
            return redirect(url_for('submit'))

        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Database error: {e}")
            flash("An error occurred while submitting. Please try again.", "error")
            return render_template("submit.html")

        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    return render_template("submit.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    """Handle contact form - both display and processing"""
    if request.method == "POST":
        # Get and validate form data
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        if not all([name, email, message]):
            flash("Please fill all required fields", "error")
            return render_template("contact.html")

        # Basic email validation
        if "@" not in email or "." not in email:
            flash("Please enter a valid email address", "error")
            return render_template("contact.html")

        conn = None
        cur = None
        try:
            conn = connect_db()
            if conn is None:
                flash("Database connection error. Please try again later.", "error")
                return render_template("contact.html")

            cur = conn.cursor()
            cur.execute(
                "INSERT INTO contacts (name, email, message) VALUES (%s, %s, %s)",
                (name, email, message)
            )
            conn.commit()
            flash("Message sent successfully! We'll get back to you soon.", "success")
            return redirect(url_for('contact'))

        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Database error: {e}")
            flash("An error occurred while sending your message. Please try again.", "error")
            return render_template("contact.html")

        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    return render_template("contact.html")

# =============================================================================
# QUESTION PAPER ROUTES
# =============================================================================

@app.route('/question-papers')
def select_page():
    """
    Dynamically load all branches, semesters, and subjects from question-papers/*.json
    and render the selection UI.
    """
    qp_dir = os.path.join(os.path.dirname(__file__), 'question-papers')
    organized_data = {}  # {branch_name: {semester_display: [subjects]}}

    for file_path in glob.glob(os.path.join(qp_dir, '*.json')):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            branch_name = data.get('branch_name', os.path.splitext(os.path.basename(file_path))[0])
            semesters = data.copy()
            semesters.pop('branch_name', None)
            branch_semesters = {}
            for sem_key, subjects in semesters.items():
                # sem_key: 'sem-1', 'sem-2', etc.
                sem_number = sem_key.split('-')[-1] if '-' in sem_key else sem_key
                sem_display = f"Semester {sem_number}"
                subject_list = []
                for subject_link, subject_data in subjects.items():
                    subject_list.append({
                        'subjectName': subject_data.get('subject_name', subject_link.replace('-', ' ').title()),
                        'link': subject_link
                    })
                if subject_list:
                    branch_semesters[sem_display] = subject_list
            if branch_semesters:
                organized_data[branch_name] = branch_semesters
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            continue

    return render_template('select.html', organized_data=organized_data)


@app.route('/question-papers/<subject_name>')
def viewer_page(subject_name):
    """
    Display PDF viewer page for selected subject with all available question papers.
    Now fetches PDFs by scanning all question-papers/*.json and all branches/semesters/subjects.
    No SEO/viewerseo.json dependency.
    """
    qp_dir = os.path.join(os.path.dirname(__file__), 'question-papers')
    pdf_urls = []
    subject_display_name = subject_name.replace('-', ' ').replace('_', ' ').title()

    # Scan all question-papers/*.json for the subject
    for file_path in glob.glob(os.path.join(qp_dir, '*.json')):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Each file: {branch_name, sem-1: {...}, sem-2: {...}, ...}
            for sem_key, subjects in data.items():
                if sem_key == 'branch_name':
                    continue
                # Fix: Only process if subjects is a dict
                if not isinstance(subjects, dict):
                    continue
                for subj_key, subj_data in subjects.items():
                    if subj_key == subject_name:
                        # subj_data: {subject_name, seo_data, pdf_links}
                        pdfs = subj_data.get('pdf_links', [])
                        pdf_urls.extend(pdfs)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            continue

    if not pdf_urls:
        abort(404, description=f"No question papers found for subject: {subject_name}")

    pdf_data_list = [
        {'filename': url.split('/')[-1].split('?')[0], 'url': url}
        for url in pdf_urls
    ]

    # Basic SEO data (no viewerseo.json)
    seo_data = {
        'title': f"SPPU {subject_display_name} Question Papers: SPPU Codes",
        'description': f"SPPU {subject_display_name} Question Papers - View PDFs for selected subjects",
        'keywords': f"sppu, {subject_display_name}, question papers",
        'subject_name': subject_display_name,
        'branch': '',
        'semester': ''
    }

    return render_template('viewer.html',
                           subject_name=subject_name,
                           pdf_data_for_js=pdf_data_list,
                           seo_data=seo_data)

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

    with open(json_file_path, 'r', encoding='utf-8') as f:
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

@app.route('/6c012816727f4acc99f6b950165a04c0.txt')
def index_verify():
    return send_from_directory('.', '6c012816727f4acc99f6b950165a04c0.txt')

# =============================================================================
# ERROR HANDLERS
# =============================================================================
@app.route('/api/error-page-data')
def error_page_data():
    """
    API endpoint to provide all available subjects and question papers
    for the 404 error page and search functionality.
    """
    try:
        # Get all subject codes from questions directory
        subjects = []
        if os.path.exists(QUESTIONS_DIR):
            for file in os.listdir(QUESTIONS_DIR):
                if file.endswith('.json'):
                    try:
                        with open(os.path.join(QUESTIONS_DIR, file), 'r', encoding='utf-8') as f:
                            subject_data = json.load(f)
                            default = subject_data.get("default", {})
                            subject_code = file.replace('.json', '')

                            subjects.append({
                                'code': subject_code,
                                'name': default.get('subject_name', subject_code.upper()),
                                'href': f'/{subject_code}'
                            })
                    except Exception as e:
                        print(f"Error reading {file}: {e}")
                        continue

        # Sort subjects alphabetically by code
        subjects.sort(key=lambda x: x['code'])

        # Get all question papers from SEO data
        question_papers = []
        seo_index, seo_raw = load_seo_data()

        branches = seo_raw.get('branches', {})
        for branch_key, branch_data in branches.items():
            branch_name = branch_data.get('name', branch_key)
            semesters = branch_data.get('semesters', {})

            for sem_key, subjects_list in semesters.items():
                sem_number = sem_key.split('-')[-1] if '-' in sem_key else sem_key

                for subject in subjects_list:
                    link = subject.get('link')
                    if link:
                        question_papers.append({
                            'name': subject.get('subjectName', link.replace('-', ' ').title()),
                            'link': link,
                            'branch': branch_name,
                            'semester': sem_number,
                            'href': f'/questionpapers/{link}'
                        })

        # Sort question papers by branch, then semester, then name
        question_papers.sort(key=lambda x: (x['branch'], int(x['semester']) if x['semester'].isdigit() else 0, x['name']))

        return jsonify({
            'subjects': subjects,
            'questionPapers': question_papers
        })

    except Exception as e:
        print(f"Error generating error page data: {e}")
        return jsonify({
            'subjects': [],
            'questionPapers': [],
            'error': str(e)
        }), 500
    
    
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

@app.route('/api/<subject_code>/<question_no>')
def get_answer_api(subject_code, question_no):
    """
    API endpoint to retrieve answer file content by subject code and question number.
    Returns plain text content of the file(s). Multiple files are separated by dashes.
    """
    try:
        # Load the JSON file for the subject
        json_file_path = os.path.join(QUESTIONS_DIR, f"{subject_code}.json")
        
        if not os.path.exists(json_file_path):
            # Get all available subjects
            available_subjects = []
            if os.path.exists(QUESTIONS_DIR):
                for file in os.listdir(QUESTIONS_DIR):
                    if file.endswith('.json'):
                        try:
                            with open(os.path.join(QUESTIONS_DIR, file), 'r', encoding='utf-8') as f:
                                subject_data = json.load(f)
                                # Get subject_name from default section
                                subject_name = subject_data.get("default", {}).get("subject_name", "Unknown")
                                code = file.replace('.json', '')
                                available_subjects.append(f"{code} -> {subject_name}")
                        except:
                            continue
            
            response = "No subject found\n\n"
            response += "List of all available subjects:\n"
            for subject in available_subjects:
                response += f"{subject}\n"
            
            return response, 404, {'Content-Type': 'text/plain; charset=utf-8'}
        
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        questions = data.get("questions", [])
        
        # Find the question with matching question_no
        target_question = None
        for q in questions:
            if q.get("question_no") == question_no:
                target_question = q
                break
        
        if not target_question:
            # Build list of available questions
            response = "No question found\n\n"
            response += "List of available questions:\n"
            for idx, q in enumerate(questions, 1):
                q_title = q.get("title", "Untitled")
                q_no = q.get("question_no", "N/A")
                response += f"{idx} --> {q_title} (Question No: {q_no})\n"
            
            response += f"\nFormat: curl.exe https://sppucodes.vercel.app/api/{subject_code}/{{question_no}}\n"
            
            return response, 404, {'Content-Type': 'text/plain; charset=utf-8'}
        
        file_names = target_question.get("file_name", [])
        if not file_names:
            return "No files available for this question", 404, {'Content-Type': 'text/plain; charset=utf-8'}
        
        # Base directory for answers
        base_dir = os.path.abspath(os.path.dirname(__file__))
        answers_dir = os.path.join(base_dir, 'answers', subject_code)
        
        if not os.path.exists(answers_dir):
            return "Answer directory not found", 404, {'Content-Type': 'text/plain; charset=utf-8'}
        
        # Read all files and combine content
        combined_content = []
        for file_name in file_names:
            file_path = os.path.join(answers_dir, file_name)
            if not os.path.exists(file_path):
                return f"File not found: {file_name}", 404, {'Content-Type': 'text/plain; charset=utf-8'}
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    combined_content.append(content)
            except Exception as e:
                return f"Error reading file {file_name}: {str(e)}", 500, {'Content-Type': 'text/plain; charset=utf-8'}
        
        # Join content with separator if multiple files
        if len(combined_content) == 1:
            result = combined_content[0]
        else:
            separator = "\n" + "-" * 50 + "\n"
            result = separator.join(combined_content)
        
        # Return as plain text
        return result, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    
    except Exception as e:
        return f"Internal server error: {str(e)}", 500, {'Content-Type': 'text/plain; charset=utf-8'}
    
# =============================================================================
# APPLICATION ENTRY POINT
# =============================================================================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int("3000"), debug=True)