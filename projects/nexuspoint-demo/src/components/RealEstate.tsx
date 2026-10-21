"use client";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import ChatWindow, { visitorId } from "./ChatWindow";
import { PropertyArt, ReIcon, ReModal } from "./RealEstateUI";
import { dateLabel, dayAfter, localDate, timeLabel } from "@/lib/healthcare-types";
import { cityUr } from "@/lib/city";
import {
  duration, formatPkr, nextStages, replySeconds, responseStats, sizeLabel, sourceLabel, stageLabel, visitSlots,
  type Lead, type Listing, type ReRole, type ReState, type Source, type Stage, type Visit,
} from "@/lib/real-estate-types";
import "./real-estate.css";

type Say = (en: string, ur: string) => string;
type Act = (action: string, data: Record<string, unknown>) => Promise<unknown>;
type VisitOpen = { leadId?: string; listingId?: string; reschedule?: Visit };
type VP = {
  s: ReState; ur: boolean; say: Say; act: Act; pending: boolean; role: ReRole; setTab: (t: string) => void;
  openVisit: (o: VisitOpen) => void; openLead: (id: string) => void; me: string; setMe: (id: string) => void;
};
const L = (ur: boolean) => (ur ? "ur" : "en") as "en" | "ur";
const when = (at: string, ur: boolean) => `${dateLabel(at, L(ur))} · ${timeLabel(at, L(ur))}`;
const buyerName = (s: ReState, id: string) => s.buyers.find((b) => b.id === id)?.name ?? (s.buyer.id === id ? s.buyer.name : "Demo buyer");
const agentName = (s: ReState, id: string | null, ur = false) => { const a = s.agents.find((a) => a.id === id); return a ? (ur && a.name_ur ? a.name_ur : a.name) : ur ? "غیر مقرر" : "Unassigned"; };
const visitStatus: Record<Visit["status"], [string, string]> = { confirmed: ["Confirmed", "کنفرم"], completed: ["Completed", "مکمل"], cancelled: ["Cancelled", "منسوخ"], no_show: ["No-show", "نہیں آئے"] };
const kinds: [Listing["kind"], string, string][] = [["plot", "Plots", "پلاٹ"], ["house", "Houses", "گھر"], ["apartment", "Apartments", "اپارٹمنٹ"], ["commercial", "Commercial", "کمرشل"], ["file", "Files", "فائلیں"]];

function Chip({ children, tone = "" }: { children: React.ReactNode; tone?: string }) { return <span className={`re-chip ${tone}`}>{children}</span>; }
function Empty({ children }: { children: React.ReactNode }) { return <div className="re-empty"><ReIcon name="home" /><p>{children}</p></div>; }
function Stat({ n, label, note, icon = "chart" }: { n: string | number; label: string; note?: string; icon?: string }) {
  return <div className="re-card re-stat"><div className="re-row"><b className="re-stat-n">{n}</b><span className="re-tile"><ReIcon name={icon} /></span></div><span>{label}</span>{note && <small>{note}</small>}</div>;
}

