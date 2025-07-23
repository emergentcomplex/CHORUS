# Idea 00: Implement a Unified Development & Deployment Environment

**1. Concept:**
Drastically simplify the entire CHORUS development and deployment lifecycle by implementing a two-pronged solution:
1.  A **Unified Command Center (`Makefile`)** for all common local development tasks.
2.  A **Containerized Deployment (`Dockerfile`)** for perfect, cross-platform portability and production-readiness.

**2. Problem Solved:**
- **High Developer Friction:** The current process for running, testing, or resetting the system involves a long series of manual, error-prone shell commands. This creates a high cognitive load for developers and slows down the iterative cycle.
- **High Barrier to Entry:** The complex manual setup process makes it difficult for new contributors to get started.
- **Environment Inconsistency:** "It works on my machine" is a major risk. A containerized environment ensures that every developer and every deployment is running on the exact same, consistent foundation.

**3. Proposed Solution:**

- **A. The "CHORUS Command Center" (`Makefile`):**
  - A `Makefile` will be created in the project root.
  - It will provide simple, memorable commands for all major lifecycle tasks:
    - `make run`: Starts the UI and all daemons for local development.
    - `make stop`: Stops all background services.
    - `make logs`: Tails the logs of the running daemons.
    - `make test`: Runs the entire validation suite.
    - `make db-reset`: A protected command to completely wipe and re-initialize the database.
    - `make ingest-darpa`: Runs the full, multi-stage DARPA data ingestion pipeline with a single command.

- **B. Containerized Deployment (`docker-compose.yml`):**
  - A `Dockerfile` will define the application environment.
  - A `docker-compose.yml` file will orchestrate the entire CHORUS stack as a set of interconnected services (`database`, `chorus-app`, `chorus-daemons`).
  - This will transform the deployment process into a single command: `make docker-up`.

- **C. Updated Documentation:**
  - The `00_MISSION_CHARTER.md` and `02_CONTRIBUTING.md` will be updated to replace the complex manual setup instructions with the new, simplified `make` commands.

**4. Next Steps:**
- This is a foundational tooling and developer experience upgrade. It should be prioritized and implemented **as soon as possible**, as it will make all subsequent development for Phase 2 and beyond much faster and more reliable.
- The implementation requires creating the `Makefile`, `Dockerfile`, and `docker-compose.yml` in the project root and updating the documentation.
