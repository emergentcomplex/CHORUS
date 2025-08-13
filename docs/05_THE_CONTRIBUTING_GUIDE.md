# 🔱 Contributing to CHORUS

Thank you for your interest in contributing to the CHORUS project. We are building a system of judgment, and we apply that same spirit of rigor and clarity to our own development process.

This guide provides the "happy path" for making your first contribution. Our complete, detailed development lifecycle is codified in the [🔱 The Development Protocol](./07_THE_DEVELOPMENT_PROTOCOL.md), which we encourage you to read.

## Our Philosophy: The Three Ways

Our process is built on a simple philosophy:

1.  **Create Fast Flow:** We work in small, isolated batches to get value delivered smoothly.
2.  **Amplify Feedback:** We use automation and peer review to find and fix problems early.
3.  **Learn Constantly:** We treat every task, and every failure, as a learning opportunity.

## Your First Contribution: A Step-by-Step Guide

### Step 1: Set Up Your Environment

Ensure you have a working local environment. The canonical setup guide is in our main [README.md](../README.md).

### Step 2: Begin Your Mission

All work, from a major feature to a small typo fix, is a "Mission." We use a `make` command to ensure you always start from a clean, up-to-date, and isolated branch.

```bash
# This command will create a new branch for you named `feature/fix-that-one-bug`
make mission-begin MISSION_NAME=fix-that-one-bug
```

### Step 3: Make Your Changes & Commit Atomically

Make your code or documentation changes. As you work, create **atomic commits**. An atomic commit is a small, self-contained change that represents a single logical unit of work.

Your commit messages are a critical form of communication. We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

**Good Commit Message:**

```
feat(web): add pagination to the dashboard

Implements server-side pagination for the main task list to improve
performance on systems with thousands of tasks.
```

**Bad Commit Message:**

```
made some changes
```

### Step 4: Verify Your Work

Before you ask others to review your work, you must verify it yourself. Our `Makefile` provides the single command to run the entire test suite in a clean, isolated environment, exactly as our CI server will.

```bash
# This will build, start, set up, test, and tear down the entire system.
make test
```

A passing local test suite is a prerequisite for opening a Pull Request.

### Step 5: Open a Pull Request

Once your mission is complete and verified, push your branch to GitHub and open a Pull Request (PR) against the `main` branch.

```bash
git push origin feature/fix-that-one-bug
```

In the PR description, clearly explain the "why" behind your change. What problem does it solve? Link to any relevant mission documents or issues.

### Step 6: The Review Process

Opening the PR will trigger two feedback loops:

1.  **Automated Feedback:** Our CI/CD Gatekeeper will run `make test` again to provide an objective, automated verification of your change. You will see a green checkmark or a red "X" on your PR.
2.  **Human Feedback:** At least one other team member will review your PR. They will check for correctness, clarity, and adherence to our architectural principles.

Be prepared to respond to feedback and make additional changes. To update your PR, simply commit and push to the same branch.

### Step 7: The Merge

Once your PR is approved and all checks are passing, a team member will **"Squash and Merge"** your change into the `main` branch. This combines all of your commits into a single, clean commit in the project's history.

Congratulations, you have successfully contributed to CHORUS!

---

For more advanced topics, such as our failure recovery and collaborative workflows, please see the full Standard Operating Procedures in the [🔱 The Development Protocol](./07_THE_DEVELOPMENT_PROTOCOL.md).