export default function RealEstate({ slug, token, name, role, initialLang, initialTab, initialVisit = false, initialListing }: {
  slug: string; token: string; name: string; role: ReRole; initialLang: "en" | "ur"; initialTab?: string; initialVisit?: boolean; initialListing?: string;
}) {
  const [ur, setUr] = useState(initialLang === "ur"), [theme, setTheme] = useState("dark"), [s, setS] = useState<ReState | null>(null);
  const [error, setError] = useState(""), [pending, setPending] = useState(false), [toast, setToast] = useState("");
  const tabs = role === "buyer" ? ["overview", "listings", "visits", "messages"] : role === "agent" ? ["pipeline", "visits", "inbox", "listings"] : ["overview", "pipeline", "visits", "agents", "settings"];
  const [tab, setTabState] = useState(tabs.includes(initialTab ?? "") ? initialTab! : tabs[0]);
  const [visit, setVisit] = useState<VisitOpen | null>(null), [lead, setLead] = useState<string | null>(null), [enquire, setEnquire] = useState(false), [me, setMe] = useState("all");
  const visitor = useRef(""), busy = useRef(false), mounted = useRef(false), fetching = useRef(false), opened = useRef(false);
  const say: Say = (en, u) => (ur ? u : en);
  const titles: Record<string, string> = {
    overview: role === "manager" ? say("Lead sources & response", "لیڈ ذرائع اور جواب") : say("Your property search", "آپ کی پراپرٹی تلاش"),
    listings: say("Sample listings", "نمونہ لسٹنگز"), visits: say("Site visits", "سائٹ وزٹس"), messages: say("Assistant", "اسسٹنٹ"),
    pipeline: say("Lead pipeline", "لیڈ پائپ لائن"), inbox: say("Conversations", "گفتگو"), agents: say("Agents", "ایجنٹس"), settings: say("Office hours", "دفتری اوقات"),
  };
  const icons: Record<string, string> = { overview: role === "manager" ? "chart" : "home", listings: "grid", visits: "calendar", messages: "chat", pipeline: "pipeline", inbox: "chat", agents: "users", settings: "settings" };
  const setTab = (v: string) => { setTabState(v); const u = new URL(location.href); u.searchParams.set("tab", v); history.replaceState(null, "", u); };
  const refresh = useCallback(async () => {
    if (!visitor.current || fetching.current || document.visibilityState !== "visible") return;
    fetching.current = true;
    try {
      const r = await fetch(`/api/real-estate?${new URLSearchParams({ slug, t: token, visitor: visitor.current, role })}`, { cache: "no-store" }), d = await r.json();
      if (!r.ok) throw new Error(d.error ?? "Connection problem");
      if (mounted.current) { setS(d); setError(""); }
    } catch (e) { if (mounted.current) setError(e instanceof Error ? e.message : "Connection problem"); }
    finally { fetching.current = false; }
  }, [slug, token, role]);
  useEffect(() => {
    mounted.current = true; visitor.current = visitorId(slug);
    try { const t = localStorage.getItem("np-re-theme"); if (t === "light" || t === "dark") setTheme(t); } catch {}
    refresh(); const id = setInterval(refresh, 2500); document.addEventListener("visibilitychange", refresh);
    return () => { mounted.current = false; clearInterval(id); document.removeEventListener("visibilitychange", refresh); };
  }, [slug, refresh]);
  useEffect(() => { if (!toast) return; const id = setTimeout(() => setToast(""), 4500); return () => clearTimeout(id); }, [toast]);
  useEffect(() => { if (s && initialVisit && !opened.current) { opened.current = true; setVisit({ listingId: initialListing }); } }, [s, initialVisit, initialListing]);
  const act: Act = async (action, data) => {
    if (busy.current) throw new Error(say("Please wait", "انتظار کریں")); busy.current = true; setPending(true); setError("");
    try {
      const r = await fetch("/api/real-estate", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ slug, t: token, visitor: visitor.current, role, action, ...data }) }), d = await r.json();
      if (!r.ok) throw new Error(d.error ?? say("Unable to save", "محفوظ نہیں ہو سکا"));
      await refresh(); setToast(say("Saved. Demo only: no real messages or calls are sent.", "محفوظ۔ صرف ڈیمو: کوئی حقیقی پیغام یا کال نہیں بھیجی گئی۔")); return d.result;
    } catch (e) { setError(e instanceof Error ? e.message : "Connection problem"); throw e; }
    finally { busy.current = false; setPending(false); }
  };
  const link = (r: string) => `/d/${slug}/${r}?t=${encodeURIComponent(token)}${ur ? "&lang=ur" : ""}`;
  const props: VP | null = s ? { s, ur, say, act, pending, role, setTab, openVisit: setVisit, openLead: setLead, me, setMe } : null;
  const nav = tabs.map((v) => <button key={v} className={tab === v ? "active" : ""} aria-current={tab === v ? "page" : undefined} onClick={() => setTab(v)}><ReIcon name={icons[v]} />{titles[v]}</button>);
  const city = s?.city ?? "";
  return <div className="re" dir={ur ? "rtl" : "ltr"} lang={ur ? "ur" : "en"} data-re-theme={theme}>
    <aside className="re-side">
      <a className="re-brand" href={link(role === "agent" ? "agents" : role)}><span className="re-mark"><ReIcon name="pin" /></span><span>LEADLINE<small>BY NEXUSPOINT</small></span></a>
      <div className="re-biz"><b>{name}</b><small>{city ? `${ur ? cityUr(city) : city} · ` : ""}{say("Connected sales office demo", "مربوط سیلز آفس ڈیمو")}</small></div>
      <nav className="re-nav" aria-label={say("Workspace", "ورک اسپیس")}>{nav}</nav>
      <div className="re-disclosure"><b>{say("A working preview", "نمونہ ڈیمو")}</b><p>{say("Listings, prices, agents and buyers are fictional. Visits are real database bookings in this demo; no calls or messages leave it.", "لسٹنگز، قیمتیں، ایجنٹ اور خریدار فرضی ہیں۔ وزٹ اس ڈیمو کے ڈیٹابیس میں محفوظ ہوتے ہیں، کوئی کال یا پیغام باہر نہیں جاتا۔")}</p></div>
      <a className="re-back" href={`/d/${slug}?t=${encodeURIComponent(token)}${ur ? "&lang=ur" : ""}`}>{say("Back to your report", "اپنی رپورٹ پر واپس")}</a>
    </aside>
    <div className="re-main">
      <header className="re-top">
        <span className="re-crumb">{say("Workspace", "ورک اسپیس")} / <b>{titles[tab]}</b></span>
        <div className="re-tools">
          <select aria-label={say("Demo role", "ڈیمو کردار")} value={role} onChange={(e) => location.assign(link(e.target.value === "agent" ? "agents" : e.target.value))}>
            <option value="buyer">{say("Buyer portal", "خریدار پورٹل")}</option><option value="agent">{say("Agent pipeline", "ایجنٹ پائپ لائن")}</option><option value="manager">{say("Manager view", "منیجر منظر")}</option>
          </select>
          <button className="re-icon-btn" type="button" aria-label={say("Switch theme", "تھیم بدلیں")} onClick={() => { const n = theme === "dark" ? "light" : "dark"; setTheme(n); try { localStorage.setItem("np-re-theme", n); } catch {} }}><ReIcon name="sun" /></button>
          <button className="re-icon-btn re-lang" type="button" aria-label={say("Read in Urdu", "Read in English")} onClick={() => { setUr(!ur); const u = new URL(location.href); u.searchParams.set("lang", ur ? "en" : "ur"); history.replaceState(null, "", u); }}>{ur ? "EN" : "اردو"}</button>
        </div>
      </header>
      <nav className="re-mobile-nav" aria-label="Mobile navigation">{nav}</nav>
      <main className="re-content" aria-busy={!s}>
        <div className="re-heading"><p className="re-kicker">{role === "buyer" ? say("Buyer portal", "خریدار پورٹل") : role === "agent" ? say("Agent pipeline", "ایجنٹ پائپ لائن") : say("Manager view", "منیجر منظر")}</p>
          <div className="re-row"><h1>{titles[tab]}</h1>
            {s && role === "buyer" && <button className="re-btn" onClick={() => setVisit({})}><ReIcon name="calendar" />{say("Book a site visit", "سائٹ وزٹ بک کریں")}</button>}
            {s && role !== "buyer" && (tab === "pipeline" || tab === "visits") && <button className="re-btn" onClick={() => setVisit({})}><ReIcon name="calendar" />{say("Book a visit for a lead", "لیڈ کے لیے وزٹ بک کریں")}</button>}
          </div>
          <p>{say("Synthetic demo data · All times Pakistan Standard Time (PKT)", "فرضی ڈیمو ڈیٹا · تمام اوقات پاکستان کے وقت کے مطابق")}</p></div>
        {error && <div className="re-error" role="alert"><span>{error}</span><button className="re-link" onClick={refresh}>{say("Retry", "دوبارہ کوشش")}</button></div>}
        {!s || !props ? <div className="re-card"><Empty>{error ? say("Reconnect to load the office.", "آفس لوڈ کرنے کے لیے دوبارہ جڑیں۔") : say("Preparing your sample sales office…", "نمونہ سیلز آفس تیار ہو رہا ہے…")}</Empty></div> : <>
          {tab === "overview" && role === "buyer" && <BuyerOverview {...props} enquire={() => setEnquire(true)} />}
          {tab === "overview" && role === "manager" && <ManagerOverview {...props} />}
          {tab === "listings" && <Listings {...props} />}
          {tab === "visits" && <Visits {...props} />}
          {tab === "messages" && <div className="re-columns"><div className="re-card re-chat"><ChatWindow slug={slug} token={token} name={name} lang={ur ? "ur" : "en"} realEstate prompts={ur ? ["دس مرلہ پلاٹ چاہیے، بجٹ ڈھائی کروڑ", "سائٹ وزٹ بک کریں", "کیا این او سی منظور ہے؟"] : ["10 marla plot chahiye, budget 2.5 crore", "Book a site visit", "Is the society NOC approved?"]} /></div>
            <div className="re-card re-stack"><ReIcon name="bolt" /><h2>{say("Replies in seconds, qualifies like an agent", "سیکنڈوں میں جواب، ایجنٹ کی طرح جانچ")}</h2><p>{say("The assistant asks budget, society, size, timeline and whether you are overseas, one question at a time. It only shows stored sample listings, books visits into the same calendar as this portal, and passes legal and NOC questions to an agent.", "اسسٹنٹ بجٹ، سوسائٹی، سائز، وقت اور بیرون ملک ہونے کے بارے میں ایک ایک کر کے پوچھتا ہے۔ صرف محفوظ نمونہ لسٹنگز دکھاتا ہے، اسی کیلنڈر میں وزٹ بک کرتا ہے، اور قانونی یا این او سی سوال ایجنٹ کو بھیجتا ہے۔")}</p><button className="re-btn ghost" onClick={() => setTab("visits")}>{say("My site visits", "میرے سائٹ وزٹس")}</button></div></div>}
          {tab === "pipeline" && <Pipeline {...props} />}
          {tab === "inbox" && <Inbox {...props} />}
          {tab === "agents" && <Agents {...props} />}
          {tab === "settings" && <Settings {...props} />}
        </>}
        <footer className="re-foot">{say("Built by NexusPoint · Fictional listings, prices and buyers · Role switching is for presentations", "NexusPoint · فرضی لسٹنگز، قیمتیں اور خریدار · پیشکش کے لیے کردار کی تبدیلی")}</footer>
      </main>
    </div>
    {toast && <div className="re-toast" role="status">{toast}</div>}
    {props && visit && <VisitModal {...props} open={visit} onClose={() => setVisit(null)} onDone={() => { setVisit(null); if (role === "buyer") setTab("visits"); }} />}
    {props && lead && <LeadModal {...props} id={lead} onClose={() => setLead(null)} />}
    {props && enquire && <EnquiryModal {...props} onClose={() => setEnquire(false)} />}
  </div>;
}

