"use server";

import { createClient } from "@/lib/supabase/server";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://127.0.0.1:8001";

export interface DeckItem {
  id: string;
  category: "top" | "bottom" | "shoes";
  imageUrl: string;
  tags: {
    silhouette: string;
    palette: string[];
    texture: string;
    aesthetic: string;
  };
}

export type DeckData = {
  top: DeckItem[];
  bottom: DeckItem[];
  shoes: DeckItem[];
};

// The `clothing-photos` bucket is private (RLS-scoped to the owning user), so
// the deck reads through short-lived signed URLs rather than public ones.
const SIGNED_URL_TTL_SECONDS = 60 * 60;

export async function getWardrobe(): Promise<DeckData | { error: string }> {
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

  const deck: DeckData = { top: [], bottom: [], shoes: [] };

  for (const row of rows ?? []) {
    const { data: signed } = await supabase.storage
      .from("clothing-photos")
      .createSignedUrl(row.image_url, SIGNED_URL_TTL_SECONDS);
    if (!signed) continue;

    deck[row.category as DeckItem["category"]].push({
      id: row.id,
      category: row.category,
      imageUrl: signed.signedUrl,
      tags: row.tags,
    });
  }

  return deck;
}

export interface Recommendation {
  temperatureC: number;
  condition: string;
  /** Item IDs ranked most-to-least weather-appropriate, per category. */
  rankedItemIds: { top: string[]; bottom: string[]; shoes: string[] };
}

interface RecommendationApiResponse {
  temperature_c: number;
  condition: string;
  ranked_item_ids: { top?: string[]; bottom?: string[]; shoes?: string[] };
}

// Calls the FastAPI recommendation endpoint (Open-Meteo -> embed -> Pinecone,
// scoped to this user's wardrobe — see agent_docs/code_patterns.md "Frontend ->
// Recommendations"). Coordinates come from the browser's Geolocation API; if the
// user declines location access, the deck simply keeps its default ordering.
export async function getRecommendations(
  latitude: number,
  longitude: number,
): Promise<Recommendation | { error: string }> {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return { error: "You must be signed in to get recommendations." };

  try {
    const params = new URLSearchParams({
      user_id: user.id,
      latitude: String(latitude),
      longitude: String(longitude),
    });
    const res = await fetch(`${BACKEND_URL}/recommendations?${params}`);
    if (!res.ok) return { error: "Couldn't fetch weather-based recommendations." };

    const payload = (await res.json()) as RecommendationApiResponse;
    return {
      temperatureC: payload.temperature_c,
      condition: payload.condition,
      rankedItemIds: {
        top: payload.ranked_item_ids.top ?? [],
        bottom: payload.ranked_item_ids.bottom ?? [],
        shoes: payload.ranked_item_ids.shoes ?? [],
      },
    };
  } catch {
    return { error: "Couldn't reach the styling service. Try again in a moment." };
  }
}

export async function lockOutfit(input: {
  topItemId: string | null;
  bottomItemId: string | null;
  shoesItemId: string | null;
}): Promise<{ ok: true } | { ok: false; error: string }> {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return { ok: false, error: "You must be signed in to lock an outfit." };

  const { error } = await supabase.from("outfits").insert({
    user_id: user.id,
    top_item_id: input.topItemId,
    bottom_item_id: input.bottomItemId,
    shoes_item_id: input.shoesItemId,
  });
  if (error) return { ok: false, error: "Couldn't lock that outfit. Try again." };

  return { ok: true };
}
