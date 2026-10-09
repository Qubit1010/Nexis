"use client";

import { useEffect, useState } from "react";
import type { Profile, Xray } from "@/lib/db";
import type { Doctor } from "@/lib/healthcare-types";
import type { Lang } from "@/lib/i18n";
import "./healthcare-landing.css";

export type LandingBusiness = {
  slug: string;
  token: string;
  name: string;
  profile: Profile;
  xray: Xray | null;
  created_at: string;
};
export type LandingDoctor = Pick<Doctor, "id" | "name" | "specialty" | "modes">;

type SymbolName = "plus" | "arrow" | "calendar" | "heart" | "pin" | "clock" | "chat" | "record" | "check" | "tooth" | "people" | "sun" | "menu";
export function CareSymbol({ name = "plus" }: { name?: SymbolName }) {
  const paths: Record<SymbolName, React.ReactNode> = {
    plus: <path d="M12 4v16M4 12h16" />,
    arrow: <path d="M5 12h14m-6-6 6 6-6 6" />,
    calendar: <><rect x="4" y="5" width="16" height="16" rx="3" /><path d="M8 3v4m8-4v4M4 10h16m-11 5h.01M12 15h.01M15 15h.01" /></>,
    heart: <><path d="M20.8 4.9a5.5 5.5 0 0 0-7.8 0L12 6l-1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.3a5.5 5.5 0 0 0 0-7.8Z" /><path d="M4 12h4l2-3 3 6 2-3h5" /></>,
    pin: <><path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 1 1 16 0Z" /><circle cx="12" cy="10" r="2.5" /></>,
    clock: <><circle cx="12" cy="12" r="9" /><path d="M12 6v6l4 2" /></>,
    chat: <><path d="M21 11a9 9 0 0 1-9 9c-1.5 0-3-.4-4.2-1L3 21l1.3-5A9 9 0 1 1 21 11Z" /><path d="M8 10h8m-8 4h5" /></>,
    record: <><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9Z" /><path d="M14 3v6h6M8 13h8m-8 4h5" /></>,
    check: <path d="m5 12 4 4L19 6" />,
    tooth: <path d="M12 4C8 1 4 4 4 8c0 4 2 12 5 12 2 0 1-7 3-7s1 7 3 7c3 0 5-8 5-12 0-4-4-7-8-4Zm0 0 3 2" />,
    people: <><circle cx="9" cy="7" r="3" /><path d="M3 21v-3a6 6 0 0 1 12 0v3M16 4a3 3 0 0 1 0 6m2 4a5 5 0 0 1 3 4v3" /></>,
    sun: <><circle cx="12" cy="12" r="4" /><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1 1m12 12 1 1M5 19l1-1M18 6l1-1" /></>,
    menu: <path d="M4 6h16M4 12h16M4 18h16" />,
  };
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]}</svg>;
}

