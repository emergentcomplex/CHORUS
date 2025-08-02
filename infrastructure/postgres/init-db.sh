# Filename: infrastructure/postgres/init-db.sh
#!/bin/bash
set -e

# This script is executed by the official postgres container's entrypoint
# only when the database is first created. It runs as the 'postgres' superuser.

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Enable the vector extension, a prerequisite for the schema.
    CREATE EXTENSION IF NOT EXISTS vector;

    -- Grant the REPLICATION privilege to the application user for CDC.
    ALTER USER $POSTGRES_USER WITH REPLICATION;

    -- THE DEFINITIVE FIX: Create the publication as the superuser.
    -- This publication is for the task_queue table, which will be created later
    -- by the init.sql script. We create an empty publication first.
    CREATE PUBLICATION debezium_chorus_pub;
EOSQL

# Now, run the main schema creation script as the application user.
# This script will create the tables and add the task_queue table to the
# already-existing publication.
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" < /docker-entrypoint-initdb.d/init.sql