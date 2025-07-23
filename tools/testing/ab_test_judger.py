# Filename: scripts/ab_test_judger.py (v5.2 - Archiving)
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# v5.2: The definitive archiving version. Saves the output of both
#       Report A and Report B to text files for manual review.

import os
import json
import time
import subprocess
import hashlib
import asyncio
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import numpy as np

import google.generativeai as genai
from openai import OpenAI
from xai_sdk import Client as XAI_Client
from xai_sdk.chat import system as xai_system, user as xai_user
from dotenv import load_dotenv
from db_connector import get_db_connection

# --- CONFIGURATION ---
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / '.env')
USER_QUERY = "Investigate the intersection of DARPA funding, corporate hiring, public news, and academic research for Quantum Computing."
FACTORED_DSV_PATH = Path(__file__).resolve().parent.parent / 'data' / 'darpa' / 'DARPA_Semantic_Vectors_factored.dsv'
SCRIPTS_DIR = Path(__file__).resolve().parent
# --- NEW: REPORT OUTPUT FILES ---
REPORT_A_OUTPUT_FILE = Path(__file__).resolve().parent.parent / "TEST_A_BASELINE_REPORT.txt"
REPORT_B_OUTPUT_FILE = Path(__file__).resolve().parent.parent / "TEST_B_CHORUS_REPORT.txt"


# --- LLM Client Setup ---
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    OPENAI_CLIENT = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    XAI_CLIENT = XAI_Client(api_key=os.getenv("XAI_API_KEY"))
    GEMINI_JUDGE = genai.GenerativeModel("gemini-2.5-pro")
except Exception as e:
    print(f"FATAL: Could not initialize all LLM clients. Please check your API keys. Error: {e}")
    exit(1)


# --- TEST A & B (Async versions) ---
async def run_test_a():
    """Runs the naive, single-shot LLM query and returns the report."""
    print("\n" + "="*80)
    print("=      [TASK A] STARTING: NAIVE BASELINE (FULL DATA DUMP)      =")
    print("="*80)
    
    if not FACTORED_DSV_PATH.exists():
        error_msg = f"Factored DSV file not found at absolute path: {FACTORED_DSV_PATH}"
        print(f"[TASK A] FAILED: {error_msg}")
        return {"error": error_msg}

    print(f"[*] Loading the FULL DSV file from: {FACTORED_DSV_PATH}")
    with open(FACTORED_DSV_PATH, 'r', encoding='utf-8') as f:
        dsv_context = f.read()
    print(f"[*] Context loaded ({len(dsv_context)} characters).")

    prompt = f"""
    You are a senior intelligence analyst. Analyze the provided raw DARPA budget data to answer the user's query. Your analysis should be based ONLY on the provided data.
    [USER QUERY]: {USER_QUERY}
    [RAW DARPA DATA]: {dsv_context}
    [YOUR TASK]: Generate a final report with a narrative analysis, argument map, and intelligence gaps.
    """

    print("[TASK A] Submitting single, large prompt to the LLM...")
    try:
        response = await GEMINI_JUDGE.generate_content_async(prompt)
        print("[TASK A] SUCCESS: Baseline report generated.")
        return {"report": response.text}
    except Exception as e:
        return {"error": f"API call failed: {e}"}

