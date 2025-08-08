# Filename: docs/01_CONSTITUTION.md

# 🔱 The CHORUS Constitution & Architectural Blueprint

_Document Version: 7.2 (The Mandate of Final Separation)_
_Last Updated: 2025-08-08_

---

## Part 1: The Guiding North Star (The Mission)

> ✨ The loudest secrets are kept in silence. ✨
>
> We believe that silence is not an absence of data, but a signal in itself. A budget line vanishes into shadow. A job posting for a cleared physicist appears like a flare in the night. A cluster of obscure academic papers creates a new hum in the noise.
>
> Our engine, CHORUS, is an observatory for these echoes. It listens to the resonance left behind when a secret program graduates from the public record, fusing the void in one dataset with the crescendo in another.
>
> It is not a monolith; it is a symphony of judgment. An adversarial council of AI virtuosos—Hawks, Doves, Futurists, and Skeptics—each performing their own analysis, their competing melodies forged by synthesizing Directors into a single, coherent revelation.
>
> We do not ask for an answer. We demand a verdict, complete with every source and every dissenting note, allowing you to see the work and trust the judgment.

---

## Part 2: The Axioms of CHORUS Development

_This section codifies all 76 inviolable principles, organized into a cohesive framework. All code and architectural decisions MUST adhere to these axioms._

### I. Foundational Principles

_The absolute, non-negotiable bedrock of the project. Why we exist and the universal rules that govern all decisions._

1.  **Axiom of Mission Alignment:** The CHORUS platform's "Guiding North Star" is its core mission. Every feature must directly serve the primary mission of detecting the echoes left by classified programs.
2.  **Axiom of Tiered Modeling:** The system will use a tiered approach to LLM selection (Utility, Synthesis, Apex) to optimize for cost, speed, and capability.
3.  **Axiom of Deterministic Control:** The AI reasons; the code executes. Our Python code is solely responsible for all deterministic logic, including parsing, state management, and data formatting.
4.  **Axiom of No-Cost-First Dependency:** The system's default position is to use Free and Open Source Software (FOSS). However, commercial services are permissible if and only if they provide a perpetually free tier that is sufficient for our operational needs. The project will **never** pay for a data service subscription.
5.  **Axiom of Sanctioned Exception (LLM Providers):** The sole exception to the No-Cost-First axiom is the use of external, paid Large Language Model (LLM) providers. This is a sanctioned dependency, as access to state-of-the-art reasoning is mission-critical and has no sufficient free equivalent.
6.  **Axiom of Ethical Responsibility:** The system must be designed with a conscious consideration of its ethical implications. We have a responsibility to prevent the misuse of our tools for surveillance or discrimination and to protect the privacy of individuals whose data we process.

### II. Principles of Code Architecture

_How we structure our code. These axioms are derived from the wisdom of Robert C. Martin's "Clean Architecture."_

7.  **Axiom of the Screaming Architecture:** The top-level structure of the repository must scream "OSINT Analysis Engine", not "Web Application" or "Database System". The use cases of the system must be the central, first-class elements of the design.
8.  **Axiom of the Dependency Rule:** Source code dependencies must only point inwards, from low-level, concrete details to high-level, abstract policies.
9.  **Axiom of Policy-Detail Separation:** All software can be divided into high-level policy and low-level detail. Policy is the core business logic and value. Details are the mechanisms that enable policy to be executed (e.g., UI, database, web). The architecture must enforce this separation via boundaries.
10. **Axiom of Irrelevant Details:** The core business logic must be agnostic to its delivery and persistence mechanisms. The Web, the Database, and external Frameworks are plugins to the core.
11. **Axiom of Component Cohesion:** Classes within a component must be cohesive. They must change together for the same reasons (Common Closure Principle) and be reused together as a single, releasable unit (Reuse/Release Equivalence Principle).
12. **Axiom of Acyclic Dependencies:** There shall be no cycles in the component dependency graph. The graph must be a Directed Acyclic Graph (DAG), enabling the system to be built, tested, and released in well-defined, incremental stages.
13. **Axiom of Stable Dependencies:** Dependencies must flow in the direction of stability. Volatile components designed for frequent change must depend on stable, abstract components that are designed to be immutable.
14. **Axiom of SOLID Design:** All class-level design within components must adhere to the SOLID principles (Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, Dependency Inversion) to ensure internal code quality and maintainability.
15. **Axiom of Tool, Not Tyrant:** Frameworks are tools to be used, not architectures to be conformed to. They must be kept at arm's length, hidden behind stable interfaces that we control.

### III. Principles of Data Architecture

