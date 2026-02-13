"use client";

import { useEffect, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api, type InventoryItem, type Product } from "@/lib/api";

interface InventoryRow extends InventoryItem {
  product_name: string;
  product_sku: string;
}

export default function InventoryPage() {
  const router = useRouter();
  const [rows, setRows] = useState<InventoryRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Resupply dialog state
  const [resupplyRow, setResupplyRow] = useState<InventoryRow | null>(null);
  const [quantity, setQuantity] = useState("");
  const [resupplyLoading, setResupplyLoading] = useState(false);
  const [resupplyResult, setResupplyResult] = useState("");
  const [resupplyError, setResupplyError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }

    async function fetchData() {
      try {
        const [inventory, products] = await Promise.all([
          api.getInventory(token!),
          api.getProducts(),
        ]);

        const productMap = new Map<string, Product>();
        for (const p of products) {
          productMap.set(p.id, p);
        }

        const joined = inventory.map((item) => {
          const product = productMap.get(item.product_id);
          return {
            ...item,
            product_name: product?.name ?? "Unknown",
            product_sku: product?.sku ?? "—",
          };
        });

        setRows(joined);
      } catch (err) {
        if (err instanceof Error && err.message === "Unauthorized") {
          localStorage.removeItem("access_token");
          router.push("/login");
          return;
        }
        setError(err instanceof Error ? err.message : "Failed to load data");
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [router]);

  function openResupply(row: InventoryRow) {
    setResupplyRow(row);
    setQuantity("");
    setResupplyResult("");
    setResupplyError("");
  }

  function closeResupply() {
    setResupplyRow(null);
  }

  async function handleResupply(e: FormEvent) {
    e.preventDefault();
    if (!resupplyRow) return;

    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }

    setResupplyLoading(true);
    setResupplyError("");
    setResupplyResult("");

    try {
      const res = await api.requestResupply(token, resupplyRow.id, Number(quantity));
      setResupplyResult(res.message);
    } catch (err) {
      setResupplyError(err instanceof Error ? err.message : "Resupply request failed");
    } finally {
      setResupplyLoading(false);
    }
  }

  if (loading) {
    return <p className="text-muted-foreground py-8 text-center">Loading inventory…</p>;
  }

  if (error) {
    return <p className="py-8 text-center text-destructive">{error}</p>;
  }

  if (rows.length === 0) {
    return <p className="text-muted-foreground py-8 text-center">No inventory items found.</p>;
  }

  return (
    <>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Product Name</TableHead>
            <TableHead>SKU</TableHead>
            <TableHead className="text-right">Current Stock</TableHead>
            <TableHead className="text-right">Min Stock</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((row) => (
            <TableRow key={row.id}>
              <TableCell className="font-medium">{row.product_name}</TableCell>
              <TableCell>{row.product_sku}</TableCell>
              <TableCell className="text-right">{row.current_stock}</TableCell>
              <TableCell className="text-right">{row.min_stock}</TableCell>
              <TableCell className="text-right">
                <Button variant="outline" size="sm" onClick={() => openResupply(row)}>
                  Restock
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      <Dialog open={resupplyRow !== null} onOpenChange={(open) => { if (!open) closeResupply(); }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Request Restock</DialogTitle>
            <DialogDescription>
              {resupplyRow?.product_name} ({resupplyRow?.product_sku})
            </DialogDescription>
          </DialogHeader>

          {resupplyResult ? (
            <div className="space-y-4">
              <p className="text-sm text-green-600">{resupplyResult}</p>
              <DialogFooter>
                <Button variant="outline" onClick={closeResupply}>Close</Button>
              </DialogFooter>
            </div>
          ) : (
            <form onSubmit={handleResupply} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="restock-qty">Quantity</Label>
                <Input
                  id="restock-qty"
                  type="number"
                  min={1}
                  required
                  value={quantity}
                  onChange={(e) => setQuantity(e.target.value)}
                />
              </div>
              {resupplyError && (
                <p className="text-sm text-destructive">{resupplyError}</p>
              )}
              <DialogFooter>
                <Button variant="outline" type="button" onClick={closeResupply}>
                  Cancel
                </Button>
                <Button type="submit" disabled={resupplyLoading}>
                  {resupplyLoading ? "Requesting…" : "Request"}
                </Button>
              </DialogFooter>
            </form>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}
