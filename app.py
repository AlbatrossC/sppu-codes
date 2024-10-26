from flask import Flask, render_template, send_from_directory, abort

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<subject_name>')
def subject(subject_name):
    return render_template(f'subjects/{subject_name}.html')

@app.route('/answers/<subject>/<filename>')
def get_answer(subject, filename):
    try:
        return send_from_directory(f'answers/{subject}', filename)
    except FileNotFoundError:
        abort(404)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
