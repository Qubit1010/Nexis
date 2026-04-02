"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Lightbulb, PenLine, BookOpen } from "lucide-react";

const NAV = [
  {
    href: "/ideate",
    label: "Ideate",
    icon: Lightbulb,
    desc: "Scored content ideas",
  },
  {
    href: "/create",
    label: "Create",
    icon: PenLine,
    desc: "Research & write",
  },
  {
    href: "/log",
    label: "Log",
    icon: BookOpen,
    desc: "Posted content",
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-[248px] border-r border-[rgba(255,255,255,0.06)] bg-[#0d0d0d] flex flex-col h-screen shrink-0">
      {/* Brand header */}
      <div className="px-5 pt-7 pb-6 border-b border-[rgba(255,255,255,0.06)]">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl gradient-blue flex items-center justify-center shrink-0 shadow-[0_0_20px_rgba(32,142,199,0.3)]">
            <span className="text-white text-[15px] font-black tracking-tight">N</span>
          </div>
          <div>
            <p className="text-white text-[14px] font-bold leading-tight tracking-tight">NexusPoint</p>
            <p className="text-[#208ec7] text-[11px] font-medium tracking-wide mt-0.5">
              Content Engine
            </p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex flex-col gap-0.5 px-3 pt-5">
        <p className="text-[11px] font-semibold text-[#444] uppercase tracking-[0.14em] px-2 mb-2">
          Workspace
        </p>
        {NAV.map(({ href, label, icon: Icon, desc }) => {
          const active = pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={`relative flex items-center gap-3 px-3 py-3 rounded-xl transition-all duration-150 group ${
                active
                  ? "bg-[rgba(32,142,199,0.1)] text-white"
                  : "text-[#666] hover:text-[#ccc] hover:bg-[rgba(255,255,255,0.04)]"
              }`}
            >
              {/* Active left bar */}
              {active && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 rounded-full bg-[#208ec7]" />
              )}
              <Icon
                className={`w-[18px] h-[18px] shrink-0 ${
                  active ? "text-[#208ec7]" : "text-current"
                }`}
              />
              <div className="min-w-0">
                <p className={`text-[14px] font-semibold leading-tight ${active ? "text-white" : "text-current"}`}>
                  {label}
                </p>
                <p className="text-[12px] text-[#444] leading-tight mt-0.5 truncate group-hover:text-[#555] transition-colors">
                  {desc}
                </p>
              </div>
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="mt-auto px-5 py-5 border-t border-[rgba(255,255,255,0.05)]">
        <p className="text-[11px] text-[#333] tracking-widest uppercase font-medium">
          Innovate · Create · Elevate
        </p>
      </div>
    </aside>
  );
}
