# Filename: tools/setup/populate_harvest_tasks.py (PostgreSQL Pivot)
# A script to populate the harvesting_tasks table with tasks that
# our current set of harvesters can actually handle.

from chorus_engine.adapters.persistence.postgres_adapter import PostgresAdapter
import json

# The blueprint for our *implemented* harvesters.
HARVESTING_BLUEPRINT = {
    "usajobs_live_search": {
        "keywords": {"Keyword": "TS/SCI"}
    },
    "usaspending_search": {
        "keywords": {"Keyword": "defense research"}
    },
    "arxiv_search": {
        "keywords": {"Keyword": "quantum computing"}
    },
    "govinfo_search": {
        "keywords": {"Keyword": "appropriations defense"}
    }
}

def main():
    """Populates the harvesting_tasks table with the blueprint."""
    print("[*] Populating the harvesting task queue with implemented harvesters...")
    db_adapter = PostgresAdapter()
    conn = db_adapter._get_connection()
    if not conn:
        print("[!] Could not connect to the database. Aborting.")
        return
        
    try:
        with conn.cursor() as cursor:
            # Clean up old non-dynamic tasks for a clean slate.
            cursor.execute("DELETE FROM harvesting_tasks WHERE is_dynamic = FALSE")
            
            for script, config in HARVESTING_BLUEPRINT.items():
                sql = """
                    INSERT INTO harvesting_tasks (script_name, associated_keywords, status, is_dynamic) 
                    VALUES (%s, %s, 'IDLE', FALSE)
                """
                keywords_json = json.dumps(config['keywords']) if config['keywords'] else None
                cursor.execute(sql, (script, keywords_json))
            
            conn.commit()
            print(f"[+] Successfully populated {len(HARVESTING_BLUEPRINT)} tasks into the database.")
    finally:
        db_adapter._release_connection(conn)


if __name__ == "__main__":
    from chorus_engine.config import setup_path
    setup_path()
    main()
