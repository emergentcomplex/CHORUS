# Praxis: The Mandate of Foundation

### Objective

To forge a flawless, stable, and verifiable foundation for all future CHORUS development. This mission will correct the flawed build and test harness, implement the core harvester monitoring logic, and establish the automated CI/CD gatekeeper. This is the embodiment of **Axiom 49: Deliberate Velocity**.

### The Plan

- **Subphase 1.1 (The Canonical Build):**

  - **Task:** Replace the entire contents of the `Dockerfile`, `docker-compose.yml`, `docker-compose.override.yml`, and `Makefile` with the authoritative, industry-standard versions.
  - **Justification:** The existing build system is fundamentally broken. It has created a "Two Worlds" anti-pattern, leading to catastrophic, untestable failures. This step replaces it with a simple, robust, and cachable system based on documented best practices. This is the highest priority task.
  - **File(s) to Modify:** `Dockerfile`, `docker-compose.yml`, `docker-compose.override.yml`, `Makefile`.

- **Subphase 1.2 (The Harvester's Vigil):**

  - **Task:** Fully implement the `queue_and_monitor_harvester_tasks` method in the `PostgresAdapter`.
  - **Implementation:** This method will insert dynamic harvester tasks into the `harvesting_tasks` table and then enter a polling loop that checks their status until all are complete.
  - **File(s) to Modify:** `chorus_engine/adapters/persistence/postgres_adapter.py`.

- **Subphase 1.3 (The Constitutional CI/CD Gatekeeper):**
  - **Task:** Implement the automated CI/CD pipeline.
  - **Implementation:** Create a new GitHub Actions workflow at `.github/workflows/ci_cd.yml`. This workflow will trigger on every pull request and run the full, hermetic `make test` command.
  - **File(s) to Create:** `.github/workflows/ci_cd.yml`.

### Definition of Done

1.  The `make launch` and `make test` commands complete successfully from a clean checkout.
2.  The entire test suite, including a new integration test for the harvester monitor, passes reliably.
3.  The CI/CD pipeline is active and correctly passes a pull request that contains all the changes from this mission.
