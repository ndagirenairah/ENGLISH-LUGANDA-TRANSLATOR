#!/usr/bin/env python3
"""Debug Flask template loading"""

from flask import Flask, render_template
from pathlib import Path

app = Flask(__name__, template_folder='templates')

print(f"Template folder: {app.template_folder}")
print(f"Template path: {Path(app.template_folder) / 'index.html'}")

# Check the actual file
file_path = Path(app.template_folder) / 'index.html'
if file_path.exists():
    with open(file_path, 'rb') as f:
        content = f.read()
        print(f"File size: {len(content)} bytes")
        print(f"Has emoji bytes (\\xf0\\x9f): {b'\xf0\x9f' in content}")

# Now render and check
with app.app_context():
    html = render_template('index.html')
    print(f"Rendered HTML size: {len(html)} bytes")
    
    # Check for globe emoji
    globe_emoji = '\U0001f30d'
    if globe_emoji in html:
        print(f"Rendered HTML HAS globe emoji!")
        # Find where it is
        idx = html.find(globe_emoji)
        print(f"Position: {idx}")
        print(f"Context: {repr(html[max(0, idx-50):idx+50])}")
    else:
        print("Rendered HTML does NOT have globe emoji")
