from flask import Flask, render_template
import json
import os

app = Flask(__name__)

# Function to load questions from JSON file
def load_questions(subject):
    file_path = os.path.join('data', f'{subject}.json')
    with open(file_path, 'r') as file:
        questions = json.load(file)
    return questions

# Function to read code from a file
def read_code_file(file_name):
    try:
        file_path = os.path.join('code', file_name)  # Ensure it points to the right directory
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return "Code file not found."

@app.route('/')
def home():
    return render_template('index.html')

# Dynamic route for each subject
@app.route('/<subject>')
def subject_page(subject):
    questions = load_questions(subject)
    return render_template('subject.html', subject=subject.upper(), questions=questions)

@app.route('/code/<path:filename>')
def code_file(filename):
    # Read and return the content of the code file
    return read_code_file(filename)

if __name__ == '__main__':
    app.run(debug=True)
