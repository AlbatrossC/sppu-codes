from flask import Flask, render_template, send_from_directory, abort, send_file
import os

app = Flask(__name__)

# Home Page: Index.html
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/caught')
def caught():
    return render_template('caught.html')

# For Code submit and submissions page
@app.route('/submit')
def submit():
    return render_template('submits/submit.html')

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

#Testing
@app.route('/loaderio-a833ae5131281cfe4daf880e5d3580d6/')
def loaderio_folder_verification():
    return "loaderio-a833ae5131281cfe4daf880e5d3580d6"

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
@app.route('/google456489e61e0d5f11.html')
def google_verification():
    return send_file('seo/google456489e61e0d5f11.html', mimetype='text/html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=  int("3000") , debug=True)
