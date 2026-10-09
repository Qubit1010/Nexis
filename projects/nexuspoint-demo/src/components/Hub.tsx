"use client";
import { useCallback, useEffect, useMemo, useState } from "react";
import ChatWindow from "./ChatWindow";
import HealthcareWebsitePreview from "./HealthcareWebsitePreview";
import { T, fill, type Lang } from "@/lib/i18n";
import type { Health, Profile, RoiDefaults, Xray } from "@/lib/db";

type Tier = { name: string; tag_en: string; tag_ur: string; setup: number; monthly: number; rec: boolean; items_en: string[]; items_ur: string[] };
type Biz = { slug: string; token: string; code: string; name: string; sector: string; expires_at: string; created_at: string;
  profile: Profile; xray: Xray | null; site: { posts: { en: string[]; ur: string[] } } | null; roi: RoiDefaults | null; health: Health | null };
type SectorUi = { noun: { en: string; ur: string }; site: Record<Lang, { hero: string; sub: string; section: string; cta: string }>; prompts: Record<Lang, readonly string[]> };
type DashConv = { id: string; channel: string; stage: string | null; summary: string | null; handoff: boolean; last_at: string;
  action: { type: string; details: { key: string; value: string }[] } | null; messages: { role: string; content: string }[] };
type Dash = { stats: { conversations: number; avg_reply_s: number | null; actions: number; handoffs: number }; conversations: DashConv[] };

const pkr = (n: number) => "PKR " + Math.round(n).toLocaleString("en-US");
const fmtDate = (s: string, lang: Lang) => new Date(s).toLocaleDateString(lang === "ur" ? "ur-PK" : "en-GB", { day: "numeric", month: "long", year: "numeric", timeZone: "Asia/Karachi" });
const Check = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5" /></svg>;
const Cross = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18" /></svg>;
const Chat = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinejoin="round" aria-hidden="true"><path d="M4 19.5 5.2 16A8 8 0 1 1 8 18.8Z" /></svg>;

function track(slug: string, t: string, kind: string) {
  fetch("/api/event", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ slug, t, kind }) }).catch(() => {});
}

