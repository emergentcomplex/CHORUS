# Filename: web_ui.py (v2.2 - Deterministic Parsing)
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# v2.2: Implements deterministic parsing in the backend. It now takes the
#       AI's single block of text and uses regex to reliably split it into
#       structured sections for professional rendering, adhering to Axiom 3.

from flask import Flask, render_template, request, redirect, url_for, flash, abort, send_from_directory
from htmx_flask import Htmx
from scripts.db_connector import get_db_connection
import json
import markdown
import os
import hashlib
import pypandoc
import re # Import the regex module
from pathlib import Path

# --- Path Setup ---
project_root = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(project_root, 'scripts/templates')
static_dir = os.path.join(template_dir, 'static')
export_dir_base = os.path.join(project_root, 'exports')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = os.urandom(24)
htmx = Htmx(app)

# --- Hardened Queueing Function ---
def queue_new_query(query_text, mode='deep_dive'):
    """Connects to the DB and inserts a new task, with explicit error handling."""
    print("\n--- Attempting to queue new task ---")
    print(f"   Query: {query_text[:50]}...")
    
    conn = get_db_connection()
    if not conn:
        print("[!] FATAL: Could not get DB connection in queue_new_query.")
        return None

    query_data = {"query": query_text, "mode": mode}
    query_hash = hashlib.md5(json.dumps(query_data, sort_keys=True).encode()).hexdigest()
    
    try:
        with conn.cursor() as cursor:
            sql = "INSERT IGNORE INTO task_queue (user_query, query_hash, status) VALUES (%s, %s, 'PENDING')"
            cursor.execute(sql, (json.dumps(query_data), query_hash))
            conn.commit()
            if cursor.rowcount > 0:
                print(f"[+] SUCCESS: Task {query_hash} inserted and committed.")
                return query_hash
            else:
                print(f"[!] WARNING: Task {query_hash} was a duplicate.")
                return query_hash
    except Exception as e:
        print(f"[!] FATAL: An exception occurred while queueing the task: {e}")
        conn.rollback()
        return None
    finally:
        if conn: conn.close()
        print("--- Queueing attempt finished ---")

# --- Helper to get the raw report text ---
def get_report_raw_text(query_hash: str):
    """Retrieves the raw text block of the final report from the database."""
    conn = get_db_connection()
    if not conn: return None
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT state_json FROM query_state WHERE query_hash = %s", (query_hash,))
            state_row = cursor.fetchone()
            if state_row and state_row['state_json']:
                report_json = json.loads(state_row['state_json'])
                final_report_string = report_json.get('final_report_with_citations', '{}')
                # The persona_worker saves a dict which might contain raw_text or the parsed sections
                final_report_dict = json.loads(final_report_string)
                
                # Handle both old and new formats for resilience
                if 'raw_text' in final_report_dict:
                    return final_report_dict.get('raw_text')
                elif 'narrative_analysis' in final_report_dict:
                    # Reconstruct the block if we have the parsed version
                    return f"[NARRATIVE ANALYSIS]\n{final_report_dict['narrative_analysis']}\n\n[ARGUMENT MAP]\n{final_report_dict['argument_map']}\n\n[INTELLIGENCE GAPS]\n{final_report_dict['intelligence_gaps']}"
    except (json.JSONDecodeError, TypeError):
        return "Error: Could not parse report data from database."
    finally:
        if conn: conn.close()
    return None

# --- Main Routes ---
@app.route("/", methods=["GET", "POST"])
def dashboard():
    if request.method == "POST":
        query_text = request.form.get("query_text")
        mode = request.form.get("mode")
        if query_text:
            new_hash = queue_new_query(query_text, mode=mode)
            if new_hash: return redirect(url_for('query_details', query_hash=new_hash))
    return render_template('dashboard.html')

@app.route("/query/<query_hash>")
def query_details(query_hash):
    conn = get_db_connection()
    task = None
    if conn:
        try:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM task_queue WHERE query_hash = %s", (query_hash,))
                task = cursor.fetchone()
        finally:
            conn.close()
    if not task: abort(404)
    return render_template('details.html', task=task, query_hash=query_hash)

@app.route("/update_dashboard")
def update_dashboard():
    conn = get_db_connection()
    task_counts = {'pending': 0, 'in_progress': 0, 'completed': 0, 'failed': 0}
    recent_tasks = []
    if conn:
        try:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT status, COUNT(*) as count FROM task_queue GROUP BY status")
                counts = {row['status'].lower(): row['count'] for row in cursor.fetchall()}
                task_counts.update(counts)
                cursor.execute("SELECT user_query, status, created_at, worker_id, query_hash FROM task_queue ORDER BY created_at DESC LIMIT 15")
                recent_tasks = cursor.fetchall()
                for task in recent_tasks:
                    try: task['user_query_text'] = json.loads(task['user_query'])['query']
                    except: task['user_query_text'] = str(task['user_query'])
        finally:
            conn.close()
    return render_template('partials/dashboard_content.html', task_counts=task_counts, recent_tasks=recent_tasks)

# --- DEFINITIVE FIX: Upgraded Report Rendering Logic ---
@app.route("/update_report/<query_hash>")
def update_report(query_hash):
    conn = get_db_connection()
    progress_updates = []
    report_data = None # Will hold our parsed dictionary
    
    if conn:
        try:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT status_message, timestamp FROM task_progress WHERE query_hash = %s ORDER BY timestamp ASC", (query_hash,))
                progress_updates = cursor.fetchall()
            
            # 1. Get the single block of raw text from the database
            raw_text = get_report_raw_text(query_hash)
            
            if raw_text:
                # Check if the raw_text is an error message from the worker
                if raw_text.startswith("Error:"):
                    report_data = {"error": raw_text}
                else:
                    report_data = {}
                    # 2. Use regex to deterministically parse the text into sections
                    narrative = re.search(r'\[NARRATIVE ANALYSIS\](.*?)\[ARGUMENT MAP\]', raw_text, re.DOTALL)
                    arg_map = re.search(r'\[ARGUMENT MAP\](.*?)\[INTELLIGENCE GAPS\]', raw_text, re.DOTALL)
                    gaps = re.search(r'\[INTELLIGENCE GAPS\](.*)', raw_text, re.DOTALL)

                    # 3. Convert each section's Markdown to HTML for rendering
                    report_data['narrative_analysis_html'] = markdown.markdown(narrative.group(1).strip() if narrative else "")
                    report_data['argument_map_html'] = markdown.markdown(arg_map.group(1).strip() if arg_map else "")
                    report_data['intelligence_gaps_html'] = markdown.markdown(gaps.group(1).strip() if gaps else "")
        finally:
            if conn: conn.close()
            
    return render_template('partials/report_content.html', progress_updates=progress_updates, report_data=report_data)

# --- PDF Export (For completeness, assuming it exists) ---
@app.route("/export_pdf/<query_hash>", methods=["POST"])
def export_report_pdf(query_hash):
    # This is a placeholder for your actual PDF generation logic
    flash("PDF export functionality not fully implemented in this snippet.", "info")
    return redirect(url_for('query_details', query_hash=query_hash))

if __name__ == "__main__":
    app.run(debug=True, port=5001)