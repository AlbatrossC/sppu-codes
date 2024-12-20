import os
import re

def minify_html(content):
    content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)  # Remove comments
    content = re.sub(r">\s+<", "><", content)  # Remove spaces between tags
    content = re.sub(r"\s+", " ", content)  # Consolidate spaces
    content = re.sub(r'\s*=\s*', '=', content)  # Remove spaces around attributes
    return content.strip()

def minify_css(content):
    content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)  # Remove comments
    content = re.sub(r"\s*([{}:;,])\s*", r"\1", content)  # Remove spaces around syntax
    content = re.sub(r";}", "}", content)  # Remove unnecessary semicolons
    content = re.sub(r"\s+", " ", content)  # Consolidate spaces
    return content.strip()

def minify_js(content):
    content = re.sub(r"//.*?$|/\*.*?\*/", "", content, flags=re.DOTALL | re.MULTILINE)  # Remove comments
    content = re.sub(r"\s*([{}();,=+\-*/<>!&|])\s*", r"\1", content)  # Remove spaces around syntax
    content = re.sub(r";+", ";", content)  # Consolidate multiple semicolons
    content = re.sub(r"\s+", " ", content)  # Consolidate spaces
    return content.strip()

def minify_file(file_path, minify_func):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    minified_content = minify_func(content)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(minified_content)

def process_directory(base_path, extensions, minify_func):
    for root, _, files in os.walk(base_path):
        for file in files:
            if file.endswith(extensions):
                file_path = os.path.join(root, file)
                print(f"Minifying: {file_path}")
                minify_file(file_path, minify_func)

if __name__ == "__main__":
    # File type mappings
    directories = {
        "templates": (".html", minify_html),
        os.path.join("static", "css"): (".css", minify_css),
        os.path.join("static", "js"): (".js", minify_js),
    }

    # Process directories
    for dir_path, (ext, func) in directories.items():
        process_directory(dir_path, (ext,), func)

    print("Minification completed!")
