from flask import Flask, render_template
import json
import os

app = Flask(__name__)

# Function to load questions from JSON file
def load_questions(subject):
    file_path = os.path.join('data', f'{subject}.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            questions = json.load(file)
        return questions
    except FileNotFoundError:
        return {"error": "File not found"}
    except json.JSONDecodeError:
        return {"error": "Error decoding JSON"}

# Function to read code from a file
def read_code_file(file_name):
    try:
        file_path = os.path.join('code', file_name)
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return "Code file not found."
    except UnicodeDecodeError:
        return "Error reading code file due to invalid encoding."

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/<subject>')
def subject_page(subject):
    questions = load_questions(subject)
    return render_template('subject.html', subject=subject.upper(), questions=questions)

@app.route('/code/<path:filename>')
def code_file(filename):
    return read_code_file(filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
