# Filename: scripts/populate_harvest_tasks.py
# A one-time script to populate the intelligent harvesting_tasks table.

from db_connector import get_db_connection
import json

# The complete blueprint for our seven-source data lake
HARVESTING_BLUEPRINT = {
    "scrape_reference_library_advanced.py": {
        "is_dynamic": False, "interval": 9999, "keywords": None
    },
    "scrape_geopolitical.py": {
        "is_dynamic": True, "interval": 72, "keywords": None
    },
    "scrape_academic.py": {
        "is_dynamic": True, "interval": 72, "keywords": None
    },
    "scrape_contracts.py": {
        "is_dynamic": True, "interval": 24, "keywords": ["defense", "research"]
    },
    "scrape_jobs.py": {
        "is_dynamic": True, "interval": 24, "keywords": ["TS/SCI", "cleared"]
    },
    "scrape_news.py": {
        "is_dynamic": True, "interval": 12, "keywords": ["DARPA", "military tech"]
    },
    "scrape_gdelt.py": {
        "is_dynamic": True, "interval": 12, "keywords": ["DARPA", "geopolitics"]
    }
}

def main():
    """Populates the harvesting_tasks table with the blueprint."""
    print("[*] Populating the intelligent harvesting task queue with all 7 sources...")
    conn = get_db_connection()
    if not conn:
        print("[!] Could not connect to the database. Aborting.")
        return
        
    cursor = conn.cursor()
    
    for script, config in HARVESTING_BLUEPRINT.items():
        sql = """
            INSERT INTO harvesting_tasks (script_name, is_dynamic, scrape_interval_hours, associated_keywords) 
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                is_dynamic=VALUES(is_dynamic), 
                scrape_interval_hours=VALUES(scrape_interval_hours), 
                associated_keywords=VALUES(associated_keywords);
        """
        keywords_json = json.dumps(config['keywords']) if config['keywords'] else None
        cursor.execute(sql, (script, config['is_dynamic'], config['interval'], keywords_json))
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"[+] Successfully populated {len(HARVESTING_BLUEPRINT)} tasks into the database.")

if __name__ == "__main__":
    main()
