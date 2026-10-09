import { notFound } from "next/navigation";
import { authorised, expired, getBusiness } from "@/lib/db";
import Healthcare from "./Healthcare";

export default async function HealthcarePage({
  params,
  searchParams,
  role,
}: {
  params: Promise<{ slug: string }>;
  searchParams: Promise<Record<string, string | undefined>>;
  role: "patient" | "clinic" | "doctor";
}) {
  const { slug } = await params,
    sp = await searchParams;
  const b = await getBusiness(slug);
  if (!authorised(b, sp.t ?? null) || b.sector !== "healthcare") notFound();
  if (expired(b))
    return (
      <div className="hub gone">
        <div>
          <h1>This demo has ended</h1>
          <p>Contact NexusPoint for a fresh preview.</p>
          <a className="btn" href="https://wa.me/923118340514">
            WhatsApp NexusPoint
          </a>
        </div>
      </div>
    );
  return (
    <Healthcare
      slug={b.slug}
      token={b.token}
      name={b.name}
      role={role}
      initialLang={sp.lang === "ur" ? "ur" : "en"}
      initialTab={sp.tab}
      initialBookingDoctor={role === "patient" && sp.book === "1" ? sp.doctor : undefined}
      initialBooking={role === "patient" && sp.book === "1"}
    />
  );
}
