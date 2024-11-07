from flask import Flask, render_template, send_from_directory, abort
import os

app = Flask(__name__)

#Home Page: Index.html
@app.route('/')
def index():
    return render_template('index.html')

#For Code submit and submissions page.
@app.route('/submit')
def submit():
    return render_template('submits/submit.html')


#Dynamic Subject page: templates/subjects/.. e"x oop.html , dsl.html
@app.route('/<subject_name>')
def subject(subject_name):
    try:
        return render_template(f'subjects/{subject_name}.html')
    except Exception:
        return render_template("error.html")
    
#File name: to get link for a file. for ex. https://codecave.vercel.app/answers/dsl/grpA_1.py
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

# Route to serve images
@app.route('/images/<filename>')
def get_image(filename):
    base_dir = os.path.abspath(os.path.dirname(__file__))
    images_dir = os.path.join(base_dir, 'images')
    
    return send_from_directory(images_dir, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
