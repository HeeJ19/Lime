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

  const paths = (rows ?? []).map((row) => row.image_url);
  const { data: signedUrls } = await supabase.storage
    .from("clothing-photos")
    .createSignedUrls(paths, SIGNED_URL_TTL_SECONDS);

  const urlMap = new Map(
    (signedUrls ?? []).flatMap((s) => (s.path && s.signedUrl ? [[s.path, s.signedUrl]] : [])),
  );

  const items: WardrobeItem[] = (rows ?? []).flatMap((row) => {
    const imageUrl = urlMap.get(row.image_url);
    if (!imageUrl) return [];
    return [
      {
        id: row.id,
        category: row.category as WardrobeItem["category"],
        imageUrl,
        silhouette: row.tags?.silhouette ?? "",
        aesthetic: row.tags?.aesthetic ?? "",
      },
    ];
  });

  return items;
}
