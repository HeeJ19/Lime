"use client";

import {
  motion,
  useMotionValue,
  useReducedMotion,
  useTransform,
  type PanInfo,
} from "framer-motion";
import Image from "next/image";
import type { DeckItem } from "@/app/deck/actions";

const SWIPE_DISTANCE_THRESHOLD = 120;
const SWIPE_VELOCITY_THRESHOLD = 500;

interface SwipeCardProps {
  item: DeckItem;
  isTop: boolean;
  onSwiped: (direction: "left" | "right") => void;
}

export function SwipeCard({ item, isTop, onSwiped }: SwipeCardProps) {
  const prefersReducedMotion = useReducedMotion();
  const x = useMotionValue(0);
  const rotate = useTransform(x, [-280, 280], [-16, 16]);
  const keepOpacity = useTransform(x, [40, 160], [0, 1]);
  const skipOpacity = useTransform(x, [-160, -40], [1, 0]);

  function handleDragEnd(_event: PointerEvent | MouseEvent | TouchEvent, info: PanInfo) {
    const { offset, velocity } = info;
    if (offset.x > SWIPE_DISTANCE_THRESHOLD || velocity.x > SWIPE_VELOCITY_THRESHOLD) {
      onSwiped("right");
    } else if (offset.x < -SWIPE_DISTANCE_THRESHOLD || velocity.x < -SWIPE_VELOCITY_THRESHOLD) {
      onSwiped("left");
    }
  }

  return (
    <motion.div
      className="absolute inset-0 touch-none select-none"
      style={isTop ? { x, rotate: prefersReducedMotion ? 0 : rotate } : undefined}
      drag={isTop ? "x" : false}
      dragConstraints={{ left: 0, right: 0 }}
      dragElastic={0.65}
      dragTransition={{ bounceStiffness: 400, bounceDamping: 30 }}
      onDragEnd={isTop ? handleDragEnd : undefined}
      whileTap={isTop ? { scale: 0.97 } : undefined}
      initial={{ scale: 0.94, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      exit={{
        x: x.get() >= 0 ? 480 : -480,
        opacity: 0,
        transition: { duration: prefersReducedMotion ? 0.01 : 0.18, ease: "easeIn" },
      }}
      transition={{ type: "spring", stiffness: 320, damping: 28 }}
    >
      <div className="relative flex h-full w-full flex-col overflow-hidden rounded-3xl border border-border bg-card shadow-xl">
        {isTop && (
          <>
            <motion.span
              style={{ opacity: keepOpacity }}
              className="pointer-events-none absolute top-6 right-6 z-10 rounded-full border-2 border-primary bg-background/80 px-4 py-1 font-heading text-sm font-semibold tracking-wide text-primary uppercase"
              aria-hidden="true"
            >
              Keep
            </motion.span>
            <motion.span
              style={{ opacity: skipOpacity }}
              className="pointer-events-none absolute top-6 left-6 z-10 rounded-full border-2 border-muted-foreground bg-background/80 px-4 py-1 font-heading text-sm font-semibold tracking-wide text-muted-foreground uppercase"
              aria-hidden="true"
            >
              Skip
            </motion.span>
          </>
        )}
        <div className="relative flex-1 bg-muted">
          <Image
            src={item.imageUrl}
            alt={`${item.tags.aesthetic} ${item.category} — ${item.tags.silhouette} silhouette, ${item.tags.texture} texture`}
            fill
            sizes="(max-width: 640px) 90vw, 420px"
            className="object-contain p-6"
            draggable={false}
            priority={isTop}
          />
        </div>
        <div className="flex flex-wrap gap-2 border-t border-border p-4">
          <Chip label={item.tags.silhouette} />
          <Chip label={item.tags.texture} />
          <Chip label={item.tags.aesthetic} />
        </div>
      </div>
    </motion.div>
  );
}

function Chip({ label }: { label: string }) {
  return (
    <span className="rounded-full bg-secondary px-3 py-1 text-sm font-medium text-secondary-foreground capitalize">
      {label}
    </span>
  );
}
