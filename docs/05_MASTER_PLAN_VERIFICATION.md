# 🔱 Master Plan: The Great Verification

_Document Version: 1.0_
_Last Updated: 2025-07-29_

---

## Objective

To create a comprehensive, automated testing suite that validates the correctness and resilience of the entire dataflow architecture, and to produce a definitive, cross-platform quickstart guide. This plan addresses the critical testing gap created by the "Great Dataflow Transformation" and ensures the system's reliability and maintainability as per our core axioms.

## Guiding Axioms

-   **Axiom 38 (Provable Capability):** A component is not "done" until it is proven to be correct, performant, and resilient through a dedicated test suite.
-   **Axiom 39 (Comprehensive Verification):** The system's correctness must be proven at three levels: unit tests for isolated logic, integration tests for component collaboration, and end-to-end tests for the complete mission workflow.
-   **Axiom 16 (Reliability by Design):** The system must be presumed to operate on unreliable hardware and networks. Our tests must validate this resilience.

---

## The Step-by-Step Plan

### ✅ Step 1: Foundational Tooling
-   **Status:** Completed
-   **Objective:** Integrate `pytest-docker` to manage our containerized services within the test suite. Create a session-wide fixture that reliably starts, health-checks, and configures the full Docker stack.

### ✅ Step 2: Validate the CDC Pipeline
-   **Status:** Completed
-   **Objective:** Create a new integration test that proves a change in MariaDB is correctly captured by Debezium and published to the Redpanda topic.

### ✅ Step 3: Validate the Stream Processor
-   **Status:** Completed
-   **Objective:** Create a new integration test that proves our `task_state_manager` service correctly consumes a message from Redpanda and writes the derived state to Redis.

### ✅ Step 4: Fortify the E2E Test
-   **Status:** In Progress
-   **Objective:** Upgrade the existing end-to-end test to validate the entire dataflow, checking for consistent state in both MariaDB and Redis.
-   **Actions:**
    1.  Modified `test_full_mission.py` to use the `dataflow_services` fixture.
    2.  Removed manual process management from the E2E test.
    3.  Added assertions to verify that the final task state is consistent between MariaDB and Redis.

### Step 5: Unify Test Suite & Refine Quickstart Guide
-   **Status:** Pending
-   **Objective:** Integrate the new dataflow tests into the `make test-all` command and rewrite the Quickstart guide for cross-platform, verifiable setup.
