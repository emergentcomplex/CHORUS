# 🔱 The CHORUS Constitution & Architectural Blueprint

_Document Version: 9.0 (The Mandate of Gnosis - Final Synthesis)_
_Last Updated: 2025-08-13_

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

_This section codifies all inviolable principles, organized into a cohesive framework. All code and architectural decisions MUST adhere to these axioms._

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
25. **Axiom of Data Stratification:** The system shall treat data storage as a stratified hierarchy, not a monolith. The choice of storage medium for any piece of data **MUST** be a deliberate decision based on its specific lifecycle, velocity, and access patterns. The default strata are:
    - **Ephemeral State (e.g., Redis):** For high-velocity, low-importance data that can be lost without compromising the system's integrity. Used for caches, session data, and transient materialized views.
    - **Relational State (e.g., PostgreSQL):** For low-velocity, high-importance, structured data that serves as the System of Record for core application entities and metadata. This is the default for data requiring transactional integrity and complex queries.
    - **Log State (e.g., Redpanda/Kafka):** For immutable, append-only event streams that represent the system's nervous system. This is the transport layer for Change Data Capture and asynchronous dataflows.
    - **File State (e.g., Docker Volumes):** For large, unstructured, or binary data that is the primordial source of truth (the "Datalake") or for operational artifacts (logs). All data in this stratum **MUST** have an automated pruning or rotation policy to prevent indefinite expansion.
    - **Version Control State (e.g., Git):** For low-velocity, human-readable configuration and documentation that defines the system's architecture and intent. This is the System of Record for the _process_, not the _application_.

### IV. Principles of AI & Mission Logic

_How the engine thinks. These axioms define the specific "business logic" of the adversarial AI council._

26. **Axiom of Adversarial Analysis:** The system's final judgment must emerge from the structured, parallel debate between multiple, competing AI personas.
27. **Axiom of Hierarchical Synthesis:** Analysis is a multi-tiered process (Analyst -> Director -> Judge), with each tier adding a layer of abstraction and judgment.
28. **Axiom of the Analytical Triumvirate:** The council is a three-tiered hierarchy: 16 Analysts, 4 Directors, and 1 final Judge.
29. **Axiom of Persona-Specialization:** Analysts are specialists in both a data vertical and a worldview.
30. **Axiom of Dialectic Rigor:** Analysis is a dialogue. Before elevation, an analytical product must be subjected to a structured, attributed critique by its peers.
31. **Axiom of Persona-Driven Collection:** Data collection is an integral and biased part of the analysis itself, not a neutral preliminary step.
32. **Axiom of Tool-Assisted Analysis:** Personas must have access to external tools to enrich their analysis in real-time.
33. **Axiom of Pragmatic Harvesting:** A harvester's goal is to acquire a high-quality _signal_, not to exhaustively mirror a data source. All harvesters must have a `max_results` limit.
34. **Axiom of Reversible Cognition:** All learning must be auditable, traceable, and reversible. Changes to a persona's cognitive state must be recorded in a versioned, transactional manner.
35. **Axiom of Temporal Self-Awareness:** The system must be aware of its own cognitive state across time, enabling reproducibility, validation of changes, and forensic analysis.
36. **Axiom of Systemic Learning:** The system must be a learning organization, capable of both tactical learning (filling knowledge gaps) and strategic learning (improving its own cognitive processes).

### V. Principles of Praxis & Organization (The Gnosis Axioms)

_How we work, how we organize, and how we prove our work is correct. These axioms govern the development process itself, synthesizing the wisdom of our foundational texts._

37. **Axiom of the Three Ways:** Our work is guided by three principles: enabling **fast flow** through systems thinking, creating **amplified feedback loops** to fix problems at the source, and fostering a **culture of continual learning** to institutionalize improvement.
38. **Axiom of Measurable Outcomes:** Our performance is defined by four key metrics: **Lead Time for Changes**, **Deployment Frequency**, **Mean Time to Restore (MTTR)**, and **Change Failure Rate**. We measure outcomes, not activity.
39. **Axiom of Limited Cognitive Load:** The primary limiting factor to our velocity is team cognitive load. Our architecture and processes must be designed to minimize this load, primarily by providing a stable, self-service internal platform.
40. **Axiom of the Stream-Aligned Team:** We operate as a single, long-lived, stream-aligned team with end-to-end ownership of the CHORUS engine. Our goal is to deliver a continuous stream of value to our users.
41. **Axiom of Visible Work:** All work—missions, forge work, maintenance, and unplanned work—must be made visible on a central Kanban board to enable flow management and bottleneck identification.
42. **Axiom of Small Batches:** All work must be decomposed into the smallest possible increments that still deliver value. This reduces risk and accelerates feedback.
43. **Axiom of Topic Branches:** All code changes must be made on short-lived, single-purpose topic branches. The `main` branch is the immutable source of truth and must always be stable and deployable.
44. **Axiom of Atomic Commits:** A commit is the smallest unit of logical change. Each commit must be atomic, self-contained, and accompanied by a well-formed message that explains its intent.
45. **Axiom of Lightweight Change Approval:** Change approval is achieved through automated testing and peer review via Pull Requests. There is no external, heavyweight Change Advisory Board (CAB).
46. **Axiom of Stable Interfaces:** The system's core logic must depend on abstractions, not on concretions. All interactions with external dependencies (databases, LLMs, web APIs) **MUST** be routed through an internal adapter that implements a stable, project-defined interface.
47. **Axiom of Schema-First Development:** The database schema is the ground truth. All code must conform precisely to the established table structures.
48. **Axiom of Atomic Implementation:** All code provided during development must be a **complete, drop-in replacement** for the file it modifies.
49. **Axiom of Atomic Attribution:** Every external fact must be verifiable and traceable to its source.
50. **Axiom of Report Conciseness:** The final report must be clear and to the point, referencing foundational data once in summary.
51. **Axiom of Internal Challenge:** The system must be constitutionally required to attempt to falsify its own conclusions via a formal, internal Red Team.
52. **Axiom of Quantified Confidence:** All analytical conclusions must be accompanied by a numerical confidence score.
53. **Axiom of Auditable AI:** Every interaction with an external AI model must be auditable, logging the prompt, response, provider, and precise token counts.
54. **Axiom of Economic Significance:** Architecture represents the significant design decisions that shape a system, where "significant" is measured by the long-term cost of change.
55. **Axiom of Deliberate Velocity:** The only way to go fast is to go well. Taking the time to ensure a clean, tested architecture is the only way to enable sustainable, high-speed development.
56. **Axiom of Deferred Decisions:** A good architecture maximizes the number of decisions _not_ made. Decisions regarding volatile, low-level details (frameworks, databases, etc.) must be deferred to the latest responsible moment.

