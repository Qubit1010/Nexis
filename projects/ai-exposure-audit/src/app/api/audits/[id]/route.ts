import { NextRequest, NextResponse } from "next/server";
import { ValidationError, deleteAudit, getAudit, saveAudit, validateAuditInput } from "@/lib/db";

export const dynamic = "force-dynamic";

type Ctx = { params: Promise<{ id: string }> };

export async function GET(_req: NextRequest, { params }: Ctx) {
  const { id } = await params;
  const audit = getAudit(id);
  if (!audit) return NextResponse.json({ error: "Audit not found" }, { status: 404 });
  return NextResponse.json({ audit });
}

export async function PUT(req: NextRequest, { params }: Ctx) {
  const { id } = await params;
  try {
    if (!getAudit(id)) return NextResponse.json({ error: "Audit not found" }, { status: 404 });
    const input = validateAuditInput(await req.json());
    return NextResponse.json({ audit: saveAudit(id, input) });
  } catch (err) {
    if (err instanceof ValidationError) {
      return NextResponse.json({ error: err.message }, { status: 400 });
    }
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Failed to save audit" },
      { status: 500 }
    );
  }
}

export async function DELETE(_req: NextRequest, { params }: Ctx) {
  const { id } = await params;
  if (!deleteAudit(id)) return NextResponse.json({ error: "Audit not found" }, { status: 404 });
  return NextResponse.json({ ok: true });
}
