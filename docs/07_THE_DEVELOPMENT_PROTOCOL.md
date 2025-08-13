# 🔱 The CHORUS Development Protocol

_Document Version: 5.0 (The Mandate of Codification)_
_Last Updated: 2025-08-13_

---

## Part 1: The Philosophy of Flow

> ✨ _"The goal of software architecture is to minimize the human resources required to build and maintain the required system."_ - Robert C. Martin

> ✨ _"Improving daily work is even more important than doing daily work."_ - Gene Kim, The Phoenix Project

This document codifies the complete System Lifecycle Protocol for the CHORUS project. It is the synthesis of wisdom from our foundational texts: _Accelerate_, _The Phoenix Project_, _Pro Git_, and _Team Topologies_. Our protocol is not a rigid set of rules but a framework for achieving a state of fast, sustainable, and predictable **flow**.

This protocol is built upon three core philosophies, known as **The Three Ways**:

1.  **The First Way: Systems Thinking.** We optimize for the performance of the entire system, not the output of individual silos. Our goal is a fast, smooth, and uninterrupted flow of work from mission conception to verified deployment.
2.  **The Second Way: Amplify Feedback Loops.** We create fast, constant feedback at every stage of the process. This includes automated testing, peer review, and blameless post-mortems. The goal is to find and fix problems at the source, where the cost is lowest.
3.  **The Third Way: A Culture of Continual Learning.** We foster a high-trust environment that encourages experimentation, risk-taking, and learning from failure. We understand that mastery is the result of practice and repetition, and we institutionalize the process of improvement.

---

## Part 2: The Four Measures of Success

Our performance is not measured by activity, but by outcomes. We track the four key metrics defined in _Accelerate_ as the definitive indicators of our development health.

| Metric                    | Definition                                                           | Target        | Rationale                                                              |
| ------------------------- | -------------------------------------------------------------------- | ------------- | ---------------------------------------------------------------------- |
| **Lead Time for Changes** | The time from a commit on `main` to that code running in production. | **< 1 day**   | Measures our overall process efficiency and deployment automation.     |
| **Deployment Frequency**  | How often we deploy to production.                                   | **On-demand** | Measures our ability to deliver value in small, safe batches.          |
| **Mean Time to Restore**  | The time it takes to restore service after a production failure.     | **< 1 hour**  | Measures our system's resilience and our ability to debug effectively. |
| **Change Failure Rate**   | The percentage of deployments that cause a failure in production.    | **< 15%**     | Measures the quality and stability of our development process.         |

---

## Part 3: The Team Structure

We are a single, **Stream-Aligned Team** with end-to-end ownership of the CHORUS engine. Our mission is to deliver a continuous stream of value to our users.

- **Cognitive Load:** Our primary architectural goal is to limit the cognitive load on the team. We achieve this by creating a strong internal **Platform** (our `Makefile` and CI/CD pipeline) that provides self-service capabilities for testing and deployment.
- **Interaction Modes:**
  - Our default interaction mode is **X-as-a-Service**, where we consume our own platform to accelerate our work.
  - When tackling a new, complex problem, we temporarily adopt a **Collaboration** mode, working closely together to define the solution before returning to the service-based model.

---

## Part 4: The Mission Lifecycle Protocol

All work is organized into discrete, verifiable **Missions**. A mission is a single, logical unit of work that results in a valuable change to the system.

### The Four Types of Work

We recognize and manage four distinct types of work, making them visible on our project Kanban board:

1.  **Mission Work (Business Projects):** The primary, value-creating features defined in our `docs/missions/` directory.
2.  **Forge Work (Internal Projects):** Improvements to our own development tools and infrastructure (e.g., upgrading the CI/CD pipeline).
3.  **Maintenance (Changes):** Small, routine updates and dependency management.
4.  **Unplanned Work (Recovery):** Bug fixes and incident response. A primary goal of this protocol is to minimize this category of work by building quality in from the start.

### The Git Workflow: Topic Branches and Atomic Commits

Our Git strategy is designed for clarity, stability, and easy debugging.

1.  **Main is the Source of Truth:** The `main` branch is always stable, deployable, and represents the verified ground truth of the project. Direct commits to `main` are forbidden.
2.  **Topic Branches:** All work, without exception, is done on short-lived topic branches (e.g., `feature/mandate-of-the-forge`, `bugfix/fix-ui-rendering`). A branch should not live for more than a few days.
3.  **Atomic Commits:** A commit is the smallest unit of progress. Each commit must represent a single, complete, logical change. It must pass all relevant tests.
4.  **Pull Requests & Peer Review:** When a mission is complete, a Pull Request (PR) is opened to merge the topic branch into `main`. This PR is the formal mechanism for peer review and triggers our automated CI/CD Gatekeeper.
5.  **Squash and Merge:** To maintain a clean, understandable history on `main`, all commits from a topic branch are squashed into a single, meaningful commit upon merging the PR.

