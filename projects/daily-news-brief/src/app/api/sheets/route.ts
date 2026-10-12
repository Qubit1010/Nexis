import { NextResponse } from "next/server";
import { appendToSheet, sheetsError } from "@/lib/google-sheets";

interface SaveRequest {
  briefDate: string;
  title: string;
  format: string;
  timeliness: string;
  angle: string;
  hook: string;
  keyPoints: string[];
  relatedTrends: string[];
}

export async function POST(request: Request) {
  try {
    const body: SaveRequest = await request.json();
    if (!body.title?.trim() || !Array.isArray(body.keyPoints) || !Array.isArray(body.relatedTrends)) {
      return NextResponse.json({ error: "A title, key points and related trends are required." }, { status: 400 });
    }

    const now = new Date().toISOString().slice(0, 19).replace("T", " ");
    const keyPoints = body.keyPoints.join("\n");
    const relatedTrends = body.relatedTrends.join(", ");

    const row = [
      now,
      body.briefDate,
      body.title,
      body.format,
      body.timeliness,
      body.angle,
      body.hook,
      keyPoints,
      relatedTrends,
      "New",
    ];

    const saved = await appendToSheet(
      "Content Opportunities",
      ["Date Saved", "Brief Date", "Title", "Format", "Timeliness", "Angle", "Hook", "Key Points", "Related Trends", "Status"],
      row
    );
    return NextResponse.json({ success: true, message: "Saved to Google Sheet", ...saved });
  } catch (error) {
    return sheetsError(error);
  }
}
