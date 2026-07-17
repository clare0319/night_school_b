from pathlib import Path

root = Path('templates')
files = sorted(root.rglob('*.html'))
link = "    <link rel=\"stylesheet\" href=\"{{ url_for('static', filename='shared_ui.css') }}\">"
updated = []

for path in files:
    text = path.read_text(encoding='utf-8')
    if 'shared_ui.css' in text:
        continue
    if '</head>' in text.lower():
        text = text.replace('</head>', f'{link}\n</head>', 1)
        path.write_text(text, encoding='utf-8')
        updated.append(str(path))

print(f'updated {len(updated)} files')
for item in updated[:20]:
    print(item)
