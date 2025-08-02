# 🔱 The CHORUS Verification Covenant

_Document Version: 1.0_
_Last Updated: 2025-08-02_

---

## Part 1: The Mandate of Trust

> ✨ A judgment cannot be trusted if its creation cannot be verified. ✨
>
> The CHORUS engine is designed to produce high-fidelity, actionable insights. This fidelity is not an emergent property; it is an engineered outcome. The foundation of this outcome is a rigorous, automated, and multi-layered verification strategy.
>
> This document, The Verification Covenant, codifies the principles that guarantee the correctness, resilience, and performance of the CHORUS engine. It is the supreme law governing how we prove our work. Adherence to this covenant is non-negotiable, as it is the source of our trust in the system's final judgment.

---

## Part 2: The Axioms of Verification

### I. Foundational Principles of Verification

60. **Axiom of Comprehensive Verification:** The system's correctness must be proven at three levels: unit tests for isolated logic, integration tests for component collaboration, and end-to-end tests for the complete mission workflow. (Formerly Axiom 40)
61. **Axiom of the Verification Pyramid:** The test suite must adhere to the Verification Pyramid strategy. The majority of tests shall be fast, isolated unit tests; a smaller layer of integration tests shall verify component collaboration; and a minimal set of E2E tests shall validate the system as a whole.
62. **Axiom of the Four Pillars:** Every automated test must be evaluated against four pillars: it must **protect against regressions**, be **resistant to refactoring**, provide **fast feedback**, and be **maintainable**.
63. **Axiom of Behavioral Verification:** Tests must verify the publicly observable behavior of a component, not its internal implementation details. This ensures tests are resilient to refactoring and remain valuable over time.
64. **Axiom of Significant Logic:** Testing efforts must be focused on code containing significant business logic. Trivial code with no conditional or computational complexity (e.g., simple data containers, framework passthroughs) should not be subject to unit testing.

### II. Principles of Test Design & Implementation

65. **Axiom of Intrinsic Testability:** High-level policy must be testable without its low-level dependencies. The core logic must be testable in isolation from the UI, the database, or any external service. (Formerly Axiom 39)
66. **Axiom of Test Double Clarity:** Test Doubles must be used with clear intent. **Stubs** shall be used to provide state and data _to_ the system under test. **Mocks** shall be used to verify interactions and outputs _from_ the system under test.
67. **Axiom of Implementation Integrity:** The best design intentions can be destroyed by poor implementation strategy. A clean architecture must be paired with a rigorous testing strategy that verifies the system's correctness at every level. (Formerly Axiom 41)
68. **Axiom of Provable Capability:** A component is not "done" until it is proven to be correct, performant, and resilient through a dedicated test suite. (Formerly Axiom 42)

### III. Principles of the Testing Harness & Environment

69. **Axiom of the Unified Environment:** All CHORUS processes—application services, utility scripts, and the test suite—MUST be executed within the canonical containerized environment. The host machine's only role is to orchestrate the containers. (Formerly Axiom 51)
70. **Axiom of the Dual-Mode Harness:** The development harness MUST provide two distinct, clearly-defined modes: a **Verification Mode** (`make test`) that is slow, hermetic, and guarantees correctness from a clean slate for CI/CD; and an **Iteration Mode** (`make run` + `make test-fast`) that is optimized for rapid, sub-second feedback for local developers. (Formerly Axiom 52)
71. **Axiom of Hermetic Verification:** The primary verification target (`make test`) MUST be a self-contained, atomic operation. It is responsible for the entire lifecycle of its execution: building the environment, starting all services, running all setup scripts, executing the full test suite, and tearing down the environment. (Formerly Axiom 55)
72. **Axiom of True User Simulation:** End-to-end (E2E) tests MUST validate the system from the perspective of a true external user. They shall interact with the system exclusively through its public, containerized interfaces (e.g., the Web UI's HTTP endpoints). (Formerly Axiom 57)

### IV. Principles of Process & Resilience

73. **Axiom of Mandated Regression Testing:** No bug shall be considered fixed until a new, automated test is created that verifiably reproduces the failure. The development process for any bug fix is hereby mandated as: 1. **Replicate:** Create a new test that fails. 2. **Remediate:** Implement the code changes. 3. **Verify:** Confirm that the new test and all existing tests now pass. (Formerly Axiom 56)
74. **Axiom of Resilient Initialization:** All long-running services or daemons MUST NOT assume their dependencies are available at startup. Each service MUST implement a resilient, self-contained initialization loop that repeatedly attempts to establish connections to its dependencies until it succeeds. (Formerly Axiom 58)
75. **Axiom of Connection State Pessimism:** All application code MUST treat network connections, especially those held in a pool, as ephemeral and potentially stale. Persistence adapters MUST implement automatic recovery logic to detect and recover from defunct connections. (Formerly Axiom 59)
