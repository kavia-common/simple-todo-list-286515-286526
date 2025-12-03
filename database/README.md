# Database Container (SQLite)

This container provides a persistent SQLite database for the todo application.

Key points:
- Ensures `/data` directory exists at build and runtime.
- Initializes the database file `/data/todos.db` if missing.
- Applies schema from `init_db.sql` on first run (or creates a minimal table if missing).
- Exposes a healthcheck that verifies DB integrity.

## Build

From the repository root:

```
docker build -t todo-sqlite:latest -f simple-todo-list-286515-286526/database/Dockerfile simple-todo-list-286515-286526/database
```

## Run

```
docker run --name todo-db -d \
  -v $(pwd)/.dbdata:/data \
  todo-sqlite:latest
```

This mounts a host directory for persistence. The entrypoint will create `/data` and the DB file if missing.

## Connect inside the container

```
docker exec -it todo-db sh
# Using sqlite3
sqlite3 /data/todos.db
# Or using helper
python /app/db_shell.py -c "SELECT name FROM sqlite_master WHERE type='table';"
```

See `db_connection.txt` for quick snippets.

## Notes

- If you see build errors regarding missing directories, this setup explicitly creates `/data` both at build time and on container start.
- The backend should reference the database path via environment variable `DB_FILE=/data/todos.db` (configure in its container/env).