export default function Hub({ biz, tiers, sector, qr, chatUrl, viaWhatsApp, initialLang, snapshot }: {
  biz: Biz; tiers: Tier[]; sector: SectorUi; qr: string; chatUrl: string; viaWhatsApp: boolean; initialLang: Lang;
  snapshot: { role: "customer" | "business"; content: string }[] | null;
}) {
  const [lang, setLang] = useState<Lang>(initialLang);
  const t = T[lang];
  const ur = lang === "ur";
  const x = biz.xray;
  const f = biz.profile.facts;

  function toggleLang() {
    const next: Lang = ur ? "en" : "ur";
    setLang(next);
    const u = new URL(location.href);
    if (next === "ur") u.searchParams.set("lang", "ur"); else u.searchParams.delete("lang");
    history.replaceState(null, "", u);
  }
  function toggleTheme() {
    const r = document.documentElement;
    const cur = r.dataset.theme || (matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark");
    const next = cur === "dark" ? "light" : "dark";
    r.dataset.theme = next;
    try { localStorage.setItem("np-theme", next); } catch { /* private mode */ }
  }

  return (
    <div className="hub" dir={ur ? "rtl" : "ltr"} lang={lang}>
      <header className="top">
        <div className="wrap top-row">
          <img className="logo-dark" src="/logo-white.svg" alt="NexusPoint" width="152" height="42" />
          <img className="logo-light" src="/logo-black.svg" alt="NexusPoint" width="152" height="42" />
          <span className="built">{ur ? <><b>{biz.name}</b> {t.built}</> : <>{t.built} <b>{biz.name}</b></>}</span>
          <div className="tools">
            <button className="ibtn" type="button" onClick={toggleLang} style={{ fontFamily: ur ? "var(--font)" : "var(--urdu)" }}>{t.otherLang}</button>
            <button className="ibtn" type="button" onClick={toggleTheme} aria-label={t.theme}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true"><circle cx="12" cy="12" r="4.2" /><path d="M12 2.5v2.2M12 19.3v2.2M4.6 4.6l1.6 1.6M17.8 17.8l1.6 1.6M2.5 12h2.2M19.3 12h2.2M4.6 19.4l1.6-1.6M17.8 6.2l1.6-1.6" strokeLinecap="round" /></svg>
            </button>
          </div>
        </div>
        <nav className="wrap chips" aria-label="Sections">
          {(["reviews", "assistant", "dashboard", "website", "numbers", "plan"] as const).map((k) => <a key={k} href={`#${k}`}>{t.nav[k]}</a>)}
        </nav>
        <p className="wrap ribbon">{fill(t.privateUntil, { name: biz.name, date: fmtDate(biz.expires_at, lang) })}</p>
      </header>

      <main>
        <section className="hero">
          <div className="wrap hero-grid">
            <div>
              <h1 dangerouslySetInnerHTML={{ __html: fill(t.heroH, { name: escapeHtml(biz.name) }) }} />
              <p className="sub">{t.heroSub}</p>
              <p className="facts">
                {f.rating != null && <span><b className="num">{f.rating}★</b> {t.rating}</span>}
                {f.reviews != null && <span><b className="num">{f.reviews.toLocaleString("en-US")}</b> {t.reviews}</span>}
                {f.category && <span className="ltr">{f.category}</span>}
                {f.address && <span>{f.address}</span>}
              </p>
            </div>
            {biz.health && <HealthCard h={biz.health} lang={lang} />}
          </div>
        </section>

        {x && <Reviews x={x} lang={lang} />}

        <section id="assistant" className="sec tint">
          <div className="wrap as-grid">
            <div>
              <div className="sec-head" style={{ marginBottom: 0 }}>
                <p className="k">{t.asK}</p><h2>{t.asH}</h2><p>{t.asP}</p>
              </div>
              <div className="qr-card">
                <a className="qr" href={chatUrl} target="_blank" rel="noopener" aria-label={t.scanB} dangerouslySetInnerHTML={{ __html: qr }} />
                <div><b>{t.scanB}</b><p>{viaWhatsApp ? t.scanWa : fill(t.scanP, { name: biz.name })}</p></div>
              </div>
            </div>
            <div className="phone"><div className="screen">
              <ChatWindow slug={biz.slug} token={biz.token} name={biz.name} lang={lang} prompts={[...sector.prompts[lang]]} snapshot={snapshot} healthcare={biz.sector==="healthcare"} restaurant={biz.sector==="food"} school={biz.sector==="education"} />
            </div></div>
          </div>
        </section>

        {biz.sector==="healthcare"&&<section className="sec" id="care-workspaces"><div className="wrap"><div className="sec-head"><p className="k">{ur?"کلینک کا مربوط ڈیمو":"Your connected clinic"}</p><h2>{ur?"بکنگ سے مریض کے ریکارڈ تک":"From the first message to the visit record"}</h2><p>{ur?"مریض، استقبالیہ اور ڈاکٹر ایک ہی ورک فلو سے جڑے ہیں۔ ڈاکٹر، اوقات اور طبی ریکارڈ فرضی نمونے ہیں۔":"Explore the same booking from the patient, reception and doctor perspectives. Doctors, availability and medical records are fictional samples."}</p></div><div className="care-previews">{[["patient",ur?"مریض پورٹل":"Patient portal",ur?"ڈاکٹر، دستیاب اوقات، کال بکنگ اور شائع شدہ طبی رپورٹس۔":"Find doctors, book a visit or call, and view published diagnoses and reports.","01"],["clinic",ur?"کلینک انتظام":"Clinic operations",ur?"ڈاکٹر کا کیلنڈر، انتظار کی قطار، گفتگو اور عملے کی منتقلی۔":"Doctor calendars, check-in queues, conversations and staff takeover.","02"],["doctor",ur?"ڈاکٹر ورک اسپیس":"Doctor workspace",ur?"روزانہ شیڈول، ملاقات کے نوٹس، نسخے اور ریکارڈ کی اشاعت۔":"Personal schedule, visit notes, prescriptions and record publication.","03"]].map(([role,title,description,n])=><a className="care-preview" key={role} href={`/d/${biz.slug}/${role}?t=${encodeURIComponent(biz.token)}${ur?"&lang=ur":""}`}><span className="num">{n}</span><h3>{title}</h3><p>{description}</p><b>{ur?"ڈیمو کھولیں":"Open workspace"} →</b></a>)}</div></div></section>}
        {biz.sector==='food'&&<section className="sec" id="restaurant-workspaces"><div className="wrap"><div className="sec-head"><p className="k">{ur?'آپ کا مربوط ریسٹورنٹ':'Your connected restaurant'}</p><h2>{ur?'پہلے پیغام سے کچن ٹکٹ تک':'From the first message to the kitchen ticket'}</h2><p>{ur?'آرڈر، میز بکنگ اور گفتگو ایک ساتھ۔ مینو، قیمتیں، میزیں اور مہمان فرضی نمونے ہیں۔':'Follow the same order through the customer portal, manager dashboard and kitchen. Menu prices, tables and guests are fictional samples.'}</p></div><div className="care-previews">{[['customer',ur?'کسٹمر پورٹل':'Customer portal',ur?'مینو، باسکٹ، آرڈر کی حالت، میز بکنگ اور رسیدیں۔':'Browse the menu, place sample orders, track progress and reserve tables.'],['restaurant',ur?'ریسٹورنٹ انتظام':'Restaurant operations',ur?'آرڈر، میزیں، مہمان، گفتگو اور عملے کی منتقلی۔':'Manage orders, tables, waiting guests, conversations and staff takeover.'],['kitchen',ur?'کچن بورڈ':'Kitchen board',ur?'تیاری کے ٹکٹ، مقدار، مصالحہ اور تیار آرڈر۔':'Live preparation tickets with quantities, spice preferences and item notes.']].map(([role,title,description],i)=><a className="care-preview" key={role} href={`/d/${biz.slug}/${role}?t=${encodeURIComponent(biz.token)}${ur?'&lang=ur':''}`}><span className="num">0{i+1}</span><h3>{title}</h3><p>{description}</p><b>{ur?'ڈیمو کھولیں':'Open workspace'} →</b></a>)}</div></div></section>}
        {biz.sector==='education'&&<section className="sec" id="school-workspaces"><div className="wrap"><div className="sec-head"><p className="k">{ur?'آپ کا مربوط کیمپس':'Your connected campus'}</p><h2>{ur?'پہلے سوال سے طالب علم کے ریکارڈ تک':'From the first enquiry to the student report'}</h2><p>{ur?'والدین، دفتر اور استاد کا ایک مربوط ورک فلو۔ طلبہ، کلاسیں، فیس اور نتائج فرضی ہیں۔':'Explore the same family across the parent portal, school office and teacher workspace. Students, classes, fees and results are fictional samples.'}</p></div><div className="care-previews">{[['parent',ur?'والدین پورٹل':'Parent portal',ur?'حاضری، ہوم ورک، نتائج، فیس رسیدیں اور کیمپس ملاقاتیں۔':'Follow attendance, submit homework, view published results, track fees and book campus visits.'],['school',ur?'اسکول دفتر':'School office',ur?'طلبہ، فیس کی تصدیق، داخلہ، ملاقاتیں اور گفتگو۔':'Manage students, verify sample fees, review admissions and take over family conversations.'],['teacher',ur?'استاد ورک اسپیس':'Teacher workspace',ur?'کلاس رجسٹر، ہوم ورک، طلبہ کے جواب اور نتائج کی اشاعت۔':'Record attendance, publish homework, review responses and release assessment results.']].map(([role,title,description],i)=><a className="care-preview" key={role} href={`/d/${biz.slug}/${role}?t=${encodeURIComponent(biz.token)}${ur?'&lang=ur':''}`}><span className="num">0{i+1}</span><h3>{title}</h3><p>{description}</p><b>{ur?'ڈیمو کھولیں':'Open workspace'} →</b></a>)}</div></div></section>}
        <Dashboard biz={biz} lang={lang} live={!snapshot} />
        <Website biz={biz} sector={sector} lang={lang} chatUrl={chatUrl} />
        {biz.roi && <Numbers roi={biz.roi} tier={tiers.find((x) => x.rec) ?? tiers[1]} lang={lang} onUse={() => track(biz.slug, biz.token, "roi_used")} />}
        <Plan biz={biz} tiers={tiers} lang={lang} />
      </main>
      <footer className="foot"><div className="wrap">{fill(t.foot, { date: fmtDate(biz.created_at, lang) })}</div></footer>
    </div>
  );
}

function escapeHtml(s: string) {
  return s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c] as string));
}

