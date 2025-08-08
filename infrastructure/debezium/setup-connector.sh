# Filename: infrastructure/debezium/setup-connector.sh
#!/bin/sh
# The final, robust, and idempotent Debezium connector setup script.

set -e

CONNECTOR_NAME="chorus-postgres-connector"
CONNECT_URL="http://kafka-connect:8083"
PG_HOST="postgres"
PG_PORT="5432"

echo "--- Debezium Connector Setup ---"

# 1. Wait for the PostgreSQL database to be truly ready.
# This loop repeatedly tries to connect to the database using psql.
# It will not proceed until the connection is successful, preventing race conditions.
echo "Waiting for PostgreSQL at ${PG_HOST}:${PG_PORT} to be fully initialized..."
ATTEMPTS=0
MAX_ATTEMPTS=24 # 2 minutes timeout (24 * 5s)
until PGPASSWORD=$DB_PASSWORD psql -h "$PG_HOST" -p "$PG_PORT" -U "$DB_USER" -d "$DB_NAME" -c '\q' > /dev/null 2>&1; do
    ATTEMPTS=$((ATTEMPTS+1))
    if [ ${ATTEMPTS} -gt ${MAX_ATTEMPTS} ]; then
        echo "FATAL: PostgreSQL did not become available after ${MAX_ATTEMPTS} attempts."
        exit 1
    fi
    printf '.'
    sleep 5
done
echo "\nPostgreSQL is ready."

# 2. Wait for the Kafka Connect API to be responsive.
echo "Waiting for Kafka Connect REST API at ${CONNECT_URL}..."
until $(curl --output /dev/null --silent --head --fail ${CONNECT_URL}/connectors); do
    printf '.'
    sleep 5
done
echo "\nKafka Connect REST API is up."

# 3. Build the connector configuration from the template.
# This makes the script reusable across different environments (dev, prod, test).
echo "Building connector configuration for database: ${DB_NAME}"
sed -e "s/\${DB_USER}/${DB_USER}/g" \
    -e "s/\${DB_PASSWORD}/${DB_PASSWORD}/g" \
    -e "s/\${DB_NAME}/${DB_NAME}/g" \
    /tmp/register-postgres-connector.json.template > /tmp/connector.json

# 4. Register the connector using a PUT request, which is idempotent.
# If the connector exists, its config is updated. If not, it's created.
echo "Registering/updating connector '${CONNECTOR_NAME}'..."
curl -X PUT -H "Content-Type: application/json" \
    --data "$(cat /tmp/connector.json)" \
    ${CONNECT_URL}/connectors/${CONNECTOR_NAME}/config

# 5. Poll for the connector's status to confirm it is RUNNING.
echo "\nPolling for connector status..."
until [ "$(curl -s -o /dev/null -w '%{http_code}' ${CONNECT_URL}/connectors/${CONNECTOR_NAME}/status)" -eq 200 ]; do
    printf '.'
    sleep 2
done

STATUS_JSON=$(curl --silent ${CONNECT_URL}/connectors/${CONNECTOR_NAME}/status)
if echo "${STATUS_JSON}" | grep -q '"state":"RUNNING"' && \
   ! echo "${STATUS_JSON}" | grep -q '"state":"FAILED"'; then
    echo "\n✅ SUCCESS: Debezium connector '${CONNECTOR_NAME}' is RUNNING."
    exit 0
else
    echo "\n❌ FAILURE: Debezium connector entered a FAILED state."
    echo "--- Connector Status ---"
    echo "${STATUS_JSON}"
    echo "------------------------"
    exit 1
fi