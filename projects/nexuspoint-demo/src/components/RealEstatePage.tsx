import { notFound } from "next/navigation";
import { authorised, expired, getBusiness } from "@/lib/db";
import type { ReRole } from "@/lib/real-estate-types";
import RealEstate from "./RealEstate";

export default async function RealEstatePage({ params, searchParams, role }: { params: Promise<{ slug: string }>; searchParams: Promise<Record<string, string | undefined>>; role: ReRole }) {
  const { slug } = await params, sp = await searchParams, b = await getBusiness(slug);
  if (!authorised(b, sp.t ?? null) || b.sector !== "real-estate") notFound();
  if (expired(b)) return <div className="hub gone"><div><h1>This property preview has ended</h1><p>Contact NexusPoint for a fresh demo.</p><a href="https://wa.me/923118340514">Contact NexusPoint</a></div></div>;
  return <RealEstate slug={slug} token={b.token} name={b.name} role={role} initialLang={sp.lang === "ur" ? "ur" : "en"} initialTab={sp.tab}
    initialVisit={role === "buyer" && sp.visit === "1"} initialListing={role === "buyer" ? sp.listing : undefined} />;
}
