import { NextResponse } from "next/server";
import { appendToSheet, sheetsError } from "@/lib/google-sheets";

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

    const saved = await appendToSheet(
      "Saved Articles",
      ["Date Saved", "Brief Date", "Title", "Source", "URL", "TLDR", "Status"],
      row
    );
    return NextResponse.json({ success: true, message: "Article saved to Google Sheet", ...saved });
  } catch (error) {
    return sheetsError(error);
  }
}
