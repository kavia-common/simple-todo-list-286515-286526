# Lightweight SQLite database container
# This container provides a persistent sqlite database file and basic tooling.
# It ensures required directories exist at build and runtime.

FROM python:3.11-slim

# Set environment vars
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app \
    DB_DIR=/data \
    DB_FILE=/data/todos.db

# Create directories
RUN mkdir -p ${APP_HOME} ${DB_DIR}

# Install sqlite3 CLI and tini for proper signal handling
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends sqlite3 ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Copy database helper files
WORKDIR ${APP_HOME}
COPY ./db_shell.py ${APP_HOME}/db_shell.py
COPY ./init_db.sql ${APP_HOME}/init_db.sql
COPY ./db_connection.txt ${APP_HOME}/db_connection.txt

# Ensure execute permissions
RUN chmod +x ${APP_HOME}/db_shell.py

# Initialize database if it doesn't exist at build time to validate schema,
# but main creation/check is done at container start to handle mounted volumes.
RUN sqlite3 ${DB_FILE} ".databases" || true

# Healthcheck: verifies database file exists and sqlite3 can open it
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD sh -c '[ -f "$DB_FILE" ] && sqlite3 "$DB_FILE" "PRAGMA integrity_check;" | grep -qi "ok" || exit 1'

# Expose volume for persistence
VOLUME ["${DB_DIR}"]

# Entrypoint script ensures directories exist and schema is initialized
COPY ./entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["sleep", "infinity"]
