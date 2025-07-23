# Filename: scripts/ingest_4_populate_vectordb.py (FINAL, CORRECTED)
import os
import json
from db_connector import get_db_connection
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import argparse

def main(source_name):
    source_name_lower = source_name.lower()
    DSV_PATH = f"../data/{source_name_lower}/{source_name}_Semantic_Vectors.dsv"
    
    print(f"\n--- Starting Ingestion Stage 4 for '{source_name}': Populating MariaDB Vector Table ---")
    
    conn = get_db_connection()
    if not conn:
        print("[!] FATAL: Could not connect to the database. Aborting.")
        return
    cursor = conn.cursor()

    print(f"  -> Clearing existing embeddings for source '{source_name}' to prevent duplicates...")
    sql_delete = "DELETE FROM dsv_embeddings WHERE dsv_line_id LIKE %s"
    cursor.execute(sql_delete, (f"{source_name}_%",))
    conn.commit()
    print(f"  -> Removed {cursor.rowcount} old records.")
    
    if not os.path.exists(DSV_PATH):
        print(f"[!] FATAL: DSV file not found at {DSV_PATH}. Run ingest steps 1-3 first.")
        return

    print(f"  -> Loading data lines from {os.path.basename(DSV_PATH)}...")
    with open(DSV_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    data_lines = [line.strip() for line in lines if line.startswith('>>>')]
    ids = [f"{source_name}_{i}" for i in range(len(data_lines))]

    if not data_lines:
        print(f"[!] No data lines found in {source_name} DSV file to process.")
        return

    print(f"  -> Found {len(data_lines)} data lines to embed and insert for '{source_name}'.")
    print("  -> Initializing embedding model 'all-mpnet-base-v2'...")
    model = SentenceTransformer('all-mpnet-base-v2')
    
    print("  -> Encoding data...")
    embeddings = model.encode(data_lines, show_progress_bar=True)

    print("  -> Inserting records into MariaDB...")
    # THE DEFINITIVE FIX: Remove 'IGNORE' to see errors.
    sql = "INSERT INTO dsv_embeddings (dsv_line_id, content, embedding) VALUES (%s, %s, VEC_FromText(%s))"
    
    batch_size = 1000
    for i in tqdm(range(0, len(data_lines), batch_size), desc=f"Inserting {source_name} into DB"):
        batch_records = []
        for j in range(i, min(i + batch_size, len(data_lines))):
            # Use json.dumps for clean, compliant formatting.
            embedding_str = json.dumps(embeddings[j].tolist())
            batch_records.append((ids[j], data_lines[j], embedding_str))
        
        try:
            cursor.executemany(sql, batch_records)
            conn.commit()
        except Exception as e:
            print(f"\n[!!!] DATABASE INSERT FAILED. This is the root cause.")
            print(f"      Error: {e}")
            print(f"      Problematic SQL: {cursor.statement}")
            conn.rollback()
            cursor.close()
            conn.close()
            return # Stop immediately on failure

    cursor.close()
    conn.close()
    print(f"\n✅ MariaDB vector table populated successfully with '{source_name}' data.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingestion Stage 4: Populate MariaDB with vector embeddings.")
    parser.add_argument('--source', required=True, help="The name of the source directory in ../data/ (e.g., 'Army', 'DARPA')")
    args = parser.parse_args()
    main(args.source)