function Field({ k, v }: { k: string; v: string }) { return <div className="re-field"><small>{k}</small><b dir="auto">{v}</b></div>; }
function qualFields(l: Lead, p: VP) {
  const { say, ur } = p, missing = say("Not shared yet", "ابھی نہیں بتایا");
  return [
    [say("Budget", "بجٹ"), l.budget != null ? formatPkr(l.budget, L(ur)) : missing], [say("Society or area", "سوسائٹی یا علاقہ"), l.area || missing],
    [say("Size and type", "سائز اور قسم"), [l.size, l.kind].filter(Boolean).join(" ") || missing], [say("Timeline", "وقت"), l.timeline || missing],
    [say("Buyer location", "خریدار کہاں"), l.overseas == null ? missing : l.overseas ? `${say("Overseas", "بیرون ملک")}${l.country ? " · " + l.country : ""}` : say("In Pakistan", "پاکستان میں")],
  ] as [string, string][];
}

function BuyerOverview(p: VP & { enquire: () => void }) {
  const { s, say, ur } = p, lead = s.leads[0], upcoming = s.visits.filter((v) => v.status === "confirmed");
  return <>
    <div className="re-hero">
      <div><p className="re-kicker">{say("Plots, homes and apartments", "پلاٹ، گھر اور اپارٹمنٹ")}</p><h2>{say("Find the right property. Then see it in person.", "درست پراپرٹی تلاش کریں۔ پھر خود جا کر دیکھیں۔")}</h2>
        <p>{say("Tell us your budget and society, browse sample listings, and pick a site-visit time with an agent. Overseas buyers can book from any time zone.", "اپنا بجٹ اور سوسائٹی بتائیں، نمونہ لسٹنگز دیکھیں، اور ایجنٹ کے ساتھ سائٹ وزٹ کا وقت منتخب کریں۔ بیرون ملک خریدار کسی بھی وقت بک کر سکتے ہیں۔")}</p>
        <div className="re-inline"><button className="re-btn" onClick={() => p.setTab("listings")}>{say("Browse listings", "لسٹنگز دیکھیں")}<ReIcon name="arrow" /></button><button className="re-btn ghost" onClick={p.enquire}>{say("Send an enquiry", "انکوائری بھیجیں")}</button></div></div>
      <PropertyArt kind="house" />
    </div>
    <div className="re-columns re-gap">
      <div className="re-card">
        <div className="re-card-head"><h2>{say("Your enquiry", "آپ کی انکوائری")}</h2>{lead && <Chip tone={lead.stage}>{stageLabel[lead.stage][L(ur)]}</Chip>}</div>
        {lead ? <><p className="re-summary" dir="auto">{lead.summary || say("The assistant is collecting your requirements.", "اسسٹنٹ آپ کی ضروریات معلوم کر رہا ہے۔")}</p>
          <div className="re-fields">{qualFields(lead, p).map(([k, v]) => <Field key={k} k={k} v={v} />)}</div>
          <small>{say("Agent", "ایجنٹ")}: {agentName(s, lead.agent_id, ur)} · {sourceLabel[lead.source][L(ur)]}</small></>
          : <Empty>{say("No enquiry yet. Message the assistant or send the enquiry form; it appears here and in the agent pipeline.", "ابھی کوئی انکوائری نہیں۔ اسسٹنٹ کو میسج کریں یا فارم بھیجیں، یہ یہاں اور ایجنٹ پائپ لائن میں نظر آئے گی۔")}</Empty>}
        <div className="re-inline re-gap"><button className="re-btn ghost small" onClick={() => p.setTab("messages")}>{say("Continue with the assistant", "اسسٹنٹ سے بات جاری رکھیں")}</button></div>
      </div>
      <div className="re-card re-stack">
        <div className="re-card-head"><h2>{say("Upcoming site visits", "آنے والے سائٹ وزٹس")}</h2><ReIcon name="calendar" /></div>
        {upcoming.map((v) => <div className="re-list-row" key={v.id}><b>{when(v.starts_at, ur)}</b><small>{agentName(s, v.agent_id, ur)}{v.listing_id ? " · " + (s.listings.find((l) => l.id === v.listing_id)?.code ?? "") : ""}</small></div>)}
        {!upcoming.length && <small>{say("Pick a time and an agent meets you at the site. Visits last one hour.", "وقت منتخب کریں، ایجنٹ آپ سے سائٹ پر ملے گا۔ وزٹ ایک گھنٹے کا ہوتا ہے۔")}</small>}
        <button className="re-btn small" onClick={() => p.openVisit({})}>{say("Book a site visit", "سائٹ وزٹ بک کریں")}</button>
      </div>
    </div>
    <div className="re-card-head re-gap"><h2>{say("Featured sample listings", "منتخب نمونہ لسٹنگز")}</h2><button className="re-link" onClick={() => p.setTab("listings")}>{say("All listings", "تمام لسٹنگز")}</button></div>
    <div className="re-grid">{s.listings.filter((l) => l.status === "available").slice(0, 3).map((l) => <ListingCard key={l.id} {...p} l={l} />)}</div>
  </>;
}

function ListingCard(p: VP & { l: Listing }) {
  const { l, say, ur, role } = p;
  return <article className={`re-card re-listing ${l.status}`}>
    <div className="re-listing-art"><PropertyArt kind={l.art || l.kind} /><span className="re-code">{l.code}</span>{l.status !== "available" && <span className="re-status-tag">{l.status === "reserved" ? say("Reserved", "ریزرو") : say("Sold", "فروخت")}</span>}</div>
    <div className="re-listing-body">
      <small className="re-eyebrow">{ur ? l.society_ur || l.society : l.society}{l.block ? ` · ${l.block}` : ""}</small>
      <h3 dir="auto">{ur ? l.title_ur || l.title : l.title}</h3>
      <div className="re-specs"><span>{sizeLabel(l, L(ur))}</span>{l.beds != null && <span>{l.beds} {say("bed", "بیڈ")}</span>}{l.baths != null && <span>{l.baths} {say("bath", "باتھ")}</span>}<span>{kinds.find((k) => k[0] === l.kind)?.[ur ? 2 : 1]}</span></div>
      <p dir="auto">{ur ? l.description_ur || l.description : l.description}</p>
      <div className="re-row re-price-row"><div><small>{say("Sample demand", "نمونہ ڈیمانڈ")}</small><b className="re-price">{formatPkr(l.price, L(ur))}</b></div>
        {role === "buyer" ? <button className="re-btn small" disabled={l.status === "sold"} onClick={() => p.openVisit({ listingId: l.id })}>{say("Book a visit", "وزٹ بک کریں")}</button>
          : <select aria-label={say("Listing status", "لسٹنگ کی حالت")} value={l.status} disabled={p.pending} onChange={(e) => void p.act("listing", { id: l.id, status: e.target.value }).catch(() => {})}>
            <option value="available">{say("Available", "دستیاب")}</option><option value="reserved">{say("Reserved", "ریزرو")}</option><option value="sold">{say("Sold", "فروخت")}</option></select>}
      </div>
    </div>
  </article>;
}

