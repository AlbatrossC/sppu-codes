from flask import Flask, render_template, send_from_directory, abort
import os

app = Flask(__name__)

# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<subject_name>')
def subject(subject_name):
    try:
        return render_template(f'subjects/{subject_name}.html')
    except Exception as e:
        app.logger.error(f"Error loading subject template: {e}")
        abort(404)

@app.route('/answers/<subject>/<filename>')
def get_answer(subject, filename):
    try:
        app.logger.info(f"Attempting to serve: {subject}/{filename}")
        
        # Get absolute path to the answers directory
        base_dir = os.path.abspath(os.path.dirname(__file__))
        answers_dir = os.path.join(base_dir, 'answers', subject)
        
        # Log the full path and file existence
        full_path = os.path.join(answers_dir, filename)
        app.logger.info(f"Full path: {full_path}")
        app.logger.info(f"File exists: {os.path.exists(full_path)}")
        
        # Check if directory exists
        if not os.path.exists(answers_dir):
            app.logger.error(f"Directory not found: {answers_dir}")
            abort(404)
            
        # Check if file exists
        if not os.path.exists(full_path):
            app.logger.error(f"File not found: {full_path}")
            abort(404)
            
        return send_from_directory(answers_dir, filename)
    except Exception as e:
        app.logger.error(f"Error serving file: {e}")
        abort(404)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)