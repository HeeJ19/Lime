"use client";

import Image from "next/image";
import { useEffect, useMemo, useState, useTransition } from "react";
import { Button } from "@/components/ui/button";
import { getRecommendations, lockOutfit, type DeckData, type DeckItem } from "../actions";
import { StyleStack } from "./style-stack";
import { WeatherWidget, type WeatherStatus } from "./weather-widget";

interface DeckBoardProps {
  wardrobe: DeckData;
}

type LockResult = { ok: true } | { ok: false; error: string } | null;

const CATEGORIES = [
  { key: "top", label: "Top" },
  { key: "bottom", label: "Bottom" },
  { key: "shoes", label: "Shoes" },
] as const;

type CategoryKey = (typeof CATEGORIES)[number]["key"];

export function DeckBoard({ wardrobe }: DeckBoardProps) {
  const [active, setActive] = useState<CategoryKey>("top");
  const [topIndex, setTopIndex] = useState(0);
  const [bottomIndex, setBottomIndex] = useState(0);
  const [shoesIndex, setShoesIndex] = useState(0);
  const [lockResult, setLockResult] = useState<LockResult>(null);
  const [pending, startTransition] = useTransition();
  const [weather, setWeather] = useState<WeatherStatus>(() =>
    typeof navigator !== "undefined" && "geolocation" in navigator
      ? { state: "loading" }
      : { state: "unavailable" },
  );
  const [rankedItemIds, setRankedItemIds] = useState<Record<CategoryKey, string[]> | null>(null);

  // Ask for the user's location once on mount; if they decline (or the browser
  // can't provide it), the deck just keeps its default most-recent-first order —
  // location is an enhancement, never a blocker for using the Styling Deck.
  // setWeather is only ever called from the geolocation API's own async
  // callbacks below, never synchronously from the effect body.
  useEffect(() => {
    if (!("geolocation" in navigator)) return;
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        getRecommendations(latitude, longitude).then((result) => {
          if ("error" in result) {
            setWeather({ state: "unavailable" });
            return;
          }
          setWeather({ state: "ready", temperatureC: result.temperatureC, condition: result.condition });
          setRankedItemIds(result.rankedItemIds);
        });
      },
      () => setWeather({ state: "unavailable" }),
      { timeout: 10_000, maximumAge: 10 * 60 * 1000 },
    );
  }, []);

  // Surface the weather-recommended item first in each stack while preserving
  // the rest of the wardrobe in its original order — swiping past it cycles
  // through the remaining items exactly as before.
  const orderedWardrobe: DeckData = useMemo(
    () => ({
      top: reorderByRanking(wardrobe.top, rankedItemIds?.top ?? []),
      bottom: reorderByRanking(wardrobe.bottom, rankedItemIds?.bottom ?? []),
      shoes: reorderByRanking(wardrobe.shoes, rankedItemIds?.shoes ?? []),
    }),
    [wardrobe, rankedItemIds],
  );

  const current: Record<CategoryKey, DeckItem | null> = {
    top: currentItem(orderedWardrobe.top, topIndex),
    bottom: currentItem(orderedWardrobe.bottom, bottomIndex),
    shoes: currentItem(orderedWardrobe.shoes, shoesIndex),
  };
  const advance: Record<CategoryKey, () => void> = {
    top: () => setTopIndex((i) => i + 1),
    bottom: () => setBottomIndex((i) => i + 1),
    shoes: () => setShoesIndex((i) => i + 1),
  };
  const indexFor: Record<CategoryKey, number> = { top: topIndex, bottom: bottomIndex, shoes: shoesIndex };
  const canLock = Boolean(current.top || current.bottom || current.shoes);

  function handleLock() {
    setLockResult(null);
    startTransition(async () => {
      const result = await lockOutfit({
        topItemId: current.top?.id ?? null,
        bottomItemId: current.bottom?.id ?? null,
        shoesItemId: current.shoes?.id ?? null,
      });
      setLockResult(result);
    });
  }

  return (
    <div className="flex w-full flex-col items-center gap-6 px-4 pt-4 pb-40">
      <WeatherWidget status={weather} />

      {/* Outfit preview / category switcher — also doubles as a live look at
          the combo forming, so users always see all three layers at once. */}
      <div className="flex items-center gap-3" role="tablist" aria-label="Outfit layers">
        {CATEGORIES.map(({ key, label }) => (
          <button
            key={key}
            type="button"
            role="tab"
            aria-selected={active === key}
            onClick={() => setActive(key)}
            className={`flex cursor-pointer flex-col items-center gap-1 rounded-2xl border-2 p-1.5 transition-colors ${
              active === key ? "border-primary" : "border-transparent"
            }`}
          >
            <span className="relative block size-14 overflow-hidden rounded-xl bg-muted">
              {current[key] && (
                <Image
                  src={current[key]!.imageUrl}
                  alt=""
                  fill
                  sizes="56px"
                  className="object-contain p-1"
                  draggable={false}
                />
              )}
            </span>
            <span className="text-xs font-medium text-muted-foreground">{label}</span>
          </button>
        ))}
      </div>

      <StyleStack
        label={CATEGORIES.find((c) => c.key === active)!.label}
        items={orderedWardrobe[active]}
        index={indexFor[active]}
        onSwipe={advance[active]}
      />

      <div className="fixed inset-x-0 bottom-0 z-30 flex flex-col items-center gap-2 border-t border-border bg-background/90 p-4 backdrop-blur supports-[backdrop-filter]:bg-background/70">
        {lockResult?.ok === false && (
          <p role="alert" className="text-sm text-destructive">
            {lockResult.error}
          </p>
        )}
        {lockResult?.ok === true && (
          <p role="status" className="text-sm font-medium text-primary">
            Outfit locked ✓
          </p>
        )}
        <Button
          size="lg"
          className="w-full max-w-sm"
          disabled={!canLock || pending}
          onClick={handleLock}
        >
          {pending ? "Locking…" : "Lock this fit"}
        </Button>
      </div>
    </div>
  );
}

function currentItem(items: DeckItem[], index: number): DeckItem | null {
  return items.length > 0 ? items[index % items.length] : null;
}

// Items present in `rankedIds` move to the front in ranked order; everything
// else keeps its original relative order behind them (Array.sort is stable).
function reorderByRanking(items: DeckItem[], rankedIds: string[]): DeckItem[] {
  if (rankedIds.length === 0) return items;
  const rank = new Map(rankedIds.map((id, i) => [id, i]));
  return [...items].sort((a, b) => {
    const ra = rank.get(a.id);
    const rb = rank.get(b.id);
    if (ra !== undefined && rb !== undefined) return ra - rb;
    if (ra !== undefined) return -1;
    if (rb !== undefined) return 1;
    return 0;
  });
}
