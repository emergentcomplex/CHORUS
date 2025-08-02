# Filename: tools/ingestion/ingest_3_generate_dsv_data.py

import json
import os
import re
import time
import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from dotenv import load_dotenv
import traceback
from pathlib import Path
import threading

# --- CONFIGURATION ---
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=PROJECT_ROOT / '.env')
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

ERROR_LOG_FILE = PROJECT_ROOT / "logs/ingestion_errors_stage3.log"
RAW_DATA_DIR = PROJECT_ROOT / "data/darpa/"
FINAL_DSV_PATH = PROJECT_ROOT / "data/darpa/DARPA_Semantic_Vectors.dsv"
CHUNK_SIZE_WORDS = 15000
MAX_WORKERS = 10

EXTRACTION_PROMPT = """
You are an expert data extraction system. You will be given a text chunk from a DoD budget document. Your task is to extract all "Accomplishments" and "Plans" for each Program Element (PE).

For EACH "R-2 Exhibit" you find, you MUST output the data using the following simple, line-based text format:
PE_NUM: <The PE Number>
PE_TITLE: <The PE Title>
AP_YEAR: <The Fiscal Year of the Accomplishment/Plan>
AP_TYPE: <"Accomplishments" or "Plans">
AP_TEXT: <The full, verbatim text of the accomplishment or plan sentence.>

CRITICAL DIRECTIVES:
- Each piece of data MUST be on its own line, starting with the correct key.
- Extract the AP_TEXT verbatim. Do not summarize or alter it.
- If you find a new PE, start again with the PE_NUM key.
- Your entire output must be ONLY this plain text format. No commentary.
"""

class DynamicDictionary:
    def __init__(self):
        self.lock = threading.Lock()
        self.term_maps = {"actions": {}, "objects": {}, "attributes": {}}
        self.next_indices = {"actions": 0, "objects": 0, "attributes": 0}

    def load_initial(self, dsv_path):
        print("  -> Loading initial dictionaries from DSV header...")
        with self.lock:
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
                            d_type_char, d_idx_str, d_term = line.strip().split(':', 2)
                            d_idx = int(d_idx_str)
                            if d_type_char == 'A':
                                self.term_maps["actions"][d_term] = d_idx
                                self.next_indices["actions"] = max(self.next_indices["actions"], d_idx + 1)
                            elif d_type_char == 'O':
                                self.term_maps["objects"][d_term] = d_idx
                                self.next_indices["objects"] = max(self.next_indices["objects"], d_idx + 1)
                            elif d_type_char == 'T':
                                self.term_maps["attributes"][d_term] = d_idx
                                self.next_indices["attributes"] = max(self.next_indices["attributes"], d_idx + 1)
                        except (ValueError, IndexError):
                            continue
        print(f"  -> Initial dictionaries loaded.")

    def get_or_add_term(self, term, term_type):
        with self.lock:
            term = term.strip()
            if not term: return None
            if term not in self.term_maps[term_type]:
                new_index = self.next_indices[term_type]
                self.term_maps[term_type][term] = new_index
                self.next_indices[term_type] += 1
                return new_index
            return self.term_maps[term_type][term]

dynamic_dictionary = DynamicDictionary()

def log_error(message):
    with open(ERROR_LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n" + "-"*80 + "\n")

def call_gemini_api(context_data, attempt=1, max_retries=3):
    if attempt > max_retries: return None
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        full_prompt = f"{EXTRACTION_PROMPT}\n\n[TEXT CHUNK TO ANALYZE START]\n{context_data}\n[TEXT CHUNK TO ANALYZE END]"
        response = model.generate_content(full_prompt, request_options={"timeout": 400})
        return response.text
    except Exception as e:
        log_error(f"API call failed on attempt {attempt}. Error: {e}\nTraceback:\n{traceback.format_exc()}")
        time.sleep(5 * attempt)
        return call_gemini_api(context_data, attempt + 1)

def chunk_text(text_content, chunk_size=CHUNK_SIZE_WORDS):
    words = text_content.split()
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i + chunk_size])

