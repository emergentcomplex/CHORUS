-- Filename: infrastructure/postgres/init.sql
-- 🔱 CHORUS Database Schema (v10.1 - Correct Vector Dimensions)

-- Drop existing tables to ensure a clean slate
DROP TABLE IF EXISTS task_progress CASCADE;
DROP TABLE IF EXISTS query_state CASCADE;
DROP TABLE IF EXISTS analyst_reports CASCADE;
DROP TABLE IF EXISTS director_briefings CASCADE;
DROP TABLE IF EXISTS harvesting_tasks CASCADE;
DROP TABLE IF EXISTS dsv_embeddings CASCADE;
DROP TABLE IF EXISTS semantic_vectors CASCADE;
DROP TABLE IF EXISTS task_queue CASCADE;
DROP TYPE IF EXISTS task_status_enum;

-- Enumerated type for task status
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

-- Main task queue table
CREATE TABLE task_queue (
    query_hash VARCHAR(32) PRIMARY KEY,
    user_query JSONB NOT NULL,
    status task_status_enum NOT NULL DEFAULT 'PENDING',
    worker_id VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);
ALTER TABLE task_queue REPLICA IDENTITY FULL;

-- Table for analyst reports
CREATE TABLE analyst_reports (
    report_id SERIAL PRIMARY KEY,
    query_hash VARCHAR(32) REFERENCES task_queue(query_hash) ON DELETE CASCADE,
    persona_id VARCHAR(255) NOT NULL,
    report_text TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table for director briefings
CREATE TABLE director_briefings (
    briefing_id SERIAL PRIMARY KEY,
    query_hash VARCHAR(32) REFERENCES task_queue(query_hash) ON DELETE CASCADE,
    briefing_text TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table for user-facing progress updates
CREATE TABLE task_progress (
    progress_id SERIAL PRIMARY KEY,
    query_hash VARCHAR(32) REFERENCES task_queue(query_hash) ON DELETE CASCADE,
    status_message TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Table for storing final state and reports
CREATE TABLE query_state (
    query_hash VARCHAR(32) PRIMARY KEY REFERENCES task_queue(query_hash) ON DELETE CASCADE,
    state_json JSONB
);

-- Table for managing data harvesting tasks
CREATE TABLE harvesting_tasks (
    task_id SERIAL PRIMARY KEY,
    script_name VARCHAR(255) NOT NULL,
    associated_keywords JSONB,
    status VARCHAR(50) DEFAULT 'IDLE',
    is_dynamic BOOLEAN DEFAULT FALSE,
    worker_id VARCHAR(255),
    last_attempt TIMESTAMPTZ,
    last_successful_scrape TIMESTAMPTZ,
    parent_query_hash VARCHAR(32) REFERENCES task_queue(query_hash) ON DELETE SET NULL
);

-- The new canonical table for the unified semantic space
CREATE TABLE semantic_vectors (
    vector_id UUID PRIMARY KEY,
    source_vertical VARCHAR(50) NOT NULL,
    source_identifier TEXT NOT NULL,
    document_date TIMESTAMPTZ,
    content_chunk TEXT NOT NULL,
    -- THE DEFINITIVE FIX: Correct the vector dimensions to match the model's output.
    embedding vector(384),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add indexes for faster lookups
CREATE INDEX idx_semantic_vectors_source_vertical ON semantic_vectors(source_vertical);
CREATE INDEX idx_semantic_vectors_document_date ON semantic_vectors(document_date);


-- Add the task_queue table to the publication for CDC
ALTER PUBLICATION debezium_chorus_pub ADD TABLE task_queue;