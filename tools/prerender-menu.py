"""Re-writes the menu as plain HTML inside index.html so Google can read it.
Run after any change to MENU / IMG:  python3 tools/prerender-menu.py
The script empties #cats, #cards and #extras, renders the page in English, and pastes the result back."""
import os,re
from playwright.sync_api import sync_playwright
P=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','index.html'))
t=open(P).read()
for k in ['cats','cards','extras']:
    s=t.index(f'id="{k}">')+len(f'id="{k}">')
    # find the matching closing div
    depth,i=1,s
    while depth:
        m=re.compile(r'<div\b|</div>').search(t,i); depth+=1 if m.group()=='<div' else -1; i=m.end()
    t=t[:s]+t[i-len('</div>'):]
open(P,'w').write(t)
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_context(locale='en-US').new_page()
    pg.goto('file://'+P);pg.wait_for_timeout(1500)
    parts={k:pg.eval_on_selector('#'+k,'e=>e.innerHTML') for k in ['cats','cards','extras']}
    b.close()
for k,v in parts.items(): t=t.replace(f'id="{k}"></div>',f'id="{k}">{v}</div>',1)
open(P,'w').write(t)
open(os.path.join(os.path.dirname(P),'404.html'),'w').write(t.replace('<link rel="canonical" href="https://davidpizzakohlanta.com/">','<meta name="robots" content="noindex">'))
print('menu pre-rendered')
