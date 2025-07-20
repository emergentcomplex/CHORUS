# Filename: scripts/compress_5_serialize_and_zip.py
#
# "Finalize" Phase: The final storage optimization step.
# 1. Reads the token-efficient `_factored.dsv` file.
# 2. Serializes its contents into a compact binary format.
# 3. Compresses the final binary file using Gzip for maximum storage efficiency.
#
# Input: ../data/darpa/DARPA_Semantic_Vectors_factored.dsv
# Output: ../data/darpa/DARPA_Semantic_Vectors.bin.gz

import os
import json
import struct
import gzip
import shutil
from tqdm import tqdm

# --- CONFIGURATION ---
BASE_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'darpa')
FACTORED_DSV_PATH = os.path.join(BASE_DATA_DIR, "DARPA_Semantic_Vectors_factored.dsv")
ORIGINAL_DSV_PATH = os.path.join(BASE_DATA_DIR, "DARPA_Semantic_Vectors.dsv") # For final comparison
BINARY_PATH = os.path.join(BASE_DATA_DIR, "DARPA_Semantic_Vectors.bin") # Temporary file
FINAL_COMPRESSED_PATH = os.path.join(BASE_DATA_DIR, "DARPA_Semantic_Vectors.bin.gz")

# Binary format constants
MAGIC_NUMBER = b'DSV_FAC' # Magic number for the new factored format
VERSION = 2
# H = unsigned short (2 bytes)
# < = little-endian
# Format: HeaderID, ActionID, ObjectID, AttributeID, PurposeID
RECORD_STRUCT_FORMAT = '<HHHHH'

def main():
    """
    Main function to execute the serialization and compression.
    """
    print("--- Starting Compression Stage 5: Final Serialization & Gzip ---")
    if not os.path.exists(FACTORED_DSV_PATH):
        print(f"Error: Factored input file not found at {FACTORED_DSV_PATH}. Please run script 4 first.")
        return

    # --- 1. Read all sections from the factored DSV ---
    print("Reading all sections from factored DSV...")
    meta_info = {}
    term_dictionaries = {}
    data_dictionary = {}
    factored_data_lines = []

    current_section = None
    with open(FACTORED_DSV_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            
            if line.startswith('['):
                if line == "[META]": current_section = "meta"
                elif line == "[DICTIONARIES]": current_section = "term_dicts"
                elif line == "[DATA_DICTIONARY]": current_section = "data_dicts"
                elif line == "[FACTORED_DATA]": current_section = "data"
                continue

            try:
                if current_section == "meta":
                    key, val = line.split(':', 1)
                    meta_info[key.strip()] = val.strip()
                elif current_section == "term_dicts":
                    d_type, d_idx, d_term = line.split(':', 2)
                    if d_type not in term_dictionaries: term_dictionaries[d_type] = {}
                    term_dictionaries[d_type][int(d_idx)] = d_term
                elif current_section == "data_dicts":
                    h_id, h_val = line.split(':', 1)
                    data_dictionary[h_id.strip()] = h_val.strip()
                elif current_section == "data":
                    factored_data_lines.append(line)
            except (ValueError, IndexError):
                print(f"Warning: Skipping malformed line in section '{current_section}': {line}")
                continue

    # --- 2. Write to a temporary binary file ---
    print(f"Serializing {len(factored_data_lines)} records to binary file: {BINARY_PATH}")
    with open(BINARY_PATH, 'wb') as f_bin:
        # Write Header
        f_bin.write(MAGIC_NUMBER)
        f_bin.write(struct.pack('<B', VERSION))

        # Serialize and write all dictionaries as a single JSON block
        all_dicts_payload = {
            "META": meta_info,
            "TERM_DICTS": term_dictionaries,
            "DATA_DICTS": data_dictionary
        }
        dict_bytes = json.dumps(all_dicts_payload).encode('utf-8')
        f_bin.write(struct.pack('<I', len(dict_bytes))) # 4-byte length prefix
        f_bin.write(dict_bytes)

        # Write data records
        f_bin.write(struct.pack('<I', len(factored_data_lines))) # Number of records
        for line in tqdm(factored_data_lines, desc="Packing Records"):
            try:
                header_id_str, triplet_str = line.split('|', 1)
                header_id = int(header_id_str[1:]) # Convert "H123" to 123
                
                indices = triplet_str.split(';')
                # For simplicity, we take the first index if multiple are comma-separated.
                # A more complex format would be needed for full multi-index support.
                action_idx = int(indices[0].split(',')[0]) if indices[0] else 65535
                object_idx = int(indices[1]) if indices[1] else 65535
                attr_idx = int(indices[2].split(',')[0]) if indices[2] else 65535
                purp_idx = int(indices[3]) if indices[3] else 0

                packed_data = struct.pack(
                    RECORD_STRUCT_FORMAT,
                    header_id, action_idx, object_idx, attr_idx, purp_idx
                )
                f_bin.write(packed_data)
            except (ValueError, IndexError) as e:
                print(f"\nWarning: Skipping malformed data line: {line} | Error: {e}")
                continue

    # --- 3. Gzip the binary file ---
    print(f"Applying Gzip compression to create final artifact: {FINAL_COMPRESSED_PATH}")
    with open(BINARY_PATH, 'rb') as f_in, gzip.open(FINAL_COMPRESSED_PATH, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
    
    # --- 4. Final Verification ---
    original_size = os.path.getsize(ORIGINAL_DSV_PATH)
    final_size = os.path.getsize(FINAL_COMPRESSED_PATH)
    reduction_ratio = original_size / final_size if final_size > 0 else float('inf')

    print("\n--- FINAL STORAGE VERIFICATION ---")
    print(f"Original DSV Size:      {original_size / 1024:.2f} KB")
    print(f"Final Compressed Size:  {final_size / 1024:.2f} KB")
    print(f"Total Reduction Ratio:  {reduction_ratio:.2f}x")

    if reduction_ratio > 3:
        print("\n✅ SUCCESS: Achieved target of > 3-fold total size reduction.")
    else:
        print("\n⚠️ WARNING: Did not achieve target 3-fold size reduction.")
        
    # Clean up intermediate binary file
    os.remove(BINARY_PATH)

if __name__ == "__main__":
    main()
