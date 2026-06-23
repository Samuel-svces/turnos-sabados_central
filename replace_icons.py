import re

with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

replacements = [
    ('⚙️', "<i class='bi bi-gear-fill'></i>"),
    ('🔔', "<i class='bi bi-bell-fill'></i>"),
    ('🔄', "<i class='bi bi-arrow-repeat'></i>"),
    ('➕', "<i class='bi bi-plus-circle-fill'></i>"),
    ('👤', "<i class='bi bi-person-fill'></i>"),
    ('💬', "<i class='bi bi-chat-text-fill'></i>"),
    ('ℹ️', "<i class='bi bi-info-circle-fill'></i>"),
    ('⚠️', "<i class='bi bi-exclamation-triangle-fill'></i>"),
    ('📅', "<i class='bi bi-calendar-event'></i>"),
    ('💡', "<i class='bi bi-lightbulb-fill'></i>"),
    ('❌', "<i class='bi bi-x-circle-fill'></i>"),
    ('✅', "<i class='bi bi-check-circle-fill'></i>")
]

lines = text.split('\n')
for i, line in enumerate(lines):
    if 'st.markdown(' in line or 'st.write(' in line or 'unsafe_allow_html' in line or '<div' in line or '<span' in line:
        for old, new in replacements:
            lines[i] = lines[i].replace(old, new)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
