from frontend.mapa_interativo import _TEMPLATE
import re
match = re.search(r'<script>(.*?)</script>', _TEMPLATE, re.DOTALL)
if match:
    with open('test_script.js', 'w', encoding='utf-8') as f:
        f.write(match.group(1).replace('__JS_VARS__', 'var uLat=0, uLng=0;'))
print('Extracted')
