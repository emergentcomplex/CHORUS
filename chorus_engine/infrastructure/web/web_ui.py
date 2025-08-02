# Filename: chorus_engine/infrastructure/web/web_ui.py (PostgreSQL Pivot)
import json
import os
import hashlib
import re
import sys
import time
import logging
from pathlib import Path
from threading import Thread
from collections import Counter
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash, abort, g
from htmx_flask import Htmx
import markdown
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Gauge
from psycopg2.extras import RealDictCursor

from chorus_engine.config import setup_logging
from chorus_engine.adapters.persistence.redis_adapter import RedisAdapter
from chorus_engine.adapters.persistence.postgres_adapter import PostgresAdapter

# --- Path Setup ---
project_root = Path(__file__).resolve().parent
template_dir = project_root / 'templates'
static_dir = template_dir / 'static'

# --- EXPLICITLY initialize centralized logging ---
setup_logging()
sli_logger = logging.getLogger('sli')

app = Flask(__name__, template_folder=str(template_dir), static_folder=str(static_dir))
app.secret_key = os.urandom(24)
htmx = Htmx(app)

# --- Prometheus Metrics Exporter ---
metrics = PrometheusMetrics(app)

# --- Custom Application Metrics ---
task_queue_gauge = Gauge(
    'chorus_task_queue_status_count',
    'Number of tasks in the queue by status',
    ['status']
)

# --- Instantiate adapters once for the app ---
redis_adapter = RedisAdapter()
db_adapter = PostgresAdapter()

# --- Background thread for updating custom metrics ---
def update_custom_metrics():
    """Periodically queries the derived data store and updates Prometheus gauges."""
    while True:
        try:
            all_tasks = redis_adapter.get_all_tasks_sorted_by_time()
            status_counts = Counter(task.get('status', 'UNKNOWN') for task in all_tasks)
            
            statuses = {'PENDING': 0, 'IN_PROGRESS': 0, 'COMPLETED': 0, 'FAILED': 0}
            statuses.update(status_counts)
            
            for status, count in statuses.items():
                task_queue_gauge.labels(status=status).set(count)
        except Exception as e:
            logging.error(f"Error updating custom metrics from Redis: {e}")
        
        time.sleep(30)

# --- SLI Component Mapping ---
SLI_COMPONENT_MAP = {
    'dashboard': 'C-WEB (Dashboard Load)',
    'update_dashboard': 'C-WEB (HTMX Poll)',
    'update_report': 'C-WEB (HTMX Poll)',
}

# --- SLI Measurement Middleware ---
@app.before_request
def start_timer():
    g.start_time = time.perf_counter()

@app.after_request
def log_request_latency(response):
    if 'start_time' in g and request.endpoint:
        latency_ms = (time.perf_counter() - g.start_time) * 1000
        component_name = SLI_COMPONENT_MAP.get(request.endpoint, f"C-WEB ({request.endpoint})")
        sli_logger.info(
            'request_latency',
            extra={
                'component': component_name,
                'endpoint': request.endpoint,
                'status_code': response.status_code,
                'latency_ms': round(latency_ms, 2)
            }
        )
    return response

def queue_new_query(query_text, mode='deep_dive'):
    """Connects to the DB and inserts a new task. This is a WRITE operation."""
    conn = db_adapter._get_connection()
    if not conn:
        logging.error("[!] FATAL: Could not get DB connection in queue_new_query.")
        return None

    query_data = {"query": query_text, "mode": mode}
    query_hash = hashlib.md5(json.dumps(query_data, sort_keys=True).encode()).hexdigest()
    
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO task_queue (user_query, query_hash, status) VALUES (%s, %s, 'PENDING') ON CONFLICT (query_hash) DO NOTHING"
            cursor.execute(sql, (json.dumps(query_data), query_hash))
            conn.commit()
            return query_hash
    except Exception as e:
        logging.error(f"[!] FATAL: An exception occurred while queueing the task: {e}")
        conn.rollback()
        return None
    finally:
        db_adapter._release_connection(conn)

def get_report_raw_text(query_hash: str):
    """Retrieves the raw text block of the final report from the database."""
    conn = db_adapter._get_connection()
    if not conn: return None
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT state_json FROM query_state WHERE query_hash = %s", (query_hash,))
            state_row = cursor.fetchone()
            if state_row and state_row['state_json']:
                state_json = state_row['state_json']
                if 'error' in state_json:
                    return f"Error: {state_json['error']}"
                
                report_json_str = state_json.get('final_report_with_citations', '{}')
                report_dict = json.loads(report_json_str)
                return report_dict.get('raw_text')
    except (json.JSONDecodeError, TypeError) as e:
        return f"Error: Could not parse report data from database: {e}"
    finally:
        db_adapter._release_connection(conn)
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
    task = redis_adapter.get_task_by_hash(query_hash)
    if not task: abort(404)
    return render_template('details.html', task=task, query_hash=query_hash)

@app.route("/update_dashboard")
def update_dashboard():
    all_tasks = redis_adapter.get_all_tasks_sorted_by_time()
    
    status_counts = Counter(task.get('status', 'UNKNOWN').lower() for task in all_tasks)
    task_counts = {
        'pending': status_counts.get('pending', 0),
        'in_progress': status_counts.get('in_progress', 0),
        'completed': status_counts.get('completed', 0),
        'failed': status_counts.get('failed', 0)
    }
    
    recent_tasks = all_tasks[:15]
    for task in recent_tasks:
        try:
            task['user_query_text'] = task['user_query']['query'] if isinstance(task['user_query'], dict) else json.loads(task['user_query'])['query']
            if 'created_at' in task:
                task['created_at_dt'] = datetime.fromisoformat(task['created_at'])
        except (json.JSONDecodeError, TypeError, ValueError):
            task['user_query_text'] = str(task.get('user_query', ''))
            task['created_at_dt'] = None

    return render_template('partials/dashboard_content.html', task_counts=task_counts, recent_tasks=recent_tasks)

@app.route("/update_report/<query_hash>")
def update_report(query_hash):
    conn = db_adapter._get_connection()
    progress_updates = []
    report_data = None
    
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT status_message, timestamp FROM task_progress WHERE query_hash = %s ORDER BY timestamp ASC", (query_hash,))
                progress_updates = cursor.fetchall()
        finally:
            db_adapter._release_connection(conn)
            
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
            
    return render_template('partials/report_content.html', progress_updates=progress_updates, report_data=report_data)

@app.route("/export_pdf/<query_hash>", methods=["POST"])
def export_report_pdf(query_hash):
    flash("PDF export functionality not yet implemented.", "info")
    return redirect(url_for('query_details', query_hash=query_hash))

@app.route("/health")
def health_check():
    """A simple health check endpoint for availability monitoring."""
    return {"status": "ok"}, 200

if __name__ == "__main__":
    metrics_thread = Thread(target=update_custom_metrics, daemon=True)
    metrics_thread.start()
    app.run(debug=True, port=5001)
