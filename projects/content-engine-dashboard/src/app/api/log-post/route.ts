import { NextResponse } from "next/server";
import { spawn } from "child_process";
import path from "path";

export const dynamic = "force-dynamic";

const REPO_ROOT = path.join(process.cwd(), "../..");
const SCRIPTS = path.join(
  REPO_ROOT,
  ".claude/skills/content-engine/scripts"
);

function runPythonStdin(
  script: string,
  payload: unknown
): Promise<Record<string, unknown>> {
  return new Promise((resolve, reject) => {
    const child = spawn("python", [path.join(SCRIPTS, script)], {
      cwd: REPO_ROOT,
      env: { ...process.env },
    });

    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (d: Buffer) => (stdout += d.toString()));
    child.stderr.on("data", (d: Buffer) => (stderr += d.toString()));
    child.on("close", (code) => {
      if (code !== 0) {
        reject(new Error(stderr.trim() || `Script exited with code ${code}`));
      } else {
        try {
          resolve(JSON.parse(stdout.trim()));
        } catch {
          reject(new Error("Invalid script output: " + stdout));
        }
      }
    });
    child.stdin.write(JSON.stringify(payload));
    child.stdin.end();
  });
}

// Convert flat generated text into save_content.py sections format
function buildSections(content: string) {
  const chunks = content
    .split(/\n{2,}/)
    .map((c) => c.trim())
    .filter(Boolean);

  return chunks.map((chunk) => {
    // Detect bullet lines (start with - or *)
    const lines = chunk.split("\n");
    if (lines.length > 1 && lines.every((l) => /^[-*]\s/.test(l.trim()))) {
      return { bullets: lines.map((l) => l.replace(/^[-*]\s+/, "").trim()) };
    }
    return { body: chunk };
  });
}

export async function POST(req: Request) {
  try {
    const { platform, format, title, goal, hook, content } =
      (await req.json()) as {
        platform: string;
        format: string;
        title: string;
        goal: string;
        hook: string;
        content: string;
      };

    // 1. Create the Google Doc
    const saveResult = await runPythonStdin("save_content.py", {
      title: `${platform} — ${title}`,
      sections: buildSections(content),
    });

    if (saveResult.status !== "ok") {
      throw new Error(String(saveResult.message ?? "save_content.py failed"));
    }
    const docUrl = String(saveResult.doc_url ?? "");

    // 2. Log the row to the Content Log sheet
    const logResult = await runPythonStdin("log_post.py", {
      platform,
      format,
      title,
      goal,
      hook,
      doc_url: docUrl,
    });

    return NextResponse.json({ ...logResult, doc_url: docUrl });
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
