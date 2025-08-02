# Filename: tools/testing/validate_philosophy.py (Production Grade)
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# This script is the "Constitutional Guardian." It convenes a council of AI
# judges to perform a qualitative audit of code changes, ensuring they align
# with the philosophical principles of the CHORUS Constitution.

import os
import sys
import subprocess
import json
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# --- LLM Imports ---
import google.genai as genai
from openai import OpenAI
from xai_sdk import Client as XAI_Client
from dotenv import load_dotenv

# --- CONFIGURATION ---
# Suppress noisy logs from HTTPX clients used by SDKs
logging.getLogger("httpx").setLevel(logging.WARNING)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONSTITUTION_PATH = PROJECT_ROOT / "docs/01_CONSTITUTION.md"

# The council of judges. We use fast, cost-effective models suitable for this task.
JUDGE_COUNCIL = {
    "Gemini-Flash": {"provider": "google", "model": "gemini-1.5-flash-latest"},
    "GPT-4o-mini":  {"provider": "openai", "model": "gpt-4o-mini"},
    "Grok-Llama3":  {"provider": "xai",    "model": "llama3-70b"} # Grok uses open-source models via its API
}

def get_changed_files_content() -> str:
    """Gets the content of all changed Python files in the current branch against main."""
    try:
        # Use 'main...HEAD' to compare the tip of the current branch to the common ancestor with main.
        # This is more robust for local topic branches.
        changed_files_list = subprocess.check_output(
            ['git', 'diff', '--name-only', 'main...HEAD', '--', '*.py'],
            text=True,
            stderr=subprocess.PIPE
        ).strip().split('\n')
        
        changed_files = [f for f in changed_files_list if f and os.path.exists(f)]

        if not changed_files:
            print("[*] No Python files changed in this branch compared to main. Nothing to audit.")
            return ""

        content = []
        for file_path in changed_files:
            content.append(f"--- Filename: ./{file_path} ---\n")
            with open(file_path, 'r', encoding='utf-8') as f:
                content.append(f.read())
            content.append("\n\n")
        
        return "".join(content)
    except subprocess.CalledProcessError as e:
        print(f"Warning: Could not determine changed files via git (is 'main' branch available?). Error: {e.stderr}", file=sys.stderr)
        return "Error: Could not determine changed files."

def get_llm_judgment(judge_name: str, client: any, model_name: str, prompt: str) -> dict:
    """Generic function to get a judgment from a specific LLM judge."""
    provider = JUDGE_COUNCIL[judge_name]["provider"]
    try:
        if provider == "google":
            config = genai.types.GenerationConfig(response_mime_type="application/json")
            response = client.generate_content(prompt, generation_config=config)
            return json.loads(response.text)
        elif provider == "openai":
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        elif provider == "xai":
            response = client.chat.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                json_mode=True
            )
            return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"alignment_score": 0, "rationale": f"ERROR: Judge {judge_name} failed to render a verdict. Reason: {e}"}

def main():
    """Main function to run the philosophical audit."""
    print("--- 🔱 CHORUS Philosophical Alignment Audit (Production) ---")
    
    # 1. Initialize Clients
    load_dotenv(dotenv_path=PROJECT_ROOT / '.env')
    clients = {}
    try:
        clients["google"] = genai.GenerativeModel(JUDGE_COUNCIL["Gemini-Flash"]["model"])
        clients["openai"] = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        clients["xai"] = XAI_Client(api_key=os.getenv("XAI_API_KEY"))
        print("[*] All LLM clients initialized successfully.")
    except Exception as e:
        print(f"[!] FATAL: Could not initialize all LLM clients. Check API keys. Error: {e}", file=sys.stderr)
        sys.exit(1)

    # 2. Gather Context
    print("[*] Gathering context for analysis...")
    try:
        with open(CONSTITUTION_PATH, 'r', encoding='utf-8') as f:
            constitution_text = f.read()
    except FileNotFoundError:
        print(f"[!] FATAL: Constitution not found at '{CONSTITUTION_PATH}'. Aborting.", file=sys.stderr)
        sys.exit(1)

    changed_code = get_changed_files_content()
    if not changed_code or "Error:" in changed_code:
        sys.exit(0)

    print(f"[*] Auditing {len(changed_code.split('--- Filename:')) - 1} changed Python file(s)...")

    # 3. Construct Prompt
    prompt = f"""
    You are a CHORUS Constitutional Guardian, an AI expert in software architecture and the specific principles of the CHORUS project. Your task is to perform a qualitative audit of new code contributions.

    [THE CHORUS CONSTITUTION (LOGOS & ETHOS)]
    {constitution_text}
    ---
    [THE PROPOSED CODE CHANGES]
    {changed_code}
    ---
    [YOUR TASK]
    Analyze the code changes in the context of the Constitution. Your output MUST be a single, clean JSON object with two keys: "alignment_score" (integer 0-100) and "rationale" (a concise analysis explaining your score, citing specific Axioms).
    """

    # 4. Convene the Council
    print("[*] Submitting audit request to the Council of Judges in parallel...")
    verdicts = {}
    with ThreadPoolExecutor(max_workers=len(JUDGE_COUNCIL)) as executor:
        future_to_judge = {
            executor.submit(
                get_llm_judgment,
                name,
                clients[details["provider"]],
                details["model"],
                prompt
            ): name for name, details in JUDGE_COUNCIL.items()
        }
        for future in future_to_judge:
            judge_name = future_to_judge[future]
            verdicts[judge_name] = future.result()

    # 5. Display the Report
    print("\n" + "="*80)
    print("--- COUNCIL OF JUDGES: AUDIT REPORT ---")
    
    total_score = 0
    valid_verdicts = 0
    for judge, verdict in verdicts.items():
        score = verdict.get("alignment_score", 0)
        rationale = verdict.get("rationale", "No rationale provided.")
        print("\n" + "-"*40)
        print(f"VERDICT FROM: {judge}")
        print(f"Alignment Score: {score} / 100")
        print("Rationale:")
        print(rationale)
        if "ERROR" not in rationale:
            total_score += score
            valid_verdicts += 1
    
    average_score = (total_score / valid_verdicts) if valid_verdicts > 0 else 0

    print("\n" + "="*80)
    print("--- FINAL VERDICT ---")
    print(f"Average Alignment Score: {average_score:.1f} / 100")

    if average_score < 75:
        print("\n[!] VERDICT: Low alignment score. The council finds these changes may violate the spirit of the Constitution. Review rationale carefully before merging.")
        sys.exit(1)
    else:
        print("\n[✅] VERDICT: The Council of Judges finds the proposed changes align with the CHORUS Constitution.")
        sys.exit(0)

if __name__ == "__main__":
    # Correctly add the project root to the Python path
    # to ensure that imports work regardless of execution directory.
    sys.path.insert(0, str(PROJECT_ROOT))
    main()
