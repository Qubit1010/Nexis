import { NextRequest, NextResponse } from "next/server";
import { google } from "googleapis";

export const dynamic = "force-dynamic";

const DRIVE_FOLDER_ID = "1UJzhK2UN2tVLNwAtJJEMhpS5UJBtW9G7";

function getAuth() {
  const clientId = process.env.GOOGLE_CLIENT_ID;
  const clientSecret = process.env.GOOGLE_CLIENT_SECRET;
  const refreshToken = process.env.GOOGLE_REFRESH_TOKEN;
  if (!clientId || !clientSecret || !refreshToken) {
    throw new Error("Missing GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, or GOOGLE_REFRESH_TOKEN");
  }
  const auth = new google.auth.OAuth2(clientId, clientSecret);
  auth.setCredentials({ refresh_token: refreshToken });
  return auth;
}

export async function POST(req: NextRequest) {
  try {
    const { proposal, jobType } = await req.json() as { proposal: string; jobType: string };
    if (!proposal?.trim()) {
      return NextResponse.json({ error: "proposal is required" }, { status: 400 });
    }

    const auth = getAuth();
    const docs = google.docs({ version: "v1", auth });
    const drive = google.drive({ version: "v3", auth });

    const date = new Date().toLocaleDateString("en-GB");
    const title = `Upwork Proposal - ${jobType} - ${date}`;

    // Create doc directly in the target folder
    const createRes = await drive.files.create({
      requestBody: {
        name: title,
        mimeType: "application/vnd.google-apps.document",
        parents: [DRIVE_FOLDER_ID],
      },
      fields: "id",
    });
    const docId = createRes.data.id!;

    // Insert proposal text
    await docs.documents.batchUpdate({
      documentId: docId,
      requestBody: {
        requests: [{ insertText: { location: { index: 1 }, text: proposal } }],
      },
    });

    return NextResponse.json({
      docUrl: `https://docs.google.com/document/d/${docId}/edit`,
    });
  } catch (err: unknown) {
    const e = err as { message?: string; response?: { data?: unknown } };
    const detail = e.response?.data ?? e.message ?? String(err);
    console.error("save-to-drive error:", JSON.stringify(detail, null, 2));
    return NextResponse.json({ error: String(e.message), detail }, { status: 500 });
  }
}