const serviceCopy: Record<string, [string, string, string, SymbolName]> = {
  "General consultation": ["عام معائنہ", "Start with a conversation about your concerns and next steps.", "اپنی علامات اور اگلے مراحل کے بارے میں ڈاکٹر سے بات کریں۔", "heart"],
  "Specialist OPD": ["ماہر ڈاکٹر کا معائنہ", "Explore the consultant directory and choose a suitable visit.", "ماہر ڈاکٹروں کی فہرست دیکھیں اور ملاقات کا وقت منتخب کریں۔", "people"],
  "Lab tests": ["لیب ٹیسٹ", "Keep published sample test results alongside your visit records.", "شائع شدہ نمونہ ٹیسٹ نتائج اپنے طبی ریکارڈ کے ساتھ دیکھیں۔", "record"],
  "Follow-up visits": ["دوبارہ معائنہ", "Return to your care plan with appointments and records together.", "اپنی آئندہ ملاقاتیں اور طبی ریکارڈ ایک ساتھ دیکھیں۔", "calendar"],
  "Checkup and consultation": ["دانتوں کا معائنہ", "A first conversation about your teeth, concerns and treatment options.", "دانتوں کی صحت اور علاج کے بارے میں ابتدائی گفتگو۔", "tooth"],
  "Scaling and polishing": ["اسکیلنگ اور پالش", "Ask the dental team about a cleaning consultation.", "دانتوں کی صفائی کے بارے میں ڈینٹل ٹیم سے پوچھیں۔", "tooth"],
  "Fillings": ["دانتوں کی فلنگ", "Discuss restorative options with a dental consultant.", "دانت کی بحالی کے طریقوں پر ڈاکٹر سے بات کریں۔", "tooth"],
  "Root canal treatment (RCT)": ["روٹ کینال", "Book an assessment to discuss your dental concerns.", "دانتوں کے مسائل کے جائزے کے لیے معائنہ بک کریں۔", "tooth"],
  "Crowns and bridges": ["کراؤن اور برج", "Explore options for restoring your smile at a consultation.", "معائنے میں دانتوں کی بحالی کے طریقے معلوم کریں۔", "tooth"],
  "Teeth whitening": ["دانتوں کی سفیدی", "Ask about suitability, treatment and follow-up.", "علاج اور اس کے بعد کی دیکھ بھال کے بارے میں پوچھیں۔", "tooth"],
  "Braces and aligners": ["بریسز اور الائنرز", "Talk to a consultant about alignment options.", "دانتوں کی ترتیب کے بارے میں ماہر سے بات کریں۔", "tooth"],
  "Implants": ["ڈینٹل امپلانٹس", "Start with an assessment and discuss the next steps.", "ابتدائی معائنہ کرائیں اور اگلے مراحل پر بات کریں۔", "tooth"],
  "Acne and acne scar treatment": ["کیل مہاسے اور داغوں کا علاج", "Book an assessment to discuss your skin concerns and the treatment options.", "اپنے مسئلے اور علاج کے طریقوں پر بات کرنے کے لیے معائنہ بک کریں۔", "heart"],
  "Vitiligo treatment": ["برص (وٹیلگو) کا علاج", "Book an assessment to discuss your skin concerns and the treatment options.", "اپنے مسئلے اور علاج کے طریقوں پر بات کرنے کے لیے معائنہ بک کریں۔", "heart"],
  "Psoriasis, eczema and dermatitis": ["سوریاسس، ایگزیما اور ڈرمیٹائٹس", "Book an assessment to discuss your skin concerns and the treatment options.", "اپنے مسئلے اور علاج کے طریقوں پر بات کرنے کے لیے معائنہ بک کریں۔", "heart"],
  "Hair loss and alopecia treatment": ["بالوں کے گرنے اور گنج پن کا علاج", "Book an assessment to discuss your skin concerns and the treatment options.", "اپنے مسئلے اور علاج کے طریقوں پر بات کرنے کے لیے معائنہ بک کریں۔", "heart"],
  "Pigmentation and melasma": ["پگمنٹیشن اور جھائیوں کا علاج", "Book an assessment to discuss your skin concerns and the treatment options.", "اپنے مسئلے اور علاج کے طریقوں پر بات کرنے کے لیے معائنہ بک کریں۔", "heart"],
  "Laser hair removal": ["لیزر سے ناپسندیدہ بالوں کا خاتمہ", "Book an assessment to discuss your skin concerns and the treatment options.", "اپنے مسئلے اور علاج کے طریقوں پر بات کرنے کے لیے معائنہ بک کریں۔", "heart"],
  "Fractional and scar laser": ["فریکشنل اور داغ مٹانے والا لیزر", "Book an assessment to discuss your skin concerns and the treatment options.", "اپنے مسئلے اور علاج کے طریقوں پر بات کرنے کے لیے معائنہ بک کریں۔", "heart"],
  "PRP and hair regeneration": ["پی آر پی اور بالوں کی بحالی", "Book an assessment to discuss your skin concerns and the treatment options.", "اپنے مسئلے اور علاج کے طریقوں پر بات کرنے کے لیے معائنہ بک کریں۔", "heart"],
  "Skin allergy consultation and testing": ["جلد کی الرجی کا معائنہ اور ٹیسٹ", "Book an assessment to discuss your skin concerns and the treatment options.", "اپنے مسئلے اور علاج کے طریقوں پر بات کرنے کے لیے معائنہ بک کریں۔", "heart"],
};
const cityNames: Record<string, string> = { Quetta: "کوئٹہ", Islamabad: "اسلام آباد", Rawalpindi: "راولپنڈی", Lahore: "لاہور", Karachi: "کراچی", Peshawar: "پشاور" };
const specialties: Record<string, string> = {
  "General medicine": "جنرل میڈیسن", Cardiology: "امراض قلب", Pediatrics: "بچوں کے امراض", Gynecology: "امراض نسواں",
  "General dentistry": "جنرل ڈینٹسٹری", Orthodontics: "آرتھوڈونٹکس", "Restorative dentistry": "دانتوں کی بحالی",
  Dermatology: "جلدی امراض", "Cosmetology and laser": "کاسمیٹالوجی اور لیزر", "Hair and scalp": "بال اور سر کی جلد", Allergy: "الرجی",
};
const weekdays: Record<string, string> = { Monday: "پیر", Tuesday: "منگل", Wednesday: "بدھ", Thursday: "جمعرات", Friday: "جمعہ", Saturday: "ہفتہ", Sunday: "اتوار" };