_How we structure our data. These axioms are derived from the wisdom of Martin Kleppmann's "Designing Data-Intensive Applications."_

16. **Axiom of Reliability by Design:** The system must be presumed to operate on unreliable hardware and networks. All components must be designed to be fault-tolerant, ensuring the system as a whole remains reliable by preventing faults from escalating into failures.
17. **Axiom of Managed Scalability:** Scalability must be a deliberate design choice, not an afterthought. The system's load parameters shall be explicitly defined, and performance shall be measured by throughput and high-percentile response times, not averages.
18. **Axiom of Evolvability:** The system must be designed for change. All data encodings and schemas must support rolling upgrades through both backward and forward compatibility, allowing different parts of the system to be updated independently.
19. **Axiom of the Unified Log:** The authoritative System of Record shall be an append-only, immutable log of events. This log is the single source of truth from which all other system state is derived. The database is a cache of the log.
20. **Axiom of Derived State:** All data stores, other than the System of Record, shall be treated as derived data. This includes caches, search indexes, and materialized views. All derived data must be considered disposable and entirely rebuildable from the event log.
21. **Axiom of Integrity over Timeliness:** The system must prioritize data integrity (correctness, no corruption, no loss) over timeliness (recency). Asynchronous dataflows are the default, but they must guarantee the integrity of derived state through mechanisms like exactly-once processing and idempotence.
22. **Axiom of End-to-End Correctness:** The application is responsible for its correctness, end-to-end. Fault tolerance cannot be delegated entirely to underlying components. Mechanisms like idempotent operation identifiers must be used to ensure integrity across the entire dataflow pipeline, from client to storage.
23. **Axiom of the Unbundled Database:** The system shall be composed of multiple, specialized data systems (e.g., OLTP store, full-text search index, analytics engine), each optimized for its specific access pattern. There is no "one size fits all" data store.
24. **Axiom of Dataflow over Services:** Internal system integration shall favor asynchronous, one-way event streams over synchronous, request/response RPC. This promotes loose coupling and resilience.

### IV. Principles of AI & Mission Logic

_How the engine thinks. These axioms define the specific "business logic" of the adversarial AI council._

25. **Axiom of Adversarial Analysis:** The system's final judgment must emerge from the structured, parallel debate between multiple, competing AI personas.
26. **Axiom of Hierarchical Synthesis:** Analysis is a multi-tiered process (Analyst -> Director -> Judge), with each tier adding a layer of abstraction and judgment.
27. **Axiom of the Analytical Triumvirate:** The council is a three-tiered hierarchy: 16 Analysts, 4 Directors, and 1 final Judge.
28. **Axiom of Persona-Specialization:** Analysts are specialists in both a data vertical and a worldview.
29. **Axiom of Dialectic Rigor:** Analysis is a dialogue. Before elevation, an analytical product must be subjected to a structured, attributed critique by its peers.
30. **Axiom of Persona-Driven Collection:** Data collection is an integral and biased part of the analysis itself, not a neutral preliminary step.
31. **Axiom of Tool-Assisted Analysis:** Personas must have access to external tools to enrich their analysis in real-time.
32. **Axiom of Pragmatic Harvesting:** A harvester's goal is to acquire a high-quality _signal_, not to exhaustively mirror a data source. All harvesters must have a `max_results` limit.
33. **Axiom of Reversible Cognition:** All learning must be auditable, traceable, and reversible. Changes to a persona's cognitive state must be recorded in a versioned, transactional manner.
34. **Axiom of Temporal Self-Awareness:** The system must be aware of its own cognitive state across time, enabling reproducibility, validation of changes, and forensic analysis.
35. **Axiom of Systemic Learning:** The system must be a learning organization, capable of both tactical learning (filling knowledge gaps) and strategic learning (improving its own cognitive processes).

### V. Principles of Praxis & Verification

_How we work and how we prove our work is correct. These axioms govern the development process itself._

