# 🔱 The CHORUS System SLO Charter

_Document Version: 3.0 (The Oracle Mandate)_
_Last Updated: 2025-08-12_

---

## 1. Philosophy: Measuring What Matters

This document defines the Service Level Objectives (SLOs) for the CHORUS engine. Our philosophy is to measure the health of the end-to-end dataflow, not just the performance of individual services in isolation.

We focus on three core pillars of a healthy data-intensive system:

1.  **Freshness:** How up-to-date is our derived data?
2.  **Throughput:** How much work can the system process in a given time?
3.  **Correctness:** What percentage of operations complete successfully?

These SLOs are our promise: they define a reliable and performant system. All development and operational efforts must be aligned with meeting or exceeding these targets.

---

## 2. The Critical User Journeys (CUJs)

Our SLOs are defined in the context of two critical user journeys:

1.  **The Interactive Journey:** A user submits a new query and observes the results on the dashboard. This journey is latency-sensitive.
2.  **The Asynchronous Journey:** A task is processed through the entire multi-tier analysis pipeline. This journey is throughput- and correctness-sensitive.

---

## 3. Service Level Indicators (SLIs)

These are the raw, quantitative measurements we take from the system to evaluate our SLOs.

| Component / Flow            | SLI Name                      | SLI Specification                                                         | Rationale                                                               |
| --------------------------- | ----------------------------- | ------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| **Data Ingestion Pipeline** | `cdc_to_topic_latency_ms`     | Time from DB commit to event appearance in Redpanda topic. (p95)          | Measures the freshness of our event log, the heart of the system.       |
| **Stream Processing**       | `topic_to_cache_latency_ms`   | Time from event appearance in topic to state update in Redis cache. (p95) | Measures the freshness of our primary derived data store for the UI.    |
| **Web UI**                  | `request_latency_ms`          | Time for the Flask backend to process an HTTP request. (p95)              | Measures the responsiveness of the user-facing interactive components.  |
| **Embedding Service**       | `embedder_request_latency_ms` | Time for the Embedding Service to process an HTTP request. (p95)          | Measures the performance of the critical, centralized embedding model.  |
| **Analysis Pipeline (E2E)** | `end_to_end_latency_minutes`  | Time from task creation to `COMPLETED` status for a "flash" query. (p95)  | Measures the total time-to-value for the core analytical product.       |
| **Analysis Daemons**        | `pipeline_success_rate`       | Percentage of tasks that transition to the next state without error.      | Measures the correctness and reliability of our core business logic.    |
| **Embedding Service**       | `embedder_success_rate`       | Percentage of embedding requests that complete successfully.              | Measures the reliability of the critical, centralized embedding model.  |
| **Harvester Sentinel**      | `harvester_execution_rate`    | Percentage of scheduled harvester jobs that complete successfully.        | Measures the reliability of our external data collection.               |
| **System Throughput**       | `tasks_processed_per_hour`    | The number of "flash" analysis tasks the system can complete in one hour. | Measures the overall capacity and scalability of the analysis pipeline. |

---

## 4. Service Level Objectives (SLOs)

These are the specific, measurable targets for our SLIs over a rolling 28-day period.

### 4.1. Freshness & Latency SLOs

| Component / Flow           | SLI Metric                    | Target (p95)    |
| -------------------------- | ----------------------------- | --------------- |
| **CDC Pipeline**           | `cdc_to_topic_latency_ms`     | **< 5,000 ms**  |
| **Stream Processor**       | `topic_to_cache_latency_ms`   | **< 2,000 ms**  |
| **Web UI (Dashboard)**     | `request_latency_ms`          | **< 200 ms**    |
| **Web UI (Report View)**   | `request_latency_ms`          | **< 500 ms**    |
| **Embedding Service**      | `embedder_request_latency_ms` | **< 1,500 ms**  |
| **Full Analysis Pipeline** | `end_to_end_latency_minutes`  | **< 5 minutes** |

### 4.2. Correctness & Throughput SLOs

| Component / Flow           | SLI Metric                 | Target          |
| -------------------------- | -------------------------- | --------------- |
| **Analyst Tier**           | `pipeline_success_rate`    | **> 99.5%**     |
| **Director & Judge Tiers** | `pipeline_success_rate`    | **> 99.9%**     |
| **Embedding Service**      | `embedder_success_rate`    | **> 99.9%**     |
| **Harvester Sentinel**     | `harvester_execution_rate` | **> 98.0%**     |
| **System Throughput**      | `tasks_processed_per_hour` | **> 120 tasks** |

---

## 5. Error Budget Policy

An error budget is the inverse of our SLO and represents the acceptable level of failure. For a 99.5% success SLO, our error budget is 0.5%.

- **If we are within our error budget:** We are free to innovate, deploy new features, and take calculated risks.
- **If we have exhausted our error budget:** All new feature development is halted. The team's entire focus shifts to reliability, bug fixing, and performance improvements until the system is back within its SLO targets.

This policy ensures a healthy, long-term balance between innovation and stability.
