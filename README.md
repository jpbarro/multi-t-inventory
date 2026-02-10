# multi-t-inventory

Monorepo with backend (FastAPI) and frontend in the same repository.

## Structure

- **backend/** – FastAPI API
- **frontend/** – Frontend app (to be added)

## Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

API docs: http://127.0.0.1:8000/docs

## Frontend

See `frontend/README.md` when added.
