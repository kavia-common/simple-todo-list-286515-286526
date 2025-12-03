#!/usr/bin/env python3
"""Initialize SQLite database for database.

This script creates the SQLite database file if missing, ensures base tables
exist, and adds an idempotent 'todos' table used by the app's backend.

Tables:
- app_info(id, key UNIQUE, value, created_at)
- users(id, username UNIQUE, email UNIQUE, created_at) [sample table]
- todos(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    is_completed INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
  )

Indexes/Triggers:
- idx_todos_is_completed on todos(is_completed)
- Trigger todos_set_updated_at: sets updated_at to CURRENT_TIMESTAMP on UPDATE

Seeding:
- Seeds a few example todos if the todos table is empty.

This script is idempotent; running it multiple times is safe.
"""

import sqlite3
import os

DB_NAME = "myapp.db"
DB_USER = "kaviasqlite"  # Not used for SQLite, but kept for consistency
DB_PASSWORD = "kaviadefaultpassword"  # Not used for SQLite, but kept for consistency
DB_PORT = "5000"  # Not used for SQLite, but kept for consistency

print("Starting SQLite setup...")

# Check if database already exists
db_exists = os.path.exists(DB_NAME)
if db_exists:
    print(f"SQLite database already exists at {DB_NAME}")
    # Verify it's accessible
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.execute("SELECT 1")
        conn.close()
        print("Database is accessible and working.")
    except Exception as e:
        print(f"Warning: Database exists but may be corrupted: {e}")
else:
    print("Creating new SQLite database...")

# Create database with sample tables
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Make sure foreign keys are enabled for the session
cursor.execute("PRAGMA foreign_keys = ON")

# Create initial schema
cursor.execute("""
    CREATE TABLE IF NOT EXISTS app_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE NOT NULL,
        value TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Create a sample users table as an example
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Create todos table (idempotent)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS todos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        is_completed INTEGER NOT NULL DEFAULT 0, -- 0 = false, 1 = true
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP
    )
""")

# Index to speed up filtering by completion
cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_todos_is_completed
    ON todos(is_completed)
""")

# Optional trigger to automatically set updated_at on updates
# Note: SQLite triggers cannot be created with IF NOT EXISTS until 3.35+, so we emulate idempotency
# by checking the sqlite_master for an existing trigger.
cursor.execute("""
    SELECT name FROM sqlite_master
    WHERE type = 'trigger' AND name = 'todos_set_updated_at'
""")
trigger_exists = cursor.fetchone() is not None

if not trigger_exists:
    cursor.execute("""
        CREATE TRIGGER todos_set_updated_at
        AFTER UPDATE ON todos
        FOR EACH ROW
        BEGIN
            UPDATE todos
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = NEW.id;
        END;
    """)

# Insert initial app_info data (idempotent upserts)
cursor.execute("INSERT OR REPLACE INTO app_info (key, value) VALUES (?, ?)",
               ("project_name", "database"))
cursor.execute("INSERT OR REPLACE INTO app_info (key, value) VALUES (?, ?)",
               ("version", "0.1.0"))
cursor.execute("INSERT OR REPLACE INTO app_info (key, value) VALUES (?, ?)",
               ("author", "John Doe"))
cursor.execute("INSERT OR REPLACE INTO app_info (key, value) VALUES (?, ?)",
               ("description", ""))

# Seed sample todos if none exist
cursor.execute("SELECT COUNT(*) FROM todos")
todo_count = cursor.fetchone()[0]
if todo_count == 0:
    sample_todos = [
        ("Set up project", "Initialize repository and basic structure", 1),
        ("Build backend", "Implement FastAPI endpoints for todos", 0),
        ("Create frontend", "Build React UI for managing tasks", 0),
        ("Write tests", "Add unit/integration tests", 0)
    ]
    for title, description, is_completed in sample_todos:
        cursor.execute(
            "INSERT INTO todos (title, description, is_completed) VALUES (?, ?, ?)",
            (title, description, is_completed)
        )

# Finalize changes for schema and seeds
conn.commit()

# Get database statistics
cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
table_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM app_info")
record_count = cursor.fetchone()[0]

# Get todo statistics
cursor.execute("SELECT COUNT(*) FROM todos")
todo_total = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM todos WHERE is_completed = 1")
todo_completed = cursor.fetchone()[0]

# Cleanly close connection
conn.close()

# Save connection information to a file
current_dir = os.getcwd()
connection_string = f"sqlite:///{current_dir}/{DB_NAME}"

try:
    with open("db_connection.txt", "w") as f:
        f.write(f"# SQLite connection methods:\n")
        f.write(f"# Python: sqlite3.connect('{DB_NAME}')\n")
        f.write(f"# Connection string: {connection_string}\n")
        f.write(f"# File path: {current_dir}/{DB_NAME}\n")
    print("Connection information saved to db_connection.txt")
except Exception as e:
    print(f"Warning: Could not save connection info: {e}")

# Create environment variables file for Node.js viewer
db_path = os.path.abspath(DB_NAME)

# Ensure db_visualizer directory exists
if not os.path.exists("db_visualizer"):
    os.makedirs("db_visualizer", exist_ok=True)
    print("Created db_visualizer directory")

try:
    with open("db_visualizer/sqlite.env", "w") as f:
        f.write(f"export SQLITE_DB=\"{db_path}\"\n")
    print(f"Environment variables saved to db_visualizer/sqlite.env")
except Exception as e:
    print(f"Warning: Could not save environment variables: {e}")

print("\nSQLite setup complete!")
print(f"Database: {DB_NAME}")
print(f"Location: {current_dir}/{DB_NAME}")
print("")

print("To use with Node.js viewer, run: source db_visualizer/sqlite.env")

print("\nTo connect to the database, use one of the following methods:")
print(f"1. Python: sqlite3.connect('{DB_NAME}')")
print(f"2. Connection string: {connection_string}")
print(f"3. Direct file access: {current_dir}/{DB_NAME}")
print("")

print("Database statistics:")
print(f"  Tables: {table_count}")
print(f"  App info records: {record_count}")
print(f"  Todos: total={todo_total}, completed={todo_completed}")

# If sqlite3 CLI is available, show how to use it
try:
    import subprocess
    result = subprocess.run(['which', 'sqlite3'], capture_output=True, text=True)
    if result.returncode == 0:
        print("")
        print("SQLite CLI is available. You can also use:")
        print(f"  sqlite3 {DB_NAME}")
except Exception:
    pass

# Exit successfully
print("\nScript completed successfully.")
