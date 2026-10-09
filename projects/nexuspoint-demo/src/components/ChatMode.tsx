"use client";
// Full-screen chat: what the prospect's own phone opens after scanning the QR code (Phase 1),
// before the WhatsApp number is live. Styled like a messaging app, labelled as a demo.
import ChatWindow from "./ChatWindow";
import { T, fill, type Lang } from "@/lib/i18n";

export default function ChatMode({ slug, token, name, lang, prompts,healthcare=false,restaurant=false,school=false }: { slug: string; token: string; name: string; lang: Lang; prompts: string[];healthcare?:boolean;restaurant?:boolean;school?:boolean }) {
  return (
    <div className="hub chatmode" dir={lang === "ur" ? "rtl" : "ltr"} lang={lang}>
      <p className="note">{fill(T[lang].chatNote, { name })}</p>
      <ChatWindow slug={slug} token={token} name={name} lang={lang} prompts={prompts} healthcare={healthcare} restaurant={restaurant} school={school} />
    </div>
  );
}
