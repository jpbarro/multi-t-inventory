# 🐘 Database Migrations Guide (Alembic)

This project uses **Alembic** to manage database schema changes (creating tables, adding columns, etc.) for the main application database.

> **Note on Testing:** You do NOT need to run migrations for the `test_db`. The test suite automatically creates and drops the schema on every run using `conftest.py`.

## 🚀 Quick Cheat Sheet

| Goal | Command |
| :--- | :--- |
| **Create a new migration** | `alembic revision --autogenerate -m "message"` |
| **Apply all pending migrations** | `alembic upgrade head` |
| **Undo the last migration** | `alembic downgrade -1` |
| **View migration history** | `alembic history` |
| **Reset DB to empty** | `alembic downgrade base` |