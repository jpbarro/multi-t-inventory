"""
Seed script to populate the local database with mock data.

Usage:
    cd backend
    python -m scripts.seed
"""

import asyncio
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal, engine
from app.models.tenant import Tenant
from app.models.user import User
from app.models.product import Product
from app.models.inventory import Inventory
from app.core.security import get_password_hash


# ---------------------------------------------------------------------------
# Mock data definitions
# ---------------------------------------------------------------------------

TENANTS = [
    {"name": "Acme Corp"},
    {"name": "Globex Industries"},
    {"name": "Wayne Enterprises"},
]

# All users use the same default password for easy testing
DEFAULT_PASSWORD = "Test1234!"

# Global super admin (no tenant)
SUPER_ADMIN = {"email": "superadmin@system.local", "full_name": "Super Admin"}

USERS = [
    # Acme Corp users
    {"email": "alice@acme.com", "full_name": "Alice Admin", "tenant_index": 0},
    {"email": "bob@acme.com", "full_name": "Bob Builder", "tenant_index": 0},
    {"email": "carol@acme.com", "full_name": "Carol Chen", "tenant_index": 0},
    # Globex Industries users
    {"email": "hank@globex.com", "full_name": "Hank Scorpio", "tenant_index": 1},
    {"email": "homer@globex.com", "full_name": "Homer Simpson", "tenant_index": 1},
    # Wayne Enterprises users
    {"email": "bruce@wayne.com", "full_name": "Bruce Wayne", "tenant_index": 2},
    {"email": "lucius@wayne.com", "full_name": "Lucius Fox", "tenant_index": 2},
]

PRODUCTS = [
    {
        "name": "Laptop Pro 15",
        "description": "15-inch professional laptop",
        "sku": "ELEC-LP15",
    },
    {
        "name": "Wireless Mouse",
        "description": "Ergonomic wireless mouse",
        "sku": "ELEC-WM01",
    },
    {
        "name": "USB-C Hub",
        "description": "7-in-1 USB-C docking station",
        "sku": "ELEC-HUB7",
    },
    {
        "name": "Mechanical Keyboard",
        "description": "RGB mechanical keyboard, Cherry MX",
        "sku": "ELEC-KB01",
    },
    {
        "name": 'Monitor 27"',
        "description": "27-inch 4K IPS monitor",
        "sku": "ELEC-MN27",
    },
    {
        "name": "Webcam HD",
        "description": "1080p HD webcam with microphone",
        "sku": "ELEC-WC01",
    },
    {
        "name": "Standing Desk",
        "description": "Electric height-adjustable desk",
        "sku": "FURN-SD01",
    },
    {
        "name": "Office Chair",
        "description": "Ergonomic mesh office chair",
        "sku": "FURN-CH01",
    },
    {
        "name": "Desk Lamp",
        "description": "LED desk lamp with adjustable arm",
        "sku": "FURN-DL01",
    },
    {
        "name": "Notebook A5",
        "description": "Hardcover A5 lined notebook",
        "sku": "STAT-NB01",
    },
    {
        "name": "Ballpoint Pen Pack",
        "description": "Pack of 12 black ballpoint pens",
        "sku": "STAT-BP12",
    },
    {
        "name": "Whiteboard 90x60",
        "description": "Magnetic whiteboard 90x60 cm",
        "sku": "STAT-WB01",
    },
    {
        "name": "Ethernet Cable 3m",
        "description": "Cat6 ethernet cable, 3 meters",
        "sku": "NET-EC03",
    },
    {
        "name": "Wi-Fi Router",
        "description": "Dual-band Wi-Fi 6 router",
        "sku": "NET-WR06",
    },
    {
        "name": "Surge Protector",
        "description": "6-outlet surge protector power strip",
        "sku": "ELEC-SP06",
    },
]