### VI. Principles of Verification & Environment

_How we prove our work is correct and ensure our environments are stable. These axioms are the supreme law governing the project's infrastructure and testing strategy._

57. **Axiom of Comprehensive Verification:** The system's correctness must be proven at three levels: unit tests for isolated logic, integration tests for component collaboration, and end-to-end tests for the complete mission workflow.
58. **Axiom of the Verification Pyramid:** The test suite must adhere to the Verification Pyramid strategy. The majority of tests shall be fast, isolated unit tests; a smaller layer of integration tests shall verify component collaboration; and a minimal set of E2E tests shall validate the system as a whole.
59. **Axiom of Behavioral Verification:** Tests must verify the publicly observable behavior of a component, not its internal implementation details. This ensures tests are resilient to refactoring and remain valuable over time.
60. **Axiom of Intrinsic Testability:** High-level policy must be testable without its low-level dependencies. The core logic must be testable in isolation from the UI, the database, or any external service.
61. **Axiom of Mandated Regression Testing:** No bug shall be considered fixed until a new, automated test is created that verifiably reproduces the failure. The development process for any bug fix is hereby mandated as: 1. **Replicate:** Create a new test that fails. 2. **Remediate:** Implement the code changes. 3. **Verify:** Confirm that the new test and all existing tests now pass.
62. **Axiom of True User Simulation:** End-to-end (E2E) tests MUST validate the system from the perspective of a true external user. They shall interact with the system exclusively through its public, containerized interfaces (e.g., the Web UI's HTTP endpoints).
63. **Axiom of the Unified Environment:** All CHORUS processes—application services, utility scripts, and the test suite—MUST be executed within the canonical containerized environment. The host machine's only role is to orchestrate the containers.
64. **Axiom of Environmental Independence:** Each operational environment (`production`, `development`, `testing`) MUST be defined in its own dedicated, self-contained, and fully explicit configuration file. The use of complex override chains is forbidden.
65. **Axiom of Configuration Precedence:** The configuration defined _inside_ a Docker Compose file (e.g., in an `environment` block) is the absolute, final authority for that service's runtime environment. It MUST take precedence over any and all external sources.
66. **Axiom of Idempotent Orchestration:** All primary `make` targets for starting an environment (e.g., `make run-dev`) MUST be idempotent. They must be architecturally designed to produce the exact same healthy, running state, regardless of the system's state before the command was run.
67. **Axiom of Headless Verification:** The primary verification environment (`test`) MUST be completely headless. It shall not expose any ports to the host machine, guaranteeing it can run concurrently with any other environment without conflict.
68. **Axiom of Resilient Initialization:** All long-running services or daemons MUST NOT assume their dependencies are available at startup. Each service MUST implement a resilient, self-contained initialization loop that repeatedly attempts to establish connections to its dependencies until it succeeds.
69. **Axiom of Connection State Pessimism:** All application code MUST treat network connections as ephemeral and potentially stale. Persistence adapters MUST implement automatic recovery logic to detect and recover from defunct connections.

### VII. Principles of Co-Evolution

_These axioms govern the dynamic, interactive relationship between the human operators and the AI, establishing the principle of a "living architecture" that evolves with the mission._

70. **Axiom of the Living Architecture:** The system's architecture is not a static artifact; it is a dynamic federation of logical components. The AI's context and our tooling must reflect this reality, allowing for the flexible and focused modification of individual components.
71. **Axiom of AI Agency:** The AI is not merely a passive recipient of context. It must be empowered to request deeper knowledge and propose architectural changes when a mission's requirements demand it. The system's tooling must provide a formal interface for the AI to express these needs.
72. **Axiom of Atomic Refactoring:** All architectural changes—migrating files, creating or deleting components—MUST be executed by a robust, validating tool. The tool, not the AI, is responsible for modifying the master component manifest, ensuring its integrity and preventing corruption of the architectural source of truth.
