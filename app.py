from flask import Flask, render_template, send_from_directory, abort, request, redirect, url_for, flash, jsonify
import os
import psycopg2
import json
from datetime import datetime
from hosting.quecount import quecount_bp

app = Flask(__name__)
app.secret_key = 'karlos'

# Register the quecount blueprint
app.register_blueprint(quecount_bp)

# Environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Route to get the Gemini API key
@app.route('/get-api-key')
def get_api_key():
    return jsonify({'api_key': GEMINI_API_KEY})

# Database connection function
def connect_db():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

# Custom Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html'), 500

# Route for submitting codes
@app.route('/submit', methods=["GET", "POST"])
def submit():
    conn = connect_db()
    if conn is None:
        return "Database Connection error. Please try again later"

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

            cur.close()
        except Exception as e:
            flash(f"Error inserting data: {e}", "error")
        finally:
            conn.close()

    return render_template("submit.html")

# Route for contact form
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")  # Changed from "msg" to "message"

        if name and email and message:
            try:
                conn = connect_db()
                if conn is None:
                    flash("Database connection error. Please try again later.", "error")
                    return redirect(url_for('contact'))

                cur = conn.cursor()
                cur.execute("INSERT INTO contacts (name, email, message) VALUES (%s, %s, %s)", 
                          (name, email, message))
                conn.commit()
                cur.close()
                conn.close()
                
                flash("Message sent successfully! Thank you", "success")
            except Exception as e:
                flash(f"Error inserting data: {e}", "error")
            return redirect(url_for('contact'))
        else:
            flash("PLEASE FILL ALL NECESSARY FIELDS", "error")
            
    return render_template("contact.html")

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Route for downloading codes
downloads_folder = os.path.join(app.root_path, 'downloads')

@app.route('/download')
def download():
    return render_template('download.html')

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(downloads_folder, filename)

# Function to load SEO data for a specific subject
def load_seo_data(subject):
    file_path = os.path.join(app.root_path, 'questions', f'{subject}.json')
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return None

# Function to generate FAQ schema for all questions
def generate_faq_schema(questions):
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": []
    }
    for question in questions:
        faq_schema["mainEntity"].append({
            "@type": "Question",
            "name": question["title"],
            "acceptedAnswer": {
                "@type": "Answer",
                "text": question["description"]
            }
        })
    return faq_schema

# Function to generate WebPage schema for a specific question
def generate_webpage_schema(question):
    webpage_schema = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": question["title"],
        "description": question["description"],
        "keywords": question["keywords"],
        "url": question["ogurl"]
    }
    return webpage_schema

# Function to generate QAPage schema for a specific question
def generate_qa_page_schema(question):
    qa_page_schema = {
        "@context": "https://schema.org",
        "@type": "QAPage",
        "mainEntity": {
            "@type": "Question",
            "name": question["title"],
            "text": question["title"],
            "answerCount": 1,
            "datePublished": datetime.now().isoformat(),  # Add datePublished
            "author": {
                "@type": "Organization",
                "name": "Sppu Codes",
                "url": "https://sppucodes.vercel.app"  # Add author URL
            },
            "url": question["ogurl"],  # Add URL for the question
            "acceptedAnswer": {
                "@type": "Answer",
                "text": question["description"],
                "datePublished": datetime.now().isoformat(),  # Add datePublished
                "upvoteCount": 0,  # Add upvoteCount (optional)
                "url": question["ogurl"],  # Add URL for the answer
                "author": {
                    "@type": "Organization",
                    "name": "Sppu Codes",
                    "url": "https://sppucodes.vercel.app"  # Add author URL
                }
            }
        }
    }
    return qa_page_schema

# Route for /subject/question
@app.route('/<subject>/<question>')
def subject_question(subject, question):
    seo_data = load_seo_data(subject)
    if not seo_data:
        # If no JSON file is found, render the page with default SEO data
        default_seo = {
            "title": f"{subject.capitalize()} - {question.capitalize()}",
            "description": f"Learn about {question} in {subject}.",
            "keywords": f"{subject}, {question}, education, learning",
            "ogurl": request.url
        }
        return render_template(f'subjects/{subject}.html', seo=default_seo, schema=None, question=question)

    # Find the question in the JSON data
    question_data = next((q for q in seo_data["questions"] if q["url"] == f"/{subject}/{question}"), None)
    
    if question_data:
        # Generate WebPage and QAPage schema for the question
        webpage_schema = generate_webpage_schema(question_data)
        qa_page_schema = generate_qa_page_schema(question_data)
        # Dynamically set ogurl
        question_data["ogurl"] = request.url
        # Pass the question-specific SEO data and schema to the template
        return render_template(f'subjects/{subject}.html', seo=question_data, schema=[webpage_schema, qa_page_schema], question=question)
    else:
        # If question not found, use default SEO data
        seo_data["default"]["ogurl"] = request.url
        return render_template(f'subjects/{subject}.html', seo=seo_data["default"], schema=None, question=None)

# Route for /subject
@app.route('/<subject>')
def subject(subject):
    seo_data = load_seo_data(subject)
    if not seo_data:
        # If no JSON file is found, render the page with default SEO data
        default_seo = {
            "title": f"{subject.capitalize()} - Learn {subject}",
            "description": f"Learn about {subject} with detailed questions and answers.",
            "keywords": f"{subject}, education, learning",
            "ogurl": request.url
        }
        return render_template(f'subjects/{subject}.html', seo=default_seo, schema=None, question=None)
    
    # Generate FAQ schema for all questions
    faq_schema = generate_faq_schema(seo_data["questions"])
    # Dynamically set ogurl
    seo_data["default"]["ogurl"] = request.url
    # Use default SEO data for the subject page
    return render_template(f'subjects/{subject}.html', seo=seo_data["default"], schema=faq_schema, question=None)

# Route for serving answers
@app.route('/answers/<subject>/<filename>')
def get_answer(subject, filename):
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

# Route for disclaimer page
@app.route('/disclaimer')
def disclaimer():
    return render_template('disclaimer.html')

# Route for copy page
@app.route('/copy')
def copy():
    return render_template('copy.html')

# Route for serving images
@app.route('/images/<filename>')
def get_image(filename):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    images_dir = os.path.join(base_dir, 'images')
    return send_from_directory(images_dir, filename)

# Route for sitemap
@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory('.', 'sitemap.xml')

# Route for robots.txt
@app.route('/robots.txt')
def robots():
    return send_from_directory('.', 'robots.txt')

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int("3000"), debug=True)