# Filename: tools/ingestion/ingest_1_map_dictionaries.py
# "Map" Phase: Processes small text chunks and outputs terms to simple .txt files.

import os
import time
import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from dotenv import load_dotenv
import traceback
from pathlib import Path

# --- CONFIGURATION ---
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=PROJECT_ROOT / '.env')
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

ERROR_LOG_FILE = PROJECT_ROOT / "logs/ingestion_errors_stage1.log"
RAW_DATA_DIR = PROJECT_ROOT / "data/darpa/"
CHUNK_OUTPUT_DIR = PROJECT_ROOT / "data/darpa/temp_dictionary_chunks"

# --- NEW, PLAIN TEXT PROMPT ---
EXTRACTION_PROMPT = """
You are an AI data analysis system. Your function is to process a text chunk from a DoD budget document and extract all atomic concepts of a specific type.
[PRIMARY DIRECTIVE]
Parse ONLY the provided text chunk. Your output must be a simple, one-item-per-line list of {concept_type}. Do not add any other commentary, formatting, or numbering.

Example for "actions":
develop
integrate
test
"""

def log_error(message):
    with open(ERROR_LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n" + "-"*80 + "\n")

def call_gemini_api(prompt, context_data, attempt=1, max_retries=3):
    if attempt > max_retries: return None
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        full_prompt = f"{prompt}\n\n[TEXT CHUNK TO ANALYZE START]\n{context_data}\n[TEXT CHUNK TO ANALYZE END]"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        log_error(f"API call failed on attempt {attempt}. Error: {e}\nTraceback:\n{traceback.format_exc()}")
        time.sleep(5 * attempt)
        return call_gemini_api(prompt, context_data, attempt + 1)

def chunk_text(text_content, chunk_size=30000):
    words = text_content.split()
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i + chunk_size])

def process_chunk(task_data):
    filename, chunk_index, chunk_content = task_data
    
    for concept_type in ["actions", "objects", "attributes"]:
        output_path = CHUNK_OUTPUT_DIR / f"{filename}_chunk_{chunk_index}_{concept_type}.txt"
        if output_path.exists(): continue
        
        prompt = EXTRACTION_PROMPT.format(concept_type=concept_type)
        response_str = call_gemini_api(prompt, chunk_content)
        if response_str:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(response_str)

def main():
    print("--- Starting Ingestion Stage 1: Mapping Dictionaries to Text Files ---")
    if ERROR_LOG_FILE.exists(): ERROR_LOG_FILE.unlink()
    CHUNK_OUTPUT_DIR.mkdir(exist_ok=True)
    
    all_files = sorted([f for f in RAW_DATA_DIR.iterdir() if f.suffix == ".txt"])
    tasks = []
    for file_path in all_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_text = f.read()
        for i, chunk in enumerate(chunk_text(source_text)):
            tasks.append((file_path.stem, i, chunk))

    print(f"Found {len(tasks)} chunks to process across 3 concept types.")
    with ThreadPoolExecutor(max_workers=15) as executor:
        list(tqdm(executor.map(process_chunk, tasks), total=len(tasks), desc="Mapping Concepts"))

    print("\n✅ Map phase complete. All concepts extracted to temporary text files.")

if __name__ == "__main__":
    main()