### The Commit Message Convention

All commit messages MUST adhere to the Conventional Commits specification. This provides a clear and machine-readable history.

```
<type>[optional scope]: <description>

[optional body]

[optional footer]
```

**Example:**

```
feat(forge): implement mission lifecycle toolkit

Implement the full suite of scripts in `tools/forge` to manage
the mission lifecycle, including begin, succeed, and fail states.
This fulfills the requirements of the Mandate of the Forge.

Resolves: #42
```

---

## Part 5: The Change Approval Process

We do not use a heavyweight, external Change Advisory Board (CAB). Our change approval process is lightweight, automated, and based on peer review. A change is approved if and only if:

1.  It is submitted via a Pull Request from a topic branch.
2.  It passes all automated checks in the CI/CD Gatekeeper pipeline.
3.  It is reviewed and approved by at least one other team member.

---

## Part 6: The Protocol in Action (Standard Operating Procedures)

This section serves as the canonical, detailed guide to our development workflow. It translates the principles above into concrete actions for common and edge-case scenarios.

### 6.1 The Core Mission Workflow (The "Happy Path")

This is the standard lifecycle for any new feature, bugfix, or documentation change.

1.  **Begin the Mission:** To start any new work, use the `make mission-begin` command. This ensures you are starting from the latest version of `main` and creates an isolated topic branch for your work.

    ```bash
    make mission-begin MISSION_NAME=your-mission-name
    ```

2.  **Craft Atomic Commits:** As you work, make small, logical commits. Use `git add -p` to stage specific changes and write clear, conventional commit messages. This practice is the foundation of a clean and debuggable project history. Before pushing, consider using `git rebase -i main` to clean up and squash intermediate "WIP" commits into a single, coherent history.

3.  **Propose the Change:** Once your work is complete and passes the local `make test` suite, push your branch to the remote repository and open a Pull Request (PR) on GitHub. This action formally transitions the mission state to `PENDING_REVIEW` and triggers our automated CI/CD Gatekeeper.

4.  **Merge the Verified Work:** After the PR has been approved by a peer and all CI checks are green, the final step is to merge. Use the **"Squash and Merge"** option in the GitHub UI. This integrates your entire feature as a single, atomic commit on the `main` branch, keeping the project history clean and high-level. After merging, delete the topic branch.

### 6.2 The Collaborative Workflow

When two or more developers need to work on the same mission, the remote topic branch becomes the shared point of integration.

1.  **Initial Push:** The first developer begins the mission as normal and pushes the initial branch to GitHub.
2.  **Joining the Work:** The second developer fetches the remote branch (`git fetch origin && git checkout feature/shared-mission-name`).
3.  **Syncing Work:** Developers use `git pull` and `git push` on the topic branch to share updates with each other. It is best practice to communicate frequently to avoid conflicts.

### 6.3 The Failure & Recovery Workflow

This workflow details how to handle common problems and regressions, prioritizing system stability and fast recovery.

1.  **Handling a Stale Branch:** If `main` has been updated while you were working on your topic branch, you must re-sync your branch _before_ opening a PR. The standard method is to use `rebase`:

    ```bash
    # Get the latest changes from main
    git checkout main
    git pull origin main

    # Re-apply your work on top of the latest main
    git checkout your-topic-branch
    git rebase main
    ```

2.  **Responding to a CI/CD Failure:** If your PR fails the automated tests, click "Details" on the failed check to view the logs. Fix the issue locally, and then amend your last commit (`git commit --amend`). Force-push the corrected branch (`git push --force-with-lease origin your-topic-branch`) to update the PR and re-run the tests.

3.  **Reverting a Faulty Merge (Emergency Undo):** If a change merged to `main` is found to be critically flawed, the fastest and safest recovery is to revert it.

    - Identify the faulty merge commit hash from the `main` branch history.
    - Execute `git revert <commit-hash>`. This creates a _new_ commit that inverts the changes.
    - Push this new revert commit through the standard PR process. This maintains a clean, auditable history of the event.

4.  **Finding a Regression with `git bisect`:** If `main` is broken but the cause is unclear, use `git bisect` to perform a binary search on the commit history. This tool will rapidly identify the exact commit that introduced the failure, which is only possible because we make atomic commits.

5.  **Abandoning a Flawed Mission:** If a mission is deemed unviable during review, close the PR on GitHub without merging and delete the branch. Use the `make mission-fail` command to log the `ABANDONED` state in our mission ledger. This makes failure a safe, visible, and auditable part of the learning process.

### 6.4 The Governance Workflow

Our process governs itself. Changes to our foundational documents follow the same workflow as code changes.

1.  **Proposing an Amendment:** To change the Constitution or this Development Protocol, begin a mission and open a PR with your proposed changes to the documentation.
2.  **Review and Ratification:** The change is subject to the same peer review and discussion as any code feature. Merging the PR signifies the ratification of the amendment.
