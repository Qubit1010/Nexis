"use client";

import { useEffect, useState } from "react";
import type { Profile, Xray } from "@/lib/db";
import type { Lang } from "@/lib/i18n";
import type { MenuItem } from "@/lib/restaurant-types";
import { money } from "@/lib/restaurant-types";
import { FoodArt } from "./RestaurantUI";
import "./restaurant-landing.css";

export type LandingMenuItem = Omit<MenuItem, "allergens">;
type Business = { slug: string; token: string; name: string; profile: Pick<Profile, "facts">; xray: Pick<Xray, "praise"> | null; created_at: string };
type SymbolName = "arrow" | "pin" | "clock" | "table" | "bag" | "chat" | "sun" | "menu" | "close" | "search" | "dish";
function Symbol({ name }: { name: SymbolName }) {
  const paths: Record<SymbolName, React.ReactNode> = {
    arrow: <path d="M4 12h16m-6-6 6 6-6 6" />,
    pin: <><path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 1 1 16 0Z" /><circle cx="12" cy="10" r="2.5" /></>,
    clock: <><circle cx="12" cy="12" r="9" /><path d="M12 6v6l4 2" /></>,
    table: <><rect x="3" y="7" width="18" height="10" rx="2" /><path d="M7 3v4m10-4v4M7 17v4m10-4v4" /></>,
    bag: <><path d="M5 8h14l2 13H3ZM8 8V6a4 4 0 0 1 8 0v2" /><path d="M8 12h.01M16 12h.01" /></>,
    chat: <><path d="M21 11a9 9 0 0 1-9 9c-1.5 0-3-.4-4.2-1L3 21l1.3-5A9 9 0 1 1 21 11Z" /><path d="M8 10h8m-8 4h5" /></>,
    sun: <><circle cx="12" cy="12" r="4" /><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1 1m12 12 1 1M5 19l1-1M18 6l1-1" /></>,
    menu: <path d="M4 6h16M4 12h16M4 18h16" />,
    close: <path d="m6 6 12 12M6 18 18 6" />,
    search: <><circle cx="10" cy="10" r="6" /><path d="m15 15 6 6" /></>,
    dish: <><path d="M3 16h18M5 16a7 7 0 0 1 14 0M12 6V3M2 20h20" /><circle cx="12" cy="3" r="1" /></>,
  };
  return <svg className="rl-symbol" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]}</svg>;
}
function Flourish({ className = "" }: { className?: string }) {
  return <svg className={`rl-flourish ${className}`} viewBox="0 0 100 100" fill="none" aria-hidden="true">{Array.from({ length: 12 }, (_, i) => <path key={i} d="M50 8v27" stroke="currentColor" strokeWidth="8" transform={`rotate(${i * 30} 50 50)`} />)}</svg>;
}
const categoryUr: Record<string, string> = { Karahi: "کڑاہی", Grill: "گرل", Sides: "ساتھ کے کھانے", Drinks: "مشروبات" };
const descriptionUr: Record<string, string> = {
  "Chicken karahi": "ٹماٹر، ادرک اور ہری مرچ کے ساتھ چکن کا نمونہ حصہ۔",
  "Mutton karahi": "روایتی کڑاہی میں تیار مٹن کا نمونہ حصہ۔",
  "Chicken sajji": "بلوچستان کی طرز کی سجی، خوشبودار چاول کے ساتھ۔",
  "BBQ platter": "تکہ اور سیخ کباب کی نمونہ پلیٹر۔",
  "Vegetable rice": "موسمی سبزیوں کے ساتھ چاول، سبزی خور نمونہ انتخاب۔",
  "Butter naan": "مکھن کے ساتھ تازہ نان۔", Raita: "کھیرا اور ہری جڑی بوٹیوں کے ساتھ دہی۔",
  "Karak tea": "دودھ کی کڑک چائے کا گرم کپ۔", "Fresh lime": "لیموں اور ٹھنڈے پانی کا تازہ مشروب۔",
};
const weekdays: Record<string, string> = { Monday: "پیر", Tuesday: "منگل", Wednesday: "بدھ", Thursday: "جمعرات", Friday: "جمعہ", Saturday: "ہفتہ", Sunday: "اتوار" };
const photos: Record<string, string> = { "Chicken karahi": "karahi", "Chicken sajji": "sajji", "BBQ platter": "feast" };
const featured = ["Chicken karahi", "Chicken sajji", "BBQ platter", "Mutton karahi", "Vegetable rice", "Butter naan", "Raita", "Karak tea", "Fresh lime"];

