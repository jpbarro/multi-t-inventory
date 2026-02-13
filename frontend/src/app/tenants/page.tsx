"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { api, type Tenant } from "@/lib/api";

export default function TenantsPage() {
  const router = useRouter();
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }

    async function fetchData() {
      try {
        const me = await api.getMe(token!);
        if (!me.is_superuser) {
          router.push("/inventory");
          return;
        }

        const data = await api.getTenants(token!);
        setTenants(data);
      } catch (err) {
        if (err instanceof Error && err.message === "Unauthorized") {
          localStorage.removeItem("access_token");
          router.push("/login");
          return;
        }
        setError(err instanceof Error ? err.message : "Failed to load tenants");
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [router]);

  if (loading) {
    return <p className="text-muted-foreground py-8 text-center">Loading tenants…</p>;
  }

  if (error) {
    return <p className="py-8 text-center text-destructive">{error}</p>;
  }

  if (tenants.length === 0) {
    return <p className="text-muted-foreground py-8 text-center">No tenants found.</p>;
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Name</TableHead>
          <TableHead>ID</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {tenants.map((tenant) => (
          <TableRow key={tenant.id}>
            <TableCell className="font-medium">{tenant.name}</TableCell>
            <TableCell className="font-mono text-muted-foreground">{tenant.id}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
