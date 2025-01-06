from flask import Flask, render_template, send_from_directory, abort
import os
from flask import Blueprint
from inputs.contact import contact, db 


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contact.db'
db.init_app(app)
app.register_blueprint(contact)

# Create tables
with app.app_context():
    db.create_all()

# Home Page: Index.html
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

# Dynamic Subject page: templates/subjects/... e.g., oop.html, dsl.html
@app.route('/<subject_name>')
def subject(subject_name):
    try:
        return render_template(f'subjects/{subject_name}.html')
    except Exception:
        return render_template("error.html")

#files 
@app.route('/<subject>/<filename>')
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

# Route to serve images
@app.route('/images/<filename>')
def get_image(filename):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    images_dir = os.path.join(base_dir, 'images')
    
    return send_from_directory(images_dir, filename)

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory('seo', 'sitemap.xml')
@app.route('/robots.txt')
def robots():
    return send_from_directory('seo', 'robots.txt')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=  int("3000") , debug=True)
