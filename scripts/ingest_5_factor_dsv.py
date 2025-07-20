# Filename: scripts/compress_4_factor_dsv.py
#
# "Factor" Phase: This is the primary TOKEN REDUCTION step.
# Reads the final DSV file, creates a dictionary of unique data headers,
# and rewrites the data section using compact header IDs.
# This version is for production and expects the input file to exist.
#
# Input: ../data/darpa/DARPA_Semantic_Vectors.dsv
# Output: ../data/darpa/DARPA_Semantic_Vectors_factored.dsv

import os
from collections import defaultdict
from tqdm import tqdm

# --- CONFIGURATION ---
BASE_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'darpa')
ORIGINAL_DSV_PATH = os.path.join(BASE_DATA_DIR, "DARPA_Semantic_Vectors.dsv")
FACTORED_DSV_PATH = os.path.join(BASE_DATA_DIR, "DARPA_Semantic_Vectors_factored.dsv")

def main():
    """
    Main function to execute the factoring process.
    """
    print("--- Starting Compression Stage 4: Factoring Data Headers for Token Reduction ---")

    if not os.path.exists(ORIGINAL_DSV_PATH):
        print(f"Error: Input file not found at {ORIGINAL_DSV_PATH}. Please run the ingest pipeline first.")
        return

    # --- Pass 1: Scan and Map Headers ---
    print("Scanning data section to identify unique headers...")
    header_to_triplets = defaultdict(list)
    header_map = {}
    header_counter = 0
    
    meta_and_dicts_lines = []
    in_data_section = False

    with open(ORIGINAL_DSV_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip() == "[DATA]":
                in_data_section = True
                meta_and_dicts_lines.append(line)
                continue
            
            if not in_data_section:
                meta_and_dicts_lines.append(line)
                continue

            # Now we are in the data section
            if line.startswith(">>>"):
                try:
                    # Split only on the last pipe to get the triplet
                    header, triplet = line.strip().rsplit('|', 1)
                    
                    if header not in header_map:
                        header_map[header] = f"H{header_counter}"
                        header_counter += 1
                    
                    header_to_triplets[header].append(triplet)
                except ValueError:
                    print(f"Warning: Skipping malformed data line: {line.strip()}")
                    continue
    
    print(f"Found {len(header_map)} unique data headers.")

    # --- Pass 2: Rewrite the DSV with Factored Data ---
    print(f"Rewriting to new factored file: {FACTORED_DSV_PATH}")
    with open(FACTORED_DSV_PATH, 'w', encoding='utf-8') as f_out:
        # Write original META and DICTIONARIES sections
        f_out.writelines(meta_and_dicts_lines)
        
        # Write the new DATA_DICTIONARY section
        f_out.write("\n[DATA_DICTIONARY]\n")
        # Sort by header ID (H0, H1, H2...) for consistent, readable output
        sorted_headers = sorted(header_map.items(), key=lambda item: int(item[1][1:]))
        for header, header_id in sorted_headers:
            f_out.write(f"{header_id}:{header}\n")
            
        # Write the new, highly compressed FACTORED_DATA section
        f_out.write("\n[FACTORED_DATA]\n")
        for header, header_id in tqdm(sorted_headers, desc="Writing Factored Data"):
            triplets = header_to_triplets[header]
            for triplet in triplets:
                f_out.write(f"{header_id}|{triplet}\n")

    # --- Final Report ---
    original_size = os.path.getsize(ORIGINAL_DSV_PATH)
    factored_size = os.path.getsize(FACTORED_DSV_PATH)
    reduction_percent = ((original_size - factored_size) / original_size) * 100

    print("\n--- TOKEN REDUCTION ANALYSIS ---")
    print(f"Original DSV Size:      {original_size / 1024:.2f} KB")
    print(f"Factored DSV Size:      {factored_size / 1024:.2f} KB")
    print(f"Token-Relevant Size Reduction: {reduction_percent:.2f}%")
    print("\n✅ Factoring complete. The new file is ready for LLM context or final binary compression.")

if __name__ == "__main__":
    main()
