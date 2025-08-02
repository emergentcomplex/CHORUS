# 🔱 CHORUS Dockerfile (v13 - The Final, Lean, Multi-Stage Build)

# --- Stage 1: The "Builder" Stage ---
# This stage installs all dependencies, including test tools. It is the
# base for our development and testing environments.
FROM python:3.12-slim as builder

# 1. Install system dependencies.
RUN apt-get update && apt-get install -y make postgresql-client curl && \
    rm -rf /var/lib/apt/lists/*

# 2. Set up the environment.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app

# 3. Install uv.
RUN pip install uv

# 4. Copy dependency definitions.
COPY pyproject.toml uv.lock setup.py ./

# 5. THE DEFINITIVE FIX FOR BLOAT: Install CPU-only torch.
RUN uv pip install --system torch --extra-index-url https://download.pytorch.org/whl/cpu

# 6. Install all other dependencies. uv will see torch is installed and skip it.
RUN uv pip install --system .

# 7. Copy the entire application and test source.
COPY . .

# 8. Install the application in editable mode.
RUN uv pip install --system -e .

# --- Stage 2: The "Production" Stage ---
# This stage creates the final, lean image by copying ONLY what is needed
# to RUN the application from the builder stage.
FROM python:3.12-slim as production

# 1. Set up the environment and non-root user.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app
RUN useradd -m appuser

# 2. Copy the installed Python packages from the builder stage.
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 3. Copy ONLY the application source code from the builder stage.
COPY --from=builder /app/chorus_engine ./chorus_engine
COPY --from=builder /app/setup.py .
COPY --from=builder /app/pyproject.toml .

# 4. Re-run the editable install to create the necessary links.
RUN pip install -e .

# 5. Set ownership and switch to the non-root user.
RUN chown -R appuser:appuser /app
USER appuser

CMD ["sleep", "infinity"]