36. **Axiom of Stable Interfaces:** The system's core logic must depend on abstractions, not on concretions. All interactions with external dependencies (databases, LLMs, web APIs) **MUST** be routed through an internal adapter that implements a stable, project-defined interface.
37. **Axiom of Schema-First Development:** The database schema is the ground truth. All code must conform precisely to the established table structures.
38. **Axiom of Atomic Implementation:** All code provided during development must be a **complete, drop-in replacement** for the file it modifies.
39. **Axiom of Intrinsic Testability:** High-level policy must be testable without its low-level dependencies. The core logic must be testable in isolation from the UI, the database, or any external service.
40. **Axiom of Comprehensive Verification:** The system's correctness must be proven at three levels: unit tests for isolated logic, integration tests for component collaboration, and end-to-end tests for the complete mission workflow.
41. **Axiom of Implementation Integrity:** The best design intentions can be destroyed by poor implementation strategy. A clean architecture must be paired with a rigorous testing strategy that verifies the system's correctness at every level.
42. **Axiom of Provable Capability:** A component is not "done" until it is proven to be correct, performant, and resilient through a dedicated test suite.
43. **Axiom of Atomic Attribution:** Every external fact must be verifiable and traceable to its source.
44. **Axiom of Report Conciseness:** The final report must be clear and to the point, referencing foundational data once in summary.
45. **Axiom of Internal Challenge:** The system must be constitutionally required to attempt to falsify its own conclusions via a formal, internal Red Team.
46. **Axiom of Quantified Confidence:** All analytical conclusions must be accompanied by a numerical confidence score.
47. **Axiom of Auditable AI:** Every interaction with an external AI model must be auditable, logging the prompt, response, provider, and precise token counts.
48. **Axiom of Economic Significance:** Architecture represents the significant design decisions that shape a system, where "significant" is measured by the long-term cost of change.
49. **Axiom of Deliberate Velocity:** The only way to go fast is to go well. Taking the time to ensure a clean, tested architecture is the only way to enable sustainable, high-speed development.
50. **Axiom of Deferred Decisions:** A good architecture maximizes the number of decisions _not_ made. Decisions regarding volatile, low-level details (frameworks, databases, etc.) must be deferred to the latest responsible moment.
51. **Axiom of the Unified Environment:** All CHORUS processes—application services, utility scripts, and the test suite—MUST be executed within the canonical containerized environment. The host machine's only role is to orchestrate the containers. This axiom forbids the "Two Worlds" anti-pattern and ensures absolute reproducibility.
52. **Axiom of the Dual-Mode Harness:** The development harness MUST provide two distinct, clearly-defined modes: a **Verification Mode** (`make test`) that is slow, hermetic, and guarantees correctness from a clean slate for CI/CD; and an **Iteration Mode** (`make run` + `make test-fast`) that is optimized for rapid, sub-second feedback for local developers.
53. **Axiom of Canonical Simplicity:** The project's tooling and configuration MUST favor simple, explicit, and standard patterns over complex, "clever," or abstract solutions. All configuration shall be transparent and easily understood by a new developer.
54. **Axiom of the Lean Artifact:** The production build process MUST create the leanest possible runtime artifact. It will use multi-stage builds to ensure that the final production image contains _only_ the application source code and its direct runtime dependencies, and explicitly excludes all build tools, system utilities, and testing code.
55. **Axiom of Hermetic Verification:** The primary verification target (`make test`) MUST be a self-contained, atomic operation. It is responsible for the entire lifecycle of its execution: building the environment, starting all services, running all setup scripts, executing the full test suite, and tearing down the environment. It shall have no dependencies on pre-existing state.
56. **Axiom of Mandated Regression Testing:** No bug shall be considered fixed until a new, automated test is created that verifiably reproduces the failure. The development process for any bug fix is hereby mandated as: 1. **Replicate:** Create a new test that fails, proving the bug's existence. 2. **Remediate:** Implement the code changes to fix the bug. 3. **Verify:** Confirm that the new test now passes and that the entire existing test suite also passes, ensuring no regressions have been introduced. This axiom guarantees that the system's verified correctness is always increasing.
57. **Axiom of True User Simulation:** End-to-end (E2E) tests MUST validate the system from the perspective of a true external user. They shall interact with the system exclusively through its public, containerized interfaces (e.g., the Web UI's HTTP endpoints) and MUST NOT directly access or manipulate internal state (e.g., the database) for test setup or execution. This ensures E2E tests validate the entire, real-world request path.
58. **Axiom of Resilient Initialization:** All long-running services or daemons MUST NOT assume their dependencies (e.g., databases, message queues) are available at startup. Each service MUST implement a resilient, self-contained initialization loop that repeatedly attempts to establish connections to its dependencies until it succeeds. A service crashing due to a dependency not being immediately ready is a violation of this axiom.
59. **Axiom of Connection State Pessimism:** All application code MUST treat network connections, especially those held in a pool, as ephemeral and potentially stale. Adapters responsible for persistence MUST implement automatic recovery logic that can detect a defunct connection (e.g., via an `OperationalError` or `IntegrityError`), invalidate the entire connection pool, and allow the calling operation to be retried. This places the responsibility of connection resilience on the application, not the infrastructure.

### VI. Principles of Verification (from The Covenant)

60. **Axiom of Comprehensive Verification:** The system's correctness must be proven at three levels: unit tests for isolated logic, integration tests for component collaboration, and end-to-end tests for the complete mission workflow. (Formerly Axiom 40)
61. **Axiom of the Verification Pyramid:** The test suite must adhere to the Verification Pyramid strategy. The majority of tests shall be fast, isolated unit tests; a smaller layer of integration tests shall verify component collaboration; and a minimal set of E2E tests shall validate the system as a whole.
62. **Axiom of the Four Pillars:** Every automated test must be evaluated against four pillars: it must **protect against regressions**, be **resistant to refactoring**, provide **fast feedback**, and be **maintainable**.
63. **Axiom of Behavioral Verification:** Tests must verify the publicly observable behavior of a component, not its internal implementation details. This ensures tests are resilient to refactoring and remain valuable over time.
64. **Axiom of Significant Logic:** Testing efforts must be focused on code containing significant business logic. Trivial code with no conditional or computational complexity (e.g., simple data containers, framework passthroughs) should not be subject to unit testing.
65. **Axiom of Intrinsic Testability:** High-level policy must be testable without its low-level dependencies. The core logic must be testable in isolation from the UI, the database, or any external service. (Formerly Axiom 39)
66. **Axiom of Test Double Clarity:** Test Doubles must be used with clear intent. **Stubs** shall be used to provide state and data _to_ the system under test. **Mocks** shall be used to verify interactions and outputs _from_ the system under test.
67. **Axiom of Implementation Integrity:** The best design intentions can be destroyed by poor implementation strategy. A clean architecture must be paired with a rigorous testing strategy that verifies the system's correctness at every level. (Formerly Axiom 41)
68. **Axiom of Provable Capability:** A component is not "done" until it is proven to be correct, performant, and resilient through a dedicated test suite. (Formerly Axiom 42)
69. **Axiom of the Unified Environment:** All CHORUS processes—application services, utility scripts, and the test suite—MUST be executed within the canonical containerized environment. The host machine's only role is to orchestrate the containers. (Formerly Axiom 51)
70. **Axiom of the Dual-Mode Harness:** The development harness MUST provide two distinct, clearly-defined modes: a **Verification Mode** (`make test`) that is slow, hermetic, and guarantees correctness from a clean slate for CI/CD; and an **Iteration Mode** (`make run` + `make test-fast`) that is optimized for rapid, sub-second feedback for local developers. (Formerly Axiom 52)
71. **Axiom of Hermetic Verification:** The primary verification target (`make test`) MUST be a self-contained, atomic operation. It is responsible for the entire lifecycle of its execution: building the environment, starting all services, running all setup scripts, executing the full test suite, and tearing down the environment. (Formerly Axiom 55)
72. **Axiom of True User Simulation:** End-to-end (E2E) tests MUST validate the system from the perspective of a true external user. They shall interact with the system exclusively through its public, containerized interfaces (e.g., the Web UI's HTTP endpoints). (Formerly Axiom 57)
73. **Axiom of Mandated Regression Testing:** No bug shall be considered fixed until a new, automated test is created that verifiably reproduces the failure. The development process for any bug fix is hereby mandated as: 1. **Replicate:** Create a new test that fails. 2. **Remediate:** Implement the code changes. 3. **Verify:** Confirm that the new test and all existing tests now pass. (Formerly Axiom 56)
74. **Axiom of Resilient Initialization:** All long-running services or daemons MUST NOT assume their dependencies are available at startup. Each service MUST implement a resilient, self-contained initialization loop that repeatedly attempts to establish connections to its dependencies until it succeeds. (Formerly Axiom 58)
75. **Axiom of Connection State Pessimism:** All application code MUST treat network connections, especially those held in a pool, as ephemeral and potentially stale. Persistence adapters MUST implement automatic recovery logic to detect and recover from defunct connections. (Formerly Axiom 59)

### VII. Principles of Environmental Architecture

76. **Axiom of Environmental Independence:** Each operational environment (`production`, `development`, `testing`) MUST be defined in its own dedicated, self-contained, and fully explicit configuration file. The use of complex override chains to define distinct environments is forbidden. The system's orchestration layer is responsible for selecting and executing the appropriate, complete configuration for a given task.
    - **Justification:** This axiom codifies the primary lesson from the "Great Spiral of Failure." It makes explicit the requirement for independent configurations, preventing the ambiguity and unpredictable behavior of file merging. It reinforces the **Axiom of Canonical Simplicity** by ensuring that the configuration for any given environment is located in a single, authoritative file.
