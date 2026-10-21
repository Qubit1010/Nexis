"use client";
// One-page project and listings site for a property agency or developer. Business facts come from
// the Google listing; listings, prices and imagery are labelled samples. The lead form writes a real
// lead into the demo's agent pipeline through /api/real-estate (action "enquiry").
import { useEffect, useRef, useState } from "react";
import type { Profile, Xray } from "@/lib/db";
import type { Lang } from "@/lib/i18n";
import { cityOf, cityUr } from "@/lib/city";
import { formatPkr, sizeLabel, type Listing } from "@/lib/real-estate-types";
import { visitorId } from "./ChatWindow";
import { PropertyArt, ReIcon } from "./RealEstateUI";
import "./real-estate-landing.css";

type Business = { slug: string; token: string; name: string; profile: Pick<Profile, "facts" | "city">; xray: Pick<Xray, "praise"> | null; created_at: string };
const weekdays: Record<string, string> = { Monday: "پیر", Tuesday: "منگل", Wednesday: "بدھ", Thursday: "جمعرات", Friday: "جمعہ", Saturday: "ہفتہ", Sunday: "اتوار" };
const kindNames: Record<string, [string, string]> = { plot: ["Plots", "پلاٹ"], house: ["Houses", "گھر"], apartment: ["Apartments", "اپارٹمنٹ"], commercial: ["Commercial", "کمرشل"], file: ["Files", "فائلیں"] };

