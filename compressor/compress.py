import re
import os

def minify_html(html_content):
    """Minify HTML content by removing comments and unnecessary spaces."""
    html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)  # Remove comments
    html_content = re.sub(r'\s+', ' ', html_content)  # Collapse whitespace
    html_content = re.sub(r'>\s+<', '><', html_content)  # Remove spaces between tags
    return html_content.strip()

def minify_css(css_content):
    """Minify CSS content by removing comments and unnecessary spaces."""
    css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)  # Remove comments
    css_content = re.sub(r'\s+', ' ', css_content)  # Collapse whitespace
    css_content = re.sub(r'\s*([{}:;,])\s*', r'\1', css_content)  # Remove spaces around special chars
    return css_content.strip()

def minify_js(js_content):
    """Minify JS content by removing comments and unnecessary spaces."""
    js_content = re.sub(r'//.*?\n', '', js_content)  # Remove single-line comments
    js_content = re.sub(r'/\*.*?\*/', '', js_content, flags=re.DOTALL)  # Remove multi-line comments
    js_content = re.sub(r'\s+', ' ', js_content)  # Collapse whitespace
    js_content = re.sub(r'\s*([{};:,()=+])\s*', r'\1', js_content)  # Remove spaces around special chars
    return js_content.strip()

def minify_file(file_path, file_type):
    """Minify the content of a file based on its type."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if file_type == 'html':
        minified_content = minify_html(content)
    elif file_type == 'css':
        minified_content = minify_css(content)
    elif file_type == 'js':
        minified_content = minify_js(content)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

    # Overwrite the original file with minified content
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(minified_content)
    print(f"Minified: {file_path}")

def traverse_and_minify(base_dir, extensions):
    """Traverse a directory and minify files with the given extensions."""
    for root, _, files in os.walk(base_dir):
        for file in files:
            file_ext = os.path.splitext(file)[-1].lower()
            if file_ext in extensions:
                file_type = file_ext.lstrip('.')
                file_path = os.path.join(root, file)
                minify_file(file_path, file_type)

def main():
    # Directories to process
    html_dir = 'templates'  # HTML files directory
    css_dir = 'static/css'  # CSS files directory
    js_dir = 'static/js'    # JS files directory

    # Minify HTML files
    if os.path.exists(html_dir):
        print(f"Processing HTML files in {html_dir}...")
        traverse_and_minify(html_dir, {'.html'})

    # Minify CSS files
    if os.path.exists(css_dir):
        print(f"Processing CSS files in {css_dir}...")
        traverse_and_minify(css_dir, {'.css'})

    # Minify JS files
    if os.path.exists(js_dir):
        print(f"Processing JS files in {js_dir}...")
        traverse_and_minify(js_dir, {'.js'})

if __name__ == "__main__":
    main()
