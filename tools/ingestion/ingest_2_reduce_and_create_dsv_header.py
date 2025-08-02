# Filename: tools/ingestion/ingest_2_reduce_and_create_dsv_header.py
# "Reduce" Phase: Merges all temporary dictionary files and writes the
# final DSV header and [DICTIONARIES] section.

import os
import glob
from pathlib import Path
from tqdm import tqdm

# --- CONFIGURATION ---
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHUNK_INPUT_DIR = PROJECT_ROOT / "data/darpa/temp_dictionary_chunks"
FINAL_DSV_PATH = PROJECT_ROOT / "data/darpa/DARPA_Semantic_Vectors.dsv"

def main():
    print("--- Starting Ingestion Stage 2: Reducing Dictionaries & Writing DSV Header ---")
    
    master_actions = set()
    master_objects = set()
    master_attributes = set()

    for concept_type in ["actions", "objects", "attributes"]:
        target_set = locals()[f"master_{concept_type}"]
        chunk_files = list(CHUNK_INPUT_DIR.glob(f"*_{concept_type}.txt"))
        print(f"Found {len(chunk_files)} chunk files for '{concept_type}'.")
        
        for filepath in tqdm(chunk_files, desc=f"Reducing {concept_type}"):
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    term = line.strip()
                    if term:
                        target_set.add(term)

    final_actions = sorted(list(master_actions))
    final_objects = sorted(list(master_objects))
    final_attributes = sorted(list(master_attributes))

    print("\nWriting final DSV header and dictionaries...")
    with open(FINAL_DSV_PATH, 'w', encoding='utf-8') as f:
        f.write("[META]\n")
        f.write("FILE_TYPE: DARPA_Semantic_Vector\nVERSION: 1.0\n")
        f.write("DESCRIPTION: A compressed, longitudinal semantic encoding of DARPA budget data.\n")
        f.write("DICTIONARY_FORMAT: TYPE:INDEX:TERM (A=Action, O=Object, T=Attribute)\n")
        f.write("DATA_FORMAT: HIERARCHY|PE_NUM|PROJ_NUM|INIT_TITLE|SRC_YEAR|AP_TYPE|AP_FY|TRIPLET\n")
        f.write("TRIPLET_FORMAT: ActionIndices;ObjectIndex;AttributeIndices;PurposeObjectIndex\n\n")

        f.write("[DICTIONARIES]\n")
        for i, term in enumerate(final_actions): f.write(f"A:{i}:{term}\n")
        for i, term in enumerate(final_objects): f.write(f"O:{i}:{term}\n")
        for i, term in enumerate(final_attributes): f.write(f"T:{i}:{term}\n")
        f.write("\n")

        f.write("[DATA]\n")

    print(f"✅ DSV Header and Dictionaries created successfully with {len(final_actions)} actions, {len(final_objects)} objects, {len(final_attributes)} attributes.")

if __name__ == "__main__":
    main()
