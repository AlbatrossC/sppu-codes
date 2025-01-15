# THis script will remove all the CSS from the HTML file

import os
import re

def delete_css_files(directory):
    """
    Delete all CSS files in the given directory and its subdirectories.
    """
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".css"):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")

def remove_lines_from_html(directory, pattern):
    """
    Remove lines matching the given regex pattern from all HTML files
    in the specified directory and its subdirectories.
    """
    regex = re.compile(pattern)
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    updated_lines = [line for line in lines if not regex.search(line)]
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(updated_lines)
                    print(f"Updated: {file_path}")
                except Exception as e:
                    print(f"Failed to update {file_path}: {e}")

def remove_specific_div_from_html(directory, div_id):
    """
    Remove a specific <div> block with the given ID from all HTML files
    in the specified directory and its subdirectories.
    """
    pattern = re.compile(rf'<div id="{div_id}".*?>.*?</div>', re.DOTALL)
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    updated_content = re.sub(pattern, "", content)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    print(f"Removed div from: {file_path}")
                except Exception as e:
                    print(f"Failed to update {file_path}: {e}")

# Usage
html_directory = "templates"
css_directory = "static/css"

# Delete all CSS files
delete_css_files(css_directory)

# Remove CSS link lines from HTML files
css_link_pattern = r'<link rel="stylesheet" href=".*">'
remove_lines_from_html(html_directory, css_link_pattern)

# Remove specific <div> block by ID
remove_specific_div_from_html(html_directory, "stats-modal")
