# Filename: Dockerfile
# 🔱 CHORUS Application Image (v3 - Correct Cache Permissions)

FROM chorus-base:latest

# 1. Set up the environment and non-root user.
WORKDIR /app
RUN useradd -m appuser

# 2. Create mount points and set ownership *before* copying.
RUN mkdir -p /app/datalake /app/logs /app/.pytest_cache && \
    chown -R appuser:appuser /app

# 3. Switch to the non-root user *before* copying and installing.
USER appuser

# 4. Copy the application source code as the non-root user.
COPY --chown=appuser:appuser . .

# 5. Install the application itself into the existing environment.
RUN pip install --no-cache-dir --no-deps .

# THE DEFINITIVE FIX (PART 2): Ensure the cache directory exists and is owned by appuser.
# This command runs as appuser, guaranteeing correct permissions.
RUN mkdir -p /app/.pytest_cache

# The default command is set in docker-compose.