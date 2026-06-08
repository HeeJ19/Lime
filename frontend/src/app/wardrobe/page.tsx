import Link from "next/link";
import { redirect } from "next/navigation";
import { logout } from "@/app/auth/actions";
import { Button } from "@/components/ui/button";
import { createClient } from "@/lib/supabase/server";

// Placeholder landing page for authenticated users — proves the auth chain
// works end-to-end. Replaced by the real Wardrobe Grid screen in Phase 3.
export default async function WardrobePage() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    redirect("/login");
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 p-4 text-center">
      <h1 className="text-2xl font-semibold">Welcome to your wardrobe, {user.email}</h1>
      <p className="max-w-md text-muted-foreground">
        This is a placeholder confirming you&apos;re signed in. The Ingestion Camera, Styling Deck,
        and Wardrobe Grid land in Phase 2 and Phase 3.
      </p>
      <div className="flex flex-wrap justify-center gap-3">
        <Button asChild>
          <Link href="/ingest">Add an item</Link>
        </Button>
        <Button asChild variant="secondary">
          <Link href="/deck">Style a fit</Link>
        </Button>
        <form>
          <Button formAction={logout} variant="outline">
            Log out
          </Button>
        </form>
      </div>
    </main>
  );
}
