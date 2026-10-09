import { notFound } from "next/navigation";
import { headers } from "next/headers";
import QRCode from "qrcode";
import { authorised, expired, getBusiness, logEvent } from "@/lib/db";
import { scriptedDecide } from "@/lib/scripted";
import bundles from "@/data/bundles.json";
import sectors from "@/data/sectors.json";
import Hub from "@/components/Hub";
import ChatMode from "@/components/ChatMode";
import { T, type Lang } from "@/lib/i18n";

export const dynamic = "force-dynamic";

type Props = { params: Promise<{ slug: string }>; searchParams: Promise<Record<string, string | undefined>> };

export default async function Page({ params, searchParams }: Props) {
  const { slug } = await params;
  const sp = await searchParams;
  const b = await getBusiness(slug);
  if (!authorised(b, sp.t ?? null)) notFound();
  const lang: Lang = sp.lang === "ur" ? "ur" : "en";
  if (expired(b)) {
    await logEvent(b.slug, "expired_hit");
    return (
      <div className="hub gone" dir={lang === "ur" ? "rtl" : "ltr"}>
        <div><h1>{T[lang].goneH}</h1><p>{T[lang].goneP}</p>
          <p style={{ marginTop: "1.5rem" }}><a className="btn" href="https://wa.me/923118340514">WhatsApp NexusPoint</a></p></div>
      </div>
    );
  }

  const h = await headers();
  const origin = process.env.DEMO_BASE_URL || `${h.get("x-forwarded-proto") ?? "https"}://${h.get("host")}`;
  const hubUrl = `${origin}/d/${b.slug}?t=${b.token}`;
  const wa = process.env.DEMO_WHATSAPP_NUMBER;
  const chatUrl = wa ? `https://wa.me/${wa}?text=${encodeURIComponent(`DEMO-${b.code} Assalam o alaikum`)}` : `${hubUrl}&chat=1${lang === "ur" ? "&lang=ur" : ""}`;
  const qr = await QRCode.toString(chatUrl, { type: "svg", margin: 0, color: { dark: "#02040A", light: "#FFFFFF" } });
  const sector = sectors[b.sector as keyof typeof sectors];

  if (sp.chat === "1") {
    await logEvent(b.slug, "chat_view");
    return <ChatMode slug={b.slug} token={b.token} name={b.name} lang={lang} prompts={[...sector.suggested_prompts[lang]]} healthcare={b.sector==="healthcare"} restaurant={b.sector==="food"} school={b.sector==="education"} />;
  }

  // Snapshot mode: a pre-played conversation for the offline copy (no network needed to show it).
  let snapshot: { role: "customer" | "business"; content: string }[] | null = null;
  if (sp.snapshot === "1") {
    snapshot = [];
    for (const q of sector.suggested_prompts.en.slice(0, 2)) {
      snapshot.push({ role: "customer", content: q });
      snapshot.push({ role: "business", content: scriptedDecide(b.sector, b.profile.facts, snapshot).reply });
    }
  } else {
    await logEvent(b.slug, "view", { ua: (h.get("user-agent") ?? "").slice(0, 120) });
  }

  return (
    <Hub
      biz={{ slug: b.slug, token: b.token, code: b.code, name: b.name, sector: b.sector, expires_at: b.expires_at,
        created_at: b.created_at, profile: b.profile, xray: b.xray, site: b.site, roi: b.roi, health: b.health }}
      tiers={bundles.sectors[b.sector as keyof typeof bundles.sectors]}
      sector={{ noun: sector.noun, site: sector.site, prompts: sector.suggested_prompts }}
      qr={qr} chatUrl={chatUrl} viaWhatsApp={!!wa} initialLang={lang} snapshot={snapshot}
    />
  );
}
