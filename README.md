# Getting Started

## Prerequisites

- Docker and Docker Compose
- Python 3.13+ (for local development / running tests)

## 1. Configure environment variables

Copy the example env file and adjust values if needed:

```bash
cp backend/.env.example backend/.env
```

The defaults work out of the box for local development:

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_USER` | `postgres` | PostgreSQL username |
| `POSTGRES_PASSWORD` | `password` | PostgreSQL password |
| `POSTGRES_DB` | `app_db` | Main database name |
| `DATABASE_URL` | `postgresql+asyncpg://postgres:password@localhost:5432/app_db` | SQLAlchemy connection string |
| `SECRET_KEY` | `change-me-to-a-random-secret` | Key used to sign JWT tokens |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | JWT token lifetime in minutes |

> When running via Docker Compose, the `DATABASE_URL` host is automatically
> overridden to `db` (the Docker service name) — you don't need to change it.

## 2. Start the services

```bash
docker compose up -d
```

This starts:

| Service | Port | Description |
|---------|------|-------------|
| **db** | 5432 | PostgreSQL 15 (creates `app_db` and `test_db`) |
| **api** | 8000 | FastAPI backend with hot-reload |
| **web** | 3000 | Next.js frontend with hot-reload |

## 3. Run database migrations

```bash
cd backend
docker compose exec api alembic upgrade head
```

Or, if running the API locally:

```bash
cd backend
alembic upgrade head
```

## 4. Seed mock data (optional)

```bash
cd backend
python -m scripts.seed
```

This creates 3 tenants, 7 users, 15 products, and 28 inventory items.
All users share the password **`Test1234!`**.

| Tenant | Users |
|--------|-------|
| *(no tenant)* | `superadmin@system.local` (superuser) |
| Acme Corp | `alice@acme.com`, `bob@acme.com`, `carol@acme.com` |
| Globex Industries | `hank@globex.com`, `homer@globex.com` |
| Wayne Enterprises | `bruce@wayne.com`, `lucius@wayne.com` |

## 5. Run tests

```bash
cd backend
pip install -r requirements.txt   # first time only
pytest tests/
```

Coverage for `app/crud` is printed automatically. An HTML report is generated at `backend/htmlcov/index.html`.

## 6. API docs

Once the API is running, interactive docs are available at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

# Testing Multi-Tenant Isolation with curl

The core concept: **each tenant sees only its own inventory**, even when they
stock the same products. The walkthrough below demonstrates this end-to-end
using only `curl`.

> **Base URL used below:** `http://localhost:8000/api/v1`

## Step 1 - Create two tenants (sign up)

```bash
# Tenant A
curl -s -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@tenant-a.com",
    "full_name": "Alice",
    "password": "Test1234!",
    "tenant_name": "Tenant A"
  }'
```

```bash
# Tenant B
curl -s -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "bob@tenant-b.com",
    "full_name": "Bob",
    "password": "Test1234!",
    "tenant_name": "Tenant B"
  }'
```

Each call creates a new tenant **and** its first user.

## Step 2 - Log in as each user

```bash
# Get token for Alice (Tenant A)
TOKEN_A=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice@tenant-a.com&password=Test1234!" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo "Token A: $TOKEN_A"
```

```bash
# Get token for Bob (Tenant B)
TOKEN_B=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=bob@tenant-b.com&password=Test1234!" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo "Token B: $TOKEN_B"
```

## Step 3 - Create a product (superuser only)

Products are global (shared across all tenants), so you need the superuser.

```bash
# Log in as superadmin (only needed if you ran the seed script)
TOKEN_ADMIN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=superadmin@system.local&password=Test1234!" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Create a product
curl -s -X POST http://localhost:8000/api/v1/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_ADMIN" \
  -d '{
    "name": "Widget X",
    "description": "A demo widget",
    "sku": "DEMO-WX01"
  }'
```

Save the returned `id` — you'll need it next:

```bash
PRODUCT_ID="<paste the id from the response>"
```

> If you ran the seed script, you can skip this step and use any existing
> product ID from `GET /products`.

## Step 4 - Each tenant adds the same product to their inventory

```bash
# Tenant A adds 500 units
curl -s -X POST http://localhost:8000/api/v1/inventory \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_A" \
  -d "{
    \"product_id\": \"$PRODUCT_ID\",
    \"min_stock\": 50,
    \"current_stock\": 500
  }"
```

```bash
# Tenant B adds 20 units of the same product
curl -s -X POST http://localhost:8000/api/v1/inventory \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_B" \
  -d "{
    \"product_id\": \"$PRODUCT_ID\",
    \"min_stock\": 5,
    \"current_stock\": 20
  }"
```

## Step 5 - Verify tenant isolation

Now list inventory for each tenant. Each one only sees **their own** stock:

```bash
# Tenant A sees 500 units
curl -s http://localhost:8000/api/v1/inventory \
  -H "Authorization: Bearer $TOKEN_A" | python3 -m json.tool
```

```json
[
    {
        "min_stock": 50,
        "current_stock": 500,
        "product_id": "...",
        "id": "..."
    }
]
```

```bash
# Tenant B sees 20 units
curl -s http://localhost:8000/api/v1/inventory \
  -H "Authorization: Bearer $TOKEN_B" | python3 -m json.tool
```

```json
[
    {
        "min_stock": 5,
        "current_stock": 20,
        "product_id": "...",
        "id": "..."
    }
]
```

Tenant A cannot see Tenant B's inventory and vice-versa. The isolation
is enforced at the API layer — every inventory query is automatically
filtered by the `tenant_id` extracted from the JWT token.

## Step 6 - Update inventory and confirm isolation holds

```bash
# Tenant A restocks to 999
INVENTORY_A_ID="<id from Tenant A's inventory response>"

curl -s -X PATCH "http://localhost:8000/api/v1/inventory/$INVENTORY_A_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_A" \
  -d '{"current_stock": 999}'
```

```bash
# Tenant B's inventory is unchanged
curl -s http://localhost:8000/api/v1/inventory \
  -H "Authorization: Bearer $TOKEN_B" | python3 -m json.tool
```

Tenant B still sees `"current_stock": 20`.

## Step 7 - Invite a second user to a tenant

```bash
# Alice invites a colleague to Tenant A
curl -s -X POST http://localhost:8000/api/v1/auth/invite \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_A" \
  -d '{
    "email": "charlie@tenant-a.com",
    "full_name": "Charlie"
  }'
```

The response includes a `temporary_password`. Charlie can log in and will
see the same inventory as Alice — they share the same tenant.

---

## Quick reference

| Endpoint | Method | Auth | Scope |
|----------|--------|------|-------|
| `/auth/signup` | POST | -- | Creates tenant + first user |
| `/auth/login` | POST | -- | Returns JWT token |
| `/auth/invite` | POST | Bearer | Invites user to your tenant |
| `/products` | GET | -- | Global product catalog |
| `/products` | POST | Superuser | Create product |
| `/products/{id}` | GET | -- | Get product |
| `/products/{id}` | PATCH | Superuser | Update product |
| `/products/{id}` | DELETE | Superuser | Delete product |
| `/inventory` | GET | Bearer | List **your tenant's** inventory |
| `/inventory/{product_id}` | GET | Bearer | Get inventory by product |
| `/inventory` | POST | Bearer | Add product to **your tenant's** inventory |
| `/inventory/{id}` | PATCH | Bearer | Update **your tenant's** inventory item |
| `/tenants` | GET | Superuser | List all tenants |
