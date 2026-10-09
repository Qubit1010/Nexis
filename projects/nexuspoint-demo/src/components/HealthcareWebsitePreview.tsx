"use client";
import { useState } from "react";
import type { Lang } from "@/lib/i18n";
import "./healthcare-website-preview.css";

export default function HealthcareWebsitePreview({ slug, token, name, lang, sector = "healthcare" }: { slug: string; token: string; name: string; lang: Lang; sector?: "healthcare" | "food" | "education" }) {
  const [device, setDevice] = useState("desktop");
  const [loadedLang, setLoadedLang] = useState<Lang | null>(null);
  const loaded = loadedLang === lang;
  const ur = lang === "ur";
  const url = `/d/${slug}/website?t=${encodeURIComponent(token)}${ur ? "&lang=ur" : ""}`;
  return <div className="care-web-preview">
    <div className="care-web-toolbar">
      <div><b>{ur ? "لینڈنگ پیج ٹیمپلیٹ" : sector === "education" ? "Your school & academy landing page" : sector === "food" ? "Your restaurant landing page" : "Your healthcare landing page"}</b><small>{ur ? "ایک صفحہ، آپ کے کاروبار کی معلومات کے ساتھ" : "One page, tailored to your business profile"}</small></div>
      <div className="care-web-devices" role="group" aria-label={ur ? "پیش منظر کا سائز" : "Preview viewport"}>
        <button type="button" onClick={() => setDevice("desktop")} aria-pressed={device === "desktop"}>{ur ? "ڈیسک ٹاپ" : "Desktop"}</button>
        <button type="button" onClick={() => setDevice("mobile")} aria-pressed={device === "mobile"}>{ur ? "موبائل" : "Mobile"}</button>
      </div>
      <a className="btn" href={url} target="_blank" rel="noopener noreferrer">{ur ? "مکمل نمونہ کھولیں" : "Open full preview"} ↗</a>
    </div>
    <div className="care-web-stage" data-device={device} aria-busy={!loaded}>
      {!loaded && <p className="care-web-loading" role="status">{ur ? "نمونہ لوڈ ہو رہا ہے۔" : "Loading your landing page…"}</p>}
      <iframe key={lang} src={url + "&embed=1"} title={ur ? name + " کا لینڈنگ پیج نمونہ" : name + " landing page preview"} loading="lazy" referrerPolicy="no-referrer" onLoad={() => setLoadedLang(lang)} />
    </div>
    <p className="care-web-caption">{sector === "education" ? ur ? "نمونے کے اندر اسکرول کریں یا مکمل صفحہ کھولیں۔ داخلہ درخواست، کیمپس ملاقات اور والدین پورٹل مربوط ڈیمو کھولتے ہیں۔" : "Scroll inside the preview or open the full page. Admissions enquiries, campus visits and parent access connect to the working demo." : sector === "food" ? ur ? "نمونے کے اندر اسکرول کریں یا مکمل صفحہ کھولیں۔ مینو، آرڈر اور میز بکنگ مربوط ڈیمو کھولتے ہیں۔" : "Scroll inside the preview or open the full page. Menu, ordering and table bookings connect to the working demo." : ur ? "نمونے کے اندر اسکرول کریں یا مکمل صفحہ کھولیں۔ بکنگ اور مریض پورٹل کے بٹن مربوط ڈیمو کھولتے ہیں۔" : "Scroll inside the preview or open the full page. Booking and patient portal buttons connect to the working demo."}</p>
  </div>;
}
