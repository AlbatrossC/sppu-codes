import json
import os
from pathlib import Path

def generate_markdown(json_file_path, output_dir):
    """
    Generate clean SEO-optimized markdown file from JSON data
    
    Args:
        json_file_path: Path to the JSON file
        output_dir: Directory to save the markdown file
    """
    # Read JSON file
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract default information
    default_info = data.get('default', {})
    subject_code = default_info.get('subject_code', '').lower()
    subject_name = default_info.get('subject_name', '')
    description = default_info.get('description', '')
    keywords = default_info.get('keywords', [])
    url = default_info.get('url', '')
    question_paper_url = default_info.get('question_paper_url', '')
    
    # Start building markdown content
    md_content = []
    
    # Add HTML comment for SEO metadata (invisible in rendered markdown)
    md_content.append(f'<!-- SEO Metadata')
    md_content.append(f'Title: {subject_name}')
    md_content.append(f'Description: {description}')
    md_content.append(f'Keywords: {", ".join(keywords)}')
    md_content.append(f'-->')
    md_content.append('')
    
    # Add subject name as main heading with emoji
    md_content.append(f'# 📚 {subject_name}')
    md_content.append('')
    
    # Add description
    md_content.append(f'> {description}')
    md_content.append('')
    
    # Add navigation links with emojis
    md_content.append(f'### 🌐 [Visit Subject Website]({url})')
    md_content.append('')
    md_content.append(f'### 📄 [View Question Papers]({question_paper_url})')
    md_content.append('')
    md_content.append('---')
    md_content.append('')
    
    # Group questions by group
    questions = data.get('questions', [])
    grouped_questions = {}
    
    for question in questions:
        group = question.get('group', 'Unknown')
        if group not in grouped_questions:
            grouped_questions[group] = []
        grouped_questions[group].append(question)
    
    # Generate content for each group
    for group in sorted(grouped_questions.keys()):
        # Group heading with more spacing and visual separation
        md_content.append('')
        md_content.append('')
        md_content.append(f'## 📂 GROUP {group}')
        md_content.append('')
        md_content.append('---')
        md_content.append('')
        
        for idx, question in enumerate(grouped_questions[group], 1):
            question_no = question.get('question_no', '')
            question_text = question.get('question', '')
            question_id = question.get('id', '')
            
            # Add spacing between questions
            if idx > 1:
                md_content.append('')
                md_content.append('')
            
            # Question heading with just the number
            md_content.append(f'### ❓ Question {question_no}:')
            md_content.append('')
            
            # Question text displayed prominently and clearly
            md_content.append(f'{question_text}')
            md_content.append('')
            
            # View code link - larger and more prominent with emoji
            code_link = f'https://sppucodes.vercel.app/{subject_code}/{question_id}'
            md_content.append(f'**[💻 VIEW CODE SOLUTION →]({code_link})**')
            md_content.append('')
            md_content.append('---')
            md_content.append('')
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output filename
    json_filename = Path(json_file_path).stem
    output_filename = f'{json_filename}.md'
    output_path = os.path.join(output_dir, output_filename)
    
    # Write markdown file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_content))
    
    print(f'✅ Generated: {output_filename}')
    return output_path


def process_all_json_files(questions_dir, output_dir):
    """
    Process all JSON files in the questions directory
    
    Args:
        questions_dir: Directory containing JSON files
        output_dir: Directory to save markdown files
    """
    questions_path = Path(questions_dir)
    
    if not questions_path.exists():
        print(f'❌ Error: Questions directory not found: {questions_dir}')
        return
    
    # Find all JSON files
    json_files = list(questions_path.glob('*.json'))
    
    if not json_files:
        print(f'❌ No JSON files found in {questions_dir}')
        return
    
    print(f'📂 Found {len(json_files)} JSON files')
    print(f'📝 Generating markdown files...\n')
    
    # Process each JSON file
    for json_file in json_files:
        try:
            generate_markdown(str(json_file), output_dir)
        except Exception as e:
            print(f'❌ Error processing {json_file.name}: {str(e)}')
    
    print(f'\n✨ All markdown files generated successfully in: {output_dir}')


if __name__ == '__main__':
    # Get the root directory (parent of the script's directory)
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    
    # Configuration using relative paths from root
    QUESTIONS_DIR = root_dir / 'questions'
    OUTPUT_DIR = root_dir / 'docs'
    
    # Process all JSON files
    process_all_json_files(QUESTIONS_DIR, OUTPUT_DIR)