function HealthCard({ h, lang }: { h: Health; lang: Lang }) {
  const t = T[lang];
  const C = 2 * Math.PI * 42;
  const color = h.score >= 70 ? "var(--ok)" : h.score >= 45 ? "var(--warn)" : "var(--bad)";
  return (
    <aside className="health" aria-label={t.healthH}>
      <div className="health-top">
        <svg className="ring" viewBox="0 0 100 100" role="img" aria-label={`${h.score}/100`}>
          <circle cx="50" cy="50" r="42" fill="none" stroke="var(--surface-2)" strokeWidth="9" />
          <circle cx="50" cy="50" r="42" fill="none" stroke={color} strokeWidth="9" strokeLinecap="round"
            strokeDasharray={`${(C * h.score) / 100} ${C}`} transform="rotate(-90 50 50)" />
          <text x="50" y="58" textAnchor="middle">{h.score}</text>
        </svg>
        <div><h3>{t.healthH}</h3><p>{t.healthP}</p></div>
      </div>
      <ul className="checks">
        {h.items.map((i) => <li key={i.key} className={i.ok ? "yes" : "no"}>{i.ok ? <Check /> : <Cross />}<span>{lang === "ur" ? i.ur : i.en}</span></li>)}
      </ul>
    </aside>
  );
}

