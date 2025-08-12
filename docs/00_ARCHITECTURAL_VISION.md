# 🔱 The Architectural Vision of CHORUS

> ✨ _"The goal of software architecture is to minimize the human resources required to build and maintain the required system."_ - Robert C. Martin

This document provides a series of architectural diagrams based on the **C4 Model**. Each diagram offers a different level of abstraction, allowing us to understand the system from the highest-level context down to the interaction of its core components. The diagrams are themed to reflect the pathos and purpose of the CHORUS mission.

---

### **Diagram 1: The Observatory (C4 Level 1: System Context)**

This diagram places the CHORUS engine in its world. It shows how it interacts with users and the vast, noisy universe of open-source data. It answers the question: What is CHORUS and who uses it?

```mermaid
graph TD
    subgraph "The Public Record"
        style "The Public Record" fill:#111827,stroke:#374151,color:#9ca3af
        DS1[Academic Papers]
        DS2[Gov't Spending Data]
        DS3[Job Postings]
        DS4[...]
    end

    subgraph "CHORUS Ecosystem"
        style "CHORUS Ecosystem" fill:#1e1b4b,stroke:#4f46e5,color:#e0e7ff
        C((<b>CHORUS Observatory</b><br><br><i>An autonomous engine that listens to the echoes of silence in open-source data to render judgment on hidden activities.</i>))
    end

    U[<b>Human Analyst</b><br><i>(The Inquirer)</i>]

    U -- Submits Queries & Receives Judgments --> C
    C -- Listens for Signals --> "The Public Record"

    style U fill:#431407,stroke:#f87171
```

---

### **Diagram 2: The Dataflow Engine (C4 Level 2: Containers)**

This diagram zooms into the CHORUS Observatory itself, showing the major, independently deployable services (containers) that comprise the system. It illustrates the "Unbundled Database" architecture and the flow of data through our asynchronous, event-driven ecosystem. It answers the question: What are the major building blocks of the CHORUS engine?

```mermaid
graph TD
    subgraph "Synchronous Path"
        A[<b>Web UI</b><br>(chorus-web)<br><i>Gunicorn/Flask</i>]
    end

    subgraph "System of Record"
        style "System of Record" fill:#064e3b,stroke:#34d399
        D[<b>PostgreSQL</b><br>(chorus-postgres)<br><i>The Ground Truth</i>]
    end

    subgraph "The Oracle"
        style "The Oracle" fill:#581c87,stroke:#a855f7
        O[<b>Embedding Service</b><br>(chorus-embedder)<br><i>The Source of Semantic Understanding</i>]
    end

    subgraph "Asynchronous Daemons & Workers"
        style "Asynchronous Daemons & Workers" fill:#1e3a8a,stroke:#60a5fa
        G[<b>Analysis Daemons</b><br>(chorus-launcher, etc.)]
        V[<b>Vectorizer Daemon</b><br>(chorus-vectorizer)<br><i>The Scribe</i>]
    end

    subgraph "The Unified Log (Event Stream)"
        style "The Unified Log (Event Stream)" fill:#27272a,stroke:#a1a1aa
        L[<b>Redpanda/Kafka</b><br>(chorus-redpanda)<br><i>The System's Nervous System</i>]
    end

    A -- Writes Tasks --> D
    D -- Change Data Capture --> L
    L -- Events --> G
    G -- Needs Embeddings --> O
    G -- Reads/Writes Analysis --> D
    V -- Reads Datalake & Needs Embeddings --> O
    V -- Writes Vectors --> D
```

---

### **Diagram 3: The Adversarial Council (C4 Level 3: Components)**

This diagram is a logical view, not a physical one. It zooms into the "Analysis Daemons" container to show the components that execute our core mission logic. It visualizes the flow of judgment through the three tiers of our adversarial process. It answers the question: How does CHORUS _think_?

```mermaid
graph TD
    subgraph "Tier 1: The Analysts (Divergence)"
        style "Tier 1: The Analysts (Divergence)" fill:#4a044e,stroke:#c026d3
        A1[<b>Analyst Hawk</b><br><i>Threat-focused</i>]
        A2[<b>Analyst Dove</b><br><i>Stability-focused</i>]
        A3[<b>Analyst Skeptic</b><br><i>Oversight-focused</i>]
        A4[<b>Analyst Futurist</b><br><i>Capability-focused</i>]
    end

    subgraph "Tier 2: The Directors (Synthesis)"
        style "Tier 2: The Directors (Synthesis)" fill:#0c4a6e,stroke:#0ea5e9
        DIR[<b>Director Alpha</b><br><i>Synthesizes competing views into a single, coherent briefing.</i>]
    end

    subgraph "Tier 3: The Judge (Verdict)"
        style "Tier 3: The Judge (Verdict)" fill:#7f1d1d,stroke:#ef4444
        JUDGE[<b>Judge Prime</b><br><i>Renders the final, structured, and actionable judgment.</i>]
    end

    Input[User Query] --> A1
    Input --> A2
    Input --> A3
    Input --> A4

    A1 -- Report --> DIR
    A2 -- Report --> DIR
    A3 -- Report --> DIR
    A4 -- Report --> DIR

    DIR -- Briefing --> JUDGE
    JUDGE -- Final Verdict --> Output
```
