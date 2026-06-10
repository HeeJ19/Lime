"use server";

import { revalidatePath } from "next/cache";
import { createClient } from "@/lib/supabase/server";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://127.0.0.1:8001";

export interface ItemTags {
  category: "top" | "bottom" | "shoes";
  silhouette: string;
  palette: string[];
  texture: string;
  aesthetic: string;
}

export type IngestResult =
  | { ok: true; tags: ItemTags; previewDataUrl: string }
  | { ok: false; error: string };

interface IngestResponse {
  item_id: string;
  tags: ItemTags;
  stripped_image_base64: string;
}

// Orchestrates the Vision Ingestion Pipeline from the frontend side: forwards the
// raw photo to the FastAPI AI microservice (which owns background removal, VLM
// tagging, embedding, and the Pinecone upsert — see docs/ARCHITECTURE.md), then
// persists the result to Supabase using the signed-in user's session so RLS
// scopes the new row/object to them.
export async function ingestPhoto(formData: FormData): Promise<IngestResult> {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    return { ok: false, error: "You must be signed in to add an item." };
  }

  const photo = formData.get("photo");
  if (!(photo instanceof File) || photo.size === 0) {
    return { ok: false, error: "Choose a photo first." };
  }

  const backendForm = new FormData();
  backendForm.append("file", photo);
  backendForm.append("user_id", user.id);

  let payload: IngestResponse;
  try {
    const res = await fetch(`${BACKEND_URL}/items/ingest`, {
      method: "POST",
      body: backendForm,
      signal: AbortSignal.timeout(60_000),
    });
    if (!res.ok) {
      const detail = (await res.json().catch(() => null)) as { detail?: string } | null;
      return { ok: false, error: detail?.detail ?? "Couldn't process that photo. Try again." };
    }
    payload = (await res.json()) as IngestResponse;
  } catch {
    return { ok: false, error: "Couldn't reach the styling service. Try again in a moment." };
  }

  const { item_id, tags, stripped_image_base64 } = payload;
  const imageBytes = Buffer.from(stripped_image_base64, "base64");
  // Folder-scoped path required by the storage RLS policies — see supabase/schema.sql
  const storagePath = `${user.id}/${item_id}.png`;

  const { error: uploadError } = await supabase.storage
    .from("clothing-photos")
    .upload(storagePath, imageBytes, { contentType: "image/png" });
  if (uploadError) {
    return { ok: false, error: "Couldn't save that photo. Try again." };
  }

  const { error: insertError } = await supabase.from("items").insert({
    id: item_id,
    user_id: user.id,
    category: tags.category,
    image_url: storagePath,
    tags: {
      silhouette: tags.silhouette,
      palette: tags.palette,
      texture: tags.texture,
      aesthetic: tags.aesthetic,
    },
    embedding_id: item_id,
  });
  if (insertError) {
    // Don't leave an orphaned, unowned object behind in Storage
    await supabase.storage.from("clothing-photos").remove([storagePath]);
    return { ok: false, error: "Couldn't save that item. Try again." };
  }

  revalidatePath("/wardrobe");
  return {
    ok: true,
    tags,
    previewDataUrl: `data:image/png;base64,${stripped_image_base64}`,
  };
}
