# Filename: scripts/ingest_3_generate_dsv_data.py (FINAL, Corrected Version)
# Final Stage: Processes raw documents chunk by chunk, uses the LLM to extract
# semantic data in a simple text format, then parses and appends it to the final DSV file.

import json
import os
import re
import time
import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from dotenv import load_dotenv
import traceback

# --- CONFIGURATION ---
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
ERROR_LOG_FILE = "ingestion_errors_stage3.log"
RAW_DATA_DIR = "../data/darpa/"
FINAL_DSV_PATH = "../data/darpa/DARPA_Semantic_Vectors.dsv"

# --- THE FINAL, ROBUST PROMPT ---
EXTRACTION_PROMPT = """
You are an expert data extraction system. You will be given master dictionaries and a text chunk from a DoD budget document. Your task is to extract its structure and semantic content into a simple, line-based text format.

For EACH "R-2 Exhibit" you find, you MUST output the data using the following format:
PE_NUM: <The PE Number>
PE_TITLE: <The PE Title>
AP_YEAR: <The Fiscal Year of the Accomplishment/Plan>
AP_TYPE: <"Accomplishments" or "Plans">
AP_TRIPLET: <Action Term>; <Object Term>; <Attribute Term>

CRITICAL DIRECTIVES:
- Each piece of data MUST be on its own line, starting with the correct key.
- For the AP_TRIPLET, you MUST use the exact terms found in the provided dictionaries.
- Deconstruct sentences into their atomic parts for the triplets.
- Filter out all boilerplate and summary tables.
- If you find a new PE, start again with the PE_NUM key.
- Your entire output must be ONLY this plain text format.

[MASTER DICTIONARIES START]
{dictionaries_text}
[MASTER DICTIONARIES END]
"""

def log_error(message):
    """Appends a detailed error message to the log file."""
    with open(ERROR_LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n" + "-"*80 + "\n")

def call_gemini_api(prompt, context_data, attempt=1, max_retries=3):
    """Robust API call function."""
    if attempt > max_retries: return None
    try:
        model = genai.GenerativeModel("gemini-2.5-pro-latest")
        request_options = {"timeout": 400}
        full_prompt = f"{prompt}\n\n[TEXT CHUNK TO ANALYZE START]\n{context_data}\n[TEXT CHUNK TO ANALYZE END]"
        response = model.generate_content(full_prompt, request_options=request_options)
        return response.text
    except Exception as e:
        log_error(f"API call failed on attempt {attempt}. Error: {e}\nTraceback:\n{traceback.format_exc()}")
        time.sleep(5 * attempt)
        return call_gemini_api(prompt, context_data, attempt + 1)

def chunk_text(text_content, chunk_size=50000):
    """Splits the document into overlapping chunks."""
    words = text_content.split()
    chunks = []
    for i in range(0, len(words), chunk_size - 500):
        chunks.append(" ".join(words[i:i + chunk_size]))
    return chunks # <-- THE MISSING RETURN STATEMENT

def load_dictionaries_and_create_maps(dsv_path):
    """Loads dictionaries from the DSV file and creates term-to-index maps."""
    print("  -> Loading dictionaries from DSV header...")
    actions, objects, attributes = [], [], []
    with open(dsv_path, 'r', encoding='utf-8') as f:
        in_dict_section = False
        for line in f:
            if line.strip() == "[DICTIONARIES]":
                in_dict_section = True
                continue
            if line.strip() == "[DATA]":
                break
            if in_dict_section:
                try:
                    parts = line.strip().split(':', 2)
                    if parts[0] == 'A': actions.append(parts[2])
                    elif parts[0] == 'O': objects.append(parts[2])
                    elif parts[0] == 'T': attributes.append(parts[2])
                except IndexError:
                    continue
    
    action_map = {term: i for i, term in enumerate(actions)}
    object_map = {term: i for i, term in enumerate(objects)}
    attribute_map = {term: i for i, term in enumerate(attributes)}
    
    print(f"  -> Dictionaries loaded. {len(actions)} actions, {len(objects)} objects, {len(attributes)} attributes.")
    return {"actions": actions, "objects": objects, "attributes": attributes}, {"actions": action_map, "objects": object_map, "attributes": attribute_map}

def process_and_append_chunk(task_data):
    """Processes a chunk, converts it to DSV lines, and appends to the final file."""
    prompt, chunk, year, maps = task_data
    
    response_text = call_gemini_api(prompt, chunk)
    if not response_text: return

    dsv_lines_to_append = []
    current_pe_num, current_pe_title, current_ap_year, current_ap_type = "", "", "", ""
    for line in response_text.splitlines():
        line = line.strip()
        if not line: continue
        try:
            key, value = line.split(':', 1)
            value = value.strip()
            if key == "PE_NUM": current_pe_num = value
            elif key == "PE_TITLE": current_pe_title = value
            elif key == "AP_YEAR": current_ap_year = value
            elif key == "AP_TYPE": current_ap_type = value
            elif key == "AP_TRIPLET":
                parts = [p.strip() for p in value.split(';')]
                if len(parts) == 3:
                    action_idx = maps["actions"].get(parts[0], "")
                    object_idx = maps["objects"].get(parts[1], "")
                    attr_idx = maps["attributes"].get(parts[2], "")
                    triplet_str = f"{action_idx};{object_idx};{attr_idx};"
                    dsv_lines_to_append.append(f">>>|{current_pe_num}||{current_pe_title}|{year}|{current_ap_type}|{current_ap_year}|{triplet_str}\n")
        except ValueError:
            continue

    if dsv_lines_to_append:
        with open(FINAL_DSV_PATH, 'a', encoding='utf-8') as f:
            f.writelines(dsv_lines_to_append)

def main():
    print("\n--- Starting Ingestion Stage 3: Generating DSV Data ---")
    if os.path.exists(ERROR_LOG_FILE): os.remove(ERROR_LOG_FILE)

    dictionaries, maps = load_dictionaries_and_create_maps(FINAL_DSV_PATH)
    dict_text = ""
    for term in dictionaries["actions"]: dict_text += f"Action: {term}\n"
    for term in dictionaries["objects"]: dict_text += f"Object: {term}\n"
    for term in dictionaries["attributes"]: dict_text += f"Attribute: {term}\n"
    
    prompt_with_dicts = EXTRACTION_PROMPT.format(dictionaries_text=dict_text)

    all_files = sorted([f for f in os.listdir(RAW_DATA_DIR) if f.endswith(".txt")])
    tasks = []
    for filename in all_files:
        year = os.path.splitext(filename)[0].replace("DARPA", "")
        with open(os.path.join(RAW_DATA_DIR, filename), 'r', encoding='utf-8') as f:
            source_text = f.read()
        for chunk in chunk_text(source_text):
            tasks.append((prompt_with_dicts, chunk, year, maps))

    print(f"Found {len(tasks)} total chunks to process for DSV data generation.")
    with ThreadPoolExecutor(max_workers=10) as executor:
        list(tqdm(executor.map(process_and_append_chunk, tasks), total=len(tasks), desc="Generating DSV Data"))

    print("\n✅ DSV data generation complete.")
    # The final step of generating embeddings would now be run.

if __name__ == "__main__":
    main()
