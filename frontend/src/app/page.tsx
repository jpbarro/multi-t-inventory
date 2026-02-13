import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-8 p-8">
      <div className="text-center space-y-2">
        <h1 className="text-4xl font-bold tracking-tight">
          Multi-T Inventory
        </h1>
        <p className="text-muted-foreground text-lg">
          Multi-tenant inventory management system
        </p>
      </div>

      <Separator className="max-w-md" />

      <div className="grid gap-4 md:grid-cols-3 max-w-4xl w-full">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Products
              <Badge variant="secondary">Global</Badge>
            </CardTitle>
            <CardDescription>
              Shared product catalog across all tenants
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              15 products seeded across electronics, furniture, stationery, and
              networking categories.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Inventory
              <Badge>Tenant-scoped</Badge>
            </CardTitle>
            <CardDescription>
              Each tenant manages their own stock levels
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Tenant isolation ensures that inventory data is only visible to
              users within the same organization.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Auth
              <Badge variant="outline">JWT</Badge>
            </CardTitle>
            <CardDescription>
              Sign up, login, and invite team members
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              OAuth2-compatible authentication with per-tenant user management
              and role-based access.
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="flex gap-4">
        <Button asChild>
          <Link href="/login">Login</Link>
        </Button>
        <Button variant="outline" asChild>
          <a href="http://localhost:8000/docs" target="_blank">
            API Docs
          </a>
        </Button>
        <Button variant="outline" asChild>
          <a href="http://localhost:8000/redoc" target="_blank">
            ReDoc
          </a>
        </Button>
      </div>
    </div>
  );
}
