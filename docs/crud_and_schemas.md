# 🛠️ CRUD & Schemas Cheat Sheet

This project uses the **Repository Pattern** for database access and **Pydantic V2** for data validation.

---

## 1. Pydantic Schemas (Data Validation)

We separate data into different classes to prevent **Security Leaks** (sending passwords/internal costs to the frontend) and to handle **Validation** (ids don't exist on creation).

### The Naming Convention

| Suffix | Purpose | Contains ID? | Usage |
| :--- | :--- | :--- | :--- |
| **`[ModelName]Base`** | Fields shared by *everything* (Reading & Writing). | ❌ No | Parent Class only. |
| **`[ModelName]Create`** | Fields required to *make* a new item. | ❌ No | Input for `POST /items`. |
| **`[ModelName]Update`** | Fields allowed to be *changed*. All optional. | ❌ No | Input for `PATCH /items`. |
| **`[ModelName]InDBBase`** | Mirrors the Database Table exactly. | ✅ Yes | Internal Backend use. |
| **`[ModelName]Public`** | The **Public** API Response. | ✅ Yes | Output for `GET /items`. |

### Example Structure

```python
# 1. SHARED (The foundation)
class ProductBase(BaseModel):
    name: str
    sku: str

# 2. INPUTS (What we receive)
class ProductCreate(ProductBase):
    password: str  # Required for creation

class ProductUpdate(BaseModel):
    name: Optional[str] = None  # Optional for updates

# 3. OUTPUTS (What we send back)
class ProductInDBBase(ProductBase):
    id: UUID
    internal_cost: float     # ⚠️ Secret field!
    hashed_password: str     # ⚠️ Secret field!

    model_config = ConfigDict(from_attributes=True) # This tells Pydantic "It's okay to read from a SQLAlchemy class"

class ProductPublic(ProductBase):
    # Public Response - We purposefully OMIT secrets here!
    id: UUID

    model_config = ConfigDict(from_attributes=True) # This tells Pydantic "It's okay to read from a SQLAlchemy class"

```

---

## 2. CRUD Operations (Database Access)

We use a **Generic Repository** (`CRUDBase`) to avoid writing SQL for basic operations.

### Standard Methods (Available everywhere)

| Method | Syntax | Description |
| --- | --- | --- |
| **Get (ID)** | `crud.item.get(db, id=uuid)` | Finds one record by Primary Key. |
| **Get (List)** | `crud.item.get_multi(db, skip=0, limit=100)` | Returns a paginated list. |
| **Create** | `crud.item.create(db, obj_in=schema)` | Validates input, Inserts, Commits, Refreshes. |
| **Update** | `crud.item.update(db, db_obj=obj, obj_in=update_schema)` | Smart update (only changes sent fields). |
| **Delete** | `crud.item.remove(db, id=uuid)` | Deletes record by ID. |

### How to Extend (Custom Queries)

When you need something specific (like finding by SKU), add it to your specific CRUD class.

**File:** `app/crud/crud_product.py`

```python
class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    
    # Custom Method
    async def get_by_sku(self, db: AsyncSession, *, sku: str) -> Optional[Product]:
        query = select(Product).where(Product.sku == sku)
        result = await db.execute(query)
        return result.scalars().first()

```

---

## ⚠️ Common Gotchas

### 1. The Asterisk (`*`) in CRUD

All CRUD methods use `*` to force **Keyword Arguments**.

* ❌ **Wrong:** `crud.user.remove(db, user_id)`
* ✅ **Right:** `crud.user.remove(db, id=user_id)`

### 2. The `exclude_unset` Rule

In `update()`, we use `exclude_unset=True`.

* If you send `{"name": "New"}` to an update endpoint, Pydantic sees `description` as `None`.
* Without this flag, we would accidentally set `description = NULL` in the database.
* **With this flag**, we ignore `description` and only update `name`.

### 3. Circular Imports

* **Never** import `crud` inside a Pydantic schema.
* **Never** import a Pydantic schema inside a SQLAlchemy model.
* Keep `models/`, `schemas/`, and `crud/` strictly separated.

```

```