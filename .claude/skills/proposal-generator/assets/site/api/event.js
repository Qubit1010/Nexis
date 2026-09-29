// Proposal events: view, sign, health. Vercel Node function, no dependencies.
// Trusts only api/_manifest.js (written by deploy.py) for ids, hashes, options and prices.
// Env: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, RESEND_API_KEY (optional), NOTIFY_EMAIL (optional).

const MANIFEST = require("./_manifest.js");

const SB_URL = process.env.SUPABASE_URL;
const SB_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;
const TABLE = "proposal_events";
const MAX_SIG = 400000; // bytes of data URL

function sb(path, opts = {}) {
  return fetch(`${SB_URL}/rest/v1/${path}`, {
    ...opts,
    headers: {
      apikey: SB_KEY,
      Authorization: `Bearer ${SB_KEY}`,
      "Content-Type": "application/json",
      ...(opts.headers || {}),
    },
  });
}

// Expires at the end of valid_until anywhere on earth (UTC-12).
function isExpired(validUntil) {
  return Date.now() > Date.parse(`${validUntil}T12:00:00Z`) + 86400000;
}

function clientIp(req) {
  const fwd = req.headers["x-forwarded-for"];
  return (fwd ? String(fwd).split(",")[0] : req.headers["x-real-ip"] || "").trim() || null;
}

async function existingSignature(id) {
  const r = await sb(
    `${TABLE}?proposal_id=eq.${encodeURIComponent(id)}&event_type=eq.sign` +
      `&select=signer_name,signer_email,option_id,option_name,amount_due,signature_png,version_hash,created_at&limit=1`
  );
  if (!r.ok) throw new Error(`supabase select ${r.status}`);
  const rows = await r.json();
  return rows[0] || null;
}

function signedView(row) {
  return {
    name: row.signer_name,
    email: row.signer_email,
    option_id: row.option_id,
    option_name: row.option_name,
    signed_at: row.created_at,
    signature: row.signature_png,
  };
}

async function notify(subject, lines) {
  const key = process.env.RESEND_API_KEY;
  const to = process.env.NOTIFY_EMAIL;
  if (!key || !to) return false;
  try {
    const r = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
      body: JSON.stringify({
        from: "Proposals <onboarding@resend.dev>",
        to: [to],
        subject,
        text: lines.join("\n"),
      }),
    });
    if (!r.ok) console.error("resend", r.status, await r.text());
    return r.ok;
  } catch (e) {
    console.error("resend", e);
    return false;
  }
}

module.exports = async (req, res) => {
  res.setHeader("Cache-Control", "no-store");
  // GET is the health check, and the daily Vercel cron (vercel.json) calls it so the free-tier
  // Supabase project never pauses for inactivity while a proposal is waiting to be signed.
  if (req.method !== "POST" && req.method !== "GET") return res.status(405).json({ ok: false, error: "method" });
  const b = req.method === "GET" ? { type: "health" } : req.body || {};

  if (b.type === "health") {
    let supabase = "missing_env";
    if (SB_URL && SB_KEY) {
      try {
        const r = await sb(`${TABLE}?select=id&limit=1`);
        supabase = r.ok ? "ok" : `error_${r.status}`;
      } catch (e) {
        supabase = "unreachable";
      }
    }
    return res.status(200).json({
      ok: supabase === "ok",
      proposals: Object.keys(MANIFEST).length,
      supabase,
      email: process.env.RESEND_API_KEY && process.env.NOTIFY_EMAIL ? "configured" : "not_configured",
    });
  }

  const m = MANIFEST[b.id];
  if (!m) return res.status(404).json({ ok: false, error: "unknown" });
  if (!SB_URL || !SB_KEY) return res.status(500).json({ ok: false, error: "server" });
  const current = b.hash === m.hash;

  try {
    if (b.type === "view") {
      const prior = await existingSignature(b.id);
      if (!b.internal) {
        const cnt = await sb(`${TABLE}?proposal_id=eq.${encodeURIComponent(b.id)}&event_type=eq.view&select=id&limit=1`);
        const firstView = cnt.ok && (await cnt.json()).length === 0;
        await sb(TABLE, {
          method: "POST",
          headers: { Prefer: "return=minimal" },
          body: JSON.stringify({
            proposal_id: b.id,
            version_hash: String(b.hash || "").slice(0, 64),
            event_type: "view",
            ip: clientIp(req),
            user_agent: String(req.headers["user-agent"] || "").slice(0, 400),
          }),
        });
        if (firstView && !prior) {
          await notify(`Opened: ${m.company} proposal`, [
            `${m.contact_name} (${m.company}) just opened proposal ${b.id} for the first time.`,
            `Valid until ${m.valid_until}.`,
          ]);
        }
      }
      return res.status(200).json({ ok: true, current, expired: isExpired(m.valid_until), signed: prior ? signedView(prior) : null });
    }

    if (b.type === "sign") {
      const prior = await existingSignature(b.id);
      if (prior) return res.status(200).json({ ok: false, error: "already_signed", signed: signedView(prior) });
      if (!current) return res.status(409).json({ ok: false, error: "version_mismatch" });
      if (isExpired(m.valid_until)) return res.status(410).json({ ok: false, error: "expired" });

      const opt = m.options[b.option_id];
      const name = String(b.name || "").trim();
      const email = String(b.email || "").trim();
      const sig = String(b.signature || "");
      if (!opt || name.length < 2 || name.length > 120 || !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email) ||
          !sig.startsWith("data:image/png;base64,") || sig.length > MAX_SIG) {
        return res.status(400).json({ ok: false, error: "invalid" });
      }
      const consent = `${name} confirmed authority to accept this proposal on behalf of ${m.company} and agreed to ` +
        `${opt.name} at ${opt.price_label} on the stated terms. Proposal ${b.id}, version ${m.hash}.`;

      const ins = await sb(TABLE, {
        method: "POST",
        headers: { Prefer: "return=representation" },
        body: JSON.stringify({
          proposal_id: b.id,
          version_hash: m.hash,
          event_type: "sign",
          signer_name: name,
          signer_email: email,
          signer_title: String(b.title || "").trim().slice(0, 160) || null,
          option_id: b.option_id,
          option_name: opt.name,
          amount_due: opt.due_amount,
          currency: opt.currency,
          consent_text: consent,
          signature_png: sig,
          ip: clientIp(req),
          user_agent: String(req.headers["user-agent"] || "").slice(0, 400),
        }),
      });
      if (ins.status === 409) {
        const again = await existingSignature(b.id);
        return res.status(200).json({ ok: false, error: "already_signed", signed: again ? signedView(again) : null });
      }
      if (!ins.ok) {
        console.error("supabase insert", ins.status, await ins.text());
        return res.status(500).json({ ok: false, error: "server" });
      }
      const row = (await ins.json())[0];
      await notify(`SIGNED: ${m.company} accepted ${opt.name}`, [
        `${name} <${email}> signed proposal ${b.id} for ${m.company}.`,
        `Option: ${opt.name} (${opt.price_label}). Due to start: ${opt.due_label}.`,
        opt.has_pay_url
          ? "The page sent them to your Payoneer link. Watch Payoneer for the payment."
          : `No pay link on this option: create a Payoneer payment request for ${opt.due_label} to ${email} now.`,
      ]);
      return res.status(200).json({ ok: true, signed: signedView(row) });
    }

    return res.status(400).json({ ok: false, error: "type" });
  } catch (e) {
    console.error(e);
    return res.status(500).json({ ok: false, error: "server" });
  }
};
