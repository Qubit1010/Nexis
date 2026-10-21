import { NextResponse } from "next/server";
import { authorised, expired, getBusiness, rest, type Conversation } from "@/lib/db";
import { reAction, reAvailability, reState } from "@/lib/real-estate";
import { leadSummary, STAGES, type ReRole } from "@/lib/real-estate-types";

export const dynamic = "force-dynamic";
const json = (data: unknown, status = 200) => NextResponse.json(data, { status, headers: { "Cache-Control": "no-store" } });
const bad = (message: string): never => { throw new Error(`INVALID: ${message}`); };
const id = (v: unknown) => typeof v === "string" && /^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/i.test(v);
const text = (v: unknown, max: number) => v === undefined || (typeof v === "string" && v.length <= max);

async function access(p: Record<string, unknown>) {
  if (typeof p.slug !== "string" || typeof p.t !== "string") bad("Invalid link");
  const b = await getBusiness(p.slug as string);
  if (!authorised(b, p.t as string) || b.sector !== "real-estate") throw new Error("NOT_FOUND: Property demo not found");
  if (expired(b)) throw new Error("EXPIRED: This preview has expired");
  if (typeof p.visitor !== "string" || !/^[a-zA-Z0-9_-]{8,64}$/.test(p.visitor) || !["buyer", "agent", "manager"].includes(p.role as string)) bad("Invalid demo session");
  return { b, visitor: p.visitor as string, role: p.role as ReRole };
}
function error(e: unknown) {
  const m = e instanceof Error ? e.message : "";
  const match = m.match(/(INVALID|CONFLICT|NOT_FOUND|EXPIRED): ([^"\\]+)/);
  return json({ error: match?.[2] ?? "Property demo connection problem. Please try again." },
    match ? ({ INVALID: 400, CONFLICT: 409, NOT_FOUND: 404, EXPIRED: 410 } as Record<string, number>)[match[1]] ?? 500 : 500);
}

export async function GET(req: Request) {
  try {
    const p = Object.fromEntries(new URL(req.url).searchParams), { b, visitor, role } = await access({ ...p, role: p.role ?? "buyer" });
    if (p.date) {
      if (!/^\d{4}-\d{2}-\d{2}$/.test(p.date)) bad("Choose a valid day");
      return json({ slots: (await reAvailability(b, p.date)).slots });
    }
    return json(await reState(b, visitor, role));
  } catch (e) { return error(e); }
}

export async function POST(req: Request) {
  try {
    const p = await req.json(), { b, visitor, role } = await access({ ...p, role: p.role ?? "buyer" }), action = p.action;
    if (typeof action !== "string") bad("Choose an action");
    const data: Record<string, unknown> = { ...p };
    for (const k of ["slug", "t", "visitor", "role", "action"]) delete data[k];
    for (const k of ["id", "leadId", "listingId", "agentId"]) if (data[k] !== undefined && !id(data[k])) bad("Invalid record identifier");
    for (const [k, max] of [["name", 80], ["area", 80], ["size", 40], ["timeline", 60], ["country", 60], ["message", 500], ["notes", 500], ["text", 2000], ["reason", 200], ["assignedTo", 80]] as const)
      if (!text(data[k], max)) bad("Invalid text field");
    if (data.overseas !== undefined && typeof data.overseas !== "boolean") bad("Invalid overseas flag");
    if (["enquiry", "reserve"].includes(action) && (typeof data.requestId !== "string" || data.requestId.length < 8 || data.requestId.length > 100)) bad("Retry identifier required");

    if (action === "enquiry") {
      if (role !== "buyer") bad("Use the buyer demo for enquiries");
      if (typeof data.name !== "string" || data.name.trim().length < 2) bad("Enter a sample name");
      if (data.budget !== undefined && (!Number.isInteger(data.budget) || (data.budget as number) < 100000 || (data.budget as number) > 100000000000)) bad("Choose a budget");
      if (data.kind !== undefined && !["", "plot", "house", "apartment", "commercial", "file"].includes(data.kind as string)) bad("Choose a property type");
      const q = { budget: (data.budget as number) ?? null, area: (data.area as string) ?? "", size: (data.size as string) ?? "", kind: (data.kind as string) ?? "",
        timeline: (data.timeline as string) ?? "", overseas: (data.overseas as boolean) ?? null, country: (data.country as string) ?? "", name: (data.name as string).trim() };
      const summary = leadSummary(q) + (typeof data.message === "string" && data.message.trim() ? ` Message: "${data.message.trim().slice(0, 200)}"` : "");
      return json({ result: await reAction(b, visitor, role, "enquiry", { ...data, name: q.name, summary }) });
    }
    if (action === "reserve" || (action === "visit" && data.start !== undefined)) {
      if (typeof data.start !== "string" || !Number.isFinite(Date.parse(data.start))) bad("Choose a valid time");
    }
    if (action === "visit" && data.start === undefined && !["completed", "cancelled", "no_show"].includes(data.status as string)) bad("Invalid visit status");
    if (["visit", "stage", "assign", "note", "listing", "agent"].includes(action) && !id(data.id)) bad("Invalid record identifier");
    if (action === "stage" && !STAGES.includes(data.stage as (typeof STAGES)[number])) bad("Invalid pipeline stage");
    if (action === "assign" && !id(data.agentId)) bad("Choose an agent");
    if (action === "note" && (typeof data.text !== "string" || !data.text.trim() || data.text.length > 500)) bad("Write a short note");
    if (action === "listing" && !["available", "reserved", "sold"].includes(data.status as string)) bad("Invalid listing status");
    if (action === "agent" && typeof data.active !== "boolean") bad("Choose agent availability");
    if (action === "settings" && (!Number.isInteger(data.openMin) || !Number.isInteger(data.closeMin) || (data.openMin as number) < 0 || (data.closeMin as number) > 1440 ||
      (data.closeMin as number) - (data.openMin as number) < 60 || (data.openMin as number) % 30 || (data.closeMin as number) % 30)) bad("Use valid 30-minute aligned hours");

    if (action === "conversation") {
      if (role === "buyer" || !id(data.id)) bad("Use the agent pipeline");
      const scope = `slug=eq.${encodeURIComponent(b.slug)}&id=eq.${data.id}`;
      const c = (await rest<Conversation>("GET", `demo_conversations?${scope}&limit=1`))[0];
      if (!c) throw new Error("NOT_FOUND: Conversation not found");
      if (data.text) {
        if (!c.staff_mode) bad("Take over before replying");
        await rest("POST", "demo_messages", { conversation_id: c.id, role: "business", content: data.text, source: "staff" }, "return=minimal");
      }
      const patch: Record<string, unknown> = { last_at: new Date().toISOString() };
      if (typeof data.staffMode === "boolean") { patch.staff_mode = data.staffMode; patch.handoff = data.staffMode; }
      if (data.assignedTo !== undefined) patch.assigned_to = data.assignedTo || null;
      await rest("PATCH", `demo_conversations?${scope}`, patch, "return=minimal");
      return json({ result: { ok: true } });
    }
    if (!["buyer", "reserve", "visit", "stage", "assign", "note", "listing", "agent", "settings"].includes(action)) bad("Unknown action");
    return json({ result: await reAction(b, visitor, role, action, data) });
  } catch (e) { return error(e); }
}
