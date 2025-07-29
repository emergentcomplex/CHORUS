# 🔱 The CHORUS Constitution & Architectural Blueprint
_Document Version: 4.2 (Comprehensive Verification)_
_Last Updated: 2025-07-29_

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

_This section codifies all 41 inviolable principles. All code and architectural decisions MUST adhere to these axioms._

### I. Foundational Axioms (The Bedrock)

1.  **Axiom of Mission Alignment:** The CHORUS platform's "Guiding North Star" is its core mission. Every feature must directly serve the primary mission of detecting the echoes left by classified programs.
2.  **Axiom of Tiered Modeling:** The system will use a tiered approach to LLM selection (Utility, Synthesis, Apex) to optimize for cost, speed, and capability.
3.  **Axiom of Deterministic Control:** The AI reasons; the code executes. Our Python code is solely responsible for all deterministic logic, including parsing, state management, and data formatting.
4.  **Axiom of Stable Interfaces:** The system's core logic must depend on abstractions, not on concretions. All interactions with external dependencies (databases, LLMs, web APIs) **MUST** be routed through an internal adapter that implements a stable, project-defined interface.
5.  **Axiom of Schema-First Development:** The database schema is the ground truth. All code must conform precisely to the established table structures.
6.  **Axiom of Atomic Implementation:** All code provided during development must be a **complete, drop-in replacement** for the file it modifies.

### II. Architectural Axioms (The Structure)

#### Macro-Architecture (System Layers)
7.  **Axiom of the Screaming Architecture:** The top-level structure of the repository must scream "OSINT Analysis Engine", not "Web Application" or "Database System". The use cases of the system must be the central, first-class elements of the design.
8.  **Axiom of the Dependency Rule:** Source code dependencies must only point inwards, from low-level, concrete details to high-level, abstract policies.
9.  **Axiom of Policy-Detail Separation:** All software can be divided into high-level policy and low-level detail. Policy is the core business logic and value. Details are the mechanisms that enable policy to be executed (e.g., UI, database, web). The architecture must enforce this separation via boundaries.
10. **Axiom of Irrelevant Details:** The core business logic must be agnostic to its delivery and persistence mechanisms. The Web, the Database, and external Frameworks are plugins to the core.

#### Meso-Architecture (Component Design)
11. **Axiom of Component Cohesion:** Classes within a component must be cohesive. They must change together for the same reasons (Common Closure Principle) and be reused together as a single, releasable unit (Reuse/Release Equivalence Principle).
12. **Axiom of Acyclic Dependencies:** There shall be no cycles in the component dependency graph. The graph must be a Directed Acyclic Graph (DAG), enabling the system to be built, tested, and released in well-defined, incremental stages.
13. **Axiom of Stable Dependencies:** Dependencies must flow in the direction of stability. Volatile components designed for frequent change must depend on stable, abstract components that are designed to be immutable.

#### Data Architecture (Dataflow & Integration)
14. **Axiom of the Unbundled Database:** The system shall be composed of multiple, specialized data systems (e.g., OLTP store, full-text search index, analytics engine), each optimized for its specific access pattern. There is no "one size fits all" data store.
15. **Axiom of Derived State:** The system must maintain a clear distinction between the System of Record (the authoritative source of truth) and Derived Data. All derived data (caches, indexes, materialized views) must be treated as disposable and entirely rebuildable from the source of truth.
16. **Axiom of Immutable Events:** The System of Record shall be an append-only log of immutable events. This log is the central, unifying source of truth from which all other system state is derived.
17. **Axiom of Dataflow over Services:** Internal system integration shall favor asynchronous, one-way event streams over synchronous, request/response RPC. This promotes loose coupling and resilience.

#### Micro-Architecture (Implementation)
18. **Axiom of SOLID Design:** All class-level design within components must adhere to the SOLID principles (Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, Dependency Inversion) to ensure internal code quality and maintainability.
19. **Axiom of Adversarial Analysis:** The system's final judgment must emerge from the structured, parallel debate between multiple, competing AI personas.
20. **Axiom of Hierarchical Synthesis:** Analysis is a multi-tiered process (Analyst -> Director -> Judge), with each tier adding a layer of abstraction and judgment.
21. **Axiom of Persona-Driven Collection:** Data collection is an integral and biased part of the analysis itself, not a neutral preliminary step.
22. **Axiom of Tool-Assisted Analysis:** Personas must have access to external tools to enrich their analysis in real-time.
23. **Axiom of Pragmatic Harvesting:** A harvester's goal is to acquire a high-quality _signal_, not to exhaustively mirror a data source. All harvesters must have a `max_results` limit.

### III. Verifiability & Quality Axioms (The Product)

24. **Axiom of Integrity over Timeliness:** The system must prioritize data integrity (correctness, no corruption, no loss) over timeliness (recency). Asynchronous dataflows are acceptable, but they must guarantee the integrity of derived state.
25. **Axiom of End-to-End Correctness:** The application is responsible for its correctness, end-to-end. Fault tolerance cannot be delegated entirely to underlying components. Mechanisms like idempotent operation identifiers must be used to ensure integrity across the entire dataflow pipeline.
26. **Axiom of Intrinsic Testability:** High-level policy must be testable without its low-level dependencies. The core logic must be testable in isolation from the UI, the database, or any external service.
27. **Axiom of Atomic Attribution:** Every external fact must be verifiable and traceable to its source.
28. **Axiom of Report Conciseness:** The final report must be clear and to the point, referencing foundational data once in summary.
29. **Axiom of Internal Challenge:** The system must be constitutionally required to attempt to falsify its own conclusions via a formal, internal Red Team.
30. **Axiom of Quantified Confidence:** All analytical conclusions must be accompanied by a numerical confidence score.
31. **Axiom of Auditable AI:** Every interaction with an external AI model must be auditable, logging the prompt, response, provider, and precise token counts.
32. **Axiom of Provable Capability:** A component is not "done" until it is proven to be correct, performant, and resilient through a dedicated test suite.
33. **Axiom of Comprehensive Verification:** The system's correctness must be proven at three levels: unit tests for isolated logic, integration tests for component collaboration, and end-to-end tests for the complete mission workflow.

### IV. Strategic & Learning Axioms (The Vision)

34. **Axiom of Ethical Responsibility:** The system must be designed with a conscious consideration of its ethical implications. We have a responsibility to prevent the misuse of our tools for surveillance or discrimination and to protect the privacy of individuals whose data we process.
35. **Axiom of Deferred Decisions:** A good architecture maximizes the number of decisions *not* made. Decisions regarding volatile, low-level details (frameworks, databases, etc.) must be deferred to the latest responsible moment.
36. **Axiom of the Analytical Triumvirate:** The council is a three-tiered hierarchy: 16 Analysts, 4 Directors, and 1 final Judge.
37. **Axiom of Persona-Specialization:** Analysts are specialists in both a data vertical and a worldview.
38. **Axiom of Dialectic Rigor:** Analysis is a dialogue. Before elevation, an analytical product must be subjected to a structured, attributed critique by its peers.
39. **Axiom of Reversible Cognition:** All learning must be auditable, traceable, and reversible. Changes to a persona's cognitive state must be recorded in a versioned, transactional manner.
40. **Axiom of Temporal Self-Awareness:** The system must be aware of its own cognitive state across time, enabling reproducibility, validation of changes, and forensic analysis.
41. **Axiom of Systemic Learning:** The system must be a learning organization, capable of both tactical learning (filling knowledge gaps) and strategic learning (improving its own cognitive processes).
