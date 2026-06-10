"use client";

import Image from "next/image";
import { useMemo, useState } from "react";
import type { WardrobeItem } from "../actions";

interface WardrobeGridProps {
  items: WardrobeItem[];
}

const TABS = [
  { key: "all", label: "All" },
  { key: "top", label: "Tops" },
  { key: "bottom", label: "Bottoms" },
  { key: "shoes", label: "Shoes" },
] as const;

type TabKey = (typeof TABS)[number]["key"];

export function WardrobeGrid({ items }: WardrobeGridProps) {
  const [activeTab, setActiveTab] = useState<TabKey>("all");

  const counts = useMemo<Record<TabKey, number>>(
    () => ({
      all: items.length,
      top: items.filter((i) => i.category === "top").length,
      bottom: items.filter((i) => i.category === "bottom").length,
      shoes: items.filter((i) => i.category === "shoes").length,
    }),
    [items],
  );

  const visible = useMemo(
    () => (activeTab === "all" ? items : items.filter((i) => i.category === activeTab)),
    [items, activeTab],
  );

  return (
    <div className="w-full">
      {/* Category tabs */}
      <div className="flex gap-2 overflow-x-auto pb-1" role="tablist" aria-label="Filter by category">
        {TABS.map(({ key, label }) => (
          <button
            key={key}
            type="button"
            role="tab"
            aria-selected={activeTab === key}
            onClick={() => setActiveTab(key)}
            className={`flex shrink-0 items-center gap-1.5 rounded-full border px-4 py-1.5 text-sm font-medium transition-colors ${
              activeTab === key
                ? "border-primary bg-primary text-primary-foreground"
                : "border-border bg-card text-muted-foreground hover:border-primary/50 hover:text-foreground"
            }`}
          >
            {label}
            <span
              className={`rounded-full px-1.5 py-0.5 text-xs ${
                activeTab === key ? "bg-primary-foreground/20 text-primary-foreground" : "bg-muted text-muted-foreground"
              }`}
            >
              {counts[key]}
            </span>
          </button>
        ))}
      </div>

      {/* Grid or empty state */}
      {visible.length === 0 ? (
        <div className="mt-16 flex flex-col items-center gap-2 text-center">
          <p className="text-muted-foreground">No {activeTab === "all" ? "items" : activeTab + "s"} yet.</p>
        </div>
      ) : (
        <ul className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3">
          {visible.map((item) => (
            <li key={item.id} className="flex flex-col gap-1.5">
              <div className="relative aspect-square overflow-hidden rounded-2xl bg-muted">
                <Image
                  src={item.imageUrl}
                  alt={item.silhouette || item.category}
                  fill
                  sizes="(max-width: 640px) 50vw, 33vw"
                  className="object-contain p-2"
                  draggable={false}
                />
              </div>
              <div className="px-0.5">
                <p className="truncate text-sm font-medium capitalize leading-tight">{item.silhouette}</p>
                <p className="truncate text-xs text-muted-foreground capitalize">{item.aesthetic}</p>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
