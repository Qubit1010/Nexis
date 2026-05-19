import { db } from "@/lib/db";
import { toolBriefs } from "@/lib/db/schema";
import { desc } from "drizzle-orm";
import { redirect } from "next/navigation";

export const dynamic = "force-dynamic";

export default function ToolsHome() {
  const latest = db
    .select({ date: toolBriefs.date })
    .from(toolBriefs)
    .orderBy(desc(toolBriefs.date))
    .limit(1)
    .get();

  if (latest) {
    redirect(`/tools/${latest.date}`);
  }

  return (
    <div className="max-w-2xl mx-auto px-8 py-20 text-center space-y-4">
      <h1 className="text-2xl font-bold tracking-tight">No tools brief yet</h1>
      <p className="text-muted-foreground">
        Run <code className="px-2 py-0.5 rounded bg-muted text-xs">npm run generate:tools</code> to
        create the first one, or click "Generate Tools Brief" in the sidebar.
      </p>
    </div>
  );
}