export default function HealthcareLanding({ business: b, doctors, initialLang, embedded = false }: {
  business: LandingBusiness; doctors: LandingDoctor[]; initialLang: Lang; embedded?: boolean;
}) {
  const [lang, setLang] = useState(initialLang);
  const [theme, setTheme] = useState("light");
  const [menu, setMenu] = useState(false);
  const [allServices, setAllServices] = useState(false);
  const S = (en: string, ur: string) => lang === "ur" ? ur : en;
  const f = b.profile.facts;
  const dental = /dent/i.test(f.category ?? b.name);
  const derm = !dental && /skin|derma|cosmet|laser|allerg/i.test(`${f.category ?? ""} ${b.name}`);
  const city = f.city || "Quetta";
  const cityUr = cityNames[city] ?? city;
  const base = `/d/${b.slug}?t=${encodeURIComponent(b.token)}${lang === "ur" ? "&lang=ur" : ""}`;
  const patient = (tab: string, doctor?: string) => `/d/${b.slug}/patient?t=${encodeURIComponent(b.token)}&tab=${tab}${doctor ? "&book=1&doctor=" + encodeURIComponent(doctor) : ""}${lang === "ur" ? "&lang=ur" : ""}`;
  const bookingUrl = patient("appointments") + "&book=1";
  const chatUrl = base + "&chat=1";
  const mapsUrl = /^https:\/\/(www\.)?google\.com\/maps\//.test(f.maps_url) ? f.maps_url : `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(f.address || b.name)}`;
  const praise = b.xray?.praise.filter(p => p.quotes.length).slice(0, 3) ?? [];
  const date = new Date(b.created_at).toLocaleDateString(lang === "ur" ? "ur-PK" : "en-GB", { month: "long", year: "numeric", timeZone: "Asia/Karachi" });

  useEffect(() => {
    try { const saved = localStorage.getItem("np-website-theme"); if (saved === "dark" || saved === "light") setTheme(saved); } catch {}
  }, []);
  function changeLang() {
    const next = lang === "ur" ? "en" : "ur";
    setLang(next); setMenu(false);
    const url = new URL(location.href);
    if (next === "ur") url.searchParams.set("lang", "ur"); else url.searchParams.delete("lang");
    history.replaceState(null, "", url);
  }
  function changeTheme() {
    const next = theme === "light" ? "dark" : "light";
    setTheme(next);
    try { localStorage.setItem("np-website-theme", next); } catch {}
  }
  const nav = [
    ["care-services", S("Services", "خدمات")],
    ["care-about", S("Our approach", "ہمارا طریقہ")],
    ["care-team", S("Care team", "ڈاکٹر")],
    ["care-visit", S("Plan your visit", "ملاقات کی تیاری")],
  ];
  const Button = ({ href, children, secondary = false }: { href: string; children: React.ReactNode; secondary?: boolean }) =>
    <a className={`cl-button${secondary ? " secondary" : ""}`} href={href} target={embedded ? "_top" : undefined}>{children}<CareSymbol name="arrow" /></a>;

  return <div className="cl" data-website-theme={theme} dir={lang === "ur" ? "rtl" : "ltr"} lang={lang}>
    <a className="cl-skip" href="#care-main">{S("Skip to content", "مواد پر جائیں")}</a>
    <div className="cl-demo">
      <div className="cl-wrap cl-demo-row"><span><i />{S("Private landing page preview", "نجی لینڈنگ پیج کا نمونہ")}<span className="cl-demo-extra"> · {S("Illustrative services & doctors", "فرضی خدمات اور ڈاکٹر")}</span></span>
        <div><a href={base + "#website"} target={embedded ? "_top" : undefined}>{S("Back to your report", "رپورٹ پر واپس")} <span aria-hidden="true">↗</span></a>
          <button onClick={changeLang} aria-label={S("Switch to Urdu", "انگریزی میں دیکھیں")}>{S("اردو", "English")}</button>
          <button className="cl-icon-button" onClick={changeTheme} aria-label={S("Switch colour theme", "رنگ تبدیل کریں")}><CareSymbol name="sun" /></button>
        </div>
      </div>
    </div>
    <header className="cl-header">
      <div className="cl-wrap cl-nav-row">
        <a className="cl-brand" href="#care-home" aria-label={b.name}><span className="cl-brand-symbol"><CareSymbol name={dental ? "tooth" : "plus"} /></span><span>{b.name}<small>{S(dental ? "Dental care · " + city : derm ? "Skin & laser care · " + city : "Healthcare · " + city, dental ? "دانتوں کی دیکھ بھال · " + cityUr : derm ? "جلد اور لیزر کی دیکھ بھال · " + cityUr : "صحت کی دیکھ بھال · " + cityUr)}</small></span></a>
        <nav className="cl-desktop-nav" aria-label={S("Main navigation", "مرکزی نیویگیشن")}>{nav.map(([id, text]) => <a href={`#${id}`} key={id}>{text}</a>)}</nav>
        <a className="cl-nav-book" href={bookingUrl} target={embedded ? "_top" : undefined}>{S("Book a visit", "ملاقات بک کریں")}<CareSymbol name="arrow" /></a>
        <button className="cl-menu-button cl-icon-button" onClick={() => setMenu(!menu)} aria-label={S("Toggle navigation", "مینو کھولیں")} aria-expanded={menu} aria-controls="care-mobile-nav"><CareSymbol name="menu" /></button>
      </div>
      {menu && <nav id="care-mobile-nav" className="cl-mobile-nav cl-wrap" aria-label={S("Mobile navigation", "موبائل مینو")}>{nav.map(([id, text]) => <a href={`#${id}`} key={id} onClick={() => setMenu(false)}>{text}</a>)}<a href={bookingUrl} target={embedded ? "_top" : undefined}>{S("Book a visit", "ملاقات بک کریں")}</a></nav>}
    </header>
    <main id="care-main">
      <section className="cl-hero cl-wrap" id="care-home">
        <div className="cl-hero-copy"><p className="cl-eyebrow"><span />{S(dental ? "A little care. A brighter smile." : derm ? "A little care. Healthier skin." : "A little closer to better care.", dental ? "بہتر دیکھ بھال، بہتر مسکراہٹ" : derm ? "بہتر دیکھ بھال، صحت مند جلد" : "بہتر دیکھ بھال، آپ کے قریب")}</p>
          <h1>{S(dental ? "A healthier smile." : derm ? "Skin care you can trust." : "Good care starts", dental ? "صحت مند مسکراہٹ" : derm ? "جلد کی قابلِ اعتماد دیکھ بھال" : "بہتر دیکھ بھال")}<br /><em>{S(dental || derm ? "A simpler visit." : "with you.", dental || derm ? "آسان ملاقات کے ساتھ" : "آپ سے شروع ہوتی ہے۔")}</em></h1>
          <p className="cl-lead">{S(dental ? "Explore dental care, find a consultant and plan your next visit. Everything you need to get started, in one place." : derm ? "Explore skin, hair and laser care, find a consultant and plan your next visit. Everything you need to get started, in one place." : "Find your doctor, plan your visit and keep your care connected. A simpler way to take the next step at " + b.name + ".", dental ? "دانتوں کی دیکھ بھال کی خدمات دیکھیں، ڈاکٹر منتخب کریں اور اگلی ملاقات کا وقت طے کریں۔" : derm ? "جلد، بالوں اور لیزر کی خدمات دیکھیں، ڈاکٹر منتخب کریں اور اگلی ملاقات کا وقت طے کریں۔" : b.name + " میں ڈاکٹر منتخب کریں، ملاقات بک کریں اور اپنی دیکھ بھال کا ریکارڈ ایک ساتھ رکھیں۔")}</p>
          <div className="cl-actions"><Button href={bookingUrl}>{S("Book an appointment", "اپائنٹمنٹ بک کریں")}</Button><Button href={chatUrl} secondary>{S("Talk to our assistant", "اسسٹنٹ سے بات کریں")}</Button></div>
          <div className="cl-hero-note"><CareSymbol name="check" /><p>{S("In person, by phone or by video. Choose what works for you.", "کلینک، فون یا ویڈیو۔ اپنی سہولت کے مطابق منتخب کریں۔")}<small>{S("Explore sample bookings in this preview.", "اس نمونے میں فرضی بکنگ آزمائیں۔")}</small></p></div>
        </div>
        <div className="cl-hero-visual">
          <img src="/healthcare/consultation.webp" alt={S("Illustrative physician listening to a patient in a consultation", "معائنے کے دوران مریض کی بات سنتی ڈاکٹر کی فرضی تصویر")} width="1536" height="1024" fetchPriority="high" />
          <span className="cl-photo-label">{S("Illustrative image", "فرضی تصویر")}</span>
          <div className="cl-photo-card"><span className="cl-card-icon"><CareSymbol name={dental ? "tooth" : "heart"} /></span><div><b>{S("Your care, connected.", "آپ کی دیکھ بھال، ایک ساتھ")}</b><p>{S("Appointments. Conversations. Records.", "ملاقاتیں، گفتگو اور طبی ریکارڈ")}</p></div><CareSymbol name="arrow" /></div>
          <span className="cl-visual-flower" aria-hidden="true">✳</span>
        </div>
      </section>
      <div className="cl-wrap"><div className="cl-facts">
        <div><span className="cl-fact-icon"><CareSymbol name="pin" /></span><p><b>{f.neighborhood || city}</b><small>{S("Care in your community", "آپ کے علاقے میں دیکھ بھال")}</small></p></div>
        <div><span className="cl-fact-icon"><CareSymbol name="clock" /></span><p><b>{S("Plan ahead", "ملاقات کی تیاری")}</b><small>{S("Clinic hours & directions below", "اوقات اور راستہ نیچے دیکھیں")}</small></p></div>
        {f.rating != null && <a href={mapsUrl} target="_blank" rel="noopener noreferrer"><span className="cl-rating">{f.rating}<span>★</span></span><p><b>{S("On Google", "گوگل پر")}</b><small>{f.reviews != null ? S(`${f.reviews.toLocaleString("en-US")} listing reviews`, `فہرست میں ${f.reviews.toLocaleString("en-US")} جائزے`) : S("View the business listing", "کاروبار کی فہرست دیکھیں")}</small></p></a>}
        <a href={patient("overview")} target={embedded ? "_top" : undefined}><span className="cl-fact-icon"><CareSymbol name="record" /></span><p><b>{S("Patient portal", "مریض پورٹل")}</b><small>{S("Your visits, all in one place", "آپ کی ملاقاتیں ایک جگہ")}</small></p><CareSymbol name="arrow" /></a>
      </div></div>

      <section className="cl-section cl-wrap" id="care-about">
        <div className="cl-about-head"><p className="cl-eyebrow">{S("Care with clarity", "واضح اور مربوط دیکھ بھال")}</p><h2>{S("Your next visit,", "آپ کی اگلی ملاقات")}<br /><em>{S("with fewer unknowns.", "زیادہ آسان اور واضح")}</em></h2><div><p className="cl-muted">{S("Knowing where to go and what comes next should be simple. Explore services, choose a consultation and return to your published visit records whenever you need them.", "خدمات دیکھیں، ملاقات کا وقت منتخب کریں اور ضرورت پڑنے پر اپنے شائع شدہ طبی ریکارڈ تک رسائی حاصل کریں۔")}</p><a className="cl-text-link" href="#care-how">{S("How your visit works", "ملاقات کا طریقہ")}<CareSymbol name="arrow" /></a></div></div>
        <div className="cl-about-grid">
          <article className="cl-about-feature"><CareSymbol name={dental ? "tooth" : "heart"} /><h3>{S("Local care.", "مقامی دیکھ بھال")}<br />{S("A connected experience.", "ایک مربوط تجربہ")}</h3><p>{S("Built around " + b.name + " in " + city + ".", b.name + "، " + cityUr + " کے لیے ایک مربوط تجربہ۔")}</p><a href="#care-visit">{S("Find us", "ہم تک پہنچیں")}<CareSymbol name="arrow" /></a></article>
          <article className="cl-about-detail"><span className="cl-card-icon"><CareSymbol name="chat" /></span><h3>{S("Start with a question", "ایک سوال سے آغاز کریں")}</h3><p>{S("Ask about doctors, timings or your next appointment in English, Urdu or Roman Urdu.", "ڈاکٹروں، اوقات یا اگلی ملاقات کے بارے میں انگریزی، اردو یا رومن اردو میں پوچھیں۔")}</p><a className="cl-text-link" href={chatUrl} target={embedded ? "_top" : undefined}>{S("Open assistant", "اسسٹنٹ کھولیں")}<CareSymbol name="arrow" /></a></article>
          <article className="cl-about-detail"><span className="cl-card-icon"><CareSymbol name="record" /></span><h3>{S("Keep the whole picture", "مکمل ریکارڈ ایک ساتھ")}</h3><p>{S("Appointments, published visit notes and sample reports stay connected in your patient portal.", "مریض پورٹل میں ملاقاتیں، شائع شدہ نوٹس اور نمونہ رپورٹس ایک ساتھ دیکھیں۔")}</p><a className="cl-text-link" href={patient("records")} target={embedded ? "_top" : undefined}>{S("Explore health records", "طبی ریکارڈ دیکھیں")}<CareSymbol name="arrow" /></a></article>
        </div>
      </section>

      <section className="cl-services-band" id="care-services"><div className="cl-section cl-wrap">
        <div className="cl-section-head"><div><p className="cl-eyebrow">{S("Explore our services", "ہماری خدمات دیکھیں")}</p><h2>{S(dental ? "Care for every smile." : derm ? "Care for every skin concern." : "A place to start.", dental ? "ہر مسکراہٹ کی دیکھ بھال" : derm ? "جلد کے ہر مسئلے کی دیکھ بھال" : "بہتر دیکھ بھال کا آغاز")}<br /><em>{S("A plan for your next step.", "آپ کے اگلے مرحلے کا منصوبہ")}</em></h2></div><p className="cl-muted">{S("Sample service categories for this landing page. The clinic would confirm its services before launch.", "اس لینڈنگ پیج کے لیے خدمات کے نمونے۔ اصل اجرا سے پہلے کلینک ان کی تصدیق کرے گا۔")}</p></div>
        <div className="cl-service-grid">{b.profile.services_sample.slice(0, allServices ? undefined : 6).map((name, i) => {
          const copy = serviceCopy[name];
          return <a className="cl-service-card" href={patient("doctors")} target={embedded ? "_top" : undefined} key={name}><div><span className="cl-card-icon"><CareSymbol name={copy?.[3] ?? (dental ? "tooth" : "heart")} /></span><span className="cl-service-number">0{i + 1}</span></div><h3>{S(name, copy?.[0] ?? name)}</h3><p>{copy ? S(copy[1], copy[2]) : S("Ask the clinic team about this service and a suitable consultation.", "اس خدمت اور مناسب معائنے کے بارے میں کلینک سے پوچھیں۔")}</p><span className="cl-service-link">{S("Explore consultations", "معائنہ دیکھیں")}<CareSymbol name="arrow" /></span></a>;
        })}</div>
        {b.profile.services_sample.length > 6 && <button className="cl-button secondary cl-more" onClick={() => setAllServices(!allServices)} aria-expanded={allServices}>{allServices ? S("Show fewer services", "کم خدمات دکھائیں") : S("View all services", "تمام خدمات دیکھیں")}<CareSymbol name="plus" /></button>}
        {!b.profile.services_sample.length && <p className="cl-muted">{S("Ask the clinic team to confirm available services.", "دستیاب خدمات کی تصدیق کلینک سے کریں۔")}</p>}
      </div></section>

      <section className="cl-section cl-wrap" id="care-portal"><div className="cl-portal">
        <div><p className="cl-eyebrow">{S("Your personal patient space", "آپ کا ذاتی مریض پورٹل")}</p><h2>{S("Your care doesn’t", "آپ کی دیکھ بھال")}<br /><em>{S("stop at the door.", "ملاقات کے بعد بھی جڑی رہے")}</em></h2><p>{S("Keep the next appointment and the last visit in the same place. Your portal connects you to the clinic before, during and after a consultation.", "اگلی ملاقات اور گزشتہ معائنے کا ریکارڈ ایک جگہ رکھیں۔ مریض پورٹل آپ کو کلینک سے جوڑے رکھتا ہے۔")}</p><ul>{[
          S("Find a consultant and explore sample availability", "ڈاکٹر تلاش کریں اور نمونہ دستیاب اوقات دیکھیں"),
          S("Manage visits and simulated phone or video calls", "ملاقاتیں اور فرضی فون یا ویڈیو کالز منظم کریں"),
          S("View published reports and print a copy", "شائع شدہ رپورٹس دیکھیں اور پرنٹ کریں"),
        ].map(text => <li key={text}><CareSymbol name="check" />{text}</li>)}</ul><Button href={patient("overview")}>{S("Explore the patient portal", "مریض پورٹل دیکھیں")}</Button></div>
        <div className="cl-portal-preview" aria-label={S("Patient portal features preview", "مریض پورٹل کی خصوصیات")}><div className="cl-portal-top"><span className="cl-brand-symbol"><CareSymbol name="plus" /></span><b>{S("My care", "میری دیکھ بھال")}</b><span>{S("Preview", "نمونہ")}</span></div><h3>{S("Everything, in its place.", "سب کچھ ایک جگہ")}</h3><p>{S("A clearer view of your next step.", "آپ کے اگلے مرحلے کا واضح جائزہ")}</p><a href={patient("appointments")} target={embedded ? "_top" : undefined}><span className="cl-card-icon"><CareSymbol name="calendar" /></span><div><b>{S("Your appointments", "آپ کی ملاقاتیں")}</b><small>{S("Book, reschedule or cancel", "بک کریں، وقت بدلیں یا منسوخ کریں")}</small></div><CareSymbol name="arrow" /></a><div className="cl-portal-tiles"><a href={patient("records")} target={embedded ? "_top" : undefined}><CareSymbol name="record" /><b>{S("Visit records", "طبی ریکارڈ")}</b><small>{S("Published by your doctor", "ڈاکٹر کے شائع کردہ")}</small></a><a href={patient("messages")} target={embedded ? "_top" : undefined}><CareSymbol name="chat" /><b>{S("Conversations", "گفتگو")}</b><small>{S("Stay connected to the team", "ٹیم سے رابطہ رکھیں")}</small></a></div><div className="cl-portal-bottom"><span /><p>{S("One patient. One connected history.", "ایک مریض، ایک مربوط ریکارڈ")}</p></div></div>
      </div></section>

      <section className="cl-section cl-wrap cl-team-section" id="care-team">
        <div className="cl-section-head"><div><p className="cl-eyebrow">{S("Meet the care team", "ڈاکٹروں سے ملیں")}</p><h2>{S("Find the right person", "اپنے معائنے کے لیے")}<br /><em>{S("for your next visit.", "مناسب ڈاکٹر منتخب کریں")}</em></h2></div><div><p className="cl-muted">{S("Fictional consultant profiles from the connected demo. Real names, credentials and services are confirmed with each clinic.", "یہ مربوط ڈیمو کے فرضی ڈاکٹر ہیں۔ اصل نام، اسناد اور خدمات کلینک سے تصدیق کی جائیں گی۔")}</p><a className="cl-text-link" href={patient("doctors")} target={embedded ? "_top" : undefined}>{S("All consultants & availability", "تمام ڈاکٹر اور دستیاب اوقات")}<CareSymbol name="arrow" /></a></div></div>
        <div className="cl-doctor-grid">{doctors.map((doctor, i) => <article className="cl-doctor-card" key={doctor.id}>
          <div className={`cl-doctor-art art-${i % 4}`}><span className="cl-sample-tag">{S("Sample profile", "فرضی پروفائل")}</span><svg viewBox="0 0 240 190" fill="none" aria-hidden="true"><circle cx="120" cy="98" r="79" fill="currentColor" opacity=".1" /><path d="M42 190c4-45 38-68 78-68s74 23 78 68" fill="currentColor" opacity=".18" /><path d="m95 132 25 55 25-55" fill="white" opacity=".8" /><circle cx="120" cy="88" r="35" fill="currentColor" opacity=".24" /><path d="M90 87c0-38 59-45 65-6-21-4-40-13-51-19-1 10-5 18-14 25Z" fill="currentColor" opacity=".3" /><path d="M102 151v16c0 12 36 12 36 0v-16" stroke="currentColor" strokeWidth="3" opacity=".4" /><circle cx="138" cy="178" r="6" stroke="currentColor" strokeWidth="3" opacity=".4" /></svg><span className="cl-doctor-initials">{doctor.name.replace(/^Dr\. /, "").split(" ").map(n => n[0]).slice(0, 2).join("")}</span></div>
          <div className="cl-doctor-info"><p>{S(doctor.specialty, specialties[doctor.specialty] ?? doctor.specialty)}</p><h3 dir="auto">{doctor.name}</h3><small>{doctor.modes.map(mode => mode === "in_person" ? S("In person", "کلینک") : mode === "phone" ? S("Phone", "فون") : S("Video", "ویڈیو")).join(" · ")}</small><a href={patient("doctors", doctor.id)} target={embedded ? "_top" : undefined}>{S("View available times", "دستیاب اوقات دیکھیں")}<CareSymbol name="arrow" /></a></div>
        </article>)}</div>
        {!doctors.length && <div className="cl-directory-empty"><CareSymbol name="people" /><p>{S("Consultant profiles are being prepared. Open the patient portal to check the latest directory.", "ڈاکٹروں کے پروفائل تیار ہو رہے ہیں۔ تازہ فہرست مریض پورٹل میں دیکھیں۔")}</p><Button href={patient("doctors")}>{S("Check the directory", "ڈاکٹروں کی فہرست دیکھیں")}</Button></div>}
      </section>

      <section className="cl-section cl-wrap" id="care-how">
        <div className="cl-section-head"><div><p className="cl-eyebrow">{S("Three simple steps", "تین آسان مراحل")}</p><h2>{S("Less figuring it out.", "کم الجھن")}<br /><em>{S("More moving forward.", "آگے بڑھنے کا آسان راستہ")}</em></h2></div><Button href={bookingUrl} secondary>{S("Plan my appointment", "ملاقات طے کریں")}</Button></div>
        <div className="cl-steps">{[
          ["01", "people", S("Choose your consultant", "ڈاکٹر منتخب کریں"), S("Browse the directory, explore consultation modes and select a suitable time.", "ڈاکٹروں کی فہرست دیکھیں اور اپنی سہولت کے مطابق معائنے کا وقت منتخب کریں۔")],
          ["02", "calendar", S("Make the visit your own", "اپنی سہولت کے مطابق ملاقات"), S("Book in person, by phone or by video. Manage changes through the portal.", "کلینک، فون یا ویڈیو ملاقات بک کریں۔ پورٹل سے وقت تبدیل کر سکتے ہیں۔")],
          ["03", "record", S("Keep your care connected", "دیکھ بھال کا ریکارڈ رکھیں"), S("Return to published visit notes, sample reports and follow-up information.", "شائع شدہ نوٹس، نمونہ رپورٹس اور اگلی ملاقات کی معلومات دیکھیں۔")],
        ].map(([n, icon, title, text]) => <article key={n}><div><span>{n}</span><CareSymbol name={icon as SymbolName} /></div><h3>{title}</h3><p>{text}</p></article>)}</div>
      </section>

      {praise.length > 0 && <section className="cl-reviews-band"><div className="cl-section cl-wrap">
        <div className="cl-section-head"><div><p className="cl-eyebrow">{S("From the community", "مقامی لوگوں کی رائے")}</p><h2>{S("A few words from", "مقامی لوگوں کے")}<br /><em>{S("local patients.", "چند الفاظ")}</em></h2></div><p className="cl-muted">{S("Selected excerpts from the researched Google listing. Snapshot: " + date + ". View the full listing for all feedback.", "گوگل کی تحقیق شدہ فہرست سے منتخب اقتباسات۔ " + date + " کی معلومات۔ تمام آرا کے لیے مکمل فہرست دیکھیں۔")}</p></div>
        <div className="cl-review-grid">{praise.map((p, i) => <figure key={i}><span className="cl-quote-mark" aria-hidden="true">“</span><blockquote dir="auto">{p.quotes[0]}</blockquote><figcaption><span className="cl-review-dot"><CareSymbol name="chat" /></span><div><b>{S(p.theme_en, p.theme_ur)}</b><small>{S("Google review excerpt", "گوگل جائزے کا اقتباس")}</small></div></figcaption></figure>)}</div><a className="cl-text-link" href={mapsUrl} target="_blank" rel="noopener noreferrer">{S("Read the full Google listing", "گوگل کی مکمل فہرست دیکھیں")}<CareSymbol name="arrow" /></a>
      </div></section>}

      <section className="cl-section cl-wrap" id="care-visit">
        <div className="cl-section-head"><div><p className="cl-eyebrow">{S("Plan your visit", "ملاقات کی تیاری")}</p><h2>{S("Close to home.", "آپ کے قریب")}<br /><em>{S("Easy to find.", "پہنچنا آسان")}</em></h2></div><p className="cl-muted">{S("Check the listed hours and get directions before you travel. Consultant availability is shown separately in the patient portal.", "آنے سے پہلے درج اوقات اور راستہ دیکھیں۔ ڈاکٹر کے دستیاب اوقات مریض پورٹل میں الگ دکھائے جاتے ہیں۔")}</p></div>
        <div className="cl-visit-grid"><div className="cl-location"><div className="cl-map-art" aria-hidden="true"><svg viewBox="0 0 600 260" preserveAspectRatio="xMidYMid slice"><rect width="600" height="260" fill="currentColor" opacity=".05" /><path d="M0 40h600M0 170h600M110 0v260M410 0v260M0 260 350 0M245 0l100 260" stroke="currentColor" strokeWidth="22" opacity=".1" /><path d="M0 40h600M0 170h600M110 0v260M410 0v260M0 260 350 0M245 0l100 260" stroke="var(--cl-card)" strokeWidth="12" /><path d="M55 83h78v58H55zm380 111h113v48H435zM443 70h107v68H443zM145 192h73v51h-73z" fill="currentColor" opacity=".09" /></svg><span className="cl-map-pin"><CareSymbol name="pin" /></span><b>{city}</b></div><div className="cl-location-copy"><p className="cl-eyebrow">{S("Visit us in " + city, cityUr + " میں ہم تک پہنچیں")}</p><h3>{b.name}</h3><p dir="auto">{f.address || S("Address not recorded. Please ask the clinic team.", "پتہ درج نہیں ہے۔ کلینک سے پوچھیں۔")}</p>{f.extras.length > 0 && <ul>{f.extras.map(extra => <li key={extra}><CareSymbol name="check" /><span>{S(extra, extra.replace("Wheelchair accessible entrance", "وہیل چیئر کے لیے قابل رسائی داخلہ").replace("Wheelchair accessible parking lot", "وہیل چیئر کے لیے پارکنگ").replace("Wheelchair accessible restroom", "وہیل چیئر کے لیے قابل رسائی واش روم"))}</span></li>)}</ul>}<a className="cl-button secondary" href={mapsUrl} target="_blank" rel="noopener noreferrer">{S("Get directions on Google Maps", "گوگل میپس پر راستہ دیکھیں")}<CareSymbol name="arrow" /></a></div></div>
          <div className="cl-hours"><span className="cl-card-icon"><CareSymbol name="clock" /></span><h3>{S("Clinic hours", "کلینک کے اوقات")}</h3><p>{S("From the researched Google listing · PKT", "گوگل کی تحقیق شدہ فہرست کے مطابق · پاکستانی وقت")}</p><dl>{f.hours.map(({ day, hours }) => <div key={day}><dt>{S(day, weekdays[day] ?? day)}</dt><dd className={/closed/i.test(hours) ? "closed" : ""} dir="ltr">{S(hours, /closed/i.test(hours) ? "بند" : hours)}</dd></div>)}</dl>{!f.hours.length && <p className="cl-hours-empty">{S("Hours not recorded. Ask the clinic before travelling.", "اوقات درج نہیں ہیں۔ آنے سے پہلے کلینک سے پوچھیں۔")}</p>}<p className="cl-hours-note">{S("Listing snapshot: " + date + ". Please confirm changes with the clinic.", "فہرست کی معلومات: " + date + "۔ تبدیلی کی تصدیق کلینک سے کریں۔")}</p><a className="cl-text-link" href={chatUrl} target={embedded ? "_top" : undefined}>{S("Ask about your visit", "ملاقات کے بارے میں پوچھیں")}<CareSymbol name="arrow" /></a></div>
        </div>
      </section>

      <section className="cl-section cl-wrap cl-faq"><div><p className="cl-eyebrow">{S("Before your visit", "ملاقات سے پہلے")}</p><h2>{S("A little more", "کچھ مزید")}<br /><em>{S("peace of mind.", "وضاحت")}</em></h2><p className="cl-muted">{S("A few useful answers before you start.", "آغاز سے پہلے چند مفید جوابات۔")}</p><a className="cl-text-link" href={chatUrl} target={embedded ? "_top" : undefined}>{S("Have another question?", "کوئی اور سوال ہے؟")}<CareSymbol name="chat" /></a></div><div className="cl-faq-list">{[
          [S("How do I book an appointment?", "اپائنٹمنٹ کیسے بک کروں؟"), S("Open the patient portal, select a consultant and choose an available sample time. You can also start with the assistant. Bookings in this outreach preview are saved only in the demo.", "مریض پورٹل کھولیں، ڈاکٹر اور دستیاب نمونہ وقت منتخب کریں۔ اسسٹنٹ بھی مدد کر سکتا ہے۔ اس نمونے کی بکنگ صرف ڈیمو میں محفوظ ہوتی ہے۔")],
          [S("Can I speak to a doctor remotely?", "کیا فون یا ویڈیو پر بات ہو سکتی ہے؟"), S("The demo offers phone and video consultation modes alongside clinic visits. Calls are simulated in this preview. Real remote consultation services would be confirmed by the clinic.", "ڈیمو میں کلینک کے ساتھ فون اور ویڈیو کے طریقے موجود ہیں۔ اس نمونے کی کالز فرضی ہیں۔ اصل خدمات کلینک سے تصدیق کی جائیں گی۔")],
          [S("Where can I see my visit records?", "طبی ریکارڈ کہاں دیکھوں؟"), S("Published visit notes, sample prescriptions and reports appear in the Health records section of your patient portal. You can print a report or save it as a PDF.", "مریض پورٹل کے طبی ریکارڈ میں شائع شدہ نوٹس، نمونہ نسخے اور رپورٹس دیکھیں۔ رپورٹ پرنٹ یا پی ڈی ایف میں محفوظ کی جا سکتی ہے۔")],
          [S("Can I change an appointment?", "کیا ملاقات کا وقت بدل سکتا ہوں؟"), S("Use Appointments in the patient portal to reschedule to another available sample slot or cancel. The assistant and reception workspace use the same booking calendar.", "مریض پورٹل میں ملاقاتوں سے دستیاب وقت پر منتقل کریں یا منسوخ کریں۔ اسسٹنٹ اور استقبالیہ ایک ہی بکنگ کیلنڈر استعمال کرتے ہیں۔")],
          [S("Are these the clinic’s real doctors and services?", "کیا یہ کلینک کے اصل ڈاکٹر اور خدمات ہیں؟"), S("This is a private outreach template. Consultant profiles, service categories, bookings and medical records are illustrative. Business name, location, hours and Google rating come from the researched profile. Clinic information and staff would be verified before a public launch.", "یہ نجی آؤٹ ریچ ٹیمپلیٹ ہے۔ ڈاکٹر، خدمات، بکنگ اور طبی ریکارڈ فرضی ہیں۔ کاروبار کا نام، پتہ، اوقات اور گوگل ریٹنگ تحقیق شدہ پروفائل سے ہیں۔ اصل اجرا سے پہلے معلومات کی تصدیق ہوگی۔")],
        ].map(([question, answer]) => <details key={question}><summary>{question}<CareSymbol name="plus" /></summary><p>{answer}</p></details>)}</div></section>

      <section className="cl-wrap cl-last-section"><div className="cl-final-cta"><span className="cl-final-flower" aria-hidden="true">✳</span><div><p className="cl-eyebrow">{S("Make room for your health", "اپنی صحت کے لیے وقت نکالیں")}</p><h2>{S("Your next step", "آپ کا اگلا مرحلہ")}<br /><em>{S("starts here.", "یہاں سے شروع ہوتا ہے۔")}</em></h2></div><div><p>{S("A question, a consultation, a follow-up. Let’s make getting started a little easier.", "ایک سوال، معائنہ یا دوبارہ ملاقات۔ آغاز کو آسان بنائیں۔")}</p><div className="cl-actions"><Button href={bookingUrl}>{S("Book an appointment", "اپائنٹمنٹ بک کریں")}</Button><Button href={chatUrl} secondary>{S("Ask a question", "سوال پوچھیں")}</Button></div></div></div></section>
    </main>
    <footer className="cl-footer"><div className="cl-wrap"><div className="cl-footer-grid"><div><a className="cl-brand" href="#care-home"><span className="cl-brand-symbol"><CareSymbol name={dental ? "tooth" : "plus"} /></span><span>{b.name}</span></a><p>{S("Care in your community. Connected to you.", "آپ کے علاقے میں دیکھ بھال، آپ سے جڑی ہوئی۔")}</p></div><div><b>{S("Explore", "دیکھیں")}</b>{nav.map(([id, text]) => <a href={`#${id}`} key={id}>{text}</a>)}</div><div><b>{S("For patients", "مریضوں کے لیے")}</b>{[["appointments", S("Appointments", "ملاقاتیں")], ["records", S("Health records", "طبی ریکارڈ")], ["messages", S("Messages", "پیغامات")]].map(([tab, text]) => <a key={tab} href={patient(tab)} target={embedded ? "_top" : undefined}>{text}</a>)}</div><div><b>{S("Visit the clinic", "کلینک آئیں")}</b><p dir="auto">{f.address || S("Ask the clinic for directions.", "کلینک سے راستہ پوچھیں۔")}</p><a href={mapsUrl} target="_blank" rel="noopener noreferrer">{S("Google Maps", "گوگل میپس")} ↗</a></div></div><div className="cl-footer-bottom"><p>{S("Private concept by NexusPoint. One landing page, tailored to " + b.name + ".", "نیکسس پوائنٹ کا نجی نمونہ۔ " + b.name + " کے لیے ایک لینڈنگ پیج۔")}</p><a href={base + "#website"} target={embedded ? "_top" : undefined}>{S("Return to outreach report", "آؤٹ ریچ رپورٹ پر واپس")} ↗</a></div></div></footer>
  </div>;
}
