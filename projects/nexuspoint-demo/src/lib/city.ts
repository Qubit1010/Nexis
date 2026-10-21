// City awareness for demos. A demo carries its city in profile.city (written by make_demo); older
// Quetta demos have none, so everything falls back to Quetta and renders exactly as before.
// Both markets are on Pakistan Standard Time, so dates and times stay Asia/Karachi everywhere.

export const cityNames: Record<string, string> = {
  Quetta: "کوئٹہ", Islamabad: "اسلام آباد", Rawalpindi: "راولپنڈی", Lahore: "لاہور", Karachi: "کراچی", Peshawar: "پشاور",
};

export type Market = "quetta" | "islamabad";

type CityProfile = { city?: string | null; market?: string | null; facts?: { city?: string | null; address?: string | null } | null } | null | undefined;

const KNOWN = Object.keys(cityNames);

function known(value: string | null | undefined): string | null {
  if (!value) return null;
  const hit = KNOWN.find((c) => c.toLowerCase() === value.trim().toLowerCase());
  return hit ?? null;
}

/** The demo's city: explicit profile.city, then a recognised Maps city, then the address, then Quetta. */
export function cityOf(profile: CityProfile): string {
  if (!profile) return "Quetta";
  const explicit = profile.city?.trim();
  if (explicit) return known(explicit) ?? explicit;
  const fromFacts = known(profile.facts?.city);
  if (fromFacts) return fromFacts;
  const address = profile.facts?.address ?? "";
  return KNOWN.find((c) => new RegExp(`\\b${c}\\b`, "i").test(address)) ?? "Quetta";
}

export function cityUr(city: string): string {
  return cityNames[city] ?? city;
}

/** Which approved price list applies. Rawalpindi prospects are sold on Islamabad pricing. */
export function marketOf(profile: CityProfile): Market {
  if (profile?.market === "islamabad" || profile?.market === "quetta") return profile.market;
  return /^(islamabad|rawalpindi)$/i.test(cityOf(profile)) ? "islamabad" : "quetta";
}

/** Replace {city} in stored sector copy. Older demos stored the literal text, newer ones a template. */
export function fillCity(text: string, city: string): string {
  return text.replace(/\{city\}/g, city);
}

/** Today's date and time in Pakistan (PKT, both markets). */
export function pktToday(now = new Date()): string {
  return (
    now.toLocaleDateString("en-GB", { timeZone: "Asia/Karachi", weekday: "long", day: "numeric", month: "long", year: "numeric" }) +
    ", " +
    now.toLocaleTimeString("en-US", { timeZone: "Asia/Karachi", hour: "numeric", minute: "2-digit" })
  );
}