function Listings(p: VP) {
  const { s, say, ur } = p, [kind, setKind] = useState("all"), [society, setSociety] = useState("all"), [max, setMax] = useState(0);
  const societies = [...new Set(s.listings.map((l) => l.society))];
  const shown = s.listings.filter((l) => (kind === "all" || l.kind === kind) && (society === "all" || l.society === society) && (!max || l.price <= max));
  return <>
    <div className="re-filters">
      <div className="re-tabs" role="group" aria-label={say("Property type", "پراپرٹی کی قسم")}><button className={kind === "all" ? "active" : ""} onClick={() => setKind("all")}>{say("All", "تمام")}</button>{kinds.filter(([k]) => s.listings.some((l) => l.kind === k)).map(([k, en, u]) => <button key={k} className={kind === k ? "active" : ""} onClick={() => setKind(k)}>{ur ? u : en}</button>)}</div>
      <select aria-label={say("Society", "سوسائٹی")} value={society} onChange={(e) => setSociety(e.target.value)}><option value="all">{say("All societies", "تمام سوسائٹیز")}</option>{societies.map((x) => <option key={x} value={x}>{x}</option>)}</select>
      <select aria-label={say("Maximum budget", "زیادہ سے زیادہ بجٹ")} value={max} onChange={(e) => setMax(Number(e.target.value))}><option value={0}>{say("Any budget", "کوئی بھی بجٹ")}</option>{[5e6, 1e7, 2.5e7, 5e7, 1e8].map((n) => <option key={n} value={n}>{say("Up to ", "تک ")}{formatPkr(n, L(ur))}</option>)}</select>
    </div>
    <div className="re-grid">{shown.map((l) => <ListingCard key={l.id} {...p} l={l} />)}</div>
    {!shown.length && <div className="re-card"><Empty>{say("No sample listing matches these filters.", "ان فلٹرز کے مطابق کوئی نمونہ لسٹنگ نہیں۔")}</Empty></div>}
    <p className="re-note">{say("Fictional listings and demand prices for this outreach demo. Availability, approvals and final prices are confirmed by an agent.", "یہ آؤٹ ریچ ڈیمو کی فرضی لسٹنگز اور قیمتیں ہیں۔ دستیابی، منظوری اور آخری قیمت ایجنٹ کنفرم کرے گا۔")}</p>
  </>;
}

function Visits(p: VP) {
  const { s, say, ur, role } = p, [filter, setFilter] = useState("upcoming");
  const now = new Date(s.server_time).getTime();
  const rows = s.visits.filter((v) => filter === "all" || (filter === "upcoming" ? v.status === "confirmed" : v.status !== "confirmed"))
    .filter((v) => role === "buyer" || p.me === "all" || v.agent_id === p.me).sort((a, b) => a.starts_at.localeCompare(b.starts_at));
  const days = [...new Set(rows.map((v) => localDate(v.starts_at)))];
  return <>
    <div className="re-filters"><div className="re-tabs">{[["upcoming", say("Upcoming", "آنے والے")], ["past", say("Completed & cancelled", "مکمل اور منسوخ")], ["all", say("All", "تمام")]].map(([k, t]) => <button key={k} className={filter === k ? "active" : ""} onClick={() => setFilter(k)}>{t}</button>)}</div>
      {role !== "buyer" && <AgentFilter {...p} />}</div>
    {days.map((d) => <section key={d} className="re-day"><h3>{dateLabel(`${d}T12:00:00+05:00`, L(ur))}</h3>
      {rows.filter((v) => localDate(v.starts_at) === d).map((v) => { const l = s.listings.find((x) => x.id === v.listing_id), started = new Date(v.starts_at).getTime() <= now;
        return <div className="re-card re-visit" key={v.id}>
          <div className="re-visit-time"><b>{timeLabel(v.starts_at, L(ur))}</b><small>{say("1 hour", "ایک گھنٹہ")}</small></div>
          <div className="re-visit-body"><b>{role === "buyer" ? (l ? `${l.code} · ${ur ? l.title_ur || l.title : l.title}` : say("Site visit with an agent", "ایجنٹ کے ساتھ سائٹ وزٹ")) : buyerName(s, v.buyer_id)}</b>
            <small>{agentName(s, v.agent_id, ur)}{role !== "buyer" && l ? ` · ${l.code}, ${l.society}` : ""} · {v.source === "chat" ? say("Booked by the assistant", "اسسٹنٹ نے بک کیا") : v.source === "staff" ? say("Booked by staff", "عملے نے بک کیا") : v.source === "sample" ? say("Sample booking", "نمونہ بکنگ") : say("Booked online", "آن لائن بک")}</small></div>
          <Chip tone={v.status}>{visitStatus[v.status][ur ? 1 : 0]}</Chip>
          {v.status === "confirmed" && <div className="re-inline">
            <button className="re-btn ghost small" onClick={() => p.openVisit({ reschedule: v })}>{say("Reschedule", "وقت بدلیں")}</button>
            <button className="re-btn danger small" disabled={p.pending} onClick={() => void p.act("visit", { id: v.id, status: "cancelled" }).catch(() => {})}>{say("Cancel", "منسوخ")}</button>
            {role !== "buyer" && <><button className="re-btn small" disabled={p.pending || !started} onClick={() => void p.act("visit", { id: v.id, status: "completed" }).catch(() => {})}>{say("Mark done", "مکمل")}</button>
              <button className="re-btn ghost small" disabled={p.pending || !started} onClick={() => void p.act("visit", { id: v.id, status: "no_show" }).catch(() => {})}>{say("No-show", "نہیں آئے")}</button>
              <button className="re-link" onClick={() => p.openLead(v.lead_id)}>{say("Open lead", "لیڈ کھولیں")}</button></>}
          </div>}
        </div>; })}
    </section>)}
    {!rows.length && <div className="re-card"><Empty>{say("No site visits in this view.", "اس منظر میں کوئی سائٹ وزٹ نہیں۔")}</Empty></div>}
  </>;
}

function AgentFilter(p: VP) {
  return <label className="re-agent-filter">{p.say("Agent", "ایجنٹ")}<select value={p.me} onChange={(e) => p.setMe(e.target.value)}><option value="all">{p.say("All agents", "تمام ایجنٹس")}</option>{p.s.agents.map((a) => <option key={a.id} value={a.id}>{p.ur && a.name_ur ? a.name_ur : a.name}</option>)}</select></label>;
}

const COLUMNS: Stage[] = ["new", "qualified", "visit_booked", "negotiating", "won", "lost"];
function Pipeline(p: VP) {
  const { s, say, ur } = p, [query, setQuery] = useState("");
  const leads = s.leads.filter((l) => (p.me === "all" || l.agent_id === p.me) && `${buyerName(s, l.buyer_id)} ${l.area} ${l.summary}`.toLowerCase().includes(query.toLowerCase()));
  return <>
    <div className="re-filters"><label className="re-search"><ReIcon name="search" /><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder={say("Search buyers, areas, summaries", "خریدار، علاقہ یا خلاصہ تلاش کریں")} aria-label={say("Search leads", "لیڈز تلاش کریں")} /></label><AgentFilter {...p} /></div>
    <div className="re-board">{COLUMNS.map((st) => { const col = leads.filter((l) => l.stage === st);
      return <section className="re-col" key={st} aria-label={stageLabel[st][L(ur)]}><div className="re-col-head"><h2>{stageLabel[st][L(ur)]}</h2><span>{col.length}</span></div>
        {col.map((l) => <LeadCard key={l.id} {...p} l={l} />)}{!col.length && <p className="re-col-empty">{say("No leads", "کوئی لیڈ نہیں")}</p>}</section>; })}</div>
  </>;
}

