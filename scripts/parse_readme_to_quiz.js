const fs = require('fs');
const path = require('path');
const ROOT = path.resolve(__dirname, '..');
const README = path.join(ROOT, 'README.md');
const OUT = path.join(ROOT, 'docs', 'quiz.json');

function mdImageToHtml(text){
  return text.replace(/!\[[^\]]*\]\(([^)]+)\)/g, "<img src='$1' style='max-width:320px'>");
}

const txt = fs.readFileSync(README, 'utf8');
const lines = txt.split(/\r?\n/);
const items = [];
for(let i=0;i<lines.length;i++){
  const line = lines[i].trim();
  if(line.startsWith('### ')){
    let q = line.substring(4).trim();
    i++;
    const options = [];
    const extraText = [];
    while(i<lines.length){
      const l = lines[i].trim();
      if(l.startsWith('**[⬆ Back to Top]') || l.startsWith('### ')) { i--; break; }
      const m = l.match(/^- \[(x| )\] ?(.*)$/i);
      if(m){
        const correct = m[1].toLowerCase() === 'x';
        let text = m[2].trim();
        text = mdImageToHtml(text);
        // Convert inline code to HTML code tags in options
        text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
        options.push({text, correct});
      } else if (l !== '') {
        // Check if it's an image for the last option
        const imgMatch = l.match(/^!\[[^\]]*\]\(([^)]+)\)$/);
        if (imgMatch && options.length > 0) {
          options[options.length - 1].image = imgMatch[1];
        } else {
          extraText.push(l);
        }
      }
      i++;
    }
    
    let image = null;
    if (extraText.length > 0) {
      const joined = extraText.join('\n');
      const imgMatch = joined.match(/!\[[^\]]*\]\(([^)]+)\)/);
      if (imgMatch) {
        image = imgMatch[1];
        // Remove the image markdown from extra text
        const remainingText = joined.replace(/!\[[^\]]*\]\(([^)]+)\)/, '').trim();
        if (remainingText) {
          q += '\n\n' + remainingText;
        }
      } else {
        // Check if it's a code block
        if (joined.includes('```')) {
          q += '\n\n' + joined;
        } else {
          q += '\n\n' + joined;
        }
      }
    }

    // Convert markdown code blocks to HTML pre/code tags
    q = q.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
    // Convert inline code to HTML code tags
    q = q.replace(/`([^`]+)`/g, '<code>$1</code>');

    const item = {question: q, options};
    if (image) {
      item.image = image;
    }
    items.push(item);
  }
}

fs.writeFileSync(OUT, JSON.stringify(items, null, 2), 'utf8');
console.log('Wrote', OUT, 'items:', items.length);
