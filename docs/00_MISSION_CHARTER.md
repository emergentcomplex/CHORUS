# 🔱 CHORUS: The Mission Charter

> ✨ _The loudest secrets are kept in silence. We built an engine that listens._ ✨

---

## Overview

**CHORUS** is not a search engine; it is a judgment engine. It is a fully autonomous, self-healing, and evolving intelligence platform designed to fuse disparate, open-source data verticals into high-fidelity, actionable insights.

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

---

## Quickstart Guide

This guide provides the definitive steps to set up and run the entire CHORUS system locally using `make` and Docker.

### Prerequisites

- **Git:** For cloning the repository.
- **Docker & Docker Compose:** For running the entire containerized environment.
- **An IDE:** For editing code on your host machine.

### 1. Initial Setup

```bash
# Clone the repository and navigate into it
git clone <your-repo-url>
cd CHORUS

# Create your personal environment file from the template
cp .env.example .env

# Open .env with your editor and add your GOOGLE_API_KEY
# nano .env
```

### 2. Build and Run the System

This single command builds the Docker images (a one-time slow operation) and starts all services in development mode.

```bash

# This command will stop, build, and start the entire stack.
make rebuild
```

Subsequent starts can use the faster `make run` command.

### 3. Access the System

- **CHORUS C2 UI:** [http://localhost:5001](http://localhost:5001)
- **Redpanda Console (Kafka UI):** [http://localhost:8080](http://localhost:8080)

### 4. Shut Down the System

```bash
# Stop and remove all running containers and volumes.
make stop
```