function LeadCard(p: VP & { l: Lead }) {
  const { l, s, say, ur } = p, rs = replySeconds(l), b = s.buyers.find((x) => x.id === l.buyer_id);
  const visit = s.visits.find((v) => v.lead_id === l.id && v.status === "confirmed");
  return <article className="re-lead">
    <button className="re-lead-open" onClick={() => p.openLead(l.id)} aria-label={say("Open lead ", "لیڈ کھولیں ") + (b?.name ?? "")} />
    <div className="re-row"><b dir="auto">{b?.name ?? "Demo buyer"}</b>{(l.overseas ?? b?.overseas) && <Chip tone="overseas"><ReIcon name="plane" />{l.country || say("Overseas", "بیرون ملک")}</Chip>}</div>
    <div className="re-lead-meta"><span>{sourceLabel[l.source][L(ur)]}</span><span className={rs != null && rs <= 300 ? "fast" : "slow"}>{say("First reply", "پہلا جواب")} {duration(rs, L(ur))}</span></div>
    <p dir="auto">{l.summary || say("Waiting for the buyer's requirements.", "خریدار کی ضروریات کا انتظار۔")}</p>
    <div className="re-lead-tags">{l.budget != null && <Chip>{formatPkr(l.budget, L(ur))}</Chip>}{l.area && <Chip>{l.area}</Chip>}{l.size && <Chip>{l.size}</Chip>}</div>
    {visit && <small className="re-lead-visit"><ReIcon name="calendar" />{when(visit.starts_at, ur)}</small>}
    <div className="re-row re-lead-foot"><span className="re-avatar" title={agentName(s, l.agent_id)}>{agentName(s, l.agent_id).split(" ").map((x) => x[0]).join("").slice(0, 2)}</span><small>{agentName(s, l.agent_id, ur)}</small></div>
  </article>;
}

function LeadModal(p: VP & { id: string; onClose: () => void }) {
  const { s, say, ur } = p, l = s.leads.find((x) => x.id === p.id);
  const [reason, setReason] = useState(""), [note, setNote] = useState(""), [losing, setLosing] = useState(false);
  if (!l) return <ReModal title={say("Lead", "لیڈ")} onClose={p.onClose}><Empty>{say("This lead is no longer available.", "یہ لیڈ دستیاب نہیں۔")}</Empty></ReModal>;
  const conv = s.conversations.find((c) => c.id === l.conversation_id), visits = s.visits.filter((v) => v.lead_id === l.id), b = s.buyers.find((x) => x.id === l.buyer_id);
  const move = (stage: Stage) => stage === "lost" ? setLosing(true) : stage === "visit_booked" && !visits.some((v) => v.status === "confirmed") ? p.openVisit({ leadId: l.id }) : void p.act("stage", { id: l.id, stage }).catch(() => {});
  return <ReModal title={b?.name ?? say("Lead", "لیڈ")} onClose={p.onClose} wide>
    <div className="re-inline"><Chip tone={l.stage}>{stageLabel[l.stage][L(ur)]}</Chip><Chip>{sourceLabel[l.source][L(ur)]}</Chip><Chip>{say("First reply", "پہلا جواب")} {duration(replySeconds(l), L(ur))}</Chip>{l.lost_reason && <Chip tone="lost">{l.lost_reason}</Chip>}</div>
    <div className="re-ai"><small><ReIcon name="bolt" />{say("Assistant summary", "اسسٹنٹ کا خلاصہ")}</small><p dir="auto">{l.summary || say("No summary yet.", "ابھی خلاصہ نہیں۔")}</p>{l.notes && <p className="re-note" dir="auto">{l.notes}</p>}</div>
    <div className="re-fields">{qualFields(l, p).map(([k, v]) => <Field key={k} k={k} v={v} />)}</div>
    <div className="re-modal-grid">
      <div className="re-stack">
        <label>{say("Assigned agent", "ذمہ دار ایجنٹ")}<select value={l.agent_id ?? ""} disabled={p.pending} onChange={(e) => e.target.value && void p.act("assign", { id: l.id, agentId: e.target.value }).catch(() => {})}><option value="">{say("Unassigned", "غیر مقرر")}</option>{s.agents.filter((a) => a.active || a.id === l.agent_id).map((a) => <option key={a.id} value={a.id}>{a.name} · {a.title}</option>)}</select></label>
        <div><small>{say("Move to", "اگلا مرحلہ")}</small><div className="re-inline">{nextStages(l.stage).map((st) => <button key={st} className={`re-btn small ${st === "lost" ? "danger" : st === "won" ? "" : "ghost"}`} disabled={p.pending} onClick={() => move(st)}>{stageLabel[st][L(ur)]}</button>)}{!nextStages(l.stage).length && <small>{say("Closed deal", "سودا مکمل")}</small>}</div></div>
        {losing && <div className="re-inline"><input value={reason} maxLength={200} onChange={(e) => setReason(e.target.value)} placeholder={say("Why was it lost?", "لیڈ کیوں ضائع ہوئی؟")} aria-label={say("Lost reason", "وجہ")} /><button className="re-btn danger small" disabled={p.pending || reason.trim().length < 2} onClick={() => void p.act("stage", { id: l.id, stage: "lost", reason }).then(() => setLosing(false)).catch(() => {})}>{say("Mark lost", "ضائع نشان لگائیں")}</button></div>}
        <button className="re-btn small" disabled={["won", "lost"].includes(l.stage)} onClick={() => p.openVisit({ leadId: l.id, listingId: l.listing_id ?? undefined })}><ReIcon name="calendar" />{say("Book a site visit", "سائٹ وزٹ بک کریں")}</button>
        <h3>{say("Visits", "وزٹس")}</h3>{visits.map((v) => <small key={v.id}>{when(v.starts_at, ur)} · {agentName(s, v.agent_id, ur)} · {visitStatus[v.status][ur ? 1 : 0]}</small>)}{!visits.length && <small>{say("None yet", "ابھی نہیں")}</small>}
      </div>
      <div className="re-stack">
        <h3>{say("History", "تاریخ")}</h3>
        <ol className="re-history">{[...l.history].reverse().slice(0, 12).map((h, i) => <li key={i}><b>{h.kind === "stage" ? stageLabel[h.text as Stage]?.[L(ur)] ?? h.text : h.text}</b><small>{when(h.at, ur)}</small></li>)}</ol>
        <form className="re-inline" onSubmit={(e) => { e.preventDefault(); void p.act("note", { id: l.id, text: note }).then(() => setNote("")).catch(() => {}); }}><input value={note} maxLength={500} onChange={(e) => setNote(e.target.value)} placeholder={say("Add a note for the team", "ٹیم کے لیے نوٹ")} aria-label={say("Note", "نوٹ")} /><button className="re-btn ghost small" disabled={!note.trim() || p.pending}>{say("Add", "شامل")}</button></form>
      </div>
    </div>
    {conv && <><h3 className="re-gap">{say("Conversation", "گفتگو")}</h3><div className="re-transcript">{conv.messages.slice(-12).map((m, i) => <div key={i} className={`re-bubble ${m.role}`}><p dir="auto">{m.content}</p><small>{m.role === "customer" ? say("Buyer", "خریدار") : m.source === "staff" ? say("Agent", "ایجنٹ") : say("Assistant", "اسسٹنٹ")} · {timeLabel(m.at, L(ur))}</small></div>)}</div></>}
  </ReModal>;
}

