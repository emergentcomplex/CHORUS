-- Filename: infrastructure/postgres/init.sql (Definitive & Idempotent Reset)
-- This script is the canonical definition of the CHORUS database schema.
-- It is designed to be a true RESET script, dropping all objects before recreating them.

-- --- TEARDOWN PHASE ---
-- Drop objects in reverse order of dependency.
-- Use IF EXISTS to ensure the script runs without error on a clean database.

DROP PUBLICATION IF EXISTS debezium_chorus_pub;
DROP TABLE IF EXISTS task_progress;
DROP TABLE IF EXISTS query_state;
DROP TABLE IF EXISTS harvesting_tasks;
DROP TABLE IF EXISTS dsv_embeddings;
DROP TABLE IF EXISTS task_queue;

-- --- SETUP PHASE ---

-- Enable the pgvector extension for similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the table for the main analysis task queue
CREATE TABLE task_queue (
    query_hash CHAR(32) PRIMARY KEY,
    user_query JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    worker_id VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

-- Create the table for storing detailed, user-facing progress updates
CREATE TABLE task_progress (
    progress_id SERIAL PRIMARY KEY,
    query_hash CHAR(32) NOT NULL REFERENCES task_queue(query_hash) ON DELETE CASCADE,
    status_message TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create the table for storing the final JSON state of a query
CREATE TABLE query_state (
    query_hash CHAR(32) PRIMARY KEY REFERENCES task_queue(query_hash) ON DELETE CASCADE,
    state_json JSONB NOT NULL
);

-- Create the table for managing recurring and dynamic data harvesting tasks
CREATE TABLE harvesting_tasks (
    task_id SERIAL PRIMARY KEY,
    script_name VARCHAR(100) NOT NULL,
    associated_keywords JSONB,
    status VARCHAR(20) NOT NULL DEFAULT 'IDLE',
    worker_id VARCHAR(50),
    is_dynamic BOOLEAN DEFAULT FALSE,
    last_attempt TIMESTAMPTZ,
    last_successful_scrape TIMESTAMPTZ
);

-- Create the table for storing document embeddings for RAG
CREATE TABLE dsv_embeddings (
    dsv_line_id VARCHAR(255) PRIMARY KEY,
    content TEXT NOT NULL,
    embedding VECTOR(768) -- Matches all-mpnet-base-v2 dimension
);

-- Create an index for efficient vector similarity search
CREATE INDEX idx_embedding ON dsv_embeddings USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);

-- Create the Debezium publication for the task_queue table
CREATE PUBLICATION debezium_chorus_pub FOR TABLE task_queue;

-- Final confirmation message
\echo 'NOTICE: CHORUS database reset and initialization complete.'
