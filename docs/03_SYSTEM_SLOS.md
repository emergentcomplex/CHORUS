# 🔱 CHORUS Service Level Objectives (SLOs)
_Document Version: 2.1 (Canonical Naming)_

## 1. Overview

This document defines the explicit Service Level Objectives (SLOs) for the CHORUS system. These SLOs are the measurable targets for performance, availability, and integrity that guide our architectural decisions. They are our contract with our users and ourselves.

This document is structured as follows:
1.  **System Components & Journeys:** A breakdown of the system into measurable parts.
2.  **Service Level Indicators (SLIs):** The specific metrics we measure.
3.  **Service Level Objectives (SLOs):** The target values for our SLIs.
4.  **Error Budgets:** The operational meaning of our SLOs.
5.  **Architectural Triggers:** How SLO violations inform our roadmap.

---

## 2. System Components & User Journeys

| Code       | Component / Journey                  | Description                                                              |
| :--------- | :----------------------------------- | :----------------------------------------------------------------------- |
| **C-WEB**  | Web UI (Flask Application)           | The user-facing dashboard and reporting interface.                       |
| **C-DB**   | MariaDB Database                     | The primary OLTP database and vector store (System of Record).           |
| **C-LLM**  | LLM Adapter (Gemini)                 | The interface to the external Large Language Model.                      |
| **C-SENT** | Sentinel Daemon                      | The daemon responsible for orchestrating data harvesting tasks.          |
| **C-LAUN** | Launcher Daemon                      | The daemon responsible for orchestrating analysis tasks.                 |
| **J-QUERY**| Query Submission                     | User submits a query; task is created in the database.                   |
| **J-HARV** | Harvester Execution                  | A single harvester worker runs, collects data, and saves to the datalake.|
| **J-ANLZ** | Analysis Execution                   | The full analysis pipeline runs, from planning to final report synthesis.|
| **J-RPRT** | Report Viewing                       | User views the live-updating report page for an analysis session.        |
| **J-INGEST**| DARPA Ingestion Pipeline             | The `make ingest-darpa` command runs to populate the vector DB.          |

---

## 3. Service Level Indicators (SLIs)

An SLI is a direct measurement of a system's behavior.

| SLI Name                  | Description                                                              | Measurement Unit |
| :------------------------ | :----------------------------------------------------------------------- | :--------------- |
| `request_latency`         | Time elapsed to complete a request or operation.                         | Milliseconds (ms)|
| `availability`            | Proportion of valid requests that succeed.                               | Percentage (%)   |
| `data_integrity`          | Proportion of data records that are persisted without loss or corruption.| Percentage (%)   |
| `pipeline_success_rate`   | Proportion of batch jobs or pipelines that complete without fatal error. | Percentage (%)   |

---

## 4. Service Level Objectives (SLOs)

An SLO is a target value for an SLI over a given time period (typically 30 days).

### 4.1. Latency SLOs
*(Measured at the 95th percentile (p95) over a 30-day window)*

| Component / Journey | SLI                 | Target (p95) |
| :------------------ | :------------------ | :----------- |
| **C-WEB (Dashboard Load)** | `request_latency`   | `< 500ms`    |
| **C-WEB (HTMX Poll)**      | `request_latency`   | `< 200ms`    |
| **C-DB** (Standard Query)  | `request_latency`   | `< 50ms`     |
| **C-DB** (Vector Search)   | `request_latency`   | `< 800ms`    |
| **C-LLM** (API Call)       | `request_latency`   | `< 10,000ms` |
| **J-QUERY** (End-to-End)   | `request_latency`   | `< 500ms`    |
| **J-HARV (Single Task)**   | `request_latency`   | `< 5 minutes`|
| **J-ANLZ (Flash Mode)**    | `request_latency`   | `< 3 minutes`|
| **J-ANLZ (Deep Dive Mode)**| `request_latency`   | `< 15 minutes`|

### 4.2. Availability & Success SLOs
*(Measured over a 30-day window)*

| Component / Journey | SLI                       | Target    |
| :------------------ | :------------------------ | :-------- |
| **C-WEB**           | `availability`            | `99.9%`   |
| **C-SENT** (Uptime) | `availability`            | `99.5%`   |
| **C-LAUN** (Uptime) | `availability`            | `99.5%`   |
| **C-LLM** (Adapter) | `availability` (incl. retries) | `99.0%`   |
| **J-HARV (Single Task)** | `pipeline_success_rate`   | `98.0%`   |
| **J-ANLZ**          | `pipeline_success_rate`   | `98.0%`   |
| **J-INGEST**        | `pipeline_success_rate`   | `99.0%`   |

### 4.3. Data Integrity SLOs
*(Measured over a 30-day window)*

| Component           | SLI                | Target  | Rationale (Constitutional Axiom) |
| :------------------ | :----------------- | :------ | :------------------------------- |
| **C-DB** (Core Tables) | `data_integrity`   | `100%`  | **Axiom 19:** Integrity over Timeliness. The System of Record must be perfect. |
| **Datalake Files**  | `data_integrity`   | `99.9%` | **Axiom 18:** Derived State. Can be rebuilt, but should be reliable. |
| **CDC Pipeline (Future)** | `data_integrity` | `100%`  | **Axiom 17:** The Unified Log. Must not drop events. |

---

## 5. Error Budgets

An error budget is the inverse of an SLO (`100% - SLO`). It quantifies the acceptable level of failure. Exceeding the error budget requires freezing new feature development to focus on reliability.

**Example Budgets for a 30-Day Period (43,200 minutes):**

| Component         | SLO       | Error Budget (Downtime / Failures) |
| :---------------- | :-------- | :--------------------------------- |
| **C-WEB**         | `99.9%`   | `43.2 minutes` of downtime.        |
| **C-SENT/C-LAUN** | `99.5%`   | `3.6 hours` of downtime.           |
| **J-ANLZ**        | `98.0%`   | `2 failures` per 100 tasks initiated. |
| **C-DB** (Integrity) | `100%`    | `0 failures`. Any data loss is a SEV-1 incident. |

---

## 6. Architectural Triggers

This SLO document provides a data-driven framework for making major architectural decisions.

1.  **Database Load Trigger:** If the p95 latency for `C-DB (Standard Query)` exceeds **150ms** for a sustained period of 24 hours, it indicates that the polling mechanism of the daemons is overloading the database. This will trigger an architectural review to implement an event-driven push model (e.g., via the Kafka Master Plan).

2.  **Analysis Latency Trigger:** If the p95 latency for `J-ANLZ (Deep Dive Mode)` consistently exceeds its **15-minute** SLO, and the bottleneck is identified as the serial `queue_and_monitor_harvester_tasks` step, this will trigger a review to parallelize harvesting and synthesis using a stream processing model.

3.  **Reliability Trigger:** If the error budget for `J-ANLZ` or `J-HARV (Single Task)` is consumed within the first half of a 30-day period, all new feature development will be halted to address the root causes of the failures.
