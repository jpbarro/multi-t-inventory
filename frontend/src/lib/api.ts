const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface InventoryItem {
  id: string;
  min_stock: number;
  current_stock: number;
  product_id: string;
}

export interface Product {
  id: string;
  name: string;
  description: string;
  sku: string;
}

export interface MeResponse {
  id: string;
  email: string;
  full_name: string;
  tenant_id: string | null;
  is_superuser: boolean;
}

export interface Tenant {
  id: string;
  name: string;
}

export interface SupplyResponse {
  status: string;
  message: string;
  external_reference_id: string;
}

export const api = {
  async login(email: string, password: string): Promise<TokenResponse> {
    const body = new URLSearchParams({
      username: email,
      password,
    });

    const res = await fetch(`${BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => null);
      throw new Error(err?.detail ?? "Login failed");
    }

    return res.json();
  },

  async getInventory(token: string): Promise<InventoryItem[]> {
    const res = await fetch(`${BASE_URL}/inventory`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!res.ok) {
      throw new Error(res.status === 401 ? "Unauthorized" : "Failed to fetch inventory");
    }

    return res.json();
  },

  async getMe(token: string): Promise<MeResponse> {
    const res = await fetch(`${BASE_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!res.ok) {
      throw new Error(res.status === 401 ? "Unauthorized" : "Failed to fetch user");
    }

    return res.json();
  },

  async getTenants(token: string): Promise<Tenant[]> {
    const res = await fetch(`${BASE_URL}/tenants`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!res.ok) {
      throw new Error(res.status === 401 ? "Unauthorized" : "Failed to fetch tenants");
    }

    return res.json();
  },

  async requestResupply(token: string, inventoryId: string, quantity: number): Promise<SupplyResponse> {
    const res = await fetch(`${BASE_URL}/inventory/${inventoryId}/resupply`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ quantity }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => null);
      throw new Error(err?.detail ?? "Resupply request failed");
    }

    return res.json();
  },

  async getProducts(): Promise<Product[]> {
    const res = await fetch(`${BASE_URL}/products`);

    if (!res.ok) {
      throw new Error("Failed to fetch products");
    }

    return res.json();
  },
};
