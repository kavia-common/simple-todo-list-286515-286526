#!/usr/bin/env sh
set -e

APP_HOME="${APP_HOME:-/app}"
DB_DIR="${DB_DIR:-/data}"
DB_FILE="${DB_FILE:-/data/todos.db}"

# Ensure the data directory exists
mkdir -p "$DB_DIR"

# Create empty db file if not present
if [ ! -f "$DB_FILE" ]; then
  echo "Creating SQLite database at $DB_FILE"
  sqlite3 "$DB_FILE" ".databases"
fi

# Initialize schema if not already initialized
# We'll check for existence of the todos table
if ! sqlite3 "$DB_FILE" "SELECT name FROM sqlite_master WHERE type='table' AND name='todos';" | grep -q "^todos$"; then
  echo "Initializing database schema..."
  if [ -f "$APP_HOME/init_db.sql" ]; then
    sqlite3 "$DB_FILE" < "$APP_HOME/init_db.sql"
  else
    echo "Warning: init_db.sql not found; creating a minimal todos table."
    sqlite3 "$DB_FILE" "CREATE TABLE IF NOT EXISTS todos (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      completed INTEGER NOT NULL DEFAULT 0,
      created_at TEXT DEFAULT (datetime('now'))
    );"
  fi
fi

echo "Database ready at: $DB_FILE"

# Print connection helper
if [ -f "$APP_HOME/db_connection.txt" ]; then
  echo "Use this to connect inside the container:"
  cat "$APP_HOME/db_connection.txt" || true
fi

exec "$@"
