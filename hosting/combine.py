import os
from bs4 import BeautifulSoup
import re

def clean_text(t): 
    return ' '.join(re.sub(r'\*\*Q\d+:?\s*\*\*|Q\d+:\s*','',t).split())

def combine_qa(html_path, answer_dir, output_path):
    try:
        with open(html_path,'r',encoding='utf-8') as f:
            s = BeautifulSoup(f,'html.parser')
            
        if not s.html: s.append(s.new_tag('html'))
        if not s.head: s.html.insert(0,s.new_tag('head'))
        if not s.body: s.html.append(s.new_tag('body'))
        
        m1 = s.new_tag('meta',charset='utf-8')
        m2 = s.new_tag('meta',attrs={'name':'viewport','content':'width=device-width,initial-scale=1'})
        s.head.extend([m1,m2])
        
        subj = s.find('a',class_='a')
        subj_name = subj.text if subj else "Subject"
        
        # Darker header
        h = s.new_tag('header')
        h['style'] = 'padding: 25px 40px; background: #000000; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: center;'
        
        h3 = s.new_tag('h3')
        h3['style'] = 'color: #fff; margin: 0; font-size: 24px;'
        h3.string = subj_name
        
        btn = s.new_tag('a')
        btn['href'] = '/'
        btn['style'] = 'color: #3b82f6; text-decoration: none; font-size: 18px;'
        btn.string = '← Home'
        
        h.extend([h3,btn])
        
        # Smaller note with yellow background only for text
        note = s.new_tag('div')
        note['style'] = 'background: #111111; padding: 15px 40px; margin-bottom: 30px;'
        
        note_text = s.new_tag('span')
        note_text['style'] = 'background: #ffeb3b; color: #000; padding: 5px 10px; font-size: 16px; border-radius: 4px;'
        note_text.string = "🌐 Offline Mode. You can still view the content without being even connected to internet. ENJOY!"
        
        note.append(note_text)
        
        c = s.new_tag('div')
        c['class'] = 'c'
        
        qs = s.find_all('div',class_='question-item')
        if not qs: return False
        
        for i,q in enumerate(qs,1):
            qp = q.find('p')
            if not qp: continue
            
            qt = clean_text(qp.text.strip())
            b = q.find('button',class_='view-code-btn')
            if not b or 'onclick' not in b.attrs: continue
            
            fn = b['onclick'].split(',')[1].strip().strip("'")
            ap = os.path.join(answer_dir,fn)
            
            ac = ""
            if os.path.exists(ap):
                with open(ap,'r',encoding='utf-8') as af:
                    ac = af.read()
            
            qd = s.new_tag('div')
            qd['class'] = 'q'
            qd['id'] = f'q{i}'
            
            qh = s.new_tag('div')
            qh['class'] = 'h'
            qh['onclick'] = f't({i})'
            
            n = s.new_tag('span')
            n['class'] = 'n'
            n.string = f'Q{i}'
            
            tx = s.new_tag('div')
            tx['class'] = 'x'
            tx.string = qt
            
            bt = s.new_tag('button')
            bt['class'] = 'b'
            bt.string = '+'
            
            ans = s.new_tag('div')
            ans['class'] = 'a'
            ans['id'] = f'a{i}'
            
            pre = s.new_tag('pre')
            pre.string = ac or "Not found"
            
            qh.extend([n,tx,bt])
            ans.append(pre)
            qd.extend([qh,ans])
            c.append(qd)
        
        s.body.clear()
        s.body.extend([h,note,c])
        
        # Updated styling with darker theme
        style = s.new_tag('style')
        style.string = """
            body {
                font-family: system-ui;
                margin: 0;
                padding: 0;
                background: #000000;
                color: #fff;
                font-size: 18px;
                line-height: 1.6;
            }
            
            .c {
                max-width: 1000px;
                margin: 0 auto;
                padding: 0 20px;
            }
            
            .q {
                border-bottom: 1px solid #1a1a1a;
                margin-bottom: 15px;
            }
            
            .h {
                display: flex;
                gap: 20px;
                align-items: center;
                cursor: pointer;
                padding: 20px;
            }
            
            .h:hover {
                background: #111111;
            }
            
            .n {
                color: #3b82f6;
                font-size: 20px;
                font-weight: bold;
                min-width: 40px;
            }
            
            .x {
                flex: 1;
                font-size: 18px;
            }
            
            .b {
                border: 2px solid #3b82f6;
                background: none;
                color: #3b82f6;
                width: 30px;
                height: 30px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 20px;
            }
            
            .a {
                display: none;
            }
            
            .a pre {
                background: #111111;
                padding: 25px;
                margin: 0 20px 20px 80px;
                overflow-x: auto;
                font-size: 16px;
                border-radius: 4px;
                color: #e2e8f0;
            }
            
            .o {
                display: block;
            }
            
            @media(max-width: 768px) {
                body {
                    font-size: 16px;
                }
                
                .c {
                    padding: 0 15px;
                }
                
                .h {
                    padding: 15px;
                    gap: 15px;
                }
                
                .a pre {
                    margin: 0 15px 15px 60px;
                    padding: 20px;
                    font-size: 14px;
                }
            }
        """
        
        script = s.new_tag('script')
        script.string = """
            function t(i) {
                let a = document.getElementById('a'+i);
                let b = a.parentElement.querySelector('.b');
                a.classList.toggle('o');
                b.textContent = a.classList.contains('o') ? '-' : '+';
            }
        """
        
        s.head.clear()
        s.head.extend([m1,m2,style])
        s.body.append(script)
        
        with open(output_path,'w',encoding='utf-8') as o:
            o.write(str(s))
        return True
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def main():
    sd = os.path.join('templates','subjects')
    od = os.path.join('templates','offline')
    os.makedirs(od,exist_ok=True)
    
    if not os.path.exists(sd):
        print(f"Error: {sd} not found")
        return
    
    for f in os.listdir(sd):
        if f.endswith('.html'):
            sc = os.path.splitext(f)[0]
            ih = os.path.join(sd,f)
            ad = os.path.join('answers',sc)
            oh = os.path.join(od,f'offline_{sc}.html')
            
            if os.path.exists(ih):
                if combine_qa(ih,ad,oh):
                    print(f"Processed: {f}")
                else:
                    print(f"Failed: {f}")
            else:
                print(f"Missing: {ih}")

if __name__ == "__main__":
    main()