#!/usr/bin/env python3
"""Debug version to check what Flask is serving"""

from flask import Flask, render_template

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    html = render_template("index.html")
    # Check for globe emoji
    if '\U0001f30d' in html:
        print("ERROR: Flask is rendering HTML WITH emoji!", flush=True)
    else:
        print("OK: Flask is rendering HTML WITHOUT emoji", flush=True)
    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
