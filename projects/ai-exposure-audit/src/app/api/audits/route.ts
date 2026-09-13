import { NextRequest, NextResponse } from "next/server";
import { ValidationError, listAudits, saveAudit, validateAuditInput } from "@/lib/db";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    return NextResponse.json({ audits: listAudits() });
  } catch (err) {
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Failed to list audits" },
      { status: 500 }
    );
  }
}

export async function POST(req: NextRequest) {
  try {
    const input = validateAuditInput(await req.json());
    return NextResponse.json({ audit: saveAudit(null, input) }, { status: 201 });
  } catch (err) {
    if (err instanceof ValidationError) {
      return NextResponse.json({ error: err.message }, { status: 400 });
    }
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Failed to create audit" },
      { status: 500 }
    );
  }
}