function Inbox(p: VP) {
  const { s, say, ur } = p, [selected, setSelected] = useState(""), [text, setText] = useState("");
  const c = s.conversations.find((x) => x.id === selected) ?? s.conversations[0];
  if (!c) return <div className="re-card"><Empty>{say("Buyer conversations appear here after the first message.", "پہلے پیغام کے بعد خریداروں کی گفتگو یہاں نظر آئے گی۔")}</Empty></div>;
  const lead = s.leads.find((l) => l.conversation_id === c.id), buyer = s.buyers.find((b) => b.visitor === c.visitor);
  return <div className="re-inbox">
    <div className="re-card re-inbox-list">{s.conversations.map((x) => <button key={x.id} className={x.id === c.id ? "active" : ""} onClick={() => setSelected(x.id)}><b>{s.buyers.find((b) => b.visitor === x.visitor)?.name ?? say("Demo buyer", "نمونہ خریدار")}</b><small dir="auto">{x.summary ?? x.messages.at(-1)?.content}</small>{x.handoff && <Chip tone="lost">{say("Needs an agent", "ایجنٹ درکار")}</Chip>}</button>)}</div>
    <div className="re-card">
      <div className="re-row"><h2>{buyer?.name ?? say("Conversation", "گفتگو")}</h2><button className="re-btn small" disabled={p.pending} onClick={() => void p.act("conversation", { id: c.id, staffMode: !c.staff_mode, assignedTo: lead ? agentName(s, lead.agent_id) : "" }).catch(() => {})}>{c.staff_mode ? say("Hand back to assistant", "اسسٹنٹ کو واپس") : say("Take over", "گفتگو سنبھالیں")}</button></div>
      <small>{c.staff_mode ? say("An agent is replying. The assistant is paused.", "ایجنٹ جواب دے رہا ہے۔ اسسٹنٹ رکا ہوا ہے۔") : say("The assistant is replying.", "اسسٹنٹ جواب دے رہا ہے۔")}</small>
      <div className="re-transcript">{c.messages.map((m, i) => <div key={i} className={`re-bubble ${m.role}`}><p dir="auto">{m.content}</p><small>{m.role === "customer" ? say("Buyer", "خریدار") : m.source === "staff" ? say("Agent", "ایجنٹ") : say("Assistant", "اسسٹنٹ")} · {timeLabel(m.at, L(ur))}</small></div>)}</div>
      <form className="re-inline" onSubmit={(e) => { e.preventDefault(); void p.act("conversation", { id: c.id, text }).then(() => setText("")).catch(() => {}); }}><input value={text} onChange={(e) => setText(e.target.value)} maxLength={2000} disabled={!c.staff_mode} aria-label={say("Agent reply", "ایجنٹ کا جواب")} placeholder={c.staff_mode ? say("Reply as the agent…", "ایجنٹ کے طور پر جواب…") : say("Take over to reply", "جواب کے لیے گفتگو سنبھالیں")} /><button className="re-btn" disabled={!c.staff_mode || !text.trim() || p.pending}>{say("Send", "بھیجیں")}</button></form>
    </div>
    <div className="re-card re-stack re-inbox-context"><h2>{say("Lead", "لیڈ")}</h2>{lead ? <><Chip tone={lead.stage}>{stageLabel[lead.stage][L(ur)]}</Chip><p dir="auto">{lead.summary}</p><button className="re-btn ghost small" onClick={() => p.openLead(lead.id)}>{say("Open lead", "لیڈ کھولیں")}</button></> : <small>{say("No qualified lead yet.", "ابھی کوئی لیڈ نہیں۔")}</small>}</div>
  </div>;
}

function ManagerOverview(p: VP) {
  const { s, say, ur } = p;
  const stats = useMemo(() => responseStats(s.leads, s.visits), [s.leads, s.visits]);
  const maxLeads = Math.max(1, ...stats.sources.map((x) => x.leads));
  const slowest = [...s.leads].map((l) => ({ l, r: replySeconds(l) })).sort((a, b) => (b.r ?? 1e9) - (a.r ?? 1e9)).slice(0, 5);
  const upcoming = s.visits.filter((v) => v.status === "confirmed").sort((a, b) => a.starts_at.localeCompare(b.starts_at)).slice(0, 5);
  return <>
    <div className="re-grid four">
      <Stat n={stats.total} label={say("Leads in the pipeline", "پائپ لائن میں لیڈز")} icon="users" />
      <Stat n={duration(stats.medianReply, L(ur))} label={say("Median first reply", "پہلے جواب کا درمیانی وقت")} icon="bolt" note={stats.unanswered ? say(`${stats.unanswered} not answered yet`, `${stats.unanswered} کا جواب باقی`) : undefined} />
      <Stat n={stats.underFiveMin == null ? "–" : `${stats.underFiveMin}%`} label={say("Replied within 5 minutes", "پانچ منٹ میں جواب")} icon="clock" />
      <Stat n={stats.visitRate == null ? "–" : `${stats.visitRate}%`} label={say("Leads with a site visit", "سائٹ وزٹ والی لیڈز")} icon="calendar" note={say(`${s.leads.filter((l) => l.stage === "won").length} won`, `${s.leads.filter((l) => l.stage === "won").length} سودے مکمل`)} />
    </div>
    <div className="re-columns re-gap">
      <div className="re-card"><div className="re-card-head"><h2>{say("Where leads come from", "لیڈز کہاں سے آتی ہیں")}</h2><ReIcon name="chart" /></div>
        <table className="re-table"><thead><tr><th>{say("Source", "ذریعہ")}</th><th>{say("Leads", "لیڈز")}</th><th>{say("Visits", "وزٹس")}</th><th>{say("Won", "سودے")}</th><th>{say("Median reply", "درمیانی جواب")}</th></tr></thead>
          <tbody>{stats.sources.map((x) => <tr key={x.source}><td><span className="re-bar-label">{sourceLabel[x.source as Source][L(ur)]}</span><span className="re-bar"><i style={{ inlineSize: `${(x.leads / maxLeads) * 100}%` }} /></span></td><td>{x.leads}</td><td>{x.visits}</td><td>{x.won}</td><td className={x.medianReply != null && x.medianReply <= 300 ? "fast" : "slow"}>{duration(x.medianReply, L(ur))}</td></tr>)}</tbody></table>
        <small>{say("First reply = time from the enquiry arriving to the first answer, by the assistant or an agent. Sample history plus every live enquiry in this demo.", "پہلا جواب = انکوائری آنے سے پہلے جواب تک کا وقت، اسسٹنٹ یا ایجنٹ کی طرف سے۔ نمونہ تاریخ اور اس ڈیمو کی ہر نئی انکوائری۔")}</small>
      </div>
      <div className="re-stack">
        <div className="re-card"><div className="re-card-head"><h2>{say("Slowest first replies", "سب سے سست جواب")}</h2><ReIcon name="clock" /></div>
          {slowest.map(({ l, r }) => <button key={l.id} className="re-list-row re-list-btn" onClick={() => p.openLead(l.id)}><span><b>{buyerName(s, l.buyer_id)}</b><small>{sourceLabel[l.source][L(ur)]}</small></span><b className={r != null && r <= 300 ? "fast" : "slow"}>{duration(r, L(ur))}</b></button>)}</div>
        <div className="re-card"><div className="re-card-head"><h2>{say("Next site visits", "اگلے سائٹ وزٹس")}</h2><button className="re-link" onClick={() => p.setTab("visits")}>{say("All visits", "تمام وزٹس")}</button></div>
          {upcoming.map((v) => <div className="re-list-row" key={v.id}><span><b>{buyerName(s, v.buyer_id)}</b><small>{agentName(s, v.agent_id, ur)}</small></span><small>{when(v.starts_at, ur)}</small></div>)}{!upcoming.length && <small>{say("No visits booked.", "کوئی وزٹ بک نہیں۔")}</small>}</div>
      </div>
    </div>
    <div className="re-card re-gap"><div className="re-card-head"><h2>{say("Recent activity", "حالیہ سرگرمی")}</h2></div>
      {s.activity.slice(0, 6).map((a, i) => <div className="re-list-row" key={i}><b>{({ re_lead: say("New lead", "نئی لیڈ"), re_visit: say("Site visit booked", "سائٹ وزٹ بک"), re_stage: say("Pipeline move", "مرحلہ تبدیل"), re_visit_completed: say("Visit completed", "وزٹ مکمل"), re_visit_cancelled: say("Visit cancelled", "وزٹ منسوخ"), re_visit_no_show: say("No-show", "نہیں آئے") } as Record<string, string>)[a.kind] ?? a.kind}{a.detail?.source ? ` · ${String(a.detail.source)}` : ""}</b><small>{when(a.at, ur)}</small></div>)}
      {!s.activity.length && <small>{say("Activity appears when a buyer enquires or books a visit.", "خریدار کی انکوائری یا وزٹ کے بعد سرگرمی نظر آئے گی۔")}</small>}</div>
  </>;
}

