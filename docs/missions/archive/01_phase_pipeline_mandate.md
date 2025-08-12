# Praxis: The Mandate of the Pipeline

### Objective
To achieve a single, verifiable, and robust Change Data Capture (CDC) data pipeline from PostgreSQL to Redpanda using the canonical Debezium `kafka-connect` service.

### Justification
All previous attempts to build the full system have failed at this exact point. The CDC pipeline is the central nervous system of the entire CHORUS engine. Without a stable, verifiable dataflow, no other component can be trusted or tested. This mission reduces the problem to its absolute minimum, focusing all effort on solving this single, critical dependency. Success on this mission is the prerequisite for any future development.

### The Plan

*   **Subphase 1.1 (The Clean Slate):**
    *   **Task:** Create a minimal `docker-compose.yml` that starts **only** `postgres`, `redpanda`, and `kafka-connect`. No other application services.
    *   **Verification:** Prove that `docker compose up --wait` brings all three services to a healthy state.

*   **Subphase 1.2 (The Canonical Entrypoint):**
    *   **Task:** Create a custom entrypoint wrapper script (`custom-entrypoint.sh`) for the `kafka-connect` service. This script will be responsible for preparing the connector's JSON configuration from a template and then using `exec "$@"` to hand off control to the original Debezium entrypoint.
    *   **Verification:** The `kafka-connect` service must start and remain healthy. The healthcheck will be a `curl` to the `/connectors` endpoint.

*   **Subphase 1.3 (The Final Verification):**
    *   **Task:** Create a minimal `docker-compose.test.yml` and a `tests/conftest.py` that sets up an ephemeral test database. Create a single, isolated test file, `tests/test_cdc_pipeline.py`, that contains only the CDC dataflow test.
    *   **Verification:** Run a new `make test-pipeline` command that starts the minimal stack and runs only this single test file. The test must pass, proving that an `INSERT` into the test database results in a corresponding event appearing in the Redpanda topic.

### Definition of Done
1.  We have a minimal, three-service stack that starts reliably.
2.  The Debezium connector is configured and started using a robust, canonical custom entrypoint.
3.  A single, isolated `pytest` test can prove, end-to-end, that a database change creates a Kafka event.
4.  The system is now ready to be built upon this stable, verified data pipeline.
