import Link from "next/link";
import { redirect } from "next/navigation";
import { logout } from "@/app/auth/actions";
import { Button } from "@/components/ui/button";
import { createClient } from "@/lib/supabase/server";
import { getWardrobeItems } from "./actions";
import { WardrobeGrid } from "./components/wardrobe-grid";

export default async function WardrobePage() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    redirect("/login");
  }

  const result = await getWardrobeItems();
  const items = "error" in result ? [] : result;
  const hasError = "error" in result;

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-xl flex-col gap-6 px-4 pt-8" style={{ paddingBottom: "max(5rem, env(safe-area-inset-bottom))" }}>
      <header className="flex items-start justify-between gap-4">
        <div>
          <h1 className="font-heading text-3xl font-semibold tracking-tight">Your wardrobe</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {items.length === 0 ? "No items yet" : `${items.length} item${items.length === 1 ? "" : "s"}`}
          </p>
        </div>
        <form>
          <Button formAction={logout} variant="ghost" size="sm" className="text-muted-foreground">
            Log out
          </Button>
        </form>
      </header>

      <div className="flex gap-2">
        <Button asChild size="sm">
          <Link href="/ingest">Add item</Link>
        </Button>
        <Button asChild size="sm" variant="secondary">
          <Link href="/deck">Style a fit</Link>
        </Button>
      </div>

      {hasError && (
        <p className="text-sm text-destructive">Couldn&apos;t load your wardrobe — please refresh.</p>
      )}

      {!hasError && items.length === 0 ? (
        <div className="flex flex-1 flex-col items-center justify-center gap-3 text-center">
          <p className="text-muted-foreground">Your wardrobe is empty.</p>
          <p className="max-w-xs text-sm text-muted-foreground">
            Snap a photo of any clothing item and Lime will tag and save it for you.
          </p>
          <Button asChild>
            <Link href="/ingest">Add your first item</Link>
          </Button>
        </div>
      ) : (
        <WardrobeGrid items={items} />
      )}
    </main>
  );
}
