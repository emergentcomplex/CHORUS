# Filename: infrastructure/postgres/init-db.sh
# This is the single, atomic, and canonical initialization script.
# It is executed by the official postgres container's entrypoint.
# It sets up database-level configurations and then executes the main schema file.

set -e

# Run all commands as the application user against the application database.
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL

    -- 1. Create the required extension. This MUST happen first.
    CREATE EXTENSION IF NOT EXISTS vector;

    -- 2. Grant replication privileges for Debezium.
    -- This command must be run by a superuser, which the entrypoint script is.
    -- We will run it against the user specified by the environment variables.
    ALTER USER $POSTGRES_USER WITH REPLICATION;

    -- 3. Create the publication for Debezium, if it doesn't exist.
    DO \$$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_publication WHERE pubname = 'debezium_chorus_pub') THEN
            CREATE PUBLICATION debezium_chorus_pub;
        END IF;
    END
    \$$;

EOSQL

# 4. Execute the canonical schema definition script.
# This script is responsible for creating/resetting all tables.
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" < /docker-entrypoint-initdb.d/init.sql