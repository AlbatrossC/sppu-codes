from flask import Flask, render_template, send_from_directory, abort, request, redirect, url_for, flash, jsonify
import os
import psycopg2
from hosting.quecount import quecount_bp

app = Flask(__name__)
app.secret_key = 'karlos'

# Register the quecount blueprint
app.register_blueprint(quecount_bp)

DATABASE_URL = os.getenv("DATABASE_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
@app.route('/get-api-key')
def get_api_key():
    return jsonify({'api_key': GEMINI_API_KEY})  

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

@app.route('/')
def index():
    return render_template('index.html')

# For Downloading codes
downloads_folder = os.path.join(app.root_path, 'downloads')

@app.route('/download')
def download():
    return render_template('download.html')

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(downloads_folder, filename)

# Route for /subject/question
@app.route('/<subject>/<question>')
def subject_question(subject, question):
    try:
        # Pass the question parameter to the template
        return render_template(f'subjects/{subject}.html', question=question)
    except Exception:
        abort(404)

# Route for /subject
@app.route('/<subject>')
def subject(subject):
    try:
        # Render the subject page without highlighting any question
        return render_template(f'subjects/{subject}.html', question=None)
    except Exception:
        abort(404)

@app.route('/sw.js')
def serve_sw():
    return send_from_directory('.', 'sw.js', mimetype='application/javascript')

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

@app.route('/disclaimer')
def disclaimer():
    return render_template('disclaimer.html')

@app.route('/copy')
def copy():
    return render_template('copy.html')

@app.route('/images/<filename>')
def get_image(filename):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    images_dir = os.path.join(base_dir, 'images')
    return send_from_directory(images_dir, filename)

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory('.', 'sitemap.xml')

@app.route('/robots.txt')
def robots():
    return send_from_directory('.', 'robots.txt')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int("3000"), debug=True)