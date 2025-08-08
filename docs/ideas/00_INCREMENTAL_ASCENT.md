# Praxis: The Incremental Ascent

### Objective
To achieve absolute, verifiable stability by incrementally integrating our application services on top of our known-good external dependencies. We will build the system up one container at a time, proving each step is stable before proceeding to the next.

### Justification
The "big bang" approach has failed catastrophically. The only sane path forward is to reduce complexity at every stage, isolate variables, and build our system from a stable core outwards. This mission will result in a fully functional, verifiable `docker-compose.yml` and a stable system.

### The Plan

*   **Subphase 1.1 (The Bedrock - External Services):**
    *   **Task:** Create a `docker-compose.yml` that starts **only** the external services: `postgres`, `redis`, `redpanda`, and `kafka-connect`.
    *   **Verification:** Prove that `docker compose up --wait` brings all four services to a healthy state. This establishes our stable foundation.

*   **Subphase 1.2 (The First Light - The Web UI):**
    *   **Task:** Add the `chorus-web` service to the `docker-compose.yml`.
    *   **Verification:** Prove that `docker compose up --wait` now brings all **five** services to a healthy state. This will be the first and most critical test of our application's runtime environment. We will debug this single container until it works perfectly.

*   **Subphase 1.3 (The First Worker - The Launcher):**
    *   **Task:** Add the `chorus-launcher` service.
    *   **Verification:** Prove that `docker compose up --wait` brings all **six** services to a healthy state.

*   **Subphase 1.4 (The Council of Daemons):**
    *   **Task:** Add the remaining core daemons one by one: `chorus-synthesis-daemon` and then `chorus-sentinel`.
    *   **Verification:** After adding each service, we will prove that the entire stack comes up healthy.

*   **Subphase 1.5 (The Nervous System - The Stream Processor):**
    *   **Task:** Add the `chorus-stream-processor` service.
    *   **Verification:** Prove that the full stack of application services is now healthy and stable.

*   **Subphase 1.6 (The Final Verification):**
    *   **Task:** Add the `chorus-tester` service and run the full `make test` command.
    *   **Verification:** The entire test suite must pass, proving that the incrementally-built, stable system is also a correct one.

### Definition of Done
1.  We have a `docker-compose.yml` file that can reliably start every single service in the stack.
2.  The `make test` command completes successfully.
3.  The system is stable, verifiable, and ready for feature development.
