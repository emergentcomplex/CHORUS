# 🔱 Praxis: The Mandate of the BGE Oracle (Redux, Integrated)

## I. Objective

To correctly implement the "Mandate of the Oracle," achieving a stable, performant, and verifiable Retrieval-Augmented Generation (RAG) pipeline by architecturally isolating the embedding model into a dedicated microservice. This mission will be executed with the full knowledge gained from the previous failed attempt, and will **simultaneously upgrade the embedding model to the state-of-the-art `BAAI/bge-small-en-v1.5`** to maximize retrieval fidelity from the outset.

## II. Guiding Precepts & Inviolable Constraints (The Lessons Learned)

**A. The Primacy of the Guardian:** The CI/CD pipeline is the absolute foundation. All infrastructure changes will be immediately verified via `act` and the remote CI runner to prevent environmental divergence.

**B. The Codified Truths:** All implementation will adhere to the following known truths: 1. The `gthread` Gunicorn worker **MUST** be used for the embedding service to prevent `fork()`-related deadlocks. 2. The **`BAAI/bge-small-en-v1.5`** model produces **384-dimension** vectors. The database schema **MUST** reflect this. 3. The embedding model **MUST** be baked into the base Docker image to ensure a fast, deterministic, and memory-safe startup in resource-constrained CI environments. 4. Redpanda **MUST** be run with the `--developer-mode` flag to ensure stability in the `act` and CI environments. 5. **The BGE model achieves maximum performance when queries are prepended with the instruction: `"Represent this sentence for searching relevant passages: "`.**

## III. The Plan

### **Phase 1: Forge the Unbreakable Foundation (Infrastructure First)**

This phase makes the environment robust _before_ we add any new application code.

1.  **Sub-Phase 1.1: Harden Redpanda**

    - **Action:** Modify `docker-compose.dev.yml`, `docker-compose.prod.yml`, and `docker-compose.test.yml` to add the `--developer-mode` flag to the `redpanda` service's command.

2.  **Sub-Phase 1.2: Bake the BGE Model**

    - **Action:** Create `tools/setup/download_embedding_model.py`. This script will download the **`BAAI/bge-small-en-v1.5`** model to a non-conflicting directory (`/opt/models`).
    - **Action:** Modify `Dockerfile.base` to copy and run this script, baking the model into the base image.
    - **Action:** Modify the final `Dockerfile` to `chown` the `/opt/models` directory for the `appuser`.

3.  **Verification:** After this phase, commit the changes. The CI/CD pipeline must pass cleanly on the existing (reverted) codebase with these new infrastructure settings. This proves our foundation is sound.

### **Phase 2: The BGE Oracle Reborn (Correct Implementation)**

With a stable foundation, we now build the application using the upgraded model.

1.  **Sub-Phase 2.1: The Oracle's Sanctum**

    - **Action:** Create `chorus_engine/infrastructure/services/embedding_service.py`, ensuring it loads the **`BAAI/bge-small-en-v1.5`** model from the baked-in `/opt/models` path.
    - **Action:** Create `wsgi_embedder.py`.
    - **Action:** Modify all three `docker-compose.*.yml` files to add the `chorus-embedder` service, configured with the `gthread` worker, a `depends_on: postgres` block, and a resilient `start_period`.

2.  **Sub-Phase 2.2: The Scribe's Pilgrimage**

    - **Action:** Modify `infrastructure/postgres/init.sql` to replace the `dsv_embeddings` table with the `semantic_vectors` table, using the correct `vector(384)` dimension.
    - **Action:** Create `chorus_engine/infrastructure/daemons/vectorizer.py` with the corrected logic for `source_vertical` parsing, `UUID` string casting, and the file-handling race condition.
    - **Action:** Modify all three `docker-compose.*.yml` files to add the `chorus-vectorizer` service.

3.  **Sub-Phase 2.3: The Analyst's Divination**

    - **Action:** Refactor the `PostgresAdapter`, `interfaces`, `entities`, and `RunAnalystTier` use case to be fully aligned. The `PostgresAdapter` will be refactored to call the Oracle service and **MUST** prepend the BGE query instruction (`"Represent this sentence for searching relevant passages: "`) to the query text.

4.  **Sub-Phase 2.4: The Final, Verifiable Prophecy**
    - **Action:** Create `tests/integration/test_rag_pipeline.py` and fix the unit tests in `tests/unit/test_use_cases.py`.
    - **Verification:** Run `make test`. It must pass with 100% success.

## IV. Acceptance Criteria

- **AC-1:** The CI/CD pipeline passes on the reverted codebase after the infrastructure hardening in Phase 1.
- **AC-2:** The `chorus-base` image is successfully built and contains the **`bge-small-en-v1.5`** model.
- **AC-3:** The Oracle service and Vectorizer daemon are correctly implemented, applying all codified lessons.
- **AC-4:** The `PostgresAdapter` correctly implements the BGE query instruction.
- **AC-5:** All application code (adapters, entities, use cases) and all tests (unit, integration) are fully aligned.
- **AC-6:** The final `make test` command completes with 100% success, proving the mission is complete and the system is stable.
