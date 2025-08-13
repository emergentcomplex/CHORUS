# Filename: Dockerfile
# 🔱 CHORUS Application Image (v5 - Final Datalake Permissions)

FROM chorus-base:latest

# 1. Set up the environment and non-root user.
WORKDIR /app
RUN useradd -m appuser

# 2. Create mount points and set ownership *before* copying.
RUN mkdir -p /app/datalake /app/logs /app/.pytest_cache && \
    chown -R appuser:appuser /app

# THE DEFINITIVE FIX: Make the datalake directory world-writable.
# This ensures that the non-root appuser inside the container can write to
# the volume mounted from the host, regardless of the host user's UID.
RUN chmod 777 /app/datalake

# 3. Switch to the non-root user *before* copying and installing.
USER appuser

# 4. Copy the application source code as the non-root user.
COPY --chown=appuser:appuser . .

# 5. Install the application itself into the existing environment.
RUN pip install --no-cache-dir --no-deps .

# 6. Ensure the cache directory exists and is owned by appuser.
RUN mkdir -p /app/.pytest_cache

# The default command is set in docker-compose.