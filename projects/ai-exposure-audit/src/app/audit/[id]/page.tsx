import { notFound } from "next/navigation";
import { getAudit } from "@/lib/db";
import { getRubricBundle } from "@/lib/rubric";
import Workspace from "@/components/Workspace";

export const dynamic = "force-dynamic";

export default async function AuditPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const audit = getAudit(id);
  if (!audit) notFound();

  const { rubric, pricebook, sources } = getRubricBundle();

  return <Workspace initialAudit={audit} rubric={rubric} pricebook={pricebook} sources={sources} />;
}
