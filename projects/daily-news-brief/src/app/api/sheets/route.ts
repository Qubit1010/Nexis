import { NextResponse } from "next/server";
import { appendToSheet, sheetsError } from "@/lib/google-sheets";
import { saveEverywhere } from "@/lib/content-os";

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

    const result = await saveEverywhere(
      () =>
        appendToSheet(
          "Content Opportunities",
          ["Date Saved", "Brief Date", "Title", "Format", "Timeliness", "Angle", "Hook", "Key Points", "Related Trends", "Status"],
          row
        ),
      {
        title: body.title,
        summary: [body.angle, body.hook].filter(Boolean).join("\n\n") || null,
        source: "practical_idea",
        payload: { format: body.format, timeliness: body.timeliness, keyPoints: body.keyPoints, relatedTrends: body.relatedTrends, briefDate: body.briefDate },
      }
    );
    if (!result.ok) return sheetsError(result.sheetError);
    return NextResponse.json({ success: true, message: result.sheet ? "Saved to Google Sheet" : "Saved to Content OS (Google Sheet save failed)", ...(result.sheet || {}), contentOs: result.contentOs, sheetSaved: !!result.sheet });
  } catch (error) {
    return sheetsError(error);
  }
}
