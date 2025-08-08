# Filename: infrastructure/postgres/init-db.sh
#!/bin/bash
# This is the single, atomic, and canonical initialization script.
# It is executed by the official postgres container's entrypoint.

set -e

# Run all commands as the application user against the application database.
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL

    -- 1. Create the required extension. This MUST happen first.
    CREATE EXTENSION IF NOT EXISTS vector;

    -- 2. Grant replication privileges for Debezium.
    -- This command must be run by a superuser, which the entrypoint script is.
    -- We will run it against the user specified by the environment variables.
    ALTER USER $POSTGRES_USER WITH REPLICATION;

    -- 3. Create the publication for Debezium.
    CREATE PUBLICATION debezium_chorus_pub;

    -- 4. Define the custom ENUM type for task status.
    DO \$$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'task_status_enum') THEN
            CREATE TYPE task_status_enum AS ENUM (
                'PENDING',
                'PENDING_ANALYSIS',
                'ANALYSIS_IN_PROGRESS',
                'PENDING_SYNTHESIS',
                'SYNTHESIS_IN_PROGRESS',
                'PENDING_JUDGMENT',
                'JUDGMENT_IN_PROGRESS',
                'COMPLETED',
                'FAILED'
            );
        END IF;
    END
    \$$;

    -- 5. Create all tables, now that the vector type exists.

    CREATE TABLE IF NOT EXISTS task_queue (
        query_hash VARCHAR(32) PRIMARY KEY,
        user_query JSONB NOT NULL,
        status task_status_enum NOT NULL DEFAULT 'PENDING',
        worker_id VARCHAR(255),
        created_at TIMESTAMPTZ DEFAULT NOW(),
        started_at TIMESTAMPTZ,
        completed_at TIMESTAMPTZ
    );

    -- Add the specific table to the publication.
    ALTER PUBLICATION debezium_chorus_pub ADD TABLE task_queue;

    CREATE TABLE IF NOT EXISTS task_progress (
        progress_id SERIAL PRIMARY KEY,
        query_hash VARCHAR(32) NOT NULL REFERENCES task_queue(query_hash) ON DELETE CASCADE,
        status_message TEXT NOT NULL,
        timestamp TIMESTAMPTZ DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS query_state (
        query_hash VARCHAR(32) PRIMARY KEY REFERENCES task_queue(query_hash) ON DELETE CASCADE,
        state_json JSONB,
        last_updated TIMESTAMPTZ DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS analyst_reports (
        report_id SERIAL PRIMARY KEY,
        query_hash VARCHAR(32) NOT NULL REFERENCES task_queue(query_hash) ON DELETE CASCADE,
        persona_id VARCHAR(255) NOT NULL,
        report_text TEXT,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS director_briefings (
        briefing_id SERIAL PRIMARY KEY,
        query_hash VARCHAR(32) NOT NULL REFERENCES task_queue(query_hash) ON DELETE CASCADE,
        briefing_text TEXT,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS dsv_embeddings (
        dsv_line_id VARCHAR(255) PRIMARY KEY,
        content TEXT,
        embedding vector(768)
    );

    CREATE TABLE IF NOT EXISTS harvesting_tasks (
        task_id SERIAL PRIMARY KEY,
        script_name VARCHAR(255) NOT NULL,
        associated_keywords JSONB,
        status VARCHAR(50) DEFAULT 'IDLE',
        is_dynamic BOOLEAN DEFAULT FALSE,
        parent_query_hash VARCHAR(32),
        last_attempt TIMESTAMPTZ,
        last_successful_scrape TIMESTAMPTZ,
        worker_id VARCHAR(255)
    );

EOSQL