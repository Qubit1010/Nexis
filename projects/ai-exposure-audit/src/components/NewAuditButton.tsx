"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { DIMENSION_IDS } from "@/lib/types";

const EQUAL_WEIGHTS = Object.fromEntries(DIMENSION_IDS.map((d) => [d, 0.2]));

export default function NewAuditButton() {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function create() {
    if (!name.trim()) return;
    setBusy(true);
    setError(null);
    try {
      const res = await fetch("/api/audits", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          business: { name: name.trim(), positioning: "" },
          weights: EQUAL_WEIGHTS,
          rubric_version: "1.0.0",
          pricebook_version: "1.0.0",
          lines: [],
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? "Could not create the audit");
      router.push(`/audit/${data.audit.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setBusy(false);
    }
  }

  if (!open) {
    return (
      <button className="btn btn-primary" onClick={() => setOpen(true)}>
        New audit
      </button>
    );
  }

  return (
    <div className="flex flex-col items-end gap-2">
      <div className="flex gap-2">
        <input
          autoFocus
          className="field w-64"
          placeholder="Business name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") create();
            if (e.key === "Escape") setOpen(false);
          }}
        />
        <button className="btn btn-primary" onClick={create} disabled={busy || !name.trim()}>
          {busy ? "..." : "Create"}
        </button>
        <button className="btn" onClick={() => setOpen(false)} disabled={busy}>
          Cancel
        </button>
      </div>
      {error && <p className="text-[12px] text-signal-severe">{error}</p>}
    </div>
  );
}
