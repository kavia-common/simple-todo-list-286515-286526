#!/usr/bin/env python3
"""
PUBLIC_INTERFACE
db_shell.py: A minimal SQLite shell helper for executing single SQL statements against the todos.db.

Usage:
  python db_shell.py -c "SQL_STATEMENT"
Environment:
  - DB_FILE: path to the sqlite database file (default: /data/todos.db)

This helper is intentionally simple to adhere to the sqlite_app rule of single-statement executions.
"""
import argparse
import os
import sqlite3
import sys

# PUBLIC_INTERFACE
def main():
    """Entry point: executes a single SQL command and prints results."""
    parser = argparse.ArgumentParser(description="Execute a single SQL statement against the SQLite database.")
    parser.add_argument("-c", "--command", dest="command", required=True, help="SQL statement to execute (single statement)")
    args = parser.parse_args()

    db_file = os.environ.get("DB_FILE", "/data/todos.db")
    # Ensure directory exists
    os.makedirs(os.path.dirname(db_file), exist_ok=True)

    try:
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()
        cur.execute(args.command)
        rows = cur.fetchall()
        conn.commit()
        for row in rows:
            print("\t".join([str(col) for col in row]))
    except sqlite3.Error as e:
        print(f"SQLite error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        try:
            conn.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()