function Agents(p: VP) {
  const { s, say, ur } = p;
  return <div className="re-grid">{s.agents.map((a) => { const open = s.leads.filter((l) => l.agent_id === a.id && !["won", "lost"].includes(l.stage)).length, visits = s.visits.filter((v) => v.agent_id === a.id && v.status === "confirmed").length;
    return <div className="re-card re-stack" key={a.id}><div className="re-inline"><span className="re-avatar big">{a.name.split(" ").map((x) => x[0]).join("")}</span><div><h2>{ur && a.name_ur ? a.name_ur : a.name}</h2><small>{a.title} · {a.areas}</small></div></div>
      <div className="re-fields"><Field k={say("Open leads", "جاری لیڈز")} v={String(open)} /><Field k={say("Booked visits", "بک وزٹس")} v={String(visits)} /><Field k={say("Deals won", "مکمل سودے")} v={String(s.leads.filter((l) => l.agent_id === a.id && l.stage === "won").length)} /></div>
      <button className={`re-btn small ${a.active ? "ghost" : ""}`} disabled={p.pending} onClick={() => void p.act("agent", { id: a.id, active: !a.active }).catch(() => {})}>{a.active ? say("Mark unavailable", "غیر حاضر نشان لگائیں") : say("Mark available", "حاضر نشان لگائیں")}</button>
      <small>{a.active ? say("Receives new site visits", "نئے سائٹ وزٹ ملتے ہیں") : say("Not offered for new visits", "نئے وزٹ کے لیے دستیاب نہیں")}</small></div>; })}</div>;
}

function Settings(p: VP) {
  const { s, say } = p, [open, setOpen] = useState(s.settings.open_min), [close, setClose] = useState(s.settings.close_min);
  const clock = (n: number) => `${String(Math.floor(n / 60)).padStart(2, "0")}:${String(n % 60).padStart(2, "0")}`;
  return <div className="re-grid two"><div className="re-card re-stack"><h2>{say("Site-visit hours", "سائٹ وزٹ کے اوقات")}</h2>
    <p>{say("Visits are offered on the hour within these hours, every day, for the next 14 days. Changing hours never cancels an existing visit; move it first.", "انہی اوقات میں ہر گھنٹے، روزانہ، اگلے 14 دن کے لیے وزٹ پیش کیے جاتے ہیں۔ اوقات بدلنے سے موجودہ وزٹ منسوخ نہیں ہوتا، پہلے اسے منتقل کریں۔")}</p>
    <label>{say("Opens (PKT)", "آغاز")}<select value={open} onChange={(e) => setOpen(Number(e.target.value))}>{Array.from({ length: 24 }, (_, i) => i * 60).map((n) => <option key={n} value={n}>{clock(n)}</option>)}</select></label>
    <label>{say("Closes (PKT)", "اختتام")}<select value={close} onChange={(e) => setClose(Number(e.target.value))}>{Array.from({ length: 24 }, (_, i) => (i + 1) * 60).map((n) => <option key={n} value={n}>{clock(n)}</option>)}</select></label>
    <button className="re-btn" disabled={p.pending || close - open < 60} onClick={() => void p.act("settings", { openMin: open, closeMin: close }).catch(() => {})}>{say("Save hours", "اوقات محفوظ کریں")}</button></div>
    <div className="re-card re-stack"><h2>{say("What is connected in this demo", "اس ڈیمو میں کیا جڑا ہے")}</h2><p>{say("Website form, WhatsApp-style assistant, buyer portal and agent pipeline share one database. In a live build, Facebook lead forms and Zameen enquiries arrive in the same pipeline.", "ویب سائٹ فارم، واٹس ایپ طرز کا اسسٹنٹ، خریدار پورٹل اور ایجنٹ پائپ لائن ایک ہی ڈیٹابیس استعمال کرتے ہیں۔ اصل نظام میں فیس بک اور زمین کی انکوائریاں بھی اسی پائپ لائن میں آتی ہیں۔")}</p><p>{say("No phone line, WhatsApp number, ad account or listing portal is connected in this outreach preview.", "اس ڈیمو میں کوئی فون، واٹس ایپ نمبر، اشتہاری اکاؤنٹ یا لسٹنگ پورٹل منسلک نہیں۔")}</p></div></div>;
}

