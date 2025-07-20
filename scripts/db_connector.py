# Filename: scripts/db_connector.py (v2.0 - Robust Pathing)
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# v2.0: Implements a robust method for finding the project root and loading
#       the .env file, ensuring all scripts connect to the same database
#       regardless of where they are executed from.

import mariadb
import os
from dotenv import load_dotenv
from pathlib import Path

# --- DEFINITIVE FIX: Robust .env file loading ---
# This searches upwards from the current file's location until it finds a directory
# containing a '.env' file, which is our project root.
def find_project_root():
    current_path = Path(__file__).resolve()
    while current_path != current_path.parent:
        if (current_path / ".env").exists():
            return current_path
        current_path = current_path.parent
    return None

PROJECT_ROOT = find_project_root()
if PROJECT_ROOT:
    load_dotenv(dotenv_path=PROJECT_ROOT / ".env")
else:
    print("FATAL: Could not find the project root with the .env file.")
    # Fallback for safety, though it might be incorrect
    load_dotenv()


class SingletonDBPool:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print("Database connection pool is being created for the first time...")
            cls._instance = super(SingletonDBPool, cls).__new__(cls)
            try:
                cls._instance.pool = mariadb.ConnectionPool(
                    user=os.getenv("DB_USER"),
                    password=os.getenv("DB_PASSWORD"),
                    host=os.getenv("DB_HOST"),
                    port=int(os.getenv("DB_PORT", 3306)),
                    database=os.getenv("DB_NAME"),
                    pool_name="chorus_pool",
                    pool_size=10
                )
                print("Database connection pool successfully created.")
            except (mariadb.Error, TypeError) as e:
                print(f"FATAL: Error creating database connection pool: {e}")
                print("       Please ensure DB_* variables are set correctly in your .env file.")
                cls._instance.pool = None
        return cls._instance

    def get_connection(self):
        if self.pool is None:
            print("[!] ERROR: Connection pool is not available.")
            return None
        try:
            return self.pool.get_connection()
        except mariadb.PoolError as e:
            print(f"[!] ERROR: Failed to get connection from pool: {e}")
            return None

def get_db_connection():
    pool_manager = SingletonDBPool()
    return pool_manager.get_connection()