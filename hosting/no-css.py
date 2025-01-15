import os
import re

def remove_lines_and_delete_css_files(directory, pattern, css_directory):
    regex = re.compile(pattern)
    
    # Remove lines from HTML files
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                updated_lines = [line for line in lines if not regex.search(line)]
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(updated_lines)

    # Delete all CSS files in the static/css directory
    for css_file in os.listdir(css_directory):
        if css_file.endswith(".css"):
            css_file_path = os.path.join(css_directory, css_file)
            os.remove(css_file_path)
            print(f"Deleted CSS file: {css_file_path}")

# Usage
html_directory = "templates"
css_link_pattern = r'<link rel="stylesheet" href=".*">'
css_directory = "static/css"
remove_lines_and_delete_css_files(html_directory, css_link_pattern, css_directory)
