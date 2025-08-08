# Filename: Dockerfile
# 🔱 CHORUS Application Image (Correct Permissions)

FROM chorus-base:latest

# 1. Set up the environment and non-root user.
WORKDIR /app
RUN useradd -m appuser

# 2. THE DEFINITIVE FIX: Create mount points and set ownership *before* copying.
# This ensures that even when volumes are mounted, the base directories are owned by appuser.
RUN mkdir -p /app/datalake /app/logs /app/.pytest_cache && \
    chown -R appuser:appuser /app

# 3. Switch to the non-root user *before* copying and installing.
USER appuser

# 4. Copy the application source code as the non-root user.
COPY --chown=appuser:appuser . .

# 5. Install the application itself into the existing environment.
RUN pip install --no-cache-dir --no-deps .

# The default command is inherited from the base image or set in docker-compose.