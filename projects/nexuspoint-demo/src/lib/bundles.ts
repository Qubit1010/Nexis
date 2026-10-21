// Approved price lists per market (quetta, islamabad), produced by scripts/sync_bundles.py.
// Older private files had one top-level {terms, sectors} list; that shape is read as Quetta.
import type { Market } from "./city.ts";

export type Tier = { name: string; tag_en: string; tag_ur: string; setup: number; monthly: number; rec: boolean; items_en: string[]; items_ur: string[] };
type PriceList = { terms: Record<string, string>; sectors: Record<string, Tier[]> };
export type Bundles = { markets?: Partial<Record<Market, PriceList>> } & Partial<PriceList>;

export function priceList(bundles: Bundles, market: Market): PriceList | null {
  const list = bundles.markets?.[market];
  if (list) return list;
  if (market === "quetta" && bundles.sectors) return { terms: bundles.terms ?? {}, sectors: bundles.sectors };
  return null;
}

/** Tiers for a sector in a market, or null when that market has no approved prices for it. */
export function tiersFor(bundles: Bundles, market: Market, sector: string): Tier[] | null {
  const tiers = priceList(bundles, market)?.sectors[sector];
  return tiers && tiers.length ? tiers : null;
}
