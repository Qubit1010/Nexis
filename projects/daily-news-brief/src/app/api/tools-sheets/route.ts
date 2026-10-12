import { NextResponse } from "next/server";
import { appendToSheet, sheetsConfig, sheetsError } from "@/lib/google-sheets";

interface SaveRequest {
  briefDate: string;
  name: string;
  url: string;
  domain: string;
  domainSlug: string;
  oneLiner: string;
  bestUseCase: string;
  howToSteps: string[];
  audienceHook: string;
  pricingTier: string | null;
  tags: string[];
}

export async function POST(request: Request) {
  try {
    const body: SaveRequest = await request.json();
    if (!body.name?.trim() || !Array.isArray(body.howToSteps) || !Array.isArray(body.tags)) {
      return NextResponse.json({ error: "A tool name, steps and tags are required." }, { status: 400 });
    }
    const sheetTab = sheetsConfig().GOOGLE_SHEETS_TOOLS_TAB || "Tool Content Drafts";

    const now = new Date().toISOString().slice(0, 19).replace("T", " ");
    const howTo = body.howToSteps.map((s, i) => `${i + 1}. ${s}`).join("\n");
    const tags = body.tags.join(", ");

    const row = [
      now,
      body.briefDate,
      body.name,
      body.url,
      body.domain,
      body.pricingTier ?? "unknown",
      body.oneLiner,
      body.bestUseCase,
      howTo,
      body.audienceHook,
      tags,
      "New",
    ];

    const saved = await appendToSheet(sheetTab,
      ["Date Saved", "Brief Date", "Tool", "URL", "Domain", "Pricing", "One Liner", "Best Use Case", "How To", "Audience Hook", "Tags", "Status"],
      row);

    return NextResponse.json({
      success: true,
      message: `Saved to "${sheetTab}" tab`,
      ...saved,
    });
  } catch (error) {
    return sheetsError(error);
  }
}
