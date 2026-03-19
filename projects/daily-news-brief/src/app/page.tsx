import { db } from "@/lib/db";
import { briefs } from "@/lib/db/schema";
import { desc } from "drizzle-orm";
import { redirect } from "next/navigation";
import { EmptyState } from "@/components/empty-state";

export const dynamic = "force-dynamic";

export default function Home() {
  const latestBrief = db
    .select({ date: briefs.date })
    .from(briefs)
    .orderBy(desc(briefs.date))
    .limit(1)
    .get();

  if (latestBrief) {
    redirect(`/brief/${latestBrief.date}`);
  }

  return <EmptyState />;
}
