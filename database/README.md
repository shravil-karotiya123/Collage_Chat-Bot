# Database Directory (`database/`)

## Purpose
The `database/` directory holds persistent local relational databases (e.g. SQLite database files, schema migrations, and audit logs).

## Storage Policy
- **Local Persistence**: Stores task state, model execution logs, and workflow history off-grid.
- **Git Ignored**: Data contents are ignored by `.gitignore`.
