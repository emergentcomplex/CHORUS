# Filename: infrastructure/postgres/init-db.sh
#!/bin/bash
set -e

# This script is executed by the official postgres container's entrypoint
# only when the database is first created.

# Perform all actions as the 'postgres' superuser.
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Enable the vector extension, which is a prerequisite for the schema.
    CREATE EXTENSION IF NOT EXISTS vector;

    -- Grant the REPLICATION privilege to the application user.
    -- This is essential for the Debezium CDC connector to work.
    ALTER USER $POSTGRES_USER WITH REPLICATION;
EOSQL

# After the superuser tasks are done, run the main schema creation script
# as the application user. This ensures correct ownership of tables.
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" < /docker-entrypoint-initdb.d/init.sql