# Filename: docs/ideas/00_mandate_of_final_separation.md

# 🔱 Praxis: The Mandate of Final Separation

## I. Objective

To implement a fully isolated, three-environment architecture for CHORUS by creating three dedicated, self-contained Docker Compose files (`prod`, `dev`, `test`) and a master `Makefile` to orchestrate them. This will definitively resolve all known data, network, and configuration conflicts, resulting in a lean production environment, a full-featured development environment, and a hermetic CI/CD test environment that can all be run concurrently.

## II. Justification

This mission is the direct result of the lessons learned from the failure of **Hypothesis #9: The Override Model is a Viable Pattern for Distinct Environments**. The previous override-based model (`-f file1.yml -f file2.yml`) proved to be brittle, ambiguous, and the root cause of a persistent cycle of failures. By moving to a fully explicit, one-file-per-environment model, we adhere to the new **Axiom 76 (Environmental Independence)** and create a system that is robust, predictable, and maintainable. This is the final step required to stabilize the CHORUS platform.

## III. The Plan

This mission will be executed in a series of atomic, verifiable steps.

- **Subphase 1.1 (The Production Blueprint):**

  - **Task:** Create the `docker-compose.prod.yml` file.
  - **Implementation:** This file will define all services required for a production run. It will be configured by `.env.prod`, map all necessary ports for user access (e.g., 5001), and mount a persistent, named volume for the PostgreSQL database (`postgres_data_prod`). It will **not** include any volume mounts for source code. It will also define the `setup-connector` service.

- **Subphase 1.2 (The Development Blueprint):**

  - **Task:** Create the `docker-compose.dev.yml` file.
  - **Implementation:** This file will define the development environment. It will be configured by `.env.dev`, map services to a different set of host ports (e.g., 5002) to allow for concurrent execution, and mount a separate persistent volume (`postgres_data_dev`). It will include volume mounts for the application source code (`.:/app`) to enable live reloading. It will also define the `setup-connector` service.

- **Subphase 1.3 (The Verification Blueprint):**

  - **Task:** Create the `docker-compose.test.yml` file.
  - **Implementation:** This file will define a completely headless and ephemeral environment. It will **not** map any ports to the host. It will use an ephemeral, unnamed volume for the database that is destroyed after the run. It will include all services necessary for the E2E test, including the `chorus-tester` and `setup-connector` services.

- **Subphase 1.4 (The Master Orchestrator):**

  - **Task:** Create the final, definitive `Makefile`.
  - **Implementation:** This `Makefile` will be the canonical user interface for the system. It will contain explicit targets like `run-prod`, `run-dev`, and `test`. Each target will use the `--env-file` and `-f` flags to point to the single, correct, self-contained Compose file for that specific task, completely eliminating the flawed file-merging logic.

- **Subphase 1.5 (The Utility Infrastructure):**

  - **Task:** Create the `infrastructure/debezium/Dockerfile.setup` file.
  - **Implementation:** This file will define a minimal Debian-based image that contains both the `curl` and `postgresql-client` packages, providing a robust, correct-by-construction environment for the `setup-connector` script.

- **Subphase 1.6 (The Resilient Script):**

  - **Task:** Update the `infrastructure/debezium/setup-connector.sh` script.
  - **Implementation:** The script will be hardened to include a `psql` polling loop that waits for the PostgreSQL database to be fully initialized and ready to accept connections before attempting to configure the Debezium connector.

- **Subphase 1.7 (The Cleanup):**
  - **Task:** Remove the now-obsolete base `docker-compose.yml` file to prevent any future confusion.

## IV. Acceptance Criteria

The mission shall be considered complete if and only if all of the following criteria are met and can be verified by an independent operator.

- **AC-1 (Development Environment):** The `make run-dev` command completes successfully, and all services are healthy. The UI is accessible and functional on port 5002.
- **AC-2 (Production Environment):** The `make run-prod` command completes successfully, and all services are healthy. The UI is accessible and functional on port 5001.
- **AC-3 (Verification Environment):** The `make test` command completes the full verification suite with zero failures.
- **AC-4 (Concurrency):** The `make run-dev` and `make run-prod` commands can be run concurrently on the same host without any data or network port conflicts.
- **AC-5 (Test Isolation):** The `make test` command can be run while `run-prod` and/or `run-dev` are active without any conflicts.
- **AC-6 (Data Isolation):** Data submitted to the `prod` environment is persisted in the `chorus-prod_postgres_data_prod` volume. Data submitted to the `dev` environment is persisted in the `chorus-dev_postgres_data_dev` volume. These volumes are independent.
- **AC-7 (Final State):** The old `docker-compose.yml` file is deleted from the repository.
