import os

# Define the directory containing the HTML files
html_dir = "templates/subjects"

# Define the button HTML to be added (without indentation)
button_html = '''<button class="explain-btn" onclick="explainCode('codeContent{}')">
  <img src="static/svg/gemini.svg" alt="Gemini Logo" class="gemini-logo">
  Explain with AI
</button>'''

# Iterate through all HTML files in the directory
for filename in os.listdir(html_dir):
    if filename.endswith(".html"):
        filepath = os.path.join(html_dir, filename)
        
        # Read the HTML file as plain text
        with open(filepath, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # Flag to track if any changes were made
        changes_made = False

        # Iterate through the lines to find the correct position
        new_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            new_lines.append(line)

            # Look for the "copy-btn" button line
            if 'class="copy-btn"' in line:
                # Check if the "Explain with AI" button already exists above
                has_explain_button = any('class="explain-btn"' in l for l in lines[max(i - 3, 0):i])

                # If the button is not present, add it
                if not has_explain_button:
                    # Find the indentation of the "copy-btn" button
                    copy_btn_indentation = line[:len(line) - len(line.lstrip())]

                    # Extract the question number from the "copyCode" function call
                    question_number = line.split("copyCode('codeContent")[1].split("'")[0]

                    # Add indentation to each line of the button HTML
                    indented_button_html = "\n".join(
                        [copy_btn_indentation + button_line for button_line in button_html.format(question_number).split("\n")]
                    )

                    # Insert the button HTML above the "copy-btn" line
                    new_lines.insert(-1, indented_button_html + "\n")
                    changes_made = True

            i += 1

        # Save the modified HTML back to the file if changes were made
        if changes_made:
            with open(filepath, "w", encoding="utf-8") as file:
                file.writelines(new_lines)
            print(f"Updated {filename}")
        else:
            print(f"No changes needed for {filename}")