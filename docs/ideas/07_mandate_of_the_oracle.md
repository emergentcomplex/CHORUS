# 🔱 Praxis: The Mandate of the Oracle

## I. Objective

To achieve a stable, performant, and verifiable Retrieval-Augmented Generation (RAG) pipeline by architecturally isolating the computationally-heavy embedding model into a dedicated, single-process microservice (The Oracle). This mission will correct the fundamental architectural flaw that caused the previous mission's cascading failures, transforming the system from a deadlocked state into a responsive, scalable, and testable platform.

## II. Guiding Precepts & Inviolable Constraints

**A. The Sanctity of the Infrastructure:**
The multi-environment architecture (`Makefile`, `docker-compose.*.yml` files) is a stable baseline. Changes are permissible **only** as explicitly required by this mandate to add the new Oracle service and its dependencies. No other modifications are sanctioned.

**B. The Lesson of the Fork (The Singleton Process Principle):**
We have proven that `fork()`-based multiprocessing is incompatible with in-process loading of large PyTorch models. This is now a codified lesson. The embedding model **MUST** be treated as a singleton process. All other application components that require embeddings **MUST** interact with it as lightweight, stateless network clients. This is the supreme architectural law of this mandate.

**C. The Mandate of Temporal Fidelity (The User's Amendment):**
Per your directive, semantic relevance alone is insufficient. The vector space **MUST** be time-aware. This mandate will implement the **"Textual Time Encoding"** pattern. The document's publication date will be prepended to its content before vectorization, impressing a temporal context directly into the semantic vector.

**D. The Primacy of the Datalake:**
The `/datalake` directory remains the absolute source of truth. The vector database is a disposable, derived index of the datalake, fulfilling **Axiom 20 (Derived State)**.

**E. The Mandate of Attribution:**
The "Chain of Justification" remains a core requirement. The final output from the Analyst persona **MUST** be engineered to provide inline citations in the format `[SOURCE: vector_id]`.

## III. The Ground Truth (The Current State)

The current state of the engine is one of perfect, hollow readiness (post-reversion).

1.  **The Blind Analysts:** The `RunAnalystTier` use case is functioning, but it reasons in a vacuum. The `PostgresAdapter.load_data_from_datalake` method is a placeholder stub.
2.  **The Silent Library:** The Harvester daemons are correctly populating the `/datalake` directory, but this data is unused.
3.  **The Flawed Prototype:** The `dsv_embeddings` table and its related adapter methods are a non-functional prototype that must be removed.

## IV. The Schema of the Oracle (The Architectural Decree)

The foundation of this mission remains the creation of the new, canonical table for our unified semantic space. The `dsv_embeddings` table is hereby abolished. In its place, we decree the creation of the `semantic_vectors` table.

| Column Name         | Data Type     | Description                                                            | Index Type         |
| :------------------ | :------------ | :--------------------------------------------------------------------- | :----------------- |
| `vector_id`         | `UUID`        | Primary Key. A unique identifier for this specific chunk of knowledge. | `PRIMARY KEY`      |
| `source_vertical`   | `VARCHAR(50)` | The origin of the data (e.g., 'arxiv', 'usaspending').                 | `BTREE`            |
| `source_identifier` | `TEXT`        | A link back to the source (e.g., the datalake filename, a URL).        |                    |
| `document_date`     | `TIMESTAMPTZ` | The publication date of the source document.                           | `BTREE`            |
| `content_chunk`     | `TEXT`        | The actual text that was vectorized (including the temporal prefix).   |                    |
| `embedding`         | `vector(768)` | The semantic vector representation of the `content_chunk`.             | `IVFFLAT` / `HNSW` |
| `created_at`        | `TIMESTAMPTZ` | When this vector was created in our system.                            |                    |

## V. The Plan

This mission will be executed in four atomic, verifiable sub-phases.

- **Sub-Phase 1: The Oracle's Sanctum (Build the Embedding Service)**

  1.  **Modify `infrastructure/postgres/init-db.sh`:** Remove the `CREATE TABLE dsv_embeddings` command. Add the new, correct `CREATE TABLE semantic_vectors` command and its BTREE indexes.
  2.  **Create `chorus_engine/infrastructure/services/embedding_service.py`:** Implement a new Flask application using the **App Factory Pattern**. The `SentenceTransformer` model **MUST** be loaded lazily inside the `create_app()` function to prevent deadlocks. It will expose a `/health` check and a `/embed` endpoint.
  3.  **Create `wsgi_embedder.py`:** Create the WSGI entry point for the new embedding service.
  4.  **Modify `docker-compose.dev.yml`, `docker-compose.prod.yml`, and `docker-compose.test.yml`:**
      - Add the new `chorus-embedder` service.
      - It **MUST** be configured to run with a single Gunicorn worker (`--workers=1`) to enforce the singleton process pattern.
      - Add a health check that targets the `/health` endpoint.

- **Sub-Phase 2: The Scribe's Pilgrimage (Refactor the Vectorizer)**

  1.  **Create `chorus_engine/infrastructure/daemons/vectorizer.py`:**
      - This daemon will **NOT** import `SentenceTransformer`.
      - Its `initialize_dependencies` function will wait for the `chorus-embedder` service to be healthy.
      - It **MUST** prepend the `document_date` to the text chunk before sending it for vectorization, implementing "Textual Time Encoding."
      - Its main loop will make a `requests.post` call to the `chorus-embedder`'s `/embed` endpoint to get embeddings.
  2.  **Modify `docker-compose` files:** Add the `chorus-vectorizer` service. It **MUST** include a `depends_on` condition to wait for the `chorus-embedder` service to be healthy.

- **Sub-Phase 3: The Analyst's Divination (Refactor the RAG Query Path)**

  1.  **Modify `chorus_engine/adapters/persistence/postgres_adapter.py`:**
      - Remove the `_get_embedding_model` class method and all `SentenceTransformer` logic.
      - The `query_semantic_space` method will now make a `requests.post` call to the `chorus-embedder` service to get the embedding for the user's query.
  2.  **Modify `docker-compose` files:** Add `depends_on` conditions for the `chorus-launcher` and `chorus-tester` services to wait for the `chorus-embedder` to be healthy.

- **Sub-Phase 4: The Final, Verifiable Prophecy (The Test)**
  1.  **Delete `tests/integration/test_vector_capabilities.py`:** This test is obsolete as it targets the removed prototype.
  2.  **Create `tests/integration/test_rag_pipeline.py`:** This will be the new, definitive integration test.
      - It will run in the hermetic test environment, which uses an isolated `./tests/test_datalake` volume.
      - The test fixture will create a clean, empty `test_datalake` directory and place a single, unique JSON file inside it.
      - The test will then poll the `semantic_vectors` table, asserting that the record appears within a reasonable timeout.
  3.  **Final Verification:** Execute `make test` and confirm that the entire suite, including the new integration test, passes with zero failures.

## VI. Acceptance Criteria

- **AC-1:** The `semantic_vectors` table exists in the database with the correct schema, and the old `dsv_embeddings` table is gone.
- **AC-2:** A new `chorus-embedder` service is running in all environments, passes its health check, and correctly returns vector embeddings when called.
- **AC-3:** The `chorus-vectorizer` daemon correctly prepends the date to content chunks before vectorization.
- **AC-4:** The new `test_rag_pipeline.py` test passes, proving that a file created in the isolated test datalake is successfully vectorized and stored in the database.
- **AC-5:** The `make test` command completes with 100% success.
