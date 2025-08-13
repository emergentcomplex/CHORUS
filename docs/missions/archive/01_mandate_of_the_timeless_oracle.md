# 🔱 Praxis: The Mandate of the Timeless Oracle

## I. Objective

To evolve the CHORUS RAG pipeline into a fully time-vector-fused system, enabling explicit, weighted temporal searches. This mission will introduce a "Query Transformer" layer, allowing an LLM to dynamically control the balance between semantic and temporal relevance based on the user's intent, dramatically increasing the engine's analytical precision.

## II. Background & Justification

The "Mandate of the Oracle" established a stable, time-aware RAG pipeline using "Textual Time Encoding." While effective, this method lacks explicit control over the importance of time in a given search.

This mandate implements the more advanced **"Time-Vector Fusion"** pattern. By representing time as a mathematical vector and fusing it with the semantic vector, we can perform nuanced, weighted searches. This allows the engine to distinguish between a query for "the history of quantum computing" (low time weight) and "recent advances in quantum computing" (high time weight), a capability critical for high-fidelity analysis.

## III. The Architectural Decree (The Schema Change)

This mission requires a formal evolution of our core semantic schema. The `embedding` column will be widened to accommodate a fused time-vector.

**Proposed `semantic_vectors` Schema v2.0:**

| Column Name | Data Type     | Description                                                                              |
| :---------- | :------------ | :--------------------------------------------------------------------------------------- |
| `embedding` | `vector(770)` | The fused vector: 768 dimensions for semantics, 2 for time (e.g., sine/cosine encoding). |
| ...         | ...           | _(all other columns remain the same)_                                                    |

## IV. The Plan

- **Sub-Phase 1: Schema Migration & Re-Vectorization**

  1.  **Modify `infrastructure/postgres/init-db.sh`:** Update the `CREATE TABLE semantic_vectors` command to use `vector(770)`.
  2.  **Create Migration Script:** Develop a standalone script to read all records from the old table, re-calculate their fused embeddings, and insert them into the new table. This ensures a seamless upgrade.

- **Sub-Phase 2: The Timeless Scribe**

  1.  **Modify `chorus-embedder`:** It will remain unchanged, continuing to provide pure 768-dim text vectors.
  2.  **Modify `vectorizer.py`:**
      - It will now be responsible for calculating the time-vector. This involves normalizing the `document_date` (e.g., to a value between 0 and 1) and encoding it (e.g., using sine/cosine functions to preserve cyclicality).
      - It will then concatenate the text-vector received from the embedder with its calculated time-vector before saving the new 770-dim vector to the database.

- **Sub-Phase 3: The Weighted Query**

  1.  **Modify `PostgresAdapter.query_semantic_space`:**
      - The method signature will be updated to accept a new `time_weight` parameter (a float, e.g., 0.0 to 1.0).
      - The underlying SQL query will be rewritten to perform a weighted distance calculation, applying the `time_weight` to the temporal dimensions of the vector during the similarity search.

- **Sub-Phase 4: The Query Transformer**

  1.  **Create New Use Case/Service:** Develop a `QueryTransformer` component.
  2.  **LLM-driven Weighting:** This component will take the user's raw query (e.g., "what's new in...") and use a fast, utility-tier LLM to analyze its temporal intent.
  3.  **Structured Output:** The LLM will output a JSON object containing the original query and a calculated `time_weight`.
  4.  **Integration:** The `RunAnalystTier` use case will first call the `QueryTransformer` before calling the `PostgresAdapter`, passing the dynamically generated weight to the search.

- **Sub-Phase 5: Verification**
  1.  **Create New Integration Tests:** Develop specific tests to prove that providing a high `time_weight` correctly prioritizes more recent documents in the search results, even if they are slightly less semantically similar.

## V. Acceptance Criteria

- **AC-1:** The `semantic_vectors` table schema is successfully migrated to use a `vector(770)` column.
- **AC-2:** The `vectorizer` daemon correctly generates and stores fused time-semantic vectors.
- **AC-3:** The `PostgresAdapter` can successfully perform a weighted vector search based on a `time_weight` parameter.
- **AC-4:** The new `QueryTransformer` can successfully analyze a user query and generate a temporal weight.
- **AC-5:** The end-to-end system correctly prioritizes recent documents for time-sensitive queries, as proven by new integration tests.
