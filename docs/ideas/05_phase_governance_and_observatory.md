# Praxis: The Sentinel Protocol (Phases 5 & 6)

### Objective
To implement the "Office of the Constitutional Guardian" and the "Cognitive Synapse" to ensure the long-term philosophical health and strategic evolution of the council. We will then build the federated "Observatory" to monitor the health of the entire distributed ecosystem.

### Justification
This final phase combines the original "Sentinel Protocol" and "Observatory" plans with the highest-level governance concepts from our prior ideas (`Idea 09` & `Idea 12`). A learning system without governance is dangerous. A distributed system without observation is a black box. This phase implements the checks and balances for our AI's own evolution and builds the tools to guide the project based on trusted, community-wide data.

### The Plan

*   **Subphase 5.1 (The Office of the Constitutional Guardian):**
    *   **Task:** Establish a permanent, automated audit function to prevent cognitive drift and internal contradictions (`Idea 09`).
    *   **Implementation:**
        1.  **Legislative Review:** A new "Constitutional Compatibility Test" will be added as a mandatory gate before any new insight is added to the knowledge base.
        2.  **Judicial Review:** The `meta_cognition_daemon` will be enhanced with a periodic "Cognitive Dissonance Audit" to check every active persona for internal consistency, flagging unstable personas for human review.
    *   **File(s) to Modify:** `distiller_worker.py` (or equivalent), `meta_cognition_daemon.py`.

*   **Subphase 5.2 (The Cognitive Synapse):**
    *   **Task:** Implement the quarterly "Synaptic Refinement" process for strategic self-organization (`Idea 12`).
    *   **Implementation:** A new, slow-running `synaptic_daemon.py` will be created. Once per quarter, it will perform a meta-analysis on the entire knowledge base to identify emergent strategic domains and propose dynamic reorganizations of the analytical council (e.g., creating new "Specialist Teams").
    *   **File(s) to Create:** `synaptic_daemon.py`.

*   **Subphase 5.3 (The Observatory Protocol):**
    *   **Task:** Build the privacy-preserving, cryptographically secure telemetry system.
    *   **Implementation:**
        1.  **Instance Identity:** Implement the "Proof-of-Instance" protocol, where each new instance generates a public/private key pair and registers its public key with the Observatory.
        2.  **Telemetry Beacon:** Create the `TelemetryBeacon` class to send anonymized, digitally signed SLI metrics.
        3.  **Watchtower:** Deploy the secure, serverless ingestion endpoint that validates signatures.
        4.  **Consent:** Implement the clear, opt-in consent screen for new users.
    *   **File(s) to Create:** `chorus_engine/infrastructure/telemetry/beacon.py`, `observatory/main.py`, `chorus_engine/infrastructure/web/templates/first_run.html`.

### Definition of Done
1.  A new unit test proves that an insight that violates a core axiom is rejected by the Constitutional Guardian.
2.  The `synaptic_daemon` can successfully run and produce a valid proposal for a new "Specialist Team" as a GitHub Issue.
3.  A new CHORUS instance correctly prompts for consent and registers with the Observatory.
4.  The Observatory's ingestion endpoint can successfully receive and validate a signed metric from a client instance.
5.  The CHORUS engine is now a fully governed, self-evolving, and community-observable ecosystem.