export default function RestaurantLanding({ business: b, menu: dishes, menuUnavailable = false, initialLang, embedded = false }: {
  business: Business; menu: LandingMenuItem[]; menuUnavailable?: boolean; initialLang: Lang; embedded?: boolean;
}) {
  const [lang, setLang] = useState(initialLang);
  const [theme, setTheme] = useState("light");
  const [navOpen, setNavOpen] = useState(false);
  const [category, setCategory] = useState("All");
  const [query, setQuery] = useState("");
  const [showAll, setShowAll] = useState(false);
  const S = (en: string, ur: string) => lang === "ur" ? ur : en;
  const f = b.profile.facts;
  const base = `/d/${b.slug}?t=${encodeURIComponent(b.token)}${lang === "ur" ? "&lang=ur" : ""}`;
  const customer = (tab: string, item?: string) => `/d/${b.slug}/customer?t=${encodeURIComponent(b.token)}&tab=${tab}${item ? "&item=" + encodeURIComponent(item) : ""}${lang === "ur" ? "&lang=ur" : ""}`;
  const reserveUrl = customer("reservations") + "&reserve=1";
  const menuUrl = customer("menu");
  const chatUrl = customer("messages");
  const mapsUrl = /^https:\/\/(www\.)?google\.com\/maps\//.test(f.maps_url) ? f.maps_url : `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(f.address || b.name)}`;
  const rank = (m: LandingMenuItem) => featured.includes(m.name) ? featured.indexOf(m.name) : featured.length;
  const filtered = [...dishes].sort((a, b) => rank(a) - rank(b)).filter(m => (category === "All" || m.category === category) && `${m.name} ${m.name_ur} ${m.category}`.toLowerCase().includes(query.trim().toLowerCase()));
  const visible = showAll || category !== "All" || query.trim() ? filtered : filtered.slice(0, 6);
  const praise = b.xray?.praise.filter(p => p.quotes.length).slice(0, 3) ?? [];
  const snapshot = new Date(b.created_at).toLocaleDateString(lang === "ur" ? "ur-PK" : "en-GB", { month: "long", year: "numeric", timeZone: "Asia/Karachi" });
  const nav = [["food-menu", S("The menu", "مینو")], ["food-story", S("Around the table", "ہمارے ساتھ")], ["food-reviews", S("Guest words", "ریویوز")], ["food-visit", S("Find us", "راستہ")]];

  useEffect(() => {
    try { const saved = localStorage.getItem("np-website-theme"); if (saved === "light" || saved === "dark") setTheme(saved); } catch {}
  }, []);
  function changeLang() {
    const next = lang === "en" ? "ur" : "en"; setLang(next); setNavOpen(false);
    const url = new URL(location.href);
    if (next === "ur") url.searchParams.set("lang", "ur"); else url.searchParams.delete("lang");
    history.replaceState(null, "", url);
  }
  function changeTheme() {
    const next = theme === "light" ? "dark" : "light"; setTheme(next);
    try { localStorage.setItem("np-website-theme", next); } catch {}
  }
  const Link = ({ href, children, secondary = false }: { href: string; children: React.ReactNode; secondary?: boolean }) =>
    <a className={`rl-button${secondary ? " secondary" : ""}`} href={href} target={embedded ? "_top" : undefined}>{children}<Symbol name="arrow" /></a>;
  const Photo = ({ name, alt, className = "" }: { name: string; alt: string; className?: string }) =>
    // Generated, illustrative food photography. The restaurant has not supplied photos.
    // eslint-disable-next-line @next/next/no-img-element
    <img className={className} src={`/restaurant/${name}.webp`} alt={alt} width="1536" height="1024" loading="lazy" />;

  return <div className="rl" lang={lang} dir={lang === "ur" ? "rtl" : "ltr"} data-food-theme={theme}>
    <a className="rl-skip" href="#food-main">{S("Skip to content", "مواد پر جائیں")}</a>
    <div className="rl-preview-strip"><span>{S("Private landing page preview", "نجی لینڈنگ پیج نمونہ")} <b>·</b> {S("Sample menu, prices & photography", "نمونہ مینو، قیمتیں اور تصاویر")}</span><a href={base} target={embedded ? "_top" : undefined}>{S("Back to your report", "اپنی رپورٹ پر واپس")} ↗</a></div>
    <header className="rl-header">
      <div className="rl-wrap rl-header-row">
        <a className="rl-brand" href="#food-main" aria-label={b.name + S(" home", " ہوم")}><span className="rl-brand-mark"><Symbol name="dish" /></span><span><b>{b.name}</b><small>{f.neighborhood ? f.neighborhood + " · " : ""}{S("Quetta", "کوئٹہ")}</small></span></a>
        <nav className={`rl-nav ${navOpen ? "open" : ""}`} id="food-navigation" aria-label={S("Page navigation", "صفحے کی نیویگیشن")}>{nav.map(([id, label]) => <a key={id} href={"#" + id} onClick={() => setNavOpen(false)}>{label}</a>)}<a className="rl-nav-reserve" href={reserveUrl} target={embedded ? "_top" : undefined}>{S("Book a table", "میز بک کریں")} ↗</a></nav>
        <div className="rl-tools">
          <button type="button" className="rl-icon-button" onClick={changeLang} aria-label={S("Read in Urdu", "Read in English")}>{lang === "en" ? "اردو" : "EN"}</button>
          <button type="button" className="rl-icon-button" onClick={changeTheme} aria-label={S("Switch to " + (theme === "light" ? "dark" : "light") + " theme", theme === "light" ? "گہری تھیم منتخب کریں" : "ہلکی تھیم منتخب کریں")}><Symbol name="sun" /></button>
          <button type="button" className="rl-icon-button rl-mobile-toggle" onClick={() => setNavOpen(!navOpen)} aria-controls="food-navigation" aria-expanded={navOpen} aria-label={S("Toggle navigation", "نیویگیشن کھولیں یا بند کریں")}><Symbol name={navOpen ? "close" : "menu"} /></button>
        </div>
      </div>
    </header>
    <main id="food-main">
      <section className="rl-wrap rl-hero">
        <div className="rl-hero-copy"><p className="rl-kicker"><span />{S("A place at the table, in Quetta", "کوئٹہ میں، آپ کے لیے ایک میز")}</p><h1>{S("Good food.", "اچھا کھانا۔")}<br /><em>{S("Great company.", "اچھا ساتھ۔")}</em></h1><p className="rl-lead">{S("For the meals that turn into moments. Explore the flavours, gather your people and make yourself at home at ", "وہ کھانا جو یادگار لمحہ بن جائے۔ پسندیدہ ذائقے منتخب کریں اور اپنوں کے ساتھ آئیں، ")}<b>{b.name}</b>.</p><div className="rl-actions"><Link href="#food-menu">{S("Explore the menu", "مینو دیکھیں")}</Link><Link href={reserveUrl} secondary>{S("Book a table", "میز بک کریں")}</Link></div><p className="rl-micro">{S("Try ordering and reservations in the connected demo.", "مربوط ڈیمو میں آرڈر اور میز بکنگ آزمائیں۔")}</p></div>
        <div className="rl-hero-visual">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img className="rl-hero-photo" src="/restaurant/feast.webp" alt={S("Illustrative Pakistani feast with karahi, sajji, naan and sides", "کڑاہی، سجی، نان اور دیگر کھانوں کی نمونہ تصویر")} width="1536" height="1024" fetchPriority="high" />
          <div className="rl-sharing"><Flourish /><span>{S("Better", "مزہ")}<br /><i>{S("together", "ساتھ ساتھ")}</i></span></div>
          {f.rating != null && <a className="rl-rating-card" href={mapsUrl} target="_blank" rel="noopener noreferrer"><span className="rl-rating-star" aria-hidden="true">★</span><div><b>{f.rating.toFixed(1)} <small>/ 5</small></b><span>{f.reviews == null ? S("Google listing rating", "گوگل لسٹنگ ریٹنگ") : S(`${f.reviews.toLocaleString("en-US")} Google reviews`, `${f.reviews.toLocaleString("ur-PK")} گوگل ریویوز`)}</span></div><Symbol name="arrow" /></a>}
          <span className="rl-photo-note">{S("Illustrative food photography", "کھانوں کی نمونہ تصاویر")}</span>
        </div>
      </section>
      <div className="rl-wrap rl-at-a-glance">
        <div><Symbol name="pin" /><span><small>{S("COME FIND US", "ہم تک آئیں")}</small><b>{f.neighborhood || S("Quetta", "کوئٹہ")}</b></span><a href="#food-visit" aria-label={S("View location and hours", "پتہ اور اوقات دیکھیں")}><Symbol name="arrow" /></a></div>
        <div><Symbol name="dish" /><span><small>{S("SOMETHING FOR EVERY CRAVING", "ہر پسند کا ذائقہ")}</small><b>{S("Karahi. Grill. Chai.", "کڑاہی۔ گرل۔ چائے۔")}</b></span></div>
        <div><Symbol name="table" /><span><small>{S("YOUR NEXT GET-TOGETHER", "اگلی محفل کی تیاری")}</small><b>{S("Save a seat, skip the guesswork", "پہلے سے اپنی میز بک کریں")}</b></span><a href={reserveUrl} target={embedded ? "_top" : undefined} aria-label={S("Find a sample table", "نمونہ میز تلاش کریں")}><Symbol name="arrow" /></a></div>
      </div>

      <section className="rl-wrap rl-section" id="food-menu">
        <div className="rl-section-head"><div><p className="rl-kicker"><span className="rl-section-number">01</span>{S("THE MENU", "مینو")}</p><h2>{S("Find your", "اپنا اگلا")}<br /><em>{S("next favourite.", "پسندیدہ ذائقہ۔")}</em></h2></div><div className="rl-head-note"><p>{S("A little spice. A little comfort. Something worth sharing.", "کچھ مصالحہ، کچھ اپنائیت۔ ذائقے جو ساتھ بانٹے جائیں۔")}</p><span className="rl-label">{S("Fictional menu & prices", "فرضی مینو اور قیمتیں")}</span></div></div>
        <div className="rl-menu-controls"><div className="rl-categories" role="group" aria-label={S("Menu categories", "مینو کی اقسام")}>{["All", ...new Set(dishes.map(m => m.category))].map(c => <button key={c} type="button" aria-pressed={category === c} onClick={() => { setCategory(c); setShowAll(false); }}>{c === "All" ? S("All dishes", "تمام کھانے") : lang === "ur" ? categoryUr[c] ?? c : c}</button>)}</div><label className="rl-search"><Symbol name="search" /><input type="search" value={query} onChange={e => setQuery(e.target.value)} placeholder={S("Find a favourite…", "کھانا تلاش کریں…")} aria-label={S("Search sample menu", "نمونہ مینو تلاش کریں")} /></label></div>
        <p className="rl-result-count" role="status">{S(`Showing ${visible.length} of ${filtered.length} sample dishes`, `${filtered.length} میں سے ${visible.length} نمونہ کھانے`)}</p>
        {visible.length > 0 ? <div className="rl-menu-grid">{visible.map(m => <article className={`rl-menu-card ${m.available ? "" : "sold-out"}`} key={m.id}>
          <div className="rl-dish-visual">{photos[m.name] ? <Photo name={photos[m.name]} alt={S(m.name + ", illustrative serving", m.name_ur + "، نمونہ تصویر")} /> : <div className="rl-dish-art"><FoodArt art={m.art} /></div>}<span>{lang === "ur" ? categoryUr[m.category] ?? m.category : m.category}</span>{!m.available && <b className="rl-sold-label">{S("Sold out in demo", "ڈیمو میں ختم")}</b>}</div>
          <div className="rl-dish-body"><div className="rl-dish-title"><h3>{lang === "ur" ? m.name_ur || m.name : m.name}</h3><b dir="ltr">{money(m.price)}</b></div><p>{lang === "ur" ? descriptionUr[m.name] ?? m.description : m.description}</p><div className="rl-dish-footer"><small>{S("Sample serving & price", "نمونہ حصہ اور قیمت")}</small>{m.available ? <a href={customer("menu", m.id)} target={embedded ? "_top" : undefined} aria-label={S("Choose " + m.name, m.name_ur + " منتخب کریں")}><Symbol name="arrow" /></a> : <button type="button" disabled aria-label={S(m.name + " sold out", m.name_ur + " ختم")}><Symbol name="close" /></button>}</div></div>
        </article>)}</div> : <div className="rl-empty" role={menuUnavailable ? "alert" : "status"}><Symbol name="dish" /><h3>{menuUnavailable ? S("The sample menu is temporarily unavailable", "نمونہ مینو ابھی دستیاب نہیں") : dishes.length ? S("No dishes match your search", "آپ کی تلاش میں کوئی کھانا نہیں ملا") : S("The sample menu is being prepared", "نمونہ مینو تیار ہو رہا ہے")}</h3><p>{menuUnavailable ? S("Open the ordering demo to retry, or ask the staff assistant.", "آرڈر ڈیمو دوبارہ کھولیں یا اسسٹنٹ سے پوچھیں۔") : S("Try another search or explore the ordering demo.", "دوسری تلاش کریں یا آرڈر ڈیمو دیکھیں۔")}</p><Link href={menuUrl}>{S("Open ordering demo", "آرڈر ڈیمو کھولیں")}</Link></div>}
        <div className="rl-menu-bottom">{!showAll && category === "All" && !query.trim() && filtered.length > 6 && <button className="rl-button secondary" onClick={() => setShowAll(true)}>{S("Show all dishes", "تمام کھانے دکھائیں")}<Symbol name="arrow" /></button>}<Link href={menuUrl}>{S("Build your sample order", "اپنا نمونہ آرڈر بنائیں")}</Link><p>{S("Ingredients and allergy requirements must be confirmed with staff.", "اجزاء اور الرجی کی ضروریات عملے سے تصدیق کریں۔")}</p></div>
      </section>

      <section className="rl-story-band" id="food-story"><div className="rl-wrap rl-story">
        <div className="rl-story-collage"><Photo name="sajji" alt={S("Illustrative sajji with rice", "چاول کے ساتھ سجی کی نمونہ تصویر")} className="rl-story-large" /><Photo name="karahi" alt={S("Illustrative chicken karahi", "چکن کڑاہی کی نمونہ تصویر")} className="rl-story-small" /><div className="rl-story-seal"><Flourish /><span>{S("Pass the naan.", "نان دیجیے۔")}<br /><i>{S("Stay a little.", "کچھ دیر بیٹھیے۔")}</i></span></div><span className="rl-story-caption">{S("Illustrative servings, shown for the website concept", "ویب سائٹ کے تصور کے لیے نمونہ کھانے")}</span></div>
        <div className="rl-story-copy"><p className="rl-kicker"><span className="rl-section-number">02</span>{S("AROUND THE TABLE", "ہماری میز پر")}</p><h2>{S("Some things", "کچھ چیزیں")}<br />{S("taste better", "زیادہ لطف دیتی ہیں")}<br /><em>{S("together.", "ساتھ ساتھ۔")}</em></h2><p>{S("A family catch-up. A long-overdue dinner with friends. Or just your favourite plate after a busy day. There is always a reason to make time for a good meal.", "فیملی کے ساتھ ملاقات، دوستوں کے ساتھ ڈنر، یا مصروف دن کے بعد پسندیدہ کھانا۔ اچھے کھانے کے لیے ہمیشہ کچھ وقت نکالیے۔")}</p><p>{S("Start with the menu, choose your favourites and let the connected ordering experience take care of the next step.", "مینو سے پسندیدہ کھانے منتخب کریں، اور مربوط آرڈر ڈیمو میں اگلا مرحلہ مکمل کریں۔")}</p><Link href={reserveUrl}>{S("Make it a gathering", "اپنی محفل کی میز بک کریں")}</Link></div>
      </div></section>

      <section className="rl-wrap rl-section rl-your-way" id="food-order">
        <div className="rl-section-head"><div><p className="rl-kicker"><span className="rl-section-number">03</span>{S("HOW YOU LIKE IT", "آپ کی پسند کے مطابق")}</p><h2>{S("Your meal.", "آپ کا کھانا۔")} <em>{S("Your way.", "آپ کا انداز۔")}</em></h2></div><p className="rl-head-note">{S("One menu, with a simple next step for every kind of plan.", "ایک مینو، ہر موقع کے لیے آسان اگلا مرحلہ۔")}</p></div>
        <div className="rl-way-grid">{([
          ["table", S("Pull up a chair", "میز پر تشریف لائیں"), S("Choose a date, party size and a table available in the sample reservation system.", "تاریخ، مہمانوں کی تعداد اور ڈیمو میں دستیاب میز منتخب کریں۔"), S("Find a table", "میز تلاش کریں"), reserveUrl],
          ["bag", S("Take the flavour with you", "ذائقہ اپنے ساتھ لے جائیں"), S("Build a pickup or delivery sample order, add preferences and follow its kitchen ticket.", "پک اپ یا ڈیلیوری کا نمونہ آرڈر بنائیں، ہدایات دیں اور تیاری چیک کریں۔"), S("Start an order", "آرڈر شروع کریں"), menuUrl],
          ["chat", S("A little help choosing", "انتخاب میں کچھ مدد"), S("Ask about the sample menu or your booking. Staff can take over when you need them.", "نمونہ مینو یا بکنگ کے بارے میں پوچھیں۔ ضرورت پڑنے پر عملہ جواب دے سکتا ہے۔"), S("Talk to the assistant", "اسسٹنٹ سے بات کریں"), chatUrl],
        ] as const).map(([icon, title, text, cta, url], i) => <article className="rl-way-card" key={icon}><div className="rl-way-top"><Symbol name={icon} /><span>0{i + 1}</span></div><h3>{title}</h3><p>{text}</p><a href={url} target={embedded ? "_top" : undefined}>{cta}<Symbol name="arrow" /></a></article>)}</div>
        <p className="rl-demo-note">{S("Outreach demo: orders, tables, delivery and payments are simulated. No real restaurant service is requested.", "آؤٹ ریچ ڈیمو: آرڈر، میزیں، ڈیلیوری اور ادائیگیاں فرضی ہیں۔ کوئی حقیقی سروس طلب نہیں کی جاتی۔")}</p>
      </section>

      <section className="rl-reviews-band" id="food-reviews"><div className="rl-wrap rl-section">
        <div className="rl-section-head"><div><p className="rl-kicker"><span className="rl-section-number">04</span>{S("GUEST WORDS", "مہمانوں کی باتیں")}</p><h2>{S("From the", "میز کے")}<br /><em>{S("other side of the table.", "دوسری طرف سے۔")}</em></h2></div>{f.rating != null && <div className="rl-review-score"><span aria-hidden="true">{Array.from({length:5},(_,i)=>i<Math.floor(f.rating!)?"★":"☆").join(" ")}</span><b>{f.rating.toFixed(1)}<small> / 5</small></b><p>{f.reviews == null ? S("Google listing rating", "گوگل لسٹنگ ریٹنگ") : S(`Based on ${f.reviews.toLocaleString("en-US")} Google reviews`, `${f.reviews.toLocaleString("ur-PK")} گوگل ریویوز کی بنیاد پر`)}</p><small>{S("Listing snapshot: ", "لسٹنگ کا جائزہ: ")}{snapshot}</small></div>}</div>
        {praise.length > 0 ? <div className="rl-review-grid">{praise.map((p, i) => <figure key={i}><span className="rl-quote-mark" aria-hidden="true">“</span><blockquote dir="auto">{p.quotes[0].length > 180 ? p.quotes[0].slice(0, 180) + "…" : p.quotes[0]}</blockquote><figcaption><span className="rl-review-avatar"><Symbol name="chat" /></span><span><b>{S(p.theme_en, p.theme_ur)}</b><small>{S("Google review excerpt", "گوگل ریویو کا اقتباس")}</small></span></figcaption></figure>)}</div> : <div className="rl-review-empty"><p>{S("Explore the restaurant’s Google listing for guest reviews and public information.", "مہمانوں کے ریویوز اور معلومات کے لیے گوگل لسٹنگ دیکھیں۔")}</p></div>}
        <a className="rl-text-link" href={mapsUrl} target="_blank" rel="noopener noreferrer">{S("See the Google listing", "گوگل لسٹنگ دیکھیں")}<Symbol name="arrow" /></a>
      </div></section>

      <section className="rl-wrap rl-section" id="food-visit"><div className="rl-section-head"><div><p className="rl-kicker"><span className="rl-section-number">05</span>{S("COME ON OVER", "ہم تک آئیں")}</p><h2>{S("We’ll save you", "آپ کے لیے")}<br /><em>{S("a place.", "ایک جگہ۔")}</em></h2></div><Link href={reserveUrl}>{S("Plan a sample visit", "نمونہ ملاقات بک کریں")}</Link></div>
        <div className="rl-visit-grid"><div className="rl-location-card"><div className="rl-map-art" aria-hidden="true"><svg viewBox="0 0 600 280" fill="none"><path d="m0 20 600 235M60 0 90 280M340 0 390 280M0 150l600-40M490 0 180 280" stroke="currentColor" strokeWidth="28" /><path d="m0 20 600 235M60 0 90 280M340 0 390 280M0 150l600-40M490 0 180 280" stroke="#e8d7ad" strokeWidth="2" strokeDasharray="4 8" /></svg><div className="rl-map-pin"><Symbol name="pin" /></div><span>{S("QUETTA", "کوئٹہ")}</span></div><div className="rl-location-body"><p className="rl-kicker">{S("FIND US", "پتہ")}</p><h3>{b.name}</h3><p dir="auto">{f.address || S("Ask the team for location details.", "پتہ معلوم کرنے کے لیے عملے سے پوچھیں۔")}</p><a href={mapsUrl} target="_blank" rel="noopener noreferrer">{S("Get directions on Google Maps", "گوگل میپس پر راستہ دیکھیں")}<Symbol name="arrow" /></a><small>{S("Decorative map illustration. Open Google Maps for directions.", "نمونہ نقشہ۔ اصل راستے کے لیے گوگل میپس کھولیں۔")}</small></div></div>
          <div className="rl-hours-card"><div className="rl-hours-head"><Symbol name="clock" /><h3>{S("Make time for a meal.", "کھانے کے لیے وقت نکالیے۔")}</h3></div><p>{S("Listed visiting hours · Pakistan Standard Time", "لسٹنگ کے اوقات · پاکستان کا وقت")}</p>{f.hours.length ? <dl>{f.hours.map(h => <div key={h.day}><dt>{lang === "ur" ? weekdays[h.day] ?? h.day : h.day}</dt><dd dir="ltr">{lang === "ur" ? h.hours.replace(/Closed/gi, "بند").replace(/AM/g, "صبح").replace(/PM/g, "شام").replace(/to/g, "تا") : h.hours}</dd></div>)}</dl> : <p className="rl-missing-hours">{S("Hours are not listed. Ask the team before visiting.", "اوقات درج نہیں۔ آنے سے پہلے عملے سے تصدیق کریں۔")}</p>}<p className="rl-hours-note">{S("Confirm current hours with the restaurant before a real visit. Demo reservation times are illustrative.", "حقیقی ملاقات سے پہلے ریسٹورنٹ سے اوقات کی تصدیق کریں۔ ڈیمو بکنگ کے اوقات فرضی ہیں۔")}</p><Link href={reserveUrl}>{S("Find a sample table", "نمونہ میز تلاش کریں")}</Link></div>
        </div>
      </section>

      <section className="rl-wrap rl-faq"><div><p className="rl-kicker">{S("A FEW GOOD QUESTIONS", "کچھ اہم سوال")}</p><h2>{S("Before you", "آنے سے")}<br /><em>{S("come over.", "پہلے۔")}</em></h2></div><div className="rl-faq-list">{[
        [S("Can I reserve a table here?", "کیا یہاں میز بک کر سکتا ہوں؟"), S("Yes, in the demo. Select Book a table to choose your party size, date and an available sample table. A reservation is confirmed only after it is saved by the booking service.", "جی، ڈیمو میں۔ میز بک کریں کا بٹن دبائیں، مہمانوں کی تعداد، تاریخ اور دستیاب نمونہ میز منتخب کریں۔ بکنگ محفوظ ہونے کے بعد ہی تصدیق ہوتی ہے۔")],
        [S("Is this the restaurant’s official menu?", "کیا یہ ریسٹورنٹ کا اصل مینو ہے؟"), S("This is an illustrative outreach menu with fictional prices and food photography. The restaurant would approve its menu, prices, ingredients and photos before a public launch.", "یہ آؤٹ ریچ کا نمونہ مینو ہے، قیمتیں اور تصاویر فرضی ہیں۔ عوامی لانچ سے پہلے ریسٹورنٹ مینو، قیمتوں، اجزاء اور تصاویر کی منظوری دے گا۔")],
        [S("Can I order pickup or delivery?", "کیا پک اپ یا ڈیلیوری آرڈر دے سکتا ہوں؟"), S("The connected demo lets you choose pickup, delivery or dine-in and follow a sample kitchen ticket. It does not send a real order, arrange delivery or collect payment.", "مربوط ڈیمو میں پک اپ، ڈیلیوری یا ڈائن اِن منتخب کر کے نمونہ ٹکٹ دیکھ سکتے ہیں۔ کوئی حقیقی آرڈر، ڈیلیوری یا ادائیگی نہیں ہوتی۔")],
        [S("What if I have an allergy or a special request?", "الرجی یا خصوصی ہدایت کی صورت میں کیا کروں؟"), S("Ask the staff assistant and confirm ingredients with the restaurant. Sample ingredient labels do not establish whether a dish is suitable for an allergy.", "اسسٹنٹ سے پوچھیں اور ریسٹورنٹ کے عملے سے اجزاء کی تصدیق کریں۔ نمونہ معلومات کسی کھانے کو الرجی کے لیے محفوظ قرار نہیں دیتیں۔")],
      ].map(([question, answer]) => <details key={question}><summary>{question}<span aria-hidden="true">+</span></summary><p>{answer}</p></details>)}</div></section>

      <section className="rl-wrap rl-last"><div className="rl-last-copy"><p className="rl-kicker">{S("GOOD PLANS START WITH GOOD FOOD", "اچھے کھانے سے اچھی محفل")}</p><h2>{S("Come hungry.", "بھوک لے کر آئیں۔")}<br /><em>{S("Bring your people.", "اپنوں کو ساتھ لائیں۔")}</em></h2><div className="rl-actions"><Link href={reserveUrl}>{S("Book a table", "میز بک کریں")}</Link><Link href={menuUrl} secondary>{S("Start a sample order", "نمونہ آرڈر شروع کریں")}</Link></div></div><Flourish className="rl-last-flourish" /></section>
    </main>
    <footer className="rl-wrap rl-footer"><div><b>{b.name}</b><p>{f.neighborhood || S("Quetta", "کوئٹہ")} · {S("Quetta, Pakistan", "کوئٹہ، پاکستان")}</p></div><nav aria-label={S("Footer navigation", "فوٹر نیویگیشن")}><a href="#food-menu">{S("Menu", "مینو")}</a><a href={customer("orders")} target={embedded ? "_top" : undefined}>{S("My orders", "میرے آرڈرز")}</a><a href={reserveUrl} target={embedded ? "_top" : undefined}>{S("Reservations", "میز بکنگ")}</a><a href={chatUrl} target={embedded ? "_top" : undefined}>{S("Ask a question", "سوال پوچھیں")}</a></nav><div className="rl-footer-bottom"><span>{S("Landing page concept by NexusPoint", "NexusPoint کا لینڈنگ پیج نمونہ")}</span><span>{S("Sample menu & imagery. A private outreach preview.", "نمونہ مینو اور تصاویر۔ نجی آؤٹ ریچ پیش منظر۔")}</span><a href={base} target={embedded ? "_top" : undefined}>{S("Your review report", "آپ کی ریویو رپورٹ")} ↗</a></div></footer>
  </div>;
}
