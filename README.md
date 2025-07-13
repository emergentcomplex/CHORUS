# 🔱 CHORUS: Listening to the Silence Between the Signals

> ✨ *The loudest secrets are kept in silence. We built an engine that listens.* ✨

---

## Overview

**CHORUS** is not a search engine; it is a judgment engine. It is a fully autonomous, self-healing, and evolving intelligence platform designed to fuse disparate, open-source data verticals into high-fidelity, actionable insights.

The system was born from a simple observation: when a government research program proves its worth, it doesn't die—it "graduates" into the classified world, leaving behind a faint echo in the public record. CHORUS is designed to detect these echoes by correlating the silence in one dataset with the sudden chatter in others. It connects the dots between a DARPA program going dark, a surge in contract awards to a specific company, a spike in demand for cleared engineers with unique skills, and the global conversation surrounding a new technology.

By simulating the adversarial, multi-perspective analysis of a real-world intelligence agency, CHORUS moves beyond data retrieval into the realm of automated strategic judgment.

## Core Features

-   **Autonomous & Self-Healing:** Built on a service-oriented architecture with `systemd`-managed daemons, the system runs 24/7, survives reboots, and automatically manages its own data collection and analysis queues.
-   **Evolving Data Lake:** A "fire-and-forget" **Sentinel** process periodically and intelligently refreshes all seven data sources, ensuring the system's knowledge is never stale.
-   **Multi-Source Fusion:** Ingests and correlates data from seven distinct verticals:
    1.  **DARPA Budgets:** The primary signal for strategic intent.
    2.  **USAspending.gov:** The money trail to corporate contractors.
    3.  **Job Postings:** The human capital trail for specialized skills.
    4.  **GovInfo (CRS/USCODE):** The foundational legal and policy context.
    5.  **arXiv.org:** The bleeding edge of academic and scientific research.
    6.  **NewsAPI:** The commercial and financial signal from private industry.
    7.  **GDELT:** The global narrative from worldwide news media.
-   **Adversarial AI Council:** A "Chorus" of 16 different AI analysts and 4 directors debate and challenge findings, preventing groupthink and ensuring intellectual rigor.
-   **Verifiable Attribution:** Every claim in the final report is linked to its source with clickable citations, ensuring academic-grade verifiability.
-   **Dual-Format Export:** Generate final intelligence products as either a portable static HTML website or a professional, archival-quality PDF.
-   **Living Documentation:** The entire system is self-documenting, with a live documentation website generated directly from the codebase.

## System Architecture

CHORUS operates as two parallel, autonomous systems that feed each other: The **Sentinel** (Data Harvesting) and the **Launcher** (Data Analysis).

```mermaid
graph TD
    subgraph "Autonomous Harvesting"
        A[CHORUS Sentinel Daemon] --> B{Harvesting DB Queue};
        B --> C[Worker 1: Scrape News];
        B --> D[Worker 2: Scrape Contracts];
        C --> E[Data Lake];
        D --> E;
    end

    subgraph "Autonomous Analysis"
        F[CHORUS Launcher Daemon] --> G{Analysis DB Queue};
        G --> H[Persona Worker 1];
        G --> I[Persona Worker 2];
        H --> J[Final Report];
        I --> J;
    end

    subgraph "Analyst Interface"
        K[C2 Web Dashboard] --> G;
        J --> K;
    end

    E -- RAG --> H;
    E -- RAG --> I;
    J -- "New Keywords" --> B;

    style A fill:#083344,stroke:#0e7490,color:#fff
    style F fill:#083344,stroke:#0e7490,color:#fff
    style K fill:#4a044e,stroke:#a21caf,color:#fff