def text_to_triplet(text: str) -> str:
    lower_text = text.lower()
    action_idx, object_idx, attr_idx = "", "", ""
    with dynamic_dictionary.lock:
        for term, idx in dynamic_dictionary.term_maps["actions"].items():
            if term.lower() in lower_text:
                action_idx = str(idx)
                break
        for term, idx in dynamic_dictionary.term_maps["objects"].items():
            if term.lower() in lower_text:
                object_idx = str(idx)
                break
        for term, idx in dynamic_dictionary.term_maps["attributes"].items():
            if term.lower() in lower_text:
                attr_idx = str(idx)
                break
    return f"{action_idx};{object_idx};{attr_idx};"

def process_chunk(task_data):
    chunk, year, temp_file_path = task_data
    response_text = call_gemini_api(chunk)
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
            elif key == "AP_TEXT":
                triplet_str = text_to_triplet(value)
                dsv_lines_to_append.append(f">>>|{current_pe_num}||{current_pe_title}|{year}|{current_ap_type}|{current_ap_year}|{triplet_str}\n")
        except ValueError:
            continue

    if dsv_lines_to_append:
        with open(temp_file_path, 'a', encoding='utf-8') as f:
            f.writelines(dsv_lines_to_append)

def main():
    print("\n--- Starting Ingestion Stage 3: Generating DSV Data (Refactored) ---")
    if ERROR_LOG_FILE.exists(): ERROR_LOG_FILE.unlink()

    dynamic_dictionary.load_initial(FINAL_DSV_PATH)
    
    # Use a temporary file for intermediate data lines to avoid reading/writing the same file
    TEMP_DATA_PATH = FINAL_DSV_PATH.with_suffix(".tmp_data")
    if TEMP_DATA_PATH.exists(): TEMP_DATA_PATH.unlink()

    all_files = sorted([f for f in RAW_DATA_DIR.iterdir() if f.suffix == ".txt"])
    tasks = []
    for file_path in all_files:
        year = file_path.stem.replace("DARPA", "")
        with open(file_path, 'r', encoding='utf-8') as f:
            source_text = f.read()
        for chunk in chunk_text(source_text):
            tasks.append((chunk, year, TEMP_DATA_PATH))

    print(f"Found {len(tasks)} total chunks to process for DSV data generation.")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        list(tqdm(executor.map(process_chunk, tasks), total=len(tasks), desc="Generating DSV Data"))

    print("\nData generation complete. Rewriting final DSV with updated dictionaries...")

    # --- Final Rewrite Phase ---
    with open(FINAL_DSV_PATH, 'w', encoding='utf-8') as f_out:
        # Write META Header
        f_out.write("[META]\n")
        f_out.write("FILE_TYPE: DARPA_Semantic_Vector\nVERSION: 1.1\n")
        f_out.write("DESCRIPTION: A compressed, longitudinal semantic encoding of DARPA budget data.\n")
        f_out.write("DICTIONARY_FORMAT: TYPE:INDEX:TERM (A=Action, O=Object, T=Attribute)\n")
        f_out.write("DATA_FORMAT: HIERARCHY|PE_NUM|PROJ_NUM|INIT_TITLE|SRC_YEAR|AP_TYPE|AP_FY|TRIPLET\n")
        f_out.write("TRIPLET_FORMAT: ActionIndices;ObjectIndex;AttributeIndices;PurposeObjectIndex\n\n")

        # Write updated DICTIONARIES Section
        f_out.write("[DICTIONARIES]\n")
        with dynamic_dictionary.lock:
            for term, idx in sorted(dynamic_dictionary.term_maps["actions"].items(), key=lambda item: item[1]):
                f_out.write(f"A:{idx}:{term}\n")
            for term, idx in sorted(dynamic_dictionary.term_maps["objects"].items(), key=lambda item: item[1]):
                f_out.write(f"O:{idx}:{term}\n")
            for term, idx in sorted(dynamic_dictionary.term_maps["attributes"].items(), key=lambda item: item[1]):
                f_out.write(f"T:{idx}:{term}\n")
        f_out.write("\n")

        # Write DATA Section Header and content
        f_out.write("[DATA]\n")
        if TEMP_DATA_PATH.exists():
            with open(TEMP_DATA_PATH, 'r', encoding='utf-8') as f_in:
                f_out.write(f_in.read())
            TEMP_DATA_PATH.unlink()

    print("\n✅ DSV file rewritten with complete and consistent dictionaries.")

if __name__ == "__main__":
    main()
