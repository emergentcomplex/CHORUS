# Filename: tools/docs/generate_and_serve_docs.py
# A tool to automatically generate and serve live documentation for the CHORUS project.

import subprocess
import os
import http.server
import socketserver
import webbrowser
from pathlib import Path
import shutil
import sys
import markdown

# --- CONFIGURATION ---
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOCS_OUTPUT_DIR = PROJECT_ROOT / "docs_build"
SOURCE_CODE_DIR = PROJECT_ROOT / "chorus_engine"
MISSION_CHARTER_PATH = PROJECT_ROOT / "docs/00_MISSION_CHARTER.md"
PORT = 8001

def generate_docs():
    """Uses pdoc to scan the codebase and generate HTML documentation."""
    print(f"[*] Generating documentation for modules in '{SOURCE_CODE_DIR}'...")
    DOCS_OUTPUT_DIR.mkdir(exist_ok=True)
    try:
        # Ensure pdoc is available
        if shutil.which("pdoc") is None:
            print("[!] 'pdoc' command not found. Please ensure it is installed (`pip install pdoc`).")
            sys.exit(1)

        subprocess.run(
            [
                "pdoc",
                "--html",
                "--output-dir", str(DOCS_OUTPUT_DIR),
                "--force",
                str(SOURCE_CODE_DIR)
            ],
            check=True,
            cwd=PROJECT_ROOT # Run from project root for consistent context
        )
        print(f"[+] Documentation generated successfully in: {DOCS_OUTPUT_DIR}")
        
        # Use the Mission Charter as the documentation index.
        docs_index_path = DOCS_OUTPUT_DIR / "index.html"
        if MISSION_CHARTER_PATH.exists():
            # Convert the Markdown Mission Charter to HTML for the index page.
            with open(MISSION_CHARTER_PATH, "r", encoding="utf-8") as f:
                markdown_content = f.read()
            
            html_content = markdown.markdown(markdown_content)
            
            # Create a simple HTML wrapper for the content
            full_html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>CHORUS Mission Charter</title>
                <style>
                    body {{ font-family: sans-serif; line-height: 1.6; max-width: 800px; margin: 2rem auto; padding: 0 1rem; }}
                    a {{ color: #007bff; }}
                    h1, h2, h3 {{ border-bottom: 1px solid #ccc; padding-bottom: 0.3em; }}
                    code {{ background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
                    pre {{ background-color: #f4f4f4; padding: 1rem; border-radius: 5px; overflow-x: auto; }}
                </style>
            </head>
            <body>
                <h1><a href="chorus_engine/index.html">View Code Documentation →</a></h1>
                <hr>
                {html_content}
            </body>
            </html>
            """
            with open(docs_index_path, "w", encoding="utf-8") as f:
                f.write(full_html)

            print(f"[*] Set documentation index from '{MISSION_CHARTER_PATH.name}'.")

    except Exception as e:
        print(f"[!] Error during documentation generation: {e}")
        sys.exit(1)

def serve_docs():
    """Starts a simple, local web server to serve the generated documentation."""
    os.chdir(DOCS_OUTPUT_DIR)
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}"
        print(f"\n[*] Serving live documentation at: {url}")
        webbrowser.open_new_tab(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[*] Shutting down documentation server.")
            httpd.server_close()

if __name__ == "__main__":
    generate_docs()
    serve_docs()
