"use client";

import { useEffect, useRef, useState, useTransition } from "react";
import { ingestPhoto, type IngestResult } from "./actions";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export function IngestForm() {
  const formRef = useRef<HTMLFormElement>(null);
  const previewUrlRef = useRef<string | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [result, setResult] = useState<IngestResult | null>(null);
  const [pending, startTransition] = useTransition();

  useEffect(() => {
    return () => {
      if (previewUrlRef.current) URL.revokeObjectURL(previewUrlRef.current);
    };
  }, []);

  function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    setResult(null);
    if (previewUrlRef.current) URL.revokeObjectURL(previewUrlRef.current);
    const url = file ? URL.createObjectURL(file) : null;
    previewUrlRef.current = url;
    setPreview(url);
  }

  function handleSubmit(formData: FormData) {
    startTransition(async () => {
      const next = await ingestPhoto(formData);
      setResult(next);
      if (next.ok) {
        formRef.current?.reset();
        setPreview(null);
      }
    });
  }

  return (
    <Card className="w-full max-w-sm">
      <CardHeader>
        <CardTitle>Add an item</CardTitle>
        <CardDescription>
          Snap one clothing item on a flat surface — Lime strips the background and tags it.
          No typing required.
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <form ref={formRef} action={handleSubmit} className="flex flex-col gap-4">
          <input
            type="file"
            name="photo"
            accept="image/*"
            capture="environment"
            onChange={handleFileChange}
            className="text-sm file:mr-3 file:rounded-md file:border-0 file:bg-secondary file:px-3 file:py-2 file:text-sm file:font-medium"
          />
          {preview && (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={preview}
              alt="Selected photo preview"
              className="aspect-square w-full rounded-md border object-cover"
            />
          )}
          <Button type="submit" disabled={pending || !preview} className="w-full">
            {pending ? "Stripping background & tagging…" : "Add to wardrobe"}
          </Button>
        </form>

        {result && !result.ok && <p className="text-sm text-destructive">{result.error}</p>}

        {result?.ok && (
          <div className="flex flex-col gap-3 rounded-md border bg-muted/30 p-3">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={result.previewDataUrl}
              alt="Background-stripped item"
              className="aspect-square w-full rounded-md border bg-muted object-contain"
            />
            <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-sm">
              <dt className="text-muted-foreground">Category</dt>
              <dd className="capitalize">{result.tags.category}</dd>
              <dt className="text-muted-foreground">Silhouette</dt>
              <dd>{result.tags.silhouette}</dd>
              <dt className="text-muted-foreground">Palette</dt>
              <dd>{result.tags.palette.join(", ")}</dd>
              <dt className="text-muted-foreground">Texture</dt>
              <dd>{result.tags.texture}</dd>
              <dt className="text-muted-foreground">Aesthetic</dt>
              <dd>{result.tags.aesthetic}</dd>
            </dl>
            <p className="text-sm font-medium text-emerald-700">Saved to your wardrobe ✓</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
