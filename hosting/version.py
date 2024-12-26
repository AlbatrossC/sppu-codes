import os
import re

# Path to the templates folder
templates_folder = 'templates'

# Function to update the version
def update_version(version):
    major, minor = map(int, version.split('.'))
    if minor < 9:
        minor += 1
    else:
        major += 1
        minor = 0
    return f'{major}.{minor}'

# Function to process a single HTML file
def process_html_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Regular expression to find versioned CSS links
    css_link_pattern = re.compile(r'(<link rel="stylesheet" href="[^"]+\.css\?v=)(\d+\.\d+)(")')
    
    # Replace the version in the link
    updated_content = re.sub(css_link_pattern, lambda match: match.group(1) + update_version(match.group(2)) + match.group(3), content)
    
    # If the content has changed, write the updated content back to the file
    if updated_content != content:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(updated_content)
        print(f'Updated: {file_path}')

# Traverse through all files in the templates folder
def update_versions_in_templates():
    for root, dirs, files in os.walk(templates_folder):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                process_html_file(file_path)

# Run the script
if __name__ == "__main__":
    update_versions_in_templates()
