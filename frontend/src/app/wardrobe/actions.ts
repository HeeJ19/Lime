"use server";

import { createClient } from "@/lib/supabase/server";

export interface WardrobeItem {
  id: string;
  category: "top" | "bottom" | "shoes";
  imageUrl: string;
  silhouette: string;
  aesthetic: string;
}

const SIGNED_URL_TTL_SECONDS = 60 * 60;

export async function getWardrobeItems(): Promise<WardrobeItem[] | { error: string }> {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return { error: "You must be signed in to view your wardrobe." };

  const { data: rows, error } = await supabase
    .from("items")
    .select("id, category, image_url, tags")
    .eq("user_id", user.id)
    .order("created_at", { ascending: false });

  if (error) return { error: "Couldn't load your wardrobe. Try again." };

  const items: WardrobeItem[] = [];
  for (const row of rows ?? []) {
    const { data: signed } = await supabase.storage
      .from("clothing-photos")
      .createSignedUrl(row.image_url, SIGNED_URL_TTL_SECONDS);
    if (!signed) continue;

    items.push({
      id: row.id,
      category: row.category as WardrobeItem["category"],
      imageUrl: signed.signedUrl,
      silhouette: row.tags?.silhouette ?? "",
      aesthetic: row.tags?.aesthetic ?? "",
    });
  }

  return items;
}