function Reviews({ x, lang }: { x: Xray; lang: Lang }) {
  const t = T[lang];
  const ur = lang === "ur";
  const s = x.stats;
  const total = Object.values(s.mix).reduce((a, b) => a + b, 0) || 1;
  const word = (n: number) => `${n} ${n === 1 ? t.reviewWord : t.reviewsWord}`;
  const Col = ({ title, themes, dot }: { title: string; themes: Xray["praise"]; dot: string }) => (
    <div className="tcol">
      <h3><span className="dot" style={{ background: dot }} />{title}</h3>
      {themes.map((th, i) => (
        <div className="theme" key={i}>
          <div className="theme-head"><span>{ur ? th.theme_ur : th.theme_en}</span><span className="num">{word(th.count)}</span></div>
          <div className="bar" style={{ marginTop: ".5rem" }}><i style={{ width: `${Math.min(100, (th.count / Math.max(1, s.with_text)) * 100 * 2.2)}%`, background: dot }} /></div>
          {th.quotes.slice(0, 1).map((q) => <q key={q} dir="auto">{q}</q>)}
        </div>
      ))}
    </div>
  );
  return (
    <section id="reviews" className="sec">
      <div className="wrap">
        <div className="sec-head"><p className="k">{t.xrK}</p><h2>{fill(t.xrH, { n: s.analysed })}</h2><p>{t.xrP}</p></div>
        <div className="xr-top">
          <div>
            <p className="summary">{ur ? x.summary_ur : x.summary_en}</p>
            <p className={`reply-call${s.owner_reply_pct >= 50 ? " good" : ""}`}>
              {s.owner_reply_pct === 0 ? fill(t.replied0, { n: s.analysed }) : fill(t.repliedSome, { n: s.analysed, p: s.owner_reply_pct })}
            </p>
          </div>
          <div className="mix" aria-label={t.mix}>
            {["5", "4", "3", "2", "1"].map((k) => (
              <div className="mix-row" key={k}><span className="num">{k}★</span><div className="bar"><i style={{ width: `${(100 * (s.mix[k] ?? 0)) / total}%` }} /></div><span className="num">{s.mix[k] ?? 0}</span></div>
            ))}
          </div>
        </div>
        {x.complaints.length + x.praise.length > 0 ? (
          <div className="themes">
            <Col title={t.complain} themes={x.complaints} dot="var(--bad)" />
            <Col title={t.love} themes={x.praise} dot="var(--ok)" />
          </div>
        ) : <p className="empty" style={{ marginTop: "1.5rem" }}>{t.noText}</p>}
        {x.fixes.length > 0 && (<>
          <h3 style={{ marginTop: "2.2rem", fontSize: "1.25rem" }}>{t.fixesH}</h3>
          <div className="fixes">{x.fixes.map((fx, i) => <div className="fix" key={i}><b>{i + 1}</b><span>{ur ? fx.ur : fx.en}</span></div>)}</div>
        </>)}
      </div>
    </section>
  );
}