async def run_test_b():
    """Orchestrates the full CHORUS pipeline and returns the final report."""
    print("\n" + "="*80)
    print("=      [TASK B] STARTING: CHORUS METHOD (RAG + FUSION)      =")
    print("="*80)
    query_data = {"query": USER_QUERY, "mode": "deep_dive"}
    query_hash = hashlib.md5(json.dumps(query_data, sort_keys=True).encode()).hexdigest()

    print(f"[TASK B] Resetting and queueing task with hash: {query_hash}")
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM task_queue WHERE query_hash = %s", (query_hash,))
            cursor.execute("INSERT INTO task_queue (user_query, query_hash, status) VALUES (%s, %s, 'PENDING')", (json.dumps(query_data), query_hash))
        conn.commit()
    finally:
        conn.close()

    print("[TASK B] Launching CHORUS daemons...")
    sentinel_proc = await asyncio.create_subprocess_exec("python3", SCRIPTS_DIR / "trident_sentinel.py", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    launcher_proc = await asyncio.create_subprocess_exec("python3", SCRIPTS_DIR / "trident_launcher.py", stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    print("[TASK B] Monitoring task progress...")
    final_result = None
    start_time = time.time()
    while time.time() - start_time < 900:
        conn = get_db_connection()
        try:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT status, state_json FROM task_queue LEFT JOIN query_state USING(query_hash) WHERE query_hash = %s", (query_hash,))
                result = cursor.fetchone()
                if result and result['status'] == 'COMPLETED':
                    print("[TASK B] SUCCESS: Task COMPLETED.")
                    final_result = {"report": json.loads(result['state_json'])['final_report_with_citations']}
                    break
                if result and result['status'] == 'FAILED':
                    print("[TASK B] FAILED: Task FAILED.")
                    error_info = json.loads(result['state_json'])['error']
                    final_result = {"error": f"CHORUS pipeline failed:\n---\n{error_info}\n---"}
                    break
        finally:
            conn.close()
        await asyncio.sleep(15)

    print("[TASK B] Shutting down CHORUS daemons...")
    sentinel_proc.terminate()
    launcher_proc.terminate()

    if final_result:
        return final_result
    else:
        return {"error": "CHORUS method timed out after 15 minutes."}

# --- THE DEFINITIVE JUDGER ---
def get_llm_judgment(judge_name, model, dossier):
    """Generic function to call a specific LLM judge."""
    
    judging_prompt = f"""
    You are an impartial, expert intelligence analysis evaluator on a council of judges. Your task is to provide a quantitative score for two intelligence reports (Report A, Report B) based on a user's query.

    [USER QUERY]:
    {USER_QUERY}
    ---
    [REPORT A - "NAIVE BASELINE" METHOD]:
    {dossier['report_a']}
    ---
    [REPORT B - "CHORUS FUSION" METHOD]:
    {dossier['report_b']}
    ---

    [SCORING RUBRIC]:
    You must evaluate each report across ten dimensions. For each dimension, assign a score from 0 (complete failure) to 100 (perfect execution).

    1.  **Directness of Answer:** How well does the report directly address the user's specific query?
    2.  **Evidence-Based Reasoning:** Are the report's claims well-supported by the evidence it presents?
    3.  **Contextual Richness:** Does the report successfully integrate diverse, real-world information?
    4.  **Signal vs. Noise:** How well does the report filter out irrelevant information and focus on the most critical signals?
    5.  **Strategic Insight:** Does the report offer a higher-level, strategic perspective beyond simple summarization? (The "so what?")
    6.  **Identification of Gaps:** How effectively does the report identify specific, insightful, and actionable intelligence gaps?
    7.  **Verifiability:** How well is the report structured to allow for independent verification of its sources and claims?
    8.  **Clarity and Readability:** Is the report well-structured, clearly written, and easy for a human analyst to understand?
    9.  **Completeness:** How comprehensively does the report address all facets of the user's query?
    10. **Persona Adherence (Report B Only):** How well does Report B adhere to its assigned analytical persona (Strategic Threat Analyst)? (Score Report A as 50 for this dimension).

    [YOUR TASK]:
    Your output MUST be a single, clean JSON object. The object must contain two keys: "scorecard_a" and "scorecard_b".
    Each scorecard must be an object containing keys for all ten dimensions, with their corresponding integer scores.
    DO NOT include any other commentary or explanation.
    """
    
    try:
        if judge_name == "Gemini":
            config = genai.types.GenerationConfig(response_mime_type="application/json")
            response = model.generate_content(judging_prompt, generation_config=config)
            return json.loads(response.text)
        elif judge_name == "OpenAI":
            response = model.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": judging_prompt}], response_format={"type": "json_object"})
            return json.loads(response.choices[0].message.content)
        elif judge_name == "Grok":
            chat = model.chat.create(model="grok-4")
            chat.append(xai_system("You are a JSON-outputting evaluation bot."))
            chat.append(xai_user(judging_prompt))
            response = chat.sample()
            return json.loads(response.content)
    except Exception as e:
        print(f"[JUDGER] Call to {judge_name} failed: {e}")
        return None

def run_adjudication_council(report_a, report_b):
    """Submits reports to the full council of judges."""
    print("\n" + "="*80)
    print("=      SUBMITTING REPORTS TO ADJUDICATION COUNCIL      =")
    print("="*80)
    
    dossier = {"report_a": report_a, "report_b": report_b}
    judges = {
        "Gemini": GEMINI_JUDGE,
        "OpenAI": OPENAI_CLIENT,
        "Grok": XAI_CLIENT
    }
    
    all_verdicts = {}
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_judge = {executor.submit(get_llm_judgment, name, model, dossier): name for name, model in judges.items()}
        for future in future_to_judge:
            judge_name = future_to_judge[future]
            try:
                verdict = future.result()
                if verdict:
                    all_verdicts[judge_name] = verdict
                    print(f"[JUDGER] Verdict received from {judge_name}.")
                else:
                    all_verdicts[judge_name] = {"error": "No response"}
            except Exception as e:
                all_verdicts[judge_name] = {"error": f"Exception: {e}"}
    
    return all_verdicts

# --- MAIN ASYNC ORCHESTRATOR ---
async def main():
    """Main orchestration function."""
    async with asyncio.TaskGroup() as tg:
        print("--- Launching Test A and Test B asynchronously ---")
        task_a = tg.create_task(run_test_a())
        task_b = tg.create_task(run_test_b())

    result_a = task_a.result()
    result_b = task_b.result()

    report_a_content = result_a.get('report', json.dumps(result_a.get('error', 'Test A produced no output.')))
    report_b_content_dict = result_b.get('report', {"error": "Test B produced no output."})
    
    # Extract the raw text from the CHORUS report for the judger
    if isinstance(report_b_content_dict, str):
        try: report_b_content_dict = json.loads(report_b_content_dict)
        except json.JSONDecodeError: report_b_content_dict = {"error": "Could not parse CHORUS report JSON."}
    
    report_b_for_judger = report_b_content_dict.get('raw_text', json.dumps(report_b_content_dict))

    # --- THE DEFINITIVE FIX: SAVE REPORTS TO DISK ---
    print("\n[*] Saving reports to disk for manual review...")
    with open(REPORT_A_OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(report_a_content)
    with open(REPORT_B_OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(report_b_for_judger)
    print(f"[+] Report A saved to: {REPORT_A_OUTPUT_FILE}")
    print(f"[+] Report B saved to: {REPORT_B_OUTPUT_FILE}")
    
    verdicts = run_adjudication_council(report_a_content, report_b_for_judger)

    print("\n\n" + "="*80)
    print("=      A/B TEST - FINAL VERDICT      =")
    print("="*80)
    
    scores_a = defaultdict(list)
    scores_b = defaultdict(list)
    
    for judge, verdict in verdicts.items():
        print(f"\n--- Judge: {judge} ---")
        if "error" in verdict or "scorecard_a" not in verdict:
            print(f"  Verdict invalid: {verdict.get('error', 'Malformed scorecard')}")
            continue
        
        score_a = sum(verdict["scorecard_a"].values())
        score_b = sum(verdict["scorecard_b"].values())
        print(f"  Score A (Baseline): {score_a} / 1000")
        print(f"  Score B (CHORUS):   {score_b} / 1000")
        
        for dim, score in verdict["scorecard_a"].items(): scores_a[dim].append(score)
        for dim, score in verdict["scorecard_b"].items(): scores_b[dim].append(score)

    avg_scores_a = {dim: np.mean(s) for dim, s in scores_a.items()}
    avg_scores_b = {dim: np.mean(s) for dim, s in scores_b.items()}
    
    total_avg_a = sum(avg_scores_a.values())
    total_avg_b = sum(avg_scores_b.values())

    print("\n" + "-"*40)
    print("--- AGGREGATE COUNCIL SCORE ---")
    print(f"  Average Score A (Baseline): {total_avg_a:.1f} / 1000")
    print(f"  Average Score B (CHORUS):   {total_avg_b:.1f} / 1000")
    print("-" * 40)

    print("\n--- DEFINITIVE CONCLUSION ---")
    if total_avg_b > total_avg_a:
        print(f"✅ CHORUS (B) is the definitive winner with a score of {total_avg_b:.1f}, compared to Baseline's {total_avg_a:.1f}.")
        improvements = {dim: avg_scores_b.get(dim, 0) - avg_scores_a.get(dim, 0) for dim in avg_scores_a.keys()}
        best_dim = max(improvements, key=improvements.get)
        print(f"   The most significant improvement was in '{best_dim}', with a score increase of {improvements[best_dim]:.1f} points.")
    else:
        print(f"❌ Baseline (A) is the winner with a score of {total_avg_a:.1f}, compared to CHORUS's {total_avg_b:.1f}.")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except AttributeError:
        print("\nFATAL: This script requires Python 3.11+ for asyncio.TaskGroup.")