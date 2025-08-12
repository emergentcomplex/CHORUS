# Idea 00: Implement the System Health & Integrity Validation Suite

**1. Concept:**
Create a single, powerful diagnostic script that acts as a "pre-flight check" for the entire CHORUS repository. This tool will perform a **"Two-Source Reconciliation,"** comparing the architectural intent defined in our Constitution against the ground truth of the Git repository to provide a definitive, automated assessment of the project's health.

**2. Problem Solved:**

- **Architectural Drift:** Ensures the actual file structure never drifts out of sync with the master plan.
- **Code Rot & Orphan Files:** Automatically detects any file that has been added to the repository but has not been formally documented in the Constitution.
- **Broken Dependencies:** Catches broken Python `import` statements before the code is ever run.

**3. Proposed Solution:**

- **A. The New Script:**

  - Create a new file at `tools/diagnostics/validate_environment.py`.

- **B. The "Two-Source Reconciliation" Logic:**

  - The script will generate two lists in memory:
    1.  **The "Constitutional" List:** By parsing the File Manifest in `/docs/01_CONSTITUTION.md`.
    2.  **The "Repository" List:** By executing the `git ls-files` command to get a definitive list of all tracked files.
  - It will then perform a diff between these two lists to pass or fail the **"Constitutional Alignment Check"** (for missing files) and the **"Orphan File Detection"** check.

- **C. Additional Checks:**

  - **Dependency Integrity Check:** It will perform a static analysis of all Python files to validate their internal `import` statements.
  - **Environment Sanity Check:** It will validate the `.env` file and the database connection.

- **D. The Output:**
  - A clear, color-coded terminal report with a `[PASS]` or `[FAIL]` for each check, ending in a definitive statement of system readiness.

**4. Next Steps:**

- **Priority:** **Highest.** This is the very first thing we must build.
- **Implementation:**
  1.  Create the `tools/diagnostics/validate_environment.py` script with the two-source reconciliation logic.
  2.  Add a `make validate` command to our `Makefile`.
  3.  Update `/docs/02_CONTRIBUTING.md` to instruct developers to run `make validate` as their first step.
