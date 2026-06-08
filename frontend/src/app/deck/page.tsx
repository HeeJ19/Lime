import Link from "next/link";
import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { getWardrobe } from "./actions";
import { DeckBoard } from "./components/deck-board";

export default async function DeckPage() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    redirect("/login");
  }

  const wardrobe = await getWardrobe();

  if ("error" in wardrobe) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center gap-2 p-4 text-center">
        <p className="text-destructive">{wardrobe.error}</p>
      </main>
    );
  }

  const isEmpty = wardrobe.top.length === 0 && wardrobe.bottom.length === 0 && wardrobe.shoes.length === 0;

  if (isEmpty) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center gap-4 p-4 text-center">
        <h1 className="font-heading text-2xl font-semibold">Your deck is empty</h1>
        <p className="max-w-md text-muted-foreground">
          Add a few items to your wardrobe and they&apos;ll show up here, ready to swipe and style.
        </p>
        <Link href="/ingest" className="font-medium text-primary underline-offset-4 hover:underline">
          Add an item
        </Link>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen flex-col items-center">
      <header className="flex w-full max-w-5xl flex-col items-center gap-1 px-4 pt-8 text-center">
        <h1 className="font-heading text-3xl font-semibold tracking-tight">Style your fit</h1>
        <p className="text-muted-foreground">Swipe each stack to cycle, then lock in the combo you like.</p>
      </header>
      <DeckBoard wardrobe={wardrobe} />
    </main>
  );
}
