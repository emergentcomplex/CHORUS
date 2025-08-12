Praxis: The Mandate of Environmental Stability
Objective

To restore the integrity of the CHORUS verification suite by resolving the psycopg2.errors.ObjectInUse failure with the most minimal, non-destructive change possible. This mission will preserve the existing Docker and Compose configurations, focusing solely on correcting the logical conflict in the test setup. It will also establish a formal debriefing template for all future missions.
Justification

The root cause of the test failure is a lifecycle conflict. The docker-compose.test.yml environment correctly creates an ephemeral trident_analysis_test database for the test run. However, the tests/conftest.py fixture then also attempts to manage this database's lifecycle by issuing a DROP DATABASE command. This command fails because the Debezium service (kafka-connect), which is part of the test environment, has already connected to the database and established a logical replication slot. PostgreSQL correctly prevents the database from being dropped while it is in use.

This is a violation of Axiom 71 (Hermetic Verification), which dictates that the test harness (make test) is responsible for the entire lifecycle of its environment. The conftest.py fixture should not be managing infrastructure; it should only be concerned with test setup within the provided environment.

The solution is to remove the redundant and conflicting infrastructure management logic from conftest.py, allowing it to work in harmony with the Docker-managed environment, not against it.
The Plan

    Subphase 1.1 (The Precise Correction):

        Task: Modify the setup_test_database fixture in tests/conftest.py to remove all database creation and destruction logic.

        Implementation: The fixture will be simplified to perform a single function: wait for the Docker-provisioned test database to become available. The responsibility for creating and destroying the database and its volumes remains entirely with the make test command and docker-compose. This is the least destructive and most constitutionally-aligned fix.

        File(s) to Modify: tests/conftest.py.

    Subphase 1.2 (The Constitutional CI/CD Gatekeeper):

        Task: Implement the automated CI/CD pipeline. This is an additive change that does not modify existing code.

        Implementation: Create a new GitHub Actions workflow at .github/workflows/ci_cd.yml. This workflow will trigger on every pull request and run the full, hermetic make test command, which will now be functional.

        File(s) to Create: .github/workflows/ci_cd.yml.

    Subphase 1.3 (The Mission Debrief Protocol):

        Task: Establish a formal debriefing protocol to institutionalize learning, as requested.

        Implementation: Create a new, reusable mission debriefing template. This template will be used at the conclusion of every mission to document outcomes, successes, failures, and new lessons learned, providing a structured input for future updates to The Graveyard.

        File(s) to Create: docs/templates/DEBRIEF_TEMPLATE.md.

Definition of Done

    The make test command completes the entire test suite successfully, with no psycopg2.errors.ObjectInUse errors.

    The make run command for the local development environment remains fully functional and unaffected by the changes.

    The new CI/CD workflow file is created at .github/workflows/ci_cd.yml.

    A new mission debriefing template is created at docs/templates/DEBRIEF_TEMPLATE.md.