# Inventory assignments: (tenant_index, product_index, min_stock, current_stock)
INVENTORY = [
    # Acme Corp - has most products
    (0, 0, 10, 45),
    (0, 1, 50, 180),
    (0, 2, 20, 95),
    (0, 3, 15, 60),
    (0, 4, 5, 28),
    (0, 5, 10, 35),
    (0, 6, 5, 18),
    (0, 7, 5, 22),
    (0, 9, 100, 450),
    (0, 10, 50, 280),
    (0, 12, 30, 140),
    (0, 14, 10, 55),
    # Globex Industries - medium inventory
    (1, 0, 5, 25),
    (1, 1, 20, 90),
    (1, 3, 10, 35),
    (1, 4, 3, 12),
    (1, 6, 2, 8),
    (1, 7, 3, 14),
    (1, 8, 5, 28),
    (1, 13, 5, 18),
    # Wayne Enterprises - select high-end items
    (2, 0, 20, 90),
    (2, 2, 15, 70),
    (2, 4, 10, 45),
    (2, 6, 8, 35),
    (2, 7, 8, 38),
    (2, 11, 5, 20),
    (2, 13, 5, 30),
    (2, 14, 15, 75),
]


async def seed(session: AsyncSession) -> None:
    """Insert all mock data inside a single transaction."""

    # 1. Create tenants
    tenants: list[Tenant] = []
    for t in TENANTS:
        tenant = Tenant(id=uuid.uuid4(), name=t["name"])
        session.add(tenant)
        tenants.append(tenant)
    await session.flush()
    print(f"  Created {len(tenants)} tenants")

    # 2. Create super admin (no tenant)
    hashed = get_password_hash(DEFAULT_PASSWORD)
    super_admin = User(
        id=uuid.uuid4(),
        email=SUPER_ADMIN["email"],
        full_name=SUPER_ADMIN["full_name"],
        hashed_password=hashed,
        is_active=True,
        is_superuser=True,
        tenant_id=None,
    )
    session.add(super_admin)
    await session.flush()
    print(f"  Created super admin: {SUPER_ADMIN['email']}")

    # 3. Create tenant users
    users: list[User] = []
    for u in USERS:
        user = User(
            id=uuid.uuid4(),
            email=u["email"],
            full_name=u["full_name"],
            hashed_password=hashed,
            is_active=True,
            is_superuser=False,
            tenant_id=tenants[u["tenant_index"]].id,
        )
        session.add(user)
        users.append(user)
    await session.flush()
    print(f"  Created {len(users)} tenant users")

    # 4. Create products
    products: list[Product] = []
    for p in PRODUCTS:
        product = Product(
            id=uuid.uuid4(),
            name=p["name"],
            description=p["description"],
            sku=p["sku"],
        )
        session.add(product)
        products.append(product)
    await session.flush()
    print(f"  Created {len(products)} products")

    # 5. Create inventory
    for tenant_idx, product_idx, min_s, cur_s in INVENTORY:
        inv = Inventory(
            id=uuid.uuid4(),
            tenant_id=tenants[tenant_idx].id,
            product_id=products[product_idx].id,
            min_stock=min_s,
            current_stock=cur_s,
        )
        session.add(inv)
    await session.flush()
    print(f"  Created {len(INVENTORY)} inventory items")

    await session.commit()


async def main() -> None:
    print("Seeding database...")

    async with AsyncSessionLocal() as session:
        await seed(session)

    print("\nDone! Mock data inserted successfully.")
    print(f"\nDefault password for all users: {DEFAULT_PASSWORD}")
    print("\nSuper Admin (no tenant):")
    print(f"  - {SUPER_ADMIN['email']} ({SUPER_ADMIN['full_name']}) [superuser]")
    print("\nTenants & Users:")
    for t_idx, t in enumerate(TENANTS):
        print(f"  {t['name']}:")
        for u in USERS:
            if u["tenant_index"] == t_idx:
                print(f"    - {u['email']} ({u['full_name']})")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
