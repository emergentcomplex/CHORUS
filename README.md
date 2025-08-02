# 🔱 CHORUS: The Judgment Engine

> ✨ _The loudest secrets are kept in silence. We built an engine that listens._ ✨

<p align="center">
  <img src="https://img.shields.io/badge/build-passing-green?style=for-the-badge" alt="Build Status">
  <img src="https://img.shields.io/badge/python-3.12-blueviolet?style=for-the-badge" alt="Python Version">
  <img src="https://img.shields.io/badge/license-MIT-blue?style=for-the-badge" alt="License">
</p>

---

## 1. Core Concepts & Architectural Views

The CHORUS engine is a complex system best understood by viewing it through three distinct architectural lenses:

1.  **The Judgment Process:** The logical flow of how an AI council debates and synthesizes a query into a final verdict. This is the *why* of the system.
2.  **The Dataflow Engine:** The physical infrastructure and data's journey through our containerized, event-driven services. This is the *how* of the system.
3.  **The Development Praxis:** The workflow that developers use to build, verify, and maintain the system, governed by our `Makefile`. This is *how we trust* the system.

The following diagrams illustrate each of these views.

---

## 2. The Judgment Process: The Adversarial Council

This diagram illustrates the logical flow of analysis. A user's query is not answered directly; it is subjected to a multi-tiered, adversarial debate between specialized AI personas.

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': { 'primaryColor': '#14b8a6', 'primaryTextColor': '#ffffff', 'lineColor': '#a1a1aa'}}}%%
graph TD
    subgraph "Tier 0: The Query"
        A[User Query]
    end

    subgraph "Tier 1: The Analyst Wing (Parallel Analysis)"
        direction LR
        style AnalystTier fill:#1e293b,stroke:#334155
        
        subgraph AnalystTier[ ]
            P1["<i class='fa fa-user-secret'></i> Analyst Hawk"]
            P2["<i class='fa fa-user-secret'></i> Analyst Dove"]
            P3["<i class='fa fa-user-secret'></i> Analyst Skeptic"]
            P4["<i class='fa fa-user-secret'></i> Analyst Futurist"]
        end
        
        R1[Preliminary Report 1]
        R2[Preliminary Report 2]
        R3[Preliminary Report 3]
        R4[Preliminary Report 4]
        
        P1 --> R1
        P2 --> R2
        P3 --> R3
        P4 --> R4
    end

    subgraph "Tier 2: The Director's Synthesis"
        style Director fill:#0f766e,stroke:#14b8a6
        Director("<i class='fa fa-user-tie'></i> Director Alpha") --> Briefing{Director's Briefing}
    end

    subgraph "Tier 3: The Final Verdict"
        style Judge fill:#be123c,stroke:#f43f5e
        Judge("<i class='fa fa-gavel'></i> Judge Prime") --> Verdict([Final Verdict])
    end

    A --> AnalystTier
    R1 & R2 & R3 & R4 --> Director
    Briefing --> Judge

    classDef persona fill:#083344,stroke:#0e7490,color:#e0f2fe
    class P1,P2,P3,P4 persona;
```

---

## 3. The Dataflow Engine: The Unbundled Database

This diagram shows the physical infrastructure. It illustrates how data flows through our containerized services, from the initial write in the database to the final materialized views in the cache.

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': { 'primaryColor': '#3b82f6', 'primaryTextColor': '#ffffff', 'lineColor': '#a1a1aa'}}}%%
graph TD
    subgraph "Write Path (User Interaction)"
        A["Web UI"] -- "1. INSERT task" --> D{"PostgreSQL (System of Record)"};
    end

    subgraph "The Unified Log (The System's Nervous System)"
        style L fill:#27272a,stroke:#a1a1aa,color:#fff
        D -- "2. Change Data Capture" --> E["Debezium Connector"];
        E -- "3. Immutable Event" --> L["<i class='fa fa-stream'></i> Redpanda Topic: task_queue"];
    end

    subgraph "Derived Data Path (Asynchronous Processing)"
        style P fill:#1e3a8a,stroke:#60a5fa,color:#fff
        style S fill:#431407,stroke:#e11d48,color:#fff
        L -- "4. Consume Event" --> P["<i class='fa fa-cogs'></i> Stream Processor"];
        P -- "5. Materialize View" --> S["<i class='fa fa-bolt'></i> Redis Cache (Fast Read Store)"];
    end

    subgraph "Read & Analysis Path"
        S -- "6a. Fast Dashboard Queries" --> A;
        D -- "6b. Deep Analysis & RAG" --> G["<i class='fa fa-brain'></i> Analysis Daemons"];
    end

    style D fill:#047857,stroke:#34d399,color:#fff
```

---

## 4. The Development Praxis: The Dual-Mode Harness

This diagram explains the `Makefile`-driven development workflow, which is central to our engineering philosophy. It separates the rapid, iterative "Fast Loop" from the slow, hermetic "Verification Loop."

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': { 'primaryColor': '#d946ef', 'primaryTextColor': '#ffffff', 'lineColor': '#a1a1aa'}}}%%
graph LR
    subgraph "Developer's Machine"
        Dev(Developer) -- "Edits Code" --> Editor[<i class='fa fa-code'></i> IDE / Code Editor]
    end

    subgraph "Fast Loop (95% of workflow)"
        style FastLoop fill:#1e293b,stroke:#334155
        subgraph FastLoop [ ]
            Dev -- "1. `make run`" --> C[Running Containers]
            Editor -.-> C
            Dev -- "2. `make test-fast`" --> T1(Fast Tests)
            T1 -- "Asserts against" --> C
        end
    end
    
    subgraph "Slow Loop (On Dependency Change)"
        style SlowLoop fill:#4a044e,stroke:#a21caf
        subgraph SlowLoop [ ]
            Dev -- "`make rebuild`" --> B(Build Image) --> C2[Restart Containers]
        end
    end

    subgraph "Verification Loop (CI/CD)"
        style VerificationLoop fill:#450a0a,stroke:#be123c
        subgraph VerificationLoop [ ]
            CI(CI/CD Server) -- "`make test`" --> T2(Hermetic Test Suite)
        end
    end
```

---

## 5. The Systemic Learning Loop: The Path to Recursion

This diagram illustrates the future-state goal of the CHORUS engine: to learn from its own judgments. This represents the highest level of abstraction and the system's capacity for recursion.

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': { 'primaryColor': '#ca8a04', 'primaryTextColor': '#ffffff', 'lineColor': '#a1a1aa'}}}%%
graph TD
    A[Analysis Pipeline] --> B{Final Verdict};
    B --> C{User};
    C -- "Provides Feedback" --> D["<i class='fa fa-thumbs-up'></i><i class='fa fa-thumbs-down'></i> Feedback Store"];
    D --> E{Re-evaluation Trigger};
    E -- "Refines Personas or Knowledge" --> F["<i class='fa fa-brain'></i> Persona Cognitive State"];
    F -. "Influences Next Judgment" .-> A;
```

---

## 6. Getting Started

### Prerequisites

-   **Git:** For cloning the repository.
-   **Docker & Docker Compose:** For running the entire containerized environment.
-   **An IDE:** For editing code on your host machine.

### 1. Initial Setup

```bash
# Clone the repository and navigate into it
git clone <your-repo-url>
cd CHORUS

# Create your personal environment file from the template
cp .env.example .env

# Open .env with your editor and add your GOOGLE_API_KEY
# and any other required API keys (e.g., USAJOBS_API_KEY).
# nano .env
```

### 2. Build and Run the System

This single command builds the Docker images (a one-time slow operation) and starts all services in development mode with live code reloading.

```bash
# This command will stop, build, and start the entire stack.
make rebuild
```

Subsequent starts can use the faster `make run` command.

### 3. Access the System

-   **CHORUS C2 UI:** [http://localhost:5001](http://localhost:5001)
-   **Redpanda Console (Kafka UI):** [http://localhost:8080](http://localhost:8080)

### 4. Shut Down the System

```bash
# Stop and remove all running containers and volumes.
make stop
```

## 7. Contributing

Contributions are welcome but must adhere to the project's foundational principles. All development is guided by a strict set of axioms designed to ensure quality, consistency, and architectural integrity.

Before contributing, please familiarize yourself with the canonical documents in the `/docs` directory:
1.  **`01_CONSTITUTION.md`**: The supreme law governing the system's design and non-verification principles.
2.  **`04_VERIFICATION_COVENANT.md`**: The supreme law governing how we prove our work is correct.

## 8. License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
