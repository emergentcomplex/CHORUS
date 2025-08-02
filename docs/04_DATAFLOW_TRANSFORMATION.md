# 🔱 Master Plan: The Great Dataflow Transformation

_Document Version: 1.0_
_Last Updated: 2025-07-29_

---

## Objective

To re-architect the CHORUS engine into a scalable, resilient, and evolvable dataflow system based on an immutable event log, adhering to the Data Architecture axioms of the Constitution. This plan will systematically decouple components, introduce asynchronous data streams, and treat our primary database as the first component in a larger, unbundled system.

## Guiding Axioms

This transformation is primarily guided by the following axioms from the Constitution:

-   **Axiom 19 (The Unified Log):** The authoritative System of Record shall be an append-only, immutable log of events.
-   **Axiom 20 (Derived State):** All data stores, other than the System of Record, shall be treated as derived data.
-   **Axiom 21 (Integrity over Timeliness):** The system must prioritize data integrity over timeliness.
-   **Axiom 23 (The Unbundled Database):** The system shall be composed of multiple, specialized data systems.
-   **Axiom 24 (Dataflow over Services):** Internal system integration shall favor asynchronous, one-way event streams.

---

## The Step-by-Step Plan

### ✅ Step 1: Establish the Event Bus Foundation
-   **Status:** Completed
-   **Objective:** Introduce the core components of our new dataflow architecture: an event bus (Redpanda, a Kafka-compatible log) and a Change Data Capture (CDC) mechanism.

### ✅ Step 2: Implement the CDC Pipeline with Debezium
-   **Status:** Completed
-   **Objective:** Deploy a Debezium connector to capture all changes from the MariaDB `task_queue` table and publish them as events to a Kafka topic.

### ✅ Step 3: Create a Stream Processing Service
-   **Status:** Completed
-   **Objective:** Build a new, lightweight Python service that consumes events from the `task_queue` topic and logs them, proving the end-to-end dataflow.

### ✅ Step 4: Build a Derived Data Store
-   **Status:** Completed
-   **Objective:** Use the stream processor to populate a read-optimized data store (Redis) that represents the current state of all tasks.

### ✅ Step 5: Refactor the Web UI
-   **Status:** Completed
-   **Objective:** Modify the Web UI to read task status from the new, fast, derived data store instead of directly querying the primary MariaDB database, demonstrating the performance and decoupling benefits.
-   **Actions:**
    1.  Created a new `RedisAdapter` to encapsulate data access.
    2.  Refactored `web_ui.py` to source all dashboard data from Redis, removing the direct read dependency on MariaDB for these views.

## Conclusion

The Great Dataflow Transformation is complete. The CHORUS architecture now aligns with the principles of data-intensive design, establishing a scalable, resilient, and evolvable foundation for future development.
