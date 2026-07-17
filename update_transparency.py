from pathlib import Path
import re

root = Path('templates')
files = list(root.rglob('*.html'))
count = 0
for path in files:
    text = path.read_text(encoding='utf-8')
    if '.dialog-box {' in text and '.choices {' in text and '.choice-button {' in text:
        pattern = re.compile(r'(\s*)\.dialog-box \{.*?\n\s*\}\n\s*\.choices \{.*?\n\s*\}\n(?=\s*\.choice-button)', re.S)
        replacement = '''        .dialog-box {
            position: absolute;
            bottom: 5%;
            left: 50%;
            transform: translateX(-50%);
            width: 90%;
            height: 25%;
            background-color: rgba(255, 255, 255, 0.5);
            border-radius: 15px;
            padding: 20px;
            box-sizing: border-box;
            color: black;
            font-size: 1.2em;
            z-index: 2;
        }
        .choices {
            position: absolute;
            bottom: 35%;
            right: 5%;
            width: 90%;
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 10px;
            z-index: 3;
        }
'''
        new_text, replaced = pattern.subn(replacement, text, count=1)
        if replaced:
            text = new_text
            count += 1

    text = text.replace('        .bag-button-container {\n            position: absolute;\n            top: 5%;\n            left: 5%;\n        }\n', '        .bag-button-container {\n            position: absolute;\n            top: 5%;\n            left: 5%;\n            z-index: 4;\n        }\n')
    if '.bag-button-container {' in text and 'z-index: 4;' not in text:
        text = text.replace('.bag-button-container {', '.bag-button-container {\n            z-index: 4;')

    path.write_text(text, encoding='utf-8')

print(f'updated {count} files')
