# 🔱 CHORUS: The Mission Charter

> ✨ _The loudest secrets are kept in silence. We built an engine that listens._ ✨

---

## Overview

**CHORUS** is not a search engine; it is a judgment engine. It is a fully autonomous, self-healing, and evolving intelligence platform designed to fuse disparate, open-source data verticals into high-fidelity, actionable insights.

It is not a monolith; it is a symphony of judgment. An adversarial council of AI virtuosos—Hawks, Doves, Futurists, and Skeptics—each performing their own analysis, their competing melodies forged by synthesizing Directors into a single, coherent revelation.

We do not ask for an answer. We demand a verdict, complete with every source and every dissenting note, allowing you to see the work and trust the judgment.

---

## System Architecture

The CHORUS engine is a data-intensive application built on the principles of the "Unbundled Database" and the **C4 Model** for architectural visualization.

> **For a detailed, multi-layered breakdown of the system's architecture, please see the canonical [🔱 Architectural Vision](./00_ARCHITECTURAL_VISION.md) document.**

---

## Quickstart Guide

This guide provides the definitive steps to set up and run the entire CHORUS system locally using `make` and Docker.

### Prerequisites

- **Git:** For cloning the repository.
- **Docker & Docker Compose:** For running the entire containerized environment.
- **An IDE:** For editing code on your host machine.

### 1. Initial Setup

```bash
# Clone the repository and navigate into it
git clone <your-repo-url>
cd CHORUS

# Create your personal environment file from the template
cp .env.example .env

# Open .env with your editor and add your GOOGLE_API_KEY
# nano .env
```

### 2. Build and Run the System

This single command builds the Docker images (a one-time slow operation) and starts all services in development mode.

````bash

# This command will stop, build, and start the entire stack.
make rebuild```

Subsequent starts can use the faster `make run` command.

### 3. Access the System

- **CHORUS C2 UI:** [http://localhost:5001](http://localhost:5001)
- **Redpanda Console (Kafka UI):** [http://localhost:8080](http://localhost:8080)

### 4. Shut Down the System

```bash
# Stop and remove all running containers and volumes.
make stop
````
