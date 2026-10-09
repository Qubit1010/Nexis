import { notFound } from "next/navigation";
import { authorised, expired, getBusiness, logEvent, rest } from "@/lib/db";
import { ensureHealthcare } from "@/lib/healthcare";
import HealthcareLanding, { type LandingDoctor } from "@/components/HealthcareLanding";
import RestaurantLanding, { type LandingMenuItem } from "@/components/RestaurantLanding";
import { ensureRestaurant } from "@/lib/restaurant";
import { ensureSchool } from "@/lib/school";
import SchoolLanding, { type LandingProgram } from "@/components/SchoolLanding";

export const dynamic = "force-dynamic";
export const metadata = { title: "Landing page preview | NexusPoint", referrer: "no-referrer" as const };

export default async function Page({ params, searchParams }: {
  params: Promise<{ slug: string }>;
  searchParams: Promise<Record<string, string | undefined>>;
}) {
  const { slug } = await params;
  const sp = await searchParams;
  const b = await getBusiness(slug);
  if (!authorised(b, sp.t ?? null) || !["healthcare", "food", "education"].includes(b.sector)) notFound();
  if (expired(b)) return <div className="hub gone" dir={sp.lang === "ur" ? "rtl" : "ltr"}><div><h1>{sp.lang === "ur" ? "اس ڈیمو کی مدت ختم ہو گئی ہے۔" : "This demo has ended"}</h1><p>{sp.lang === "ur" ? "تازہ نمونے کے لیے نیکسس پوائنٹ سے رابطہ کریں۔" : "Contact NexusPoint for a fresh preview."}</p></div></div>;
  const business = { slug: b.slug, token: b.token, name: b.name, profile: b.profile, xray: b.xray, created_at: b.created_at };
  if (b.sector === "education") {
    let programs: LandingProgram[] = [];
    let programsUnavailable = false;
    try {
      await ensureSchool(b);
      programs = await rest<LandingProgram>("GET", `demo_school_classes?slug=eq.${encodeURIComponent(slug)}&select=id,name&order=name`);
    } catch { programsUnavailable = true; }
    if (sp.embed !== "1") await logEvent(slug, "website_view");
    return <SchoolLanding business={{ slug: b.slug, token: b.token, name: b.name, profile: { facts: b.profile.facts }, xray: b.xray ? { praise: b.xray.praise } : null }} programs={programs} programsUnavailable={programsUnavailable} initialLang={sp.lang === "ur" ? "ur" : "en"} embedded={sp.embed === "1"} />;
  }
  if (b.sector === "food") {
    let menu: LandingMenuItem[] = [];
    let menuUnavailable = false;
    try {
      await ensureRestaurant(b);
      menu = await rest<LandingMenuItem>("GET", `demo_menu_items?slug=eq.${encodeURIComponent(slug)}&select=id,name,name_ur,category,description,price,available,art&order=category,name`);
    } catch { menuUnavailable = true; }
    if (sp.embed !== "1") await logEvent(slug, "website_view");
    return <RestaurantLanding business={{ ...business, profile: { facts: b.profile.facts }, xray: b.xray ? { praise: b.xray.praise } : null }} menu={menu} menuUnavailable={menuUnavailable} initialLang={sp.lang === "ur" ? "ur" : "en"} embedded={sp.embed === "1"} />;
  }
  let doctors: LandingDoctor[] = [];
  try {
    await ensureHealthcare(b);
    doctors = await rest<LandingDoctor>("GET", `demo_doctors?slug=eq.${encodeURIComponent(slug)}&active=eq.true&select=id,name,specialty,modes&order=id.asc`);
  } catch { /* The landing page remains readable when the sample directory is unavailable. */ }
  if (sp.embed !== "1") await logEvent(slug, "website_view");
  return <HealthcareLanding business={business} doctors={doctors} initialLang={sp.lang === "ur" ? "ur" : "en"} embedded={sp.embed === "1"} />;
}