function Dashboard({ biz, lang, live }: { biz: Biz; lang: Lang; live: boolean }) {
  const t = T[lang];
  const [d, setD] = useState<Dash | null>(null);
  const load = useCallback(() => {
    fetch(`/api/dash?slug=${biz.slug}&t=${biz.token}`, { cache: "no-store" }).then((r) => r.json()).then(setD).catch(() => {});
  }, [biz.slug, biz.token]);
  useEffect(() => {
    if (!live) return;
    load();
    const id = setInterval(() => { if (document.visibilityState === "visible") load(); }, 2000);
    return () => clearInterval(id);
  }, [live, load]);
  const s = d?.stats;
  const ago = (iso: string) => {
    const m = Math.round((Date.now() - new Date(iso).getTime()) / 60000);
    return m < 1 ? (lang === "ur" ? "ابھی" : "just now") : lang === "ur" ? `${m} منٹ پہلے` : `${m} min ago`;
  };
  return (
    <section id="dashboard" className="sec">
      <div className="wrap">
        <div className="sec-head"><p className="k">{t.dbK}</p><h2>{t.dbH}</h2><p>{t.dbP}</p></div>
        <div className="kpis">
          <div className="kpi"><b>{s?.conversations ?? 0}</b><span>{t.kConv}</span></div>
          <div className="kpi"><b>{s?.avg_reply_s != null ? `${s.avg_reply_s}s` : "–"}</b><span>{t.kReply}</span></div>
          <div className="kpi"><b>{s?.actions ?? 0}</b><span>{t.kAct}</span></div>
          <div className="kpi"><b>{s?.handoffs ?? 0}</b><span>{t.kHand}</span></div>
        </div>
        <div className="feed">
          {!d?.conversations.length && <p className="empty">{t.emptyDb}</p>}
          {d?.conversations.map((c) => (
            <article className="card" key={c.id}>
              <div>
                <div className="card-top">
                  <span className={`stage ${c.stage ?? ""}`}>{t.stage[(c.stage ?? "qualifying") as keyof typeof t.stage] ?? c.stage}</span>
                  <span className="chan">{c.channel === "whatsapp" ? "WhatsApp" : "Web chat"} · {ago(c.last_at)}</span>
                </div>
                {c.summary && <p className="summ" dir="auto">{c.summary}</p>}
                {c.action && c.action.details.length > 0 && (
                  <div className="action">
                    <span className="ah">{t.action[c.action.type as keyof typeof t.action] ?? c.action.type}</span>
                    {c.action.details.map((kv) => <div key={kv.key}><span>{kv.key}</span><span dir="auto">{kv.value}</span></div>)}
                  </div>
                )}
              </div>
              <div className="mini">
                {c.messages.slice(-4).map((m, i) => <p key={i} className={m.role === "customer" ? "c" : ""} dir="auto">{m.content}</p>)}
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

function Website({ biz, sector, lang, chatUrl }: { biz: Biz; sector: SectorUi; lang: Lang; chatUrl: string }) {
  const t = T[lang];
  const S = sector.site[lang];
  const f = biz.profile.facts;
  const [copied, setCopied] = useState<number | null>(null);
  const posts = biz.site?.posts ?? { en: [], ur: [] };
  const all = [...posts.en.slice(0, 1).map((p) => ({ p, l: "en" })), ...posts.ur.slice(0, 1).map((p) => ({ p, l: "ur" }))];
  const education = biz.sector === "education";
  const websiteTitle = education ? lang === "ur" ? "پہلی درخواست سے روزمرہ تعلیم تک" : "From a first enquiry to everyday learning" : biz.sector === "food" ? lang === "ur" ? "پہلی جھلک سے اگلی دعوت تک" : "From a first look to the next gathering" : lang === "ur" ? "پہلے تاثر سے اگلی ملاقات تک" : "From a first impression to the next appointment";
  const websiteDescription = education ? lang === "ur" ? "آپ کے اسکول یا اکیڈمی کے لیے مکمل لینڈنگ پیج نمونہ۔ پروگرام، داخلہ درخواست، والدین پورٹل اور کیمپس ملاقات ایک صفحے پر۔" : "A complete landing page concept for your school or academy. Programs, admissions enquiries, parent access and campus visits, all on one page." : biz.sector === "food" ? lang === "ur" ? "آپ کے ریسٹورنٹ کے لیے مکمل لینڈنگ پیج نمونہ۔ مینو، آرڈر، میز بکنگ، ریویوز اور راستہ ایک صفحے پر۔" : "A complete landing page concept for your restaurant. Menu, ordering, table reservations, reviews and directions, all on one page." : lang === "ur" ? "آپ کے کاروبار کے لیے ایک مکمل لینڈنگ پیج نمونہ۔ خدمات، ڈاکٹر، مریض پورٹل، اوقات اور راستہ ایک صفحے پر۔" : "A complete landing page concept for your clinic. Services, consultants, patient access, visiting hours and directions, all on one page.";
  if (biz.sector === "healthcare" || biz.sector === "food" || biz.sector === "education") return (
    <section id="website" className="sec tint">
      <div className="wrap">
        <div className="sec-head"><p className="k">{lang === "ur" ? "آپ کی ویب سائٹ" : "Your website"}</p><h2>{websiteTitle}</h2><p>{websiteDescription}</p></div>
        <HealthcareWebsitePreview slug={biz.slug} token={biz.token} name={biz.name} lang={lang} sector={biz.sector} />
        <h3 style={{ fontSize: "1.25rem", marginBottom: "1rem" }}>{t.postsH}</h3>
        <div className="posts" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 300px), 1fr))", gap: "1rem" }}>
          {all.map(({ p, l }, i) => <div className="post" key={i} lang={l}><div className="ph"><span>{l === "ur" ? "اردو" : "English"} · Facebook / Instagram</span><button type="button" onClick={() => { navigator.clipboard?.writeText(p); setCopied(i); setTimeout(() => setCopied(null), 1500); }}>{copied === i ? t.copied : t.copy}</button></div><p>{p}</p></div>)}
        </div>
      </div>
    </section>
  );
  return (
    <section id="website" className="sec tint">
      <div className="wrap">
        <div className="sec-head"><p className="k">{t.webK}</p><h2>{t.webH}</h2><p>{t.webP}</p></div>
        <div className="web-grid">
          <div className="phone"><div className="screen site" style={{ height: "38rem" }}>
            <div className="site-bar"><span className="ltr" style={{ all: "unset", fontWeight: 800 }}>{biz.name}</span><span>{t.preview}</span></div>
            <div className="site-hero">
              <h4>{S.hero}</h4><p>{S.sub}</p>
              {f.rating != null && <p className="stars ltr">★ {f.rating} · {f.reviews?.toLocaleString("en-US")} Google reviews</p>}
              <a className="site-cta" href={chatUrl} target="_blank" rel="noopener">{S.cta}</a>
            </div>
            <div className="site-sec">
              <h5>{S.section}<span className="sample">{t.sample}</span></h5>
              <ul>{biz.profile.services_sample.map((s) => <li key={s}><span className="ltr">{s}</span></li>)}</ul>
            </div>
            {f.hours.length > 0 && (
              <div className="site-sec"><h5>{t.hours}</h5>
                <ul>{f.hours.map((h) => <li key={h.day} className="ltr"><span>{h.day}</span><span>{h.hours}</span></li>)}</ul>
              </div>
            )}
            <div className="site-sec"><h5>{t.findUs}</h5><p style={{ fontSize: ".88rem", color: "#334155" }}>{f.address}</p>
              <a href={f.maps_url} target="_blank" rel="noopener">{t.openMaps}</a></div>
            <p className="wm">{t.wm}</p>
          </div></div>
          <div>
            <h3 style={{ fontSize: "1.25rem", marginBottom: "1rem" }}>{t.postsH}</h3>
            <div className="posts">
              {all.map(({ p, l }, i) => (
                <div className="post" key={i} lang={l}>
                  <div className="ph"><span>{l === "ur" ? "اردو" : "English"} · Facebook / Instagram</span>
                    <button type="button" onClick={() => { navigator.clipboard?.writeText(p); setCopied(i); setTimeout(() => setCopied(null), 1500); }}>
                      {copied === i ? t.copied : t.copy}</button></div>
                  <p>{p}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function Field({ label, value, min, max, step, set }: { label: string; value: number; min: number; max: number; step: number; set: (n: number) => void }) {
  return (
    <div className="field">
      <label><span>{label}</span><b className="ltr">{value.toLocaleString("en-US")}</b></label>
      <input type="range" min={min} max={max} step={step} value={value} onChange={(e) => set(+e.target.value)} aria-label={label} />
    </div>
  );
}

function Numbers({ roi, tier, lang, onUse }: { roi: RoiDefaults; tier: Tier; lang: Lang; onUse: () => void }) {
  const t = T[lang];
  const [missed, setMissed] = useState(roi.missed_per_week);
  const [ticket, setTicket] = useState(roi.ticket);
  const [pct, setPct] = useState(roi.recover_pct);
  const [used, setUsed] = useState(false);
  const monthly = useMemo(() => missed * 4.3 * ticket * (pct / 100), [missed, ticket, pct]);
  const net = monthly - tier.monthly;
  const weeks = net > 0 ? Math.ceil(tier.setup / (net / 4.3)) : null;
  const touch = () => { if (!used) { setUsed(true); onUse(); } };
  return (
    <section id="numbers" className="sec">
      <div className="wrap">
        <div className="sec-head"><p className="k">{t.nuK}</p><h2>{t.nuH}</h2><p>{t.nuP}</p></div>
        <div className="roi">
          <div className="roi-in">
            <Field label={roi.missed_label[lang]} value={missed} min={1} max={100} step={1} set={(n) => { setMissed(n); touch(); }} />
            <Field label={roi.ticket_label[lang]} value={ticket} min={200} max={20000} step={100} set={(n) => { setTicket(n); touch(); }} />
            <Field label={t.recover} value={pct} min={10} max={90} step={5} set={(n) => { setPct(n); touch(); }} />
            <p className="formula">{t.formula}</p>
          </div>
          <div className="roi-out">
            <p className="big ltr">{pkr(monthly)}</p><p className="lbl">{t.perMonth}</p>
            <div className="roi-rows">
              <div><span>{t.perYear}</span><b className="ltr">{pkr(monthly * 12)}</b></div>
              <div><span>{t.growthFee}</span><b className="ltr">{pkr(tier.monthly)}</b></div>
              <div><span>{t.payback}</span><b>{weeks != null && weeks <= 52 ? `${weeks} ${t.weeks}` : t.notYet}</b></div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function Plan({ biz, tiers, lang }: { biz: Biz; tiers: Tier[]; lang: Lang }) {
  const t = T[lang];
  const ur = lang === "ur";
  const tier = tiers.find((x) => x.rec) ?? tiers[1];
  const yes = `https://wa.me/923118340514?text=${encodeURIComponent(fill(t.yesText, { name: biz.name, code: biz.code }))}`;
  const names: Record<string, string> = { Starter: "اسٹارٹر", Growth: "گروتھ", Complete: "کمپلیٹ" };
  return (
    <section id="plan" className="sec tint">
      <div className="wrap">
        <div className="sec-head"><p className="k">{t.plK}</p><h2>{t.plH}</h2></div>
        <div className="plan">
          <div className="tier">
            <div className="tn"><h3>{ur ? names[tier.name] : tier.name}</h3><span className="rec">{t.recommended}</span></div>
            <p className="tt">{ur ? tier.tag_ur : tier.tag_en}</p>
            <p className="price"><span className="ltr">{pkr(tier.setup)}</span> <small>{t.setup}</small></p>
            <p className="mo">{t.then} <b className="ltr">{pkr(tier.monthly)}</b> {t.mo}</p>
            <ul>{(ur ? tier.items_ur : tier.items_en).map((i) => <li key={i}><Check /><span>{i}</span></li>)}</ul>
          </div>
          <div className="close">
            <div className="pilot"><b>{t.pilotH}</b><p>{t.pilotP}</p></div>
            <a className="btn" href={yes} target="_blank" rel="noopener" onClick={() => track(biz.slug, biz.token, "plan_click")}><Chat />{t.yes}</a>
            <p className="alt">{t.alt}</p>
          </div>
        </div>
      </div>
    </section>
  );
}
