# Filename: scripts/generate_and_serve_docs.py
# A tool to automatically generate and serve live documentation for the CHORUS project.

import subprocess
import os
import http.server
import socketserver
import webbrowser
from pathlib import Path
import shutil

# --- CONFIGURATION ---
DOCS_OUTPUT_DIR = "../docs"
SOURCE_CODE_DIR = "./"
PORT = 8001

def generate_docs():
    """Uses pdoc to scan the codebase and generate HTML documentation."""
    print(f"[*] Generating documentation for modules in '{SOURCE_CODE_DIR}'...")
    Path(DOCS_OUTPUT_DIR).mkdir(exist_ok=True)
    try:
        subprocess.run(
            ["pdoc", "--html", "--output-dir", DOCS_OUTPUT_DIR, "--force", SOURCE_CODE_DIR],
            check=True
        )
        print("[+] Documentation generated successfully.")
        main_readme_path = Path("../README.md")
        docs_readme_path = Path(DOCS_OUTPUT_DIR) / "index.md"
        if main_readme_path.exists():
            shutil.copy(main_readme_path, docs_readme_path)
            print("[*] Copied main README.md to serve as documentation index.")
    except Exception as e:
        print(f"[!] Error during documentation generation: {e}")

def serve_docs():
    """Starts a simple, local web server to serve the generated documentation."""
    os.chdir(DOCS_OUTPUT_DIR)
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"\n[*] Serving live documentation at: http://localhost:{PORT}")
        webbrowser.open_new_tab(f"http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    generate_docs()
    serve_docs()
