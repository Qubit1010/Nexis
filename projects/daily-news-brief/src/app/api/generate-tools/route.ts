import { generateToolsBrief } from "@/lib/pipeline/tool-run";
import { NextResponse } from "next/server";

export async function POST(request: Request) {
  const expectedToken = process.env.BRIEF_AUTH_TOKEN;
  if (expectedToken) {
    const authHeader = request.headers.get("Authorization");
    if (authHeader !== `Bearer ${expectedToken}`) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }
  }

  try {
    const body = await request.json().catch(() => ({}));
    const date = body.date as string | undefined;

    const result = await generateToolsBrief(date);

    return NextResponse.json(result, {
      status: result.success ? 200 : 207,
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    return NextResponse.json(
      { success: false, error: message },
      { status: 500 }
    );
  }
}
