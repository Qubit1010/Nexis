// Aleem's control room: every demo, how often it was opened, chats, bookings, and the last activity.
// Protected by ADMIN_TOKEN (?key=...). Server-rendered, no client JS.
import { notFound } from "next/navigation";
import { rest } from "@/lib/db";

export const dynamic = "force-dynamic";

type Row = { slug: string; token: string; name: string; sector: string; created_at: string; expires_at: string };
type Ev = { slug: string; kind: string; at: string };

export default async function Admin({ searchParams }: { searchParams: Promise<Record<string, string | undefined>> }) {
  const sp = await searchParams;
  if (!process.env.ADMIN_TOKEN || sp.key !== process.env.ADMIN_TOKEN) notFound();
  const demos = await rest<Row>("GET", "demo_businesses?select=slug,token,name,sector,created_at,expires_at&order=created_at.desc");
  const events = await rest<Ev>("GET", "demo_events?select=slug,kind,at&order=at.desc&limit=2000");
  const by = (slug: string, kind: string) => events.filter((e) => e.slug === slug && e.kind === kind);
  const fmt = (s?: string) => (s ? new Date(s).toLocaleString("en-GB", { timeZone: "Asia/Karachi", dateStyle: "medium", timeStyle: "short" }) : "–");
  return (
    <div className="hub wrap" style={{ paddingBlock: "2rem" }}>
      <h1 style={{ fontSize: "2rem" }}>Demo control room</h1>
      <p style={{ color: "var(--muted)", marginTop: ".5rem" }}>Views after the meeting are your follow-up signal.</p>
      <div className="feed" style={{ marginTop: "1.5rem" }}>
        {demos.map((d) => {
          const views = by(d.slug, "view");
          const expired = new Date(d.expires_at) < new Date();
          return (
            <article className="card" key={d.slug} style={{ gridTemplateColumns: "1fr auto" }}>
              <div>
                <div className="card-top"><span className={`stage ${expired ? "" : "warm"}`}>{expired ? "Expired" : "Live"}</span><span className="chan">{d.sector} · made {fmt(d.created_at)}</span></div>
                <p className="summ">{d.name}</p>
                <p style={{ color: "var(--muted)", fontSize: ".9rem", marginTop: ".3rem" }}>
                  {views.length} views · last opened {fmt(views[0]?.at)} · {by(d.slug, "chat_start").length} chats · {by(d.slug, "booking").length + by(d.slug, "order").length + by(d.slug, "fee_lookup").length + by(d.slug, "visit").length} bookings/orders · {by(d.slug, "plan_click").length} YES clicks
                </p>
              </div>
              <a className="btn ghost" href={`/d/${d.slug}?t=${d.token}`}>Open</a>
            </article>
          );
        })}
      </div>
    </div>
  );
}