function VisitModal(p: VP & { open: VisitOpen; onClose: () => void; onDone: () => void }) {
  const { s, say, ur, role, open } = p, existing = open.reschedule;
  const [date, setDate] = useState(existing ? localDate(existing.starts_at) : localDate(s.server_time)), [start, setStart] = useState("");
  const [leadId, setLeadId] = useState(open.leadId ?? existing?.lead_id ?? s.leads.find((l) => !["won", "lost"].includes(l.stage))?.id ?? ""), [listingId, setListingId] = useState(open.listingId ?? existing?.listing_id ?? "");
  const [name, setName] = useState(s.buyer.name === "Demo buyer" ? "" : s.buyer.name), [error, setError] = useState("");
  const retry = useRef(crypto.randomUUID());
  const busy = existing ? s.busy.filter((v) => !(v.agent_id === existing.agent_id && v.starts_at === existing.starts_at)) : s.busy;
  const slots = visitSlots(date, s.agents, busy, s.settings, s.expires_at, new Date(s.server_time));
  useEffect(() => { retry.current = crypto.randomUUID(); }, [start, leadId, listingId]);
  const submit = async () => {
    setError("");
    try {
      if (role === "buyer" && name.trim() && name.trim() !== s.buyer.name) await p.act("buyer", { name: name.trim() });
      if (existing) await p.act("visit", { id: existing.id, start });
      else await p.act("reserve", { start, requestId: retry.current, ...(listingId ? { listingId } : {}), ...(role !== "buyer" ? { leadId } : {}), notes: role === "buyer" ? "Booked in the buyer portal" : "Booked by staff" });
      p.onDone();
    } catch (e) { setError(e instanceof Error ? e.message : "Connection problem"); }
  };
  return <ReModal title={existing ? say("Move a site visit", "سائٹ وزٹ کا وقت بدلیں") : say("Book a sample site visit", "نمونہ سائٹ وزٹ بک کریں")} onClose={p.onClose}>
    <p>{say("One-hour visits with an agent. The database holds the slot for one agent at a time, so two buyers can never get the same agent at the same hour.", "ایجنٹ کے ساتھ ایک گھنٹے کا وزٹ۔ ڈیٹابیس ایک وقت میں ایک ایجنٹ کا وقت محفوظ رکھتا ہے، اس لیے دو خریداروں کو ایک ہی وقت ایک ہی ایجنٹ نہیں مل سکتا۔")}</p>
    {error && <div className="re-error" role="alert">{error}</div>}
    <div className="re-form">
      {role === "buyer" && !existing && <label>{say("Your name (sample)", "آپ کا نام (نمونہ)")}<input value={name} maxLength={80} onChange={(e) => setName(e.target.value)} placeholder={say("Example: Hamza Qureshi", "مثال: حمزہ قریشی")} /></label>}
      {role !== "buyer" && !existing && <label className="full">{say("Lead", "لیڈ")}<select value={leadId} onChange={(e) => setLeadId(e.target.value)}>{s.leads.filter((l) => !["won", "lost"].includes(l.stage)).map((l) => <option key={l.id} value={l.id}>{buyerName(s, l.buyer_id)} · {stageLabel[l.stage].en}</option>)}</select></label>}
      {!existing && <label>{say("Listing (optional)", "لسٹنگ (اختیاری)")}<select value={listingId} onChange={(e) => setListingId(e.target.value)}><option value="">{say("Agent suggests options", "ایجنٹ آپشنز بتائے")}</option>{s.listings.filter((l) => l.status !== "sold").map((l) => <option key={l.id} value={l.id}>{l.code} · {l.title}, {l.society}</option>)}</select></label>}
      <label>{say("Date", "تاریخ")}<input type="date" min={localDate(s.server_time)} max={dayAfter(localDate(s.server_time), 13)} value={date} onChange={(e) => { setDate(e.target.value); setStart(""); }} /></label>
    </div>
    <h3>{say("Free times (PKT)", "دستیاب اوقات")}</h3>
    <div className="re-slots">{slots.map((t) => <button key={t} className={t === start ? "active" : ""} aria-pressed={t === start} onClick={() => setStart(t)}>{timeLabel(t, L(ur))}</button>)}</div>
    {!slots.length && <Empty>{say("No free agent on this day. Try another date.", "اس دن کوئی ایجنٹ دستیاب نہیں۔ دوسری تاریخ منتخب کریں۔")}</Empty>}
    <div className="re-modal-foot"><button className="re-btn ghost" onClick={p.onClose}>{say("Close", "بند کریں")}</button><button className="re-btn" disabled={!start || !slots.includes(start) || p.pending || (role !== "buyer" && !existing && !leadId)} onClick={submit}>{p.pending ? say("Saving…", "محفوظ ہو رہا ہے…") : existing ? say("Move visit", "وقت بدلیں") : say("Confirm visit", "وزٹ کنفرم کریں")}</button></div>
  </ReModal>;
}

function EnquiryModal(p: VP & { onClose: () => void }) {
  const { s, say } = p, [form, setForm] = useState({ name: s.buyer.name === "Demo buyer" ? "" : s.buyer.name, budget: "", area: "", size: "", kind: "", timeline: "", overseas: "", message: "" }), [done, setDone] = useState(false), [error, setError] = useState("");
  const retry = useRef(crypto.randomUUID());
  const set = (k: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => setForm({ ...form, [k]: e.target.value });
  const submit = async () => {
    setError("");
    try {
      await p.act("enquiry", { requestId: retry.current, name: form.name.trim(), ...(form.budget ? { budget: Number(form.budget) } : {}), area: form.area, size: form.size, kind: form.kind, timeline: form.timeline,
        ...(form.overseas ? { overseas: form.overseas !== "Pakistan", country: form.overseas } : {}), message: form.message });
      setDone(true);
    } catch (e) { setError(e instanceof Error ? e.message : "Connection problem"); }
  };
  return <ReModal title={say("Send a sample enquiry", "نمونہ انکوائری بھیجیں")} onClose={p.onClose}>
    {done ? <div className="re-stack"><p>{say("Received. Your enquiry is in the agent pipeline with a summary, and the assistant has acknowledged it. Book a site visit next.", "موصول ہو گئی۔ آپ کی انکوائری خلاصے کے ساتھ ایجنٹ پائپ لائن میں ہے۔ اب سائٹ وزٹ بک کریں۔")}</p><button className="re-btn" onClick={() => { p.onClose(); p.openVisit({}); }}>{say("Book a site visit", "سائٹ وزٹ بک کریں")}</button></div> : <>
      {error && <div className="re-error" role="alert">{error}</div>}
      <EnquiryFields form={form} set={set} societies={[...new Set(s.listings.map((l) => l.society))]} say={say} />
      <div className="re-modal-foot"><button className="re-btn ghost" onClick={p.onClose}>{say("Close", "بند کریں")}</button><button className="re-btn" disabled={p.pending || form.name.trim().length < 2} onClick={submit}>{say("Send enquiry", "انکوائری بھیجیں")}</button></div></>}
  </ReModal>;
}

export function EnquiryFields({ form, set, societies, say }: { form: Record<string, string>; set: (k: never) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => void; societies: string[]; say: Say }) {
  const f = set as (k: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => void;
  return <div className="re-form">
    <label>{say("Name (sample)", "نام (نمونہ)")}<input value={form.name} maxLength={80} onChange={f("name")} required /></label>
    <label>{say("Budget", "بجٹ")}<select value={form.budget} onChange={f("budget")}><option value="">{say("Choose", "منتخب کریں")}</option>{[5e6, 1e7, 2.5e7, 5e7, 1e8].map((n) => <option key={n} value={n}>{say("Up to ", "تک ")}{formatPkr(n)}</option>)}</select></label>
    <label>{say("Society or area", "سوسائٹی یا علاقہ")}<select value={form.area} onChange={f("area")}><option value="">{say("Open to suggestions", "تجاویز چاہییں")}</option>{societies.map((x) => <option key={x} value={x}>{x}</option>)}</select></label>
    <label>{say("Type", "قسم")}<select value={form.kind} onChange={f("kind")}><option value="">{say("Any", "کوئی بھی")}</option>{kinds.map(([k, en, u]) => <option key={k} value={k}>{say(en, u)}</option>)}</select></label>
    <label>{say("Size", "سائز")}<input value={form.size} maxLength={40} onChange={f("size")} placeholder={say("e.g. 10 marla", "مثلاً دس مرلہ")} /></label>
    <label>{say("Timeline", "کب تک")}<select value={form.timeline} onChange={f("timeline")}><option value="">{say("Choose", "منتخب کریں")}</option>{[["Ready now", "ابھی"], ["1-3 months", "ایک سے تین مہینے"], ["This year", "اس سال"], ["Exploring, no fixed date", "صرف دیکھ رہا ہوں"]].map(([v, u]) => <option key={v} value={v}>{say(v, u)}</option>)}</select></label>
    <label>{say("Where are you now?", "آپ اس وقت کہاں ہیں؟")}<select value={form.overseas} onChange={f("overseas")}><option value="">{say("Choose", "منتخب کریں")}</option>{[["Pakistan", "پاکستان"], ["UAE", "متحدہ عرب امارات"], ["Saudi Arabia", "سعودی عرب"], ["UK", "برطانیہ"], ["Other", "کوئی اور ملک"]].map(([v, u]) => <option key={v} value={v}>{say(v, u)}</option>)}</select></label>
    <label className="full">{say("Message (optional)", "پیغام (اختیاری)")}<textarea value={form.message} maxLength={500} onChange={f("message")} /></label>
  </div>;
}
