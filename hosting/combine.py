import os
from bs4 import BeautifulSoup
import re

def clean_text(t): return ' '.join(re.sub(r'\*\*Q\d+:?\s*\*\*|Q\d+:\s*','',t).split())

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
        
        h = s.new_tag('header')
        h['style'] = 'padding:12px;background:#1a1a1a;margin:0 0 12px;display:flex;justify-content:space-between;align-items:center;border-radius:6px'
        
        h3 = s.new_tag('h3')
        h3['style'] = 'color:#fff;margin:0'
        h3.string = subj_name
        
        btn = s.new_tag('a')
        btn['href'] = '/'
        btn['style'] = 'padding:6px 12px;background:#2196f3;color:#fff;text-decoration:none;border-radius:4px'
        btn.string = 'Home'
        
        h.extend([h3,btn])
        
        note = s.new_tag('div')
        note['style'] = 'background:#1e3a5f;color:#fff;padding:12px;margin-bottom:12px;border-radius:6px'
        note.string = "Offline Mode Active 🌐"
        
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
        
        style = s.new_tag('style')
        style.string = """*{margin:0;padding:0;box-sizing:border-box}body{font:15px/1.5 system-ui;background:#121212;color:#fff;padding:8px;min-height:100vh}.c{display:flex;flex-direction:column;gap:1px;background:#1a1a1a;border:1px solid #333;border-radius:6px;overflow:hidden}.q{background:#1a1a1a;border-bottom:1px solid #333}.h{display:flex;padding:12px;cursor:pointer;gap:8px;align-items:center}.h:hover{background:#252525}.n{color:#2196f3;font-weight:600;min-width:30px}.x{flex:1;color:#fff}.b{border:1px solid #2196f3;background:0;color:#2196f3;width:24px;height:24px;border-radius:4px;cursor:pointer}.b:hover{background:#2196f3;color:#fff}.a{height:0;overflow:hidden;transition:.2s}.a pre{padding:12px;background:#252525;font-family:monospace;white-space:pre-wrap;word-wrap:break-word;font-size:14px;line-height:1.5;color:#e0e0e0}.o{height:auto}@media(min-width:800px){body{padding:15px 10%}}@media(min-width:1200px){body{padding:20px 15%}}"""
        
        script = s.new_tag('script')
        script.string = """function t(i){let a=document.getElementById('a'+i),b=a.parentElement.querySelector('.b'),p=a.querySelector('pre');a.classList.contains('o')?(a.style.height=0,a.classList.remove('o'),b.style.background='',b.style.color=''):(a.style.height=p.offsetHeight+'px',a.classList.add('o'),b.style.background='#2196f3',b.style.color='#fff')}"""
        
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