import {
  CloudDrizzle,
  CloudFog,
  CloudLightning,
  CloudRain,
  CloudSnow,
  Cloudy,
  Loader2,
  Sun,
} from "lucide-react";

export type WeatherStatus =
  | { state: "loading" }
  | { state: "unavailable" }
  | { state: "ready"; temperatureC: number; condition: string };

const CONDITION_ICONS: Record<string, typeof Sun> = {
  clear: Sun,
  "mostly clear": Sun,
  "partly cloudy": Cloudy,
  overcast: Cloudy,
  foggy: CloudFog,
  drizzling: CloudDrizzle,
  rainy: CloudRain,
  showery: CloudRain,
  snowy: CloudSnow,
  stormy: CloudLightning,
};

// A small "real-time weather" readout above the swipe stacks (per the PRD's
// Styling Deck spec) — also doubles as the visible explanation for *why* the
// stacks are ordered the way they are ("dressed for 4°C and snowy").
export function WeatherWidget({ status }: { status: WeatherStatus }) {
  if (status.state === "loading") {
    return (
      <div className="flex items-center gap-2 rounded-full border border-border bg-card px-4 py-2 text-sm text-muted-foreground">
        <Loader2 className="size-4 animate-spin" aria-hidden="true" />
        <span>Checking the weather to style your fit…</span>
      </div>
    );
  }

  if (status.state === "unavailable") {
    return (
      <div className="rounded-full border border-border bg-card px-4 py-2 text-sm text-muted-foreground">
        Share your location for weather-matched picks — showing your wardrobe for now.
      </div>
    );
  }

  const Icon = CONDITION_ICONS[status.condition] ?? Sun;
  const rounded = Math.round(status.temperatureC);

  return (
    <div className="flex items-center gap-3 rounded-full border border-border bg-card px-4 py-2">
      <Icon className="size-5 text-primary" aria-hidden="true" />
      <p className="text-sm">
        <span className="font-semibold text-foreground">{rounded}°C</span>{" "}
        <span className="text-muted-foreground">and {status.condition} — picks dressed for it</span>
      </p>
    </div>
  );
}
