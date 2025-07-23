-- Filename: scripts/schema.sql (v1.1)
-- The complete MariaDB schema, with a corrected drop order and a fix for the harvesting_tasks table.

-- Temporarily disable foreign key checks to ensure a clean drop
SET FOREIGN_KEY_CHECKS=0;

-- Drop tables in the correct order (child tables first, then parents)
DROP TABLE IF EXISTS task_progress;
DROP TABLE IF EXISTS prompt_log;
DROP TABLE IF EXISTS query_state;
DROP TABLE IF EXISTS dsv_embeddings;
DROP TABLE IF EXISTS task_queue;
DROP TABLE IF EXISTS personas;
DROP TABLE IF EXISTS api_keys;
DROP TABLE IF EXISTS harvesting_tasks;

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS=1;

-- Create the service-aware table for API key management
CREATE TABLE api_keys (
    id INT AUTO_INCREMENT PRIMARY KEY,
    service VARCHAR(50) NOT NULL,
    api_key VARCHAR(255) NOT NULL UNIQUE,
    key_type ENUM('FREE', 'PAID') NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_used TIMESTAMP NULL,
    daily_request_count INT DEFAULT 0,
    last_reset_date DATE
);

-- Create the table for AI personas
CREATE TABLE personas (
    persona_id INT AUTO_INCREMENT PRIMARY KEY,
    persona_name VARCHAR(100) NOT NULL UNIQUE,
    persona_tier INT NOT NULL,
    persona_description TEXT NOT NULL,
    subordinate_personas JSON
);

-- Create the main analysis task queue
CREATE TABLE task_queue (
    task_id INT AUTO_INCREMENT PRIMARY KEY,
    user_query TEXT NOT NULL,
    query_hash VARCHAR(32) NOT NULL UNIQUE,
    status ENUM('PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'PAUSED') DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    worker_id VARCHAR(100) NULL,
    parent_query_hash VARCHAR(32) NULL,
    CONSTRAINT fk_parent_query FOREIGN KEY (parent_query_hash) REFERENCES task_queue(query_hash) ON DELETE SET NULL
);

-- Create the table to store the state of each analysis
CREATE TABLE query_state (
    query_hash VARCHAR(32) PRIMARY KEY,
    state_json JSON,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (query_hash) REFERENCES task_queue(query_hash) ON DELETE CASCADE
);

-- Create the table for logging all prompts and responses
CREATE TABLE prompt_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    query_hash VARCHAR(32) NOT NULL,
    tier VARCHAR(20) NOT NULL,
    step_description TEXT,
    prompt LONGTEXT,
    response LONGTEXT,
    duration_ms BIGINT,
    api_key_id INT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (query_hash) REFERENCES task_queue(query_hash) ON DELETE CASCADE,
    FOREIGN KEY (api_key_id) REFERENCES api_keys(id) ON DELETE SET NULL
);

-- Create the table for user-facing progress updates
CREATE TABLE task_progress (
    progress_id INT AUTO_INCREMENT PRIMARY KEY,
    query_hash VARCHAR(32) NOT NULL,
    status_message VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (query_hash) REFERENCES task_queue(query_hash) ON DELETE CASCADE
);

-- Create the intelligent harvesting task table
CREATE TABLE harvesting_tasks (
    task_id INT AUTO_INCREMENT PRIMARY KEY,
    script_name VARCHAR(255) NOT NULL, -- CORRECTED: Removed UNIQUE constraint
    status ENUM('IDLE', 'IN_PROGRESS', 'COMPLETED', 'FAILED') DEFAULT 'IDLE',
    is_dynamic BOOLEAN DEFAULT TRUE,
    scrape_interval_hours INT DEFAULT 24,
    last_successful_scrape TIMESTAMP NULL,
    last_attempt TIMESTAMP NULL,
    worker_id VARCHAR(100) NULL,
    retries INT DEFAULT 0,
    associated_keywords JSON NULL
);

-- Create the vector table
CREATE TABLE dsv_embeddings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dsv_line_id VARCHAR(255) NOT NULL UNIQUE,
    content TEXT NOT NULL,
    embedding VECTOR(768) NOT NULL,
    VECTOR INDEX (embedding) DISTANCE=cosine
);