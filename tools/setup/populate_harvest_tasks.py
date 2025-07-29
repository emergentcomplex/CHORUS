# Filename: tools/setup/populate_harvest_tasks.py (Definitive)
# A script to populate the harvesting_tasks table with tasks that
# our current set of harvesters can actually handle.

from chorus_engine.adapters.persistence.mariadb_adapter import MariaDBAdapter
import json

# The blueprint for our *implemented* harvesters.
HARVESTING_BLUEPRINT = {
    "usajobs_live_search": {
        "keywords": {"Keyword": "TS/SCI"}
    },
    "usaspending_search": {
        "keywords": {"Keyword": "defense research"}
    },
    "newsapi_search": {
        "keywords": {"Keyword": "DARPA"}
    },
    "arxiv_search": {
        "keywords": {"Keyword": "quantum computing"}
    }
}

def main():
    """Populates the harvesting_tasks table with the blueprint."""
    print("[*] Populating the harvesting task queue with implemented harvesters...")
    db_adapter = MariaDBAdapter()
    conn = db_adapter._get_connection()
    if not conn:
        print("[!] Could not connect to the database. Aborting.")
        return
        
    cursor = conn.cursor()
    
    # Clean up old tasks for a clean slate.
    cursor.execute("DELETE FROM harvesting_tasks")
    
    for script, config in HARVESTING_BLUEPRINT.items():
        # is_dynamic and interval are no longer relevant for this setup script.
        # All tasks are inserted as IDLE, ready to be run by the sentinel.
        sql = """
            INSERT INTO harvesting_tasks (script_name, associated_keywords, status) 
            VALUES (%s, %s, 'IDLE')
        """
        keywords_json = json.dumps(config['keywords']) if config['keywords'] else None
        cursor.execute(sql, (script, keywords_json))
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"[+] Successfully populated {len(HARVESTING_BLUEPRINT)} tasks into the database.")

if __name__ == "__main__":
    from chorus_engine.config import setup_path
    setup_path()
    main()
