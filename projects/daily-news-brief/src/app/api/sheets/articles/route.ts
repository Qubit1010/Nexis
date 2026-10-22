import { NextResponse } from "next/server";
import { appendToSheet, sheetsError } from "@/lib/google-sheets";
import { saveEverywhere } from "@/lib/content-os";

interface SaveArticleRequest {
  briefDate: string;
  title: string;
  source: string;
  url: string;
  tldr: string;
}

export async function POST(request: Request) {
  try {
    const body: SaveArticleRequest = await request.json();
    if (!body.title?.trim() || !body.url?.trim()) {
      return NextResponse.json({ error: "An article title and URL are required." }, { status: 400 });
    }

    const now = new Date().toISOString().slice(0, 19).replace("T", " ");

    const row = [
      now,
      body.briefDate,
      body.title,
      body.source,
      body.url,
      body.tldr,
      "New",
    ];

    const result = await saveEverywhere(
      () =>
        appendToSheet(
          "Saved Articles",
          ["Date Saved", "Brief Date", "Title", "Source", "URL", "TLDR", "Status"],
          row
        ),
      {
        title: body.title,
        url: body.url,
        summary: body.tldr || null,
        source: "news_article",
        payload: { publisher: body.source, briefDate: body.briefDate },
      }
    );
    if (!result.ok) return sheetsError(result.sheetError);
    return NextResponse.json({
      success: true,
      message: result.sheet ? "Article saved to Google Sheet" : "Saved to Content OS (Google Sheet save failed)",
      ...(result.sheet || {}),
      contentOs: result.contentOs,
      sheetSaved: !!result.sheet,
    });
  } catch (error) {
    return sheetsError(error);
  }
}
