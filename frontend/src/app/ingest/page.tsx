import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { IngestForm } from "./ingest-form";

export default async function IngestPage() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    redirect("/login");
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 p-4">
      <IngestForm />
    </main>
  );
}
