# 🔱 CHORUS: The Judgment Engine

> ✨ _The loudest secrets are kept in silence. We built an engine that listens._ ✨

<p align="center">
  <img src="https://img.shields.io/badge/build-passing-green?style=for-the-badge" alt="Build Status">
  <img src="https://img.shields.io/badge/python-3.12-blueviolet?style=for-the-badge" alt="Python Version">
  <img src="https://img.shields.io/badge/license-MIT-blue?style=for-the-badge" alt="License">
</p>

---

## Overview

**CHORUS** is not a search engine; it is a judgment engine. It is a fully autonomous, self-healing, and evolving intelligence platform designed to fuse disparate, open-source data verticals into high-fidelity, actionable insights.

It operates on the principle that a secret program's graduation from the public record leaves behind a pattern of echoes: a budget line vanishes, a new job posting for a cleared physicist appears, a cluster of obscure academic papers creates a new hum in the noise. CHORUS is an observatory for these echoes.

The engine's final output is not a simple answer, but a verdict—a synthesized judgment forged from the structured, adversarial debate of competing AI personas, complete with every source and every dissenting note.

## System Architecture: The Dataflow Engine

CHORUS is a data-intensive application built on the principles of the "Unbundled Database." It uses a collection of specialized, containerized services that communicate via an immutable event log (Redpanda, a Kafka-compatible stream). This architecture ensures scalability, resilience, and evolvability.

```mermaid
graph TD
    subgraph "User Interaction & Write Path"
        A[Web UI] -- Writes (e.g., New Task) --> D{PostgreSQL (System of Record)};
    end

    subgraph "The System's Nervous System (The Unified Log)"
        style L fill:#27272a,stroke:#a1a1aa,color:#fff
        D -- Change Data Capture --> E[Debezium];
        E -- Immutable Events --> L[Redpanda/Kafka Topic: task_queue];
    end

    subgraph "Asynchronous Processing & Derived Data"
        style P fill:#1e3a8a,stroke:#60a5fa,color:#fff
        style S fill:#431407,stroke:#e11d48,color:#fff
        L -- Consumes Events --> P[Stream Processor (chorus-stream-processor)];
        P -- Materializes State --> S[Redis Cache (Fast Read Store)];
    end

    subgraph "Read & Analysis Path"
        S -- Fast Dashboard Queries --> A;
        D -- Deep Analysis & RAG --> G[Analysis Daemons (chorus-launcher)];
    end

    style D fill:#047857,stroke:#34d399,color:#fff
```

## Technology Stack

-   **Backend:** Python 3.12, Flask, Gunicorn
-   **Database:** PostgreSQL w/ pgvector (System of Record, Vector Store)
-   **Streaming:** Redpanda (Kafka-compatible event log), Debezium (Change Data Capture)
-   **In-Memory Store:** Redis (Derived Data Cache)
-   **Containerization:** Docker & Docker Compose
-   **Dependency Management:** `uv`
-   **Testing:** Pytest, Mocks

## Getting Started

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

## Development Workflow

The CHORUS project uses a `Makefile` to provide a streamlined, axiom-driven development process.

### The Fast Loop (95% of your time)

This workflow is optimized for a rapid, sub-second feedback loop while you are coding.

```bash
# 1. Start all services in the background.
make run

# 2. As you make code changes, run the fast test suite.
# This runs against the already-running services.
make test-fast

# 3. View aggregated logs from all services.
make logs
```

### The Verification Loop (For CI/CD)

This is the single, atomic command that a continuous integration server must use. It is slow, hermetic, and guarantees correctness from a clean slate.

```bash
# Builds, starts, sets up, tests, and tears down the entire system.
make test
```

## Contributing

Contributions are welcome but must adhere to the project's foundational principles. All development is guided by a strict set of axioms designed to ensure quality, consistency, and architectural integrity.

Before contributing, please familiarize yourself with the canonical documents in the `/docs` directory:
1.  **`01_CONSTITUTION.md`**: The supreme law governing the system's design and non-verification principles.
2.  **`04_VERIFICATION_COVENANT.md`**: The supreme law governing how we prove our work is correct.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
