"use client";

import { AnimatePresence } from "framer-motion";
import Image from "next/image";
import type { DeckItem } from "@/app/deck/actions";
import { SwipeCard } from "./swipe-card";

interface StyleStackProps {
  label: string;
  items: DeckItem[];
  /** Unbounded counter — wraps via modulo for lookup, but stays unique across
   * cycles so each swiped card gets its own AnimatePresence exit animation. */
  index: number;
  onSwipe: () => void;
}

export function StyleStack({ label, items, index, onSwipe }: StyleStackProps) {
  return (
    <div className="flex w-full max-w-sm flex-col items-center gap-3">
      <span className="font-heading text-sm font-semibold tracking-widest text-muted-foreground uppercase">
        {label}
      </span>
      <div className="relative aspect-[3/4] w-full">
        {items.length === 0 ? (
          <EmptyStack label={label} />
        ) : (
          <>
            {items.length > 1 && <PeekCard item={items[(index + 1) % items.length]} />}
            <AnimatePresence mode="popLayout">
              <SwipeCard
                key={`${items[index % items.length].id}-${index}`}
                item={items[index % items.length]}
                isTop
                onSwiped={onSwipe}
              />
            </AnimatePresence>
          </>
        )}
      </div>
      {items.length > 0 && (
        <p className="text-xs text-muted-foreground">
          {items.length} item{items.length === 1 ? "" : "s"} · swipe to cycle
        </p>
      )}
    </div>
  );
}

function PeekCard({ item }: { item: DeckItem }) {
  return (
    <div
      aria-hidden="true"
      className="absolute inset-0 origin-bottom translate-y-2 scale-[0.94] overflow-hidden rounded-3xl border border-border bg-card opacity-70 shadow-md"
    >
      <div className="relative h-full w-full bg-muted">
        <Image
          src={item.imageUrl}
          alt=""
          fill
          sizes="(max-width: 640px) 90vw, 420px"
          className="object-contain p-6"
          draggable={false}
        />
      </div>
    </div>
  );
}

function EmptyStack({ label }: { label: string }) {
  return (
    <div className="flex h-full w-full flex-col items-center justify-center gap-2 rounded-3xl border border-dashed border-border bg-muted/40 p-8 text-center">
      <p className="font-heading text-lg font-medium text-foreground">No {label.toLowerCase()} yet</p>
      <p className="text-sm text-muted-foreground">Add a few from the wardrobe to start styling.</p>
    </div>
  );
}
