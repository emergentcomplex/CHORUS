-- Filename: infrastructure/postgres/init.sql
-- 🔱 CHORUS Database Schema (v2.4 - Correct Publication Handling)

-- The 'vector' extension is now created by the init-db.sh script.

-- Drop existing objects in reverse dependency order to ensure a clean slate.
DROP TABLE IF EXISTS director_briefings;
DROP TABLE IF EXISTS analyst_reports;
DROP TABLE IF EXISTS task_progress;
DROP TABLE IF EXISTS query_state;
DROP TABLE IF EXISTS harvesting_tasks;
DROP TABLE IF EXISTS dsv_embeddings;
DROP TABLE IF EXISTS task_queue;
DROP TYPE IF EXISTS task_status_enum;
DROP TYPE IF EXISTS harvester_status_enum;

-- === ENUMERATED TYPES ===
CREATE TYPE task_status_enum AS ENUM (
    'PENDING', 'PENDING_ANALYSIS', 'ANALYSIS_IN_PROGRESS', 'PENDING_SYNTHESIS',
    'SYNTHESIS_IN_PROGRESS', 'PENDING_JUDGMENT', 'JUDGMENT_IN_PROGRESS', 'COMPLETED', 'FAILED'
);
CREATE TYPE harvester_status_enum AS ENUM ('IDLE', 'IN_PROGRESS', 'COMPLETED', 'FAILED');

-- === CORE TABLES ===
CREATE TABLE task_queue (
    query_hash CHAR(32) PRIMARY KEY,
    user_query JSONB NOT NULL,
    status task_status_enum NOT NULL DEFAULT 'PENDING',
    worker_id VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);
CREATE INDEX idx_task_queue_status ON task_queue(status);

CREATE TABLE query_state (
    query_hash CHAR(32) PRIMARY KEY REFERENCES task_queue(query_hash) ON DELETE CASCADE,
    state_json JSONB
);

CREATE TABLE task_progress (
    progress_id SERIAL PRIMARY KEY,
    query_hash CHAR(32) NOT NULL REFERENCES task_queue(query_hash) ON DELETE CASCADE,
    status_message TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_task_progress_query_hash ON task_progress(query_hash);

-- === ADVERSARIAL COUNCIL TABLES ===
CREATE TABLE analyst_reports (
    report_id SERIAL PRIMARY KEY,
    query_hash CHAR(32) NOT NULL REFERENCES task_queue(query_hash) ON DELETE CASCADE,
    persona_id VARCHAR(255) NOT NULL,
    report_text TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_analyst_reports_query_hash ON analyst_reports(query_hash);

CREATE TABLE director_briefings (
    briefing_id SERIAL PRIMARY KEY,
    query_hash CHAR(32) NOT NULL REFERENCES task_queue(query_hash) ON DELETE CASCADE,
    briefing_text TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_director_briefings_query_hash ON director_briefings(query_hash);

-- === HARVESTING & VECTOR DB TABLES ===
CREATE TABLE harvesting_tasks (
    task_id SERIAL PRIMARY KEY,
    script_name VARCHAR(255) NOT NULL,
    associated_keywords JSONB,
    is_dynamic BOOLEAN NOT NULL DEFAULT FALSE,
    status harvester_status_enum NOT NULL DEFAULT 'IDLE',
    worker_id VARCHAR(255),
    last_attempt TIMESTAMPTZ,
    last_successful_scrape TIMESTAMPTZ
);
CREATE INDEX idx_harvesting_tasks_status ON harvesting_tasks(status);

CREATE TABLE dsv_embeddings (
    dsv_line_id VARCHAR(255) PRIMARY KEY,
    content TEXT NOT NULL,
    embedding VECTOR(768)
);

-- THE DEFINITIVE FIX: Add the newly created table to the publication
-- that was already created by the superuser in init-db.sh.
ALTER PUBLICATION debezium_chorus_pub ADD TABLE task_queue;