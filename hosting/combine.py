import os
from bs4 import BeautifulSoup
import re

def clean_question_text(text):
    text = re.sub(r'\*\*Q\d+:?\s*\*\*|Q\d+:\s*', '', text)
    return ' '.join(text.split())

def combine_qa(html_path, answer_dir, output_path):
    try:
        with open(html_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        # Ensure HTML structure exists
        if not soup.html:
            soup.append(soup.new_tag('html'))
        
        if not soup.head:
            soup.html.insert(0, soup.new_tag('head'))
        
        if not soup.body:
            soup.html.append(soup.new_tag('body'))

        # Extract subject name from the original link if available
        subject_link = soup.find('a', class_='a')
        subject_name = subject_link.text if subject_link else "Unknown Subject"

        # Create header
        header = soup.new_tag('header')
        header['style'] = 'padding: 10px; background: #f5f5f5; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;'
        
        h3 = soup.new_tag('h3')
        h3.string = subject_name
        
        home_btn = soup.new_tag('a')
        home_btn['href'] = '/'
        home_btn['style'] = 'padding: 5px 10px; background: #2196f3; color: white; text-decoration: none; border-radius: 4px;'
        home_btn.string = 'Home'
        
        header.extend([h3, home_btn])

        # Create offline note
        offline_note = soup.new_tag('div')
        offline_note['style'] = 'background: #fff3cd; padding: 15px; margin-bottom: 10px; border: 1px solid #ffeeba; border-radius: 4px;'
        offline_note.string = "You’re Offline, But Still Connected! 🌐 Don’t worry—this page is available for you to explore even without the internet. Enjoy your offline access!"

        # Create main container
        container = soup.new_tag('div')
        container['class'] = 'c'

        questions = soup.find_all('div', class_='question-item')
        
        if not questions:
            print(f"Warning: No questions found in {html_path}")
            return False

        for i, question in enumerate(questions, 1):
            question_p = question.find('p')
            if not question_p:
                continue
                
            question_text = clean_question_text(question_p.text.strip())
            
            button = question.find('button', class_='view-code-btn')
            if not button or 'onclick' not in button.attrs:
                continue
                
            filename = button['onclick'].split(',')[1].strip().strip("'")
            answer_path = os.path.join(answer_dir, filename)

            answer_content = ""
            if os.path.exists(answer_path):
                with open(answer_path, 'r', encoding='utf-8') as answer_file:
                    answer_content = answer_file.read()

            qa_div = soup.new_tag('div')
            qa_div['class'] = 'q'
            qa_div['id'] = f'q{i}'

            q_header = soup.new_tag('div')
            q_header['class'] = 'h'
            q_header['onclick'] = f't("{i}")'
            
            num = soup.new_tag('span')
            num['class'] = 'n'
            num.string = f'Q{i}'
            
            text = soup.new_tag('div')
            text['class'] = 'x'
            text.string = question_text
            
            btn = soup.new_tag('button')
            btn['class'] = 'b'
            btn.string = '+'
            
            answer = soup.new_tag('div')
            answer['class'] = 'a'
            answer['id'] = f'a{i}'
            
            pre = soup.new_tag('pre')
            pre.string = answer_content or "Not found"
            
            q_header.extend([num, text, btn])
            answer.append(pre)
            qa_div.extend([q_header, answer])
            container.append(qa_div)

        # Clear body and add new structure
        soup.body.clear()
        soup.body.extend([header, offline_note, container])

        # Add styles
        style = soup.new_tag('style')
        style.string = """
*{margin:0;padding:0;box-sizing:border-box}
body{font:15px/1.5 system-ui;background:#fff;margin:0;padding:8px}
.c{display:flex;flex-direction:column;gap:1px;background:#eee;border:1px solid #ddd}
.q{background:#fff}
.h{display:flex;padding:10px;cursor:pointer;gap:8px;align-items:center;border-bottom:1px solid #eee}
.h:hover{background:#f5f5f5}
.n{color:#2196f3;font-weight:600;min-width:30px}
.x{flex:1;color:#000;font-size:15px}
.b{border:none;background:#eee;color:#666;width:24px;height:24px;border-radius:4px;cursor:pointer}
.a{height:0;overflow:hidden;transition:.2s}
.a pre{padding:12px;background:#fff;font-family:monospace;white-space:pre-wrap;word-wrap:break-word;font-size:14px;line-height:1.5;color:#333;border-bottom:1px solid #eee}
.o{height:auto}
@media(min-width:800px){body{padding:15px 10%}}
@media(min-width:1200px){body{padding:15px 15%}}"""

        # Add script
        script = soup.new_tag('script')
        script.string = """
function t(i){
let a=document.getElementById('a'+i),
b=a.parentElement.querySelector('.b');
a.classList.toggle('o');
if(a.classList.contains('o')){
b.style.background='#2196f3';
b.style.color='#fff'
}else{
b.style.background='';
b.style.color=''
}}"""

        # Clear head and add only the necessary style
        soup.head.clear()
        soup.head.append(style)

        # Append script to body
        soup.body.append(script)

        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write(str(soup))
        return True

    except Exception as e:
        print(f"Error processing {html_path}: {str(e)}")
        return False

def main():
    subjects_dir = os.path.join('templates', 'subjects')
    output_dir = os.path.join('templates', 'offline')
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(subjects_dir):
        print(f"Error: Directory {subjects_dir} not found")
        return

    for filename in os.listdir(subjects_dir):
        if filename.endswith('.html'):
            subject_code = os.path.splitext(filename)[0]
            input_html = os.path.join(subjects_dir, filename)
            answer_directory = os.path.join('answers', subject_code)
            output_html = os.path.join(output_dir, f'offline_{subject_code}.html')
            
            if os.path.exists(input_html):
                success = combine_qa(input_html, answer_directory, output_html)
                if success:
                    print(f"Successfully processed {filename} -> offline_{subject_code}.html")
                else:
                    print(f"Failed to process {filename}")
            else:
                print(f"Warning: {input_html} not found")

if __name__ == "__main__":
    main()