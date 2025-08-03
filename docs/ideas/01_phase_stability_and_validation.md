# Praxis: The Crucible & The Gatekeeper (Phase 1)

### Objective
To forge a flawless and stable foundation for all future development by eradicating bugs, hardening our verification suite, and implementing an automated CI/CD Gatekeeper that enforces our constitutional principles.

### Justification
Before we can build higher, we must perfect the foundation. This phase combines the original "Crucible" plan with the critical tooling from our prior ideas (`Idea 00` & `Idea 03`). We will not only fix our bugs but also build the automated systems to prevent them from ever recurring. This is the embodiment of **Axiom 49: Deliberate Velocity**.

### The Plan

*   **Subphase 1.1 (Deterministic Verification):**
    *   **Task:** Refactor the brittle, log-scraping `test_daemon_resilience.py` test.
    *   **Implementation:** The test will be re-engineered to poll the database directly for the final status of its "chaos test" query, making our verification suite 100% deterministic.
    *   **File(s) to Modify:** `tests/integration/test_daemon_resilience.py`.

*   **Subphase 1.2 (The Harvester's Vigil):**
    *   **Task:** Fully implement the `queue_and_monitor_harvester_tasks` method in the `PostgresAdapter`.
    *   **Implementation:** This method will insert dynamic harvester tasks into the `harvesting_tasks` table and then enter a polling loop that checks their status until all are complete.
    *   **File(s) to Modify:** `chorus_engine/adapters/persistence/postgres_adapter.py`.

*   **Subphase 1.3 (The System Health & Integrity Validation Suite):**
    *   **Task:** Implement the "Two-Source Reconciliation" check (`Idea 00`).
    *   **Implementation:** Create a new script at `tools/diagnostics/validate_environment.py`. This script will compare the file manifest from the Constitution against `git ls-files` to detect architectural drift and orphan files. It will also perform static analysis to validate all Python `import` statements.
    *   **File(s) to Create:** `tools/diagnostics/validate_environment.py`.
    *   **File(s) to Modify:** `Makefile` (to add a `make validate` command).

*   **Subphase 1.4 (The Constitutional CI/CD Gatekeeper):**
    *   **Task:** Implement the automated CI/CD pipeline (`Idea 03`).
    *   **Implementation:** Create a new GitHub Actions workflow at `.github/workflows/ci_cd.yml`. This workflow will trigger on every pull request and run linting, the full `make test` suite, and the new `make validate` command. Branch protection rules will be enabled to require this check to pass before any merge.
    *   **File(s) to Create:** `.github/workflows/ci_cd.yml`.

### Definition of Done
1.  The entire test suite, including the refactored resilience test, passes reliably.
2.  A new integration test proves the harvester monitor is functional.
3.  The `make validate` command runs successfully and can detect deliberate architectural errors.
4.  The CI/CD pipeline is active and correctly fails a pull request that does not pass all checks.
