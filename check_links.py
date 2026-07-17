import re
import pathlib
from pathlib import Path

server_text = Path('server.py').read_text(encoding='utf-8')
route_paths = set(re.findall(r"@app\.route\(\s*['\"]([^'\"]+)['\"]", server_text))
func_names = set(re.findall(r"^def\s+([A-Za-z0-9_]+)\s*\(", server_text, re.M))

for p in sorted(Path('templates').rglob('*.html')):
    text = p.read_text(encoding='utf-8', errors='ignore')
    for m in re.finditer(r"url_for\('([^']+)'", text):
        name = m.group(1)
        if name not in func_names:
            print(f'URL_FOR_MISSING {name} in {p}')
    for m in re.finditer(r'href="([^"]+)"', text):
        href = m.group(1)
        if href.startswith(('http://', 'https://', 'mailto:', 'javascript:', '{{', '#')):
            continue
        if href.startswith('/'): 
            path = href[1:]
            if path not in route_paths:
                print(f'ROUTE_MISSING {href} in {p}')
