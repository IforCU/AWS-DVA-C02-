#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / 'README.md'
OUT = ROOT / 'quiz.html'

def md_image_to_html(text):
    # convert markdown image ![alt](path) to <img>
    return re.sub(r"!\[[^\]]*\]\(([^)]+)\)", r"<img src='\1' style='max-width:320px'>", text)

def parse(readme_text):
    lines = readme_text.splitlines()
    items = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('### '):
            q = line[4:].strip()
            i += 1
            # collect until Back to Top or next question
            options = []
            while i < len(lines):
                l = lines[i].rstrip()
                if l.strip().startswith('**[⬆ Back to Top]') or l.strip().startswith('### '):
                    break
                m = re.match(r"^- \[(x| )\] ?(.*)$", l.strip())
                if m:
                    correct = (m.group(1).lower() == 'x')
                    text = m.group(2).strip()
                    text = md_image_to_html(text)
                    options.append({'text': text, 'correct': correct})
                i += 1
            items.append({'question': q, 'options': options})
        else:
            i += 1
    return items

TEMPLATE = '''<!doctype html>
<html><head><meta charset="utf-8"><title>Quiz</title>
<style>
body{font-family:Arial,Helvetica,sans-serif;padding:20px}
.q{border:1px solid #ddd;padding:12px;margin:12px 0}
.opts{margin-top:8px}
.opt{display:block;margin:6px 0}
.correct{background:#d4ffd4}
.incorrect{background:#ffd4d4}
.controls{margin-top:8px}
button{padding:6px 10px}
img{display:block;margin:6px 0}
</style>
</head><body>
<h1>Quiz</h1>
<p>Answers are hidden. Select option(s) and click "Check" to reveal.</p>
<div id="container"></div>
<script>
const data = REPLACEME_DATA;
function render(){
  const c = document.getElementById('container');
  data.forEach((item, idx) => {
    const div = document.createElement('div'); div.className='q';
    const h = document.createElement('div'); h.innerHTML = '<strong>'+ (idx+1) +'.</strong> ' + item.question; div.appendChild(h);
    const opts = document.createElement('div'); opts.className='opts';
    const multi = item.options.filter(o=>o.correct).length>1;
    item.options.forEach((o,i)=>{
      const label = document.createElement('label'); label.className='opt';
      const input = document.createElement('input'); input.type = multi ? 'checkbox' : 'radio'; input.name = 'q'+idx; input.dataset.index = i;
      const span = document.createElement('span'); span.innerHTML = ' ' + o.text;
      label.appendChild(input); label.appendChild(span);
      opts.appendChild(label);
    });
    div.appendChild(opts);
    const controls = document.createElement('div'); controls.className='controls';
    const btn = document.createElement('button'); btn.textContent='Check';
    btn.addEventListener('click', ()=>check(idx));
    const reveal = document.createElement('button'); reveal.textContent='Reveal'; reveal.style.marginLeft='8px';
    reveal.addEventListener('click', ()=>revealAnswers(idx));
    controls.appendChild(btn); controls.appendChild(reveal);
    div.appendChild(controls);
    c.appendChild(div);
  });
}
function check(idx){
  const q = data[idx];
  const container = document.getElementById('container').children[idx];
  const inputs = container.querySelectorAll('input');
  const selected = [];
  inputs.forEach((inp)=>{ if(inp.checked) selected.push(parseInt(inp.dataset.index)); });
  const correctIdx = q.options.map((o,i)=>o.correct?i:null).filter(x=>x!==null);
  const allMatch = selected.length===correctIdx.length && selected.every(v=>correctIdx.includes(v));
  // highlight
  inputs.forEach((inp)=>{
    const i = parseInt(inp.dataset.index);
    inp.disabled = true;
    const lab = inp.parentElement;
    lab.classList.remove('correct','incorrect');
    if(q.options[i].correct) lab.classList.add('correct');
    if(inp.checked && !q.options[i].correct) lab.classList.add('incorrect');
  });
  const msg = document.createElement('div'); msg.style.marginTop='6px'; msg.textContent = allMatch ? 'Correct!' : 'Incorrect.';
  container.appendChild(msg);
}
function revealAnswers(idx){
  const q = data[idx];
  const container = document.getElementById('container').children[idx];
  const inputs = container.querySelectorAll('input');
  inputs.forEach((inp)=>{ inp.disabled = true; const i=parseInt(inp.dataset.index); const lab=inp.parentElement; if(q.options[i].correct) lab.classList.add('correct'); });
}
render();
</script>
</body></html>
'''

def main():
    txt = README.read_text(encoding='utf-8')
    items = parse(txt)
    # prepare JSON-like safe string
    import json
    for it in items:
        # ensure option text is safe HTML
        for o in it['options']:
            o['text'] = o['text'].replace("\n"," ")
    data_js = json.dumps(items, ensure_ascii=False)
    out_html = TEMPLATE.replace('REPLACEME_DATA', data_js)
    OUT.write_text(out_html, encoding='utf-8')
    print('Wrote', OUT)

if __name__ == '__main__':
    main()
