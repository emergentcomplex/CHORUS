# Filename: chorus_engine/infrastructure/web/web_ui.py (Refactored)
import json
import os
import hashlib
import re
import sys
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, flash, abort
from htmx_flask import Htmx
import markdown


from chorus_engine.adapters.persistence.mariadb_adapter import MariaDBAdapter

# --- Path Setup ---
project_root = Path(__file__).resolve().parent
template_dir = project_root / 'templates'
static_dir = template_dir / 'static'

app = Flask(__name__, template_folder=str(template_dir), static_folder=str(static_dir))
app.secret_key = os.urandom(24)
htmx = Htmx(app)

# --- Instantiate the adapter once for the app ---
db_adapter = MariaDBAdapter()

def queue_new_query(query_text, mode='deep_dive'):
    """Connects to the DB and inserts a new task, with explicit error handling."""
    conn = db_adapter._get_connection()
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
                return query_hash
            else:
                return query_hash
    except Exception as e:
        print(f"[!] FATAL: An exception occurred while queueing the task: {e}")
        conn.rollback()
        return None
    finally:
        if conn: conn.close()

def get_report_raw_text(query_hash: str):
    """Retrieves the raw text block of the final report from the database."""
    conn = db_adapter._get_connection()
    if not conn: return None
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT state_json FROM query_state WHERE query_hash = %s", (query_hash,))
            state_row = cursor.fetchone()
            if state_row and state_row['state_json']:
                state_json = json.loads(state_row['state_json'])
                if 'error' in state_json:
                    return f"Error: {state_json['error']}"
                
                report_json_str = state_json.get('final_report_with_citations', '{}')
                report_dict = json.loads(report_json_str)
                return report_dict.get('raw_text')
    except (json.JSONDecodeError, TypeError) as e:
        return f"Error: Could not parse report data from database: {e}"
    finally:
        if conn: conn.close()
    return None

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
    conn = db_adapter._get_connection()
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
    conn = db_adapter._get_connection()
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

@app.route("/update_report/<query_hash>")
def update_report(query_hash):
    conn = db_adapter._get_connection()
    progress_updates = []
    report_data = None
    
    if conn:
        try:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT status_message, timestamp FROM task_progress WHERE query_hash = %s ORDER BY timestamp ASC", (query_hash,))
                progress_updates = cursor.fetchall()
            
            raw_text = get_report_raw_text(query_hash)
            
            if raw_text:
                if raw_text.startswith("Error:"):
                    report_data = {"error": raw_text}
                else:
                    report_data = {}
                    narrative = re.search(r'\[NARRATIVE ANALYSIS\](.*?)\[ARGUMENT MAP\]', raw_text, re.DOTALL)
                    arg_map = re.search(r'\[ARGUMENT MAP\](.*?)\[INTELLIGENCE GAPS\]', raw_text, re.DOTALL)
                    gaps = re.search(r'\[INTELLIGENCE GAPS\](.*)', raw_text, re.DOTALL)

                    report_data['narrative_analysis_html'] = markdown.markdown(narrative.group(1).strip() if narrative else "")
                    report_data['argument_map_html'] = markdown.markdown(arg_map.group(1).strip() if arg_map else "")
                    report_data['intelligence_gaps_html'] = markdown.markdown(gaps.group(1).strip() if gaps else "")
        finally:
            if conn: conn.close()
            
    return render_template('partials/report_content.html', progress_updates=progress_updates, report_data=report_data)

@app.route("/export_pdf/<query_hash>", methods=["POST"])
def export_report_pdf(query_hash):
    flash("PDF export functionality not yet implemented.", "info")
    return redirect(url_for('query_details', query_hash=query_hash))

if __name__ == "__main__":
    app.run(debug=True, port=5001)
