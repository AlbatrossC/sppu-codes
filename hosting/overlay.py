import os
import re

def add_script_to_html(directory, script_to_add):
    # Iterate through all files in the directory
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                
                # Read the current contents of the file
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Check if the script is already present
                if script_to_add in content:
                    print(f"Script already present in {file_path}")
                    continue
                
                # Use regex to find the closing body tag and insert the script
                updated_content = re.sub(
                    r"(</body>)",
                    f"    {script_to_add}\n\\1",
                    content,
                    flags=re.IGNORECASE
                )
                
                # Write the updated content back to the file
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(updated_content)
                
                print(f"Added script to {file_path}")

# Directory containing HTML templates
templates_dir = "templates"  # Replace with the path to your templates directory

# Script tag to be added
script_tag = '<script src="{{ url_for(\'static\', filename=\'js/overlay.js\') }}"></script>'

# Call the function
add_script_to_html(templates_dir, script_tag)