export default function RealEstateLanding({ business: b, listings, listingsUnavailable = false, initialLang, embedded = false }: {
  business: Business; listings: Listing[]; listingsUnavailable?: boolean; initialLang: Lang; embedded?: boolean;
}) {
  const [lang, setLang] = useState(initialLang), [theme, setTheme] = useState("light"), [navOpen, setNavOpen] = useState(false), [kind, setKind] = useState("all");
  const [form, setForm] = useState({ name: "", budget: "", area: "", kind: "", size: "", timeline: "", overseas: "", message: "", listingId: "" });
  const [sending, setSending] = useState(false), [sent, setSent] = useState(false), [error, setError] = useState("");
  const retry = useRef("");
  const ur = lang === "ur", S = (en: string, u: string) => (ur ? u : en);
  const f = b.profile.facts, city = cityOf(b.profile), cityName = S(city, cityUr(city));
  const q = `?t=${encodeURIComponent(b.token)}${ur ? "&lang=ur" : ""}`, top = embedded ? "_top" : undefined;
  const hub = `/d/${b.slug}${q}`, buyer = (extra = "") => `/d/${b.slug}/buyer${q}${extra}`;
  const visitUrl = (listing?: string) => buyer(`&tab=listings&visit=1${listing ? "&listing=" + listing : ""}`), chatUrl = buyer("&tab=messages");
  const mapsUrl = /^https:\/\/(www\.)?google\.com\/maps\//.test(f.maps_url) ? f.maps_url : `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(f.address || b.name)}`;
  const shown = listings.filter((l) => kind === "all" || l.kind === kind);
  const societies = [...new Set(listings.map((l) => l.society))];
  const praise = b.xray?.praise.filter((p) => p.quotes.length).slice(0, 3) ?? [];
  const nav: [string, string][] = [["re-listings", S("Listings", "لسٹنگز")], ["re-how", S("How it works", "طریقہ کار")], ["re-overseas", S("Overseas buyers", "بیرون ملک خریدار")], ["re-enquire", S("Enquire", "انکوائری")], ["re-visit", S("Visit us", "دفتر")]];

  useEffect(() => { try { const t = localStorage.getItem("np-website-theme"); if (t === "light" || t === "dark") setTheme(t); } catch {} retry.current = crypto.randomUUID(); }, []);
  useEffect(() => { retry.current = crypto.randomUUID(); }, [form]);
  function changeLang() { const n = ur ? "en" : "ur"; setLang(n); setNavOpen(false); const u = new URL(location.href); if (n === "ur") u.searchParams.set("lang", "ur"); else u.searchParams.delete("lang"); history.replaceState(null, "", u); }
  function changeTheme() { const n = theme === "light" ? "dark" : "light"; setTheme(n); try { localStorage.setItem("np-website-theme", n); } catch {} }
  const set = (k: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => setForm({ ...form, [k]: e.target.value });
  function enquireAbout(l: Listing) {
    setForm({ ...form, listingId: l.id, area: l.society, kind: l.kind, size: sizeLabel(l), message: form.message || `Interested in ${l.code}, ${l.title}.` });
    document.getElementById("re-enquire")?.scrollIntoView({ behavior: "smooth" });
  }
  async function submit(e: React.FormEvent) {
    e.preventDefault(); setError(""); setSending(true);
    try {
      const r = await fetch("/api/real-estate", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({
        slug: b.slug, t: b.token, visitor: visitorId(b.slug), role: "buyer", action: "enquiry", requestId: retry.current, name: form.name.trim(),
        ...(form.budget ? { budget: Number(form.budget) } : {}), area: form.area, kind: form.kind, size: form.size, timeline: form.timeline, message: form.message,
        ...(form.overseas ? { overseas: form.overseas !== "Pakistan", country: form.overseas } : {}), ...(form.listingId ? { listingId: form.listingId } : {}) }) });
      const d = await r.json();
      if (!r.ok) throw new Error(d.error ?? S("Could not send. Please try again.", "بھیجا نہیں جا سکا۔ دوبارہ کوشش کریں۔"));
      setSent(true);
    } catch (err) { setError(err instanceof Error ? err.message : S("Connection problem", "کنکشن کا مسئلہ")); }
    finally { setSending(false); }
  }
  const A = ({ href, children, ghost = false }: { href: string; children: React.ReactNode; ghost?: boolean }) =>
    <a className={`el-btn${ghost ? " ghost" : ""}`} href={href} target={href.startsWith("#") ? undefined : top}>{children}<ReIcon name="arrow" /></a>;

  return <div className="el" lang={lang} dir={ur ? "rtl" : "ltr"} data-estate-theme={theme}>
    <a className="el-skip" href="#re-main">{S("Skip to content", "مواد پر جائیں")}</a>
    <div className="el-strip"><span>{S("Private website preview", "نجی ویب سائٹ نمونہ")} · {S("Sample listings, prices and illustrations", "نمونہ لسٹنگز، قیمتیں اور خاکے")}</span><a href={hub} target={top}>{S("Back to your report", "اپنی رپورٹ پر واپس")} ↗</a></div>
    <header className="el-header"><div className="el-wrap el-header-row">
      <a className="el-brand" href="#re-main"><span className="el-mark"><ReIcon name="home" /></span><span><b>{b.name}</b><small>{f.category ? f.category + " · " : ""}{cityName}</small></span></a>
      <nav className={`el-nav${navOpen ? " open" : ""}`} id="el-nav" aria-label={S("Page navigation", "صفحے کی نیویگیشن")}>{nav.map(([id, t]) => <a key={id} href={"#" + id} onClick={() => setNavOpen(false)}>{t}</a>)}</nav>
      <div className="el-tools">
        <button type="button" className="el-icon" onClick={changeLang} aria-label={S("Read in Urdu", "Read in English")}>{ur ? "EN" : "اردو"}</button>
        <button type="button" className="el-icon" onClick={changeTheme} aria-label={S("Switch theme", "تھیم بدلیں")}><ReIcon name="sun" /></button>
        <a className="el-btn small el-desktop" href={visitUrl()} target={top}>{S("Book a site visit", "سائٹ وزٹ بک کریں")}</a>
        <button type="button" className="el-icon el-menu" onClick={() => setNavOpen(!navOpen)} aria-expanded={navOpen} aria-controls="el-nav" aria-label={S("Menu", "مینو")}><ReIcon name={navOpen ? "close" : "settings"} /></button>
      </div>
    </div></header>

    <main id="re-main">
      <section className="el-wrap el-hero">
        <div className="el-hero-copy">
          <p className="el-kicker">{S(`Plots, homes and investments in ${city}`, `${cityUr(city)} میں پلاٹ، گھر اور سرمایہ کاری`)}</p>
          <h1>{S("Find the right property.", "درست پراپرٹی تلاش کریں۔")}<br /><em>{S("See it before you decide.", "فیصلے سے پہلے خود دیکھیں۔")}</em></h1>
          <p className="el-lead">{S("Tell ", "")}<b>{b.name}</b>{S(" your budget, society and size. You get matching options and a site-visit time with an agent, whether you are across town or overseas.", " کو اپنا بجٹ، سوسائٹی اور سائز بتائیں۔ آپ کو موزوں آپشنز اور ایجنٹ کے ساتھ سائٹ وزٹ کا وقت ملے گا، چاہے آپ شہر میں ہوں یا بیرون ملک۔")}</p>
          <div className="el-actions"><A href="#re-listings">{S("View listings", "لسٹنگز دیکھیں")}</A><A href={visitUrl()} ghost>{S("Book a site visit", "سائٹ وزٹ بک کریں")}</A></div>
          <ul className="el-proof">
            {f.rating != null && <li><b>{f.rating.toFixed(1)}★</b><span>{f.reviews != null ? S(`${f.reviews.toLocaleString("en-US")} Google reviews`, `${f.reviews.toLocaleString("en-US")} گوگل ریویوز`) : S("Google rating", "گوگل ریٹنگ")}</span></li>}
            <li><b>{S("< 1 min", "1 منٹ")}</b><span>{S("Reply on WhatsApp, day or night", "واٹس ایپ پر جواب، دن ہو یا رات")}</span></li>
            <li><b>{S("Gulf · UK", "خلیج · برطانیہ")}</b><span>{S("Overseas buyers welcome", "بیرون ملک خریداروں کا خیرمقدم")}</span></li>
          </ul>
        </div>
        <figure className="el-hero-art"><PropertyArt kind="house" /><figcaption>{S("Illustration only. Your projects and photography go here.", "صرف خاکہ۔ یہاں آپ کے پروجیکٹ اور تصاویر ہوں گی۔")}</figcaption>
          <a className="el-float" href={chatUrl} target={top}><ReIcon name="chat" /><span><small>{S("Ask the assistant", "اسسٹنٹ سے پوچھیں")}</small><b>{S("“10 marla in DHA, 2.5 crore?”", "”ڈی ایچ اے میں دس مرلہ، ڈھائی کروڑ؟“")}</b></span></a></figure>
      </section>

      <section className="el-wrap el-section" id="re-listings">
        <div className="el-head"><div><p className="el-kicker">01 · {S("Current listings", "موجودہ لسٹنگز")}</p><h2>{S("Plots and homes,", "پلاٹ اور گھر،")} <em>{S("ready to visit.", "دیکھنے کے لیے تیار۔")}</em></h2></div>
          <p>{S("A sample selection for this preview. Every card can turn into a site visit or a question to an agent.", "اس نمونے کے لیے منتخب لسٹنگز۔ ہر کارڈ سے سائٹ وزٹ یا ایجنٹ سے سوال کیا جا سکتا ہے۔")} <span className="el-label">{S("Fictional listings & prices", "فرضی لسٹنگز اور قیمتیں")}</span></p></div>
        <div className="el-filters" role="group" aria-label={S("Property type", "پراپرٹی کی قسم")}><button type="button" aria-pressed={kind === "all"} onClick={() => setKind("all")}>{S("All", "تمام")}</button>{Object.keys(kindNames).filter((k) => listings.some((l) => l.kind === k)).map((k) => <button type="button" key={k} aria-pressed={kind === k} onClick={() => setKind(k)}>{S(kindNames[k][0], kindNames[k][1])}</button>)}</div>
        {shown.length ? <div className="el-grid">{shown.map((l) => <article className={`el-card ${l.status}`} key={l.id}>
          <div className="el-card-art"><PropertyArt kind={l.art || l.kind} /><span className="el-code">{l.code}</span>{l.status !== "available" && <span className="el-tag">{l.status === "reserved" ? S("Reserved", "ریزرو") : S("Sold", "فروخت")}</span>}</div>
          <div className="el-card-body"><small>{ur ? l.society_ur || l.society : l.society}{l.block ? " · " + l.block : ""}</small><h3 dir="auto">{ur ? l.title_ur || l.title : l.title}</h3>
            <p className="el-specs"><span>{sizeLabel(l, ur ? "ur" : "en")}</span>{l.beds != null && <span>{l.beds} {S("bed", "بیڈ")}</span>}{l.baths != null && <span>{l.baths} {S("bath", "باتھ")}</span>}</p>
            <p dir="auto">{ur ? l.description_ur || l.description : l.description}</p>
            <div className="el-card-foot"><div><small>{S("Sample demand", "نمونہ ڈیمانڈ")}</small><b>{formatPkr(l.price, ur ? "ur" : "en")}</b></div>
              <div className="el-card-actions"><button type="button" className="el-text" onClick={() => enquireAbout(l)}>{S("Enquire", "انکوائری")}</button>{l.status !== "sold" && <a className="el-btn small" href={visitUrl(l.id)} target={top}>{S("Visit", "وزٹ")}</a>}</div></div></div>
        </article>)}</div> : <div className="el-empty" role={listingsUnavailable ? "alert" : "status"}><h3>{listingsUnavailable ? S("Listings are temporarily unavailable", "لسٹنگز فی الحال دستیاب نہیں") : S("No listings in this category", "اس قسم میں کوئی لسٹنگ نہیں")}</h3><A href={chatUrl}>{S("Ask the assistant", "اسسٹنٹ سے پوچھیں")}</A></div>}
      </section>

      <section className="el-band" id="re-how"><div className="el-wrap el-section">
        <div className="el-head"><div><p className="el-kicker">02 · {S("How it works", "طریقہ کار")}</p><h2>{S("From a first message", "پہلے پیغام سے")} <em>{S("to the site visit.", "سائٹ وزٹ تک۔")}</em></h2></div></div>
        <ol className="el-steps">{([
          ["chat", S("Tell us what you need", "اپنی ضرورت بتائیں"), S("Budget, society, plot size and timeline, on WhatsApp or the form below. In English, Urdu or Roman Urdu.", "بجٹ، سوسائٹی، پلاٹ سائز اور وقت، واٹس ایپ یا نیچے فارم پر۔ انگریزی، اردو یا رومن اردو میں۔")],
          ["bolt", S("Get options within a minute", "ایک منٹ میں آپشنز"), S("Matching listings straight away, any hour. An agent picks up with your requirements already on file.", "کسی بھی وقت فوراً موزوں لسٹنگز۔ ایجنٹ آپ کی ضروریات پہلے سے جان کر بات کرتا ہے۔")],
          ["calendar", S("Visit with an agent", "ایجنٹ کے ساتھ وزٹ"), S("Choose a free time and an agent meets you at the site. Documents and approvals are checked by the agent.", "خالی وقت منتخب کریں، ایجنٹ آپ سے سائٹ پر ملے گا۔ کاغذات اور منظوری ایجنٹ چیک کرے گا۔")],
        ] as const).map(([icon, t, d], i) => <li key={icon}><span className="el-step-n">0{i + 1}</span><ReIcon name={icon} /><h3>{t}</h3><p>{d}</p></li>)}</ol>
      </div></section>

      <section className="el-wrap el-section el-overseas" id="re-overseas">
        <div><p className="el-kicker">03 · {S("Overseas Pakistanis", "بیرون ملک پاکستانی")}</p><h2>{S("Buying from Dubai, Riyadh", "دبئی، ریاض یا لندن سے")}<br /><em>{S("or London?", "خریداری؟")}</em></h2>
          <p>{S("Message whenever it suits your time zone. We note your requirements, line up options before you land, and book the visit for your trip home.", "اپنے وقت کے مطابق کسی بھی وقت پیغام بھیجیں۔ ہم آپ کی ضروریات نوٹ کر کے آپ کے آنے سے پہلے آپشنز تیار رکھتے ہیں اور آپ کے دورے کے لیے وزٹ بک کرتے ہیں۔")}</p>
          <div className="el-actions"><A href={chatUrl}>{S("Message the assistant", "اسسٹنٹ کو پیغام بھیجیں")}</A></div></div>
        <ul className="el-checks">{[S("Replies in your time zone, day or night", "آپ کے وقت کے مطابق، دن ہو یا رات"), S("One agent who knows your file", "ایک ایجنٹ جو آپ کی تفصیل جانتا ہو"), S("Site visit booked around your trip", "آپ کے سفر کے مطابق سائٹ وزٹ"), S("NOC and transfer questions answered by an agent, with documents", "این او سی اور انتقال کے سوالات کا جواب ایجنٹ کاغذات کے ساتھ دیتا ہے")].map((t) => <li key={t}><ReIcon name="check" />{t}</li>)}</ul>
      </section>

      {praise.length > 0 && <section className="el-band"><div className="el-wrap el-section">
        <div className="el-head"><div><p className="el-kicker">04 · {S("From Google reviews", "گوگل ریویوز سے")}</p><h2>{S("What clients", "کلائنٹس")} <em>{S("say.", "کیا کہتے ہیں۔")}</em></h2></div></div>
        <div className="el-quotes">{praise.map((p, i) => <figure key={i}><blockquote dir="auto">“{p.quotes[0].length > 180 ? p.quotes[0].slice(0, 180) + "…" : p.quotes[0]}”</blockquote><figcaption>{S(p.theme_en, p.theme_ur)} · {S("Google review excerpt", "گوگل ریویو کا اقتباس")}</figcaption></figure>)}</div>
      </div></section>}

      <section className="el-wrap el-section el-enquire" id="re-enquire">
        <div className="el-enquire-copy"><p className="el-kicker">{S("Enquire", "انکوائری")}</p><h2>{S("Tell us what", "بتائیں آپ")}<br /><em>{S("you are looking for.", "کیا تلاش کر رہے ہیں۔")}</em></h2>
          <p>{S("Your enquiry goes straight to an agent's pipeline with a summary, so nobody asks you the same question twice.", "آپ کی انکوائری خلاصے کے ساتھ سیدھی ایجنٹ کی پائپ لائن میں جاتی ہے، تاکہ کوئی ایک ہی سوال دو بار نہ پوچھے۔")}</p>
          <small>{S("Demo form: use a sample name. Nothing is sent outside this preview.", "ڈیمو فارم: نمونہ نام استعمال کریں۔ کچھ بھی اس نمونے سے باہر نہیں جاتا۔")}</small></div>
        {sent ? <div className="el-form el-sent" role="status"><ReIcon name="check" /><h3>{S("Received. An agent has it.", "موصول۔ ایجنٹ تک پہنچ گئی۔")}</h3><p>{S("Your enquiry is now a lead in the agent pipeline, with an assistant summary. Pick a site-visit time next.", "آپ کی انکوائری اب اسسٹنٹ کے خلاصے کے ساتھ ایجنٹ پائپ لائن میں ہے۔ اب سائٹ وزٹ کا وقت منتخب کریں۔")}</p>
          <div className="el-actions"><A href={visitUrl(form.listingId || undefined)}>{S("Book a site visit", "سائٹ وزٹ بک کریں")}</A><A href={`/d/${b.slug}/agents${q}`} ghost>{S("See it in the agent pipeline", "ایجنٹ پائپ لائن میں دیکھیں")}</A></div></div>
          : <form className="el-form" onSubmit={submit}>
            {error && <p className="el-error" role="alert">{error}</p>}
            <label>{S("Name", "نام")}<input required minLength={2} maxLength={80} value={form.name} onChange={set("name")} placeholder={S("Sample name", "نمونہ نام")} /></label>
            <label>{S("Budget", "بجٹ")}<select value={form.budget} onChange={set("budget")}><option value="">{S("Choose", "منتخب کریں")}</option>{[5e6, 1e7, 2.5e7, 5e7, 1e8].map((n) => <option key={n} value={n}>{S("Up to ", "تک ")}{formatPkr(n, ur ? "ur" : "en")}</option>)}</select></label>
            <label>{S("Society or area", "سوسائٹی یا علاقہ")}<select value={form.area} onChange={set("area")}><option value="">{S("Open to suggestions", "تجاویز چاہییں")}</option>{societies.map((x) => <option key={x} value={x}>{x}</option>)}</select></label>
            <label>{S("Type", "قسم")}<select value={form.kind} onChange={set("kind")}><option value="">{S("Any", "کوئی بھی")}</option>{Object.entries(kindNames).map(([k, [en, u]]) => <option key={k} value={k}>{S(en, u)}</option>)}</select></label>
            <label>{S("Size", "سائز")}<input maxLength={40} value={form.size} onChange={set("size")} placeholder={S("e.g. 10 marla", "مثلاً دس مرلہ")} /></label>
            <label>{S("When are you buying?", "کب تک خریدنا ہے؟")}<select value={form.timeline} onChange={set("timeline")}><option value="">{S("Choose", "منتخب کریں")}</option>{[["Ready now", "ابھی"], ["1-3 months", "ایک سے تین مہینے"], ["This year", "اس سال"], ["Exploring, no fixed date", "صرف دیکھ رہا ہوں"]].map(([v, u]) => <option key={v} value={v}>{S(v, u)}</option>)}</select></label>
            <label>{S("Where are you now?", "آپ اس وقت کہاں ہیں؟")}<select value={form.overseas} onChange={set("overseas")}><option value="">{S("Choose", "منتخب کریں")}</option>{[["Pakistan", "پاکستان"], ["UAE", "متحدہ عرب امارات"], ["Saudi Arabia", "سعودی عرب"], ["UK", "برطانیہ"], ["Other", "کوئی اور ملک"]].map(([v, u]) => <option key={v} value={v}>{S(v, u)}</option>)}</select></label>
            <label className="full">{S("Message (optional)", "پیغام (اختیاری)")}<textarea maxLength={500} value={form.message} onChange={set("message")} /></label>
            <button className="el-btn full" disabled={sending || form.name.trim().length < 2}>{sending ? S("Sending…", "بھیجا جا رہا ہے…") : S("Send enquiry", "انکوائری بھیجیں")}<ReIcon name="arrow" /></button>
          </form>}
      </section>

      <section className="el-band" id="re-visit"><div className="el-wrap el-section el-visit">
        <div><p className="el-kicker">05 · {S("Visit the office", "دفتر تشریف لائیں")}</p><h2>{b.name}</h2><p dir="auto">{f.address || S("Ask an agent for directions.", "راستے کے لیے ایجنٹ سے پوچھیں۔")}</p><a className="el-text" href={mapsUrl} target="_blank" rel="noopener noreferrer">{S("Directions on Google Maps", "گوگل میپس پر راستہ")} ↗</a></div>
        <div><h3>{S("Office hours", "دفتری اوقات")}</h3>{f.hours.length ? <dl>{f.hours.map((h) => <div key={h.day}><dt>{ur ? weekdays[h.day] ?? h.day : h.day}</dt><dd dir="ltr">{h.hours}</dd></div>)}</dl> : <p>{S("Hours are not listed on Google. Message us before visiting.", "گوگل پر اوقات درج نہیں۔ آنے سے پہلے پیغام بھیجیں۔")}</p>}<small>{S("From the Google listing · Pakistan Standard Time", "گوگل لسٹنگ سے · پاکستان کا وقت")}</small></div>
      </div></section>

      <section className="el-wrap el-section el-faq"><div><p className="el-kicker">{S("Questions", "سوالات")}</p><h2>{S("Before you", "رابطے سے")} <em>{S("get in touch.", "پہلے۔")}</em></h2></div><div>{[
        [S("Are these real listings and prices?", "کیا یہ اصل لسٹنگز اور قیمتیں ہیں؟"), S("No. This preview uses fictional sample listings and demand prices. Your own inventory and approved prices replace them at launch.", "نہیں۔ اس نمونے میں فرضی لسٹنگز اور قیمتیں ہیں۔ لانچ پر آپ کی اپنی لسٹنگز اور منظور شدہ قیمتیں ہوں گی۔")],
        [S("Can the assistant confirm NOC or approval status?", "کیا اسسٹنٹ این او سی یا منظوری کی تصدیق کر سکتا ہے؟"), S("No. Legal, NOC, transfer and tax questions always go to an agent, who checks the documents for that exact property.", "نہیں۔ قانونی، این او سی، انتقال اور ٹیکس کے سوال ہمیشہ ایجنٹ کو جاتے ہیں، جو اسی پراپرٹی کے کاغذات دیکھتا ہے۔")],
        [S("Can I book a visit from abroad?", "کیا بیرون ملک سے وزٹ بک ہو سکتا ہے؟"), S("Yes. Pick any free time in the next two weeks, or tell the assistant your travel dates and an agent arranges a later visit.", "جی۔ اگلے دو ہفتوں میں کوئی بھی خالی وقت منتخب کریں، یا اسسٹنٹ کو اپنے سفر کی تاریخیں بتائیں اور ایجنٹ بعد کا وزٹ طے کرے گا۔")],
        [S("Are the prices final?", "کیا قیمتیں حتمی ہیں؟"), S("Final prices, discounts and payment plans are only confirmed by an agent.", "آخری قیمت، رعایت اور قسطوں کا پلان صرف ایجنٹ کنفرم کرتا ہے۔")],
      ].map(([qq, a]) => <details key={qq}><summary>{qq}<span aria-hidden="true">+</span></summary><p>{a}</p></details>)}</div></section>
    </main>
    <footer className="el-wrap el-footer"><div><b>{b.name}</b><p>{f.neighborhood ? f.neighborhood + " · " : ""}{S(city + ", Pakistan", cityUr(city) + "، پاکستان")}</p></div>
      <nav aria-label={S("Footer navigation", "فوٹر نیویگیشن")}><a href="#re-listings">{S("Listings", "لسٹنگز")}</a><a href={visitUrl()} target={top}>{S("Site visits", "سائٹ وزٹس")}</a><a href={chatUrl} target={top}>{S("Ask a question", "سوال پوچھیں")}</a></nav>
      <div className="el-footer-bottom"><span>{S("Website concept by NexusPoint", "NexusPoint کا ویب سائٹ نمونہ")}</span><span>{S("Sample listings and illustrations. A private outreach preview.", "نمونہ لسٹنگز اور خاکے۔ نجی آؤٹ ریچ پیش منظر۔")}</span><a href={hub} target={top}>{S("Your report", "آپ کی رپورٹ")} ↗</a></div></footer>
  </div>;
}
