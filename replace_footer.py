import os
import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r"<div class='app-footer'>.*?</div>"
replacement = "<div class='app-footer'>\n        © 2026 - San Vicente CES\n    </div>"
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Footer replaced successfully!')
