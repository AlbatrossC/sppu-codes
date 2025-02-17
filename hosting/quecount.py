from flask import Blueprint, render_template
import os
from bs4 import BeautifulSoup

quecount_bp = Blueprint('quecount', __name__, template_folder='../templates')

def count_questions_in_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        soup = BeautifulSoup(content, 'html.parser')
        return len(soup.find_all('div', class_='question-item'))

def process_subjects_folder(base_path='templates/subjects'):
    results = {
        "total_questions": 0,
        "subjects": {}
    }
    
    abs_path = os.path.abspath(base_path)
    if not os.path.exists(abs_path):
        return results
            
    for subject_file in os.listdir(abs_path):
        if subject_file.endswith('.html'):
            subject_name = os.path.splitext(subject_file)[0]
            file_path = os.path.join(abs_path, subject_file)
            
            question_count = count_questions_in_file(file_path)
            results["subjects"][subject_name] = question_count
            results["total_questions"] += question_count
    
    return results

@quecount_bp.route('/stats')
def stats():
    results = process_subjects_folder()
    return render_template('stats.html', results=results)