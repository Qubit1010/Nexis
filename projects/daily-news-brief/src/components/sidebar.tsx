"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { usePathname, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverTrigger, PopoverContent } from "@/components/ui/popover";
import { CATEGORIES } from "@/lib/pipeline/categories";
import { SearchDialog } from "@/components/search-dialog";
import { BookmarksPanel } from "@/components/bookmarks-panel";
import { useBookmarkContext } from "@/lib/hooks/bookmark-context";
import { ThemeToggle } from "@/components/theme-toggle";
import {
  Search,
  Bookmark,
  ArrowLeftRight,
  Loader2,
  Sparkles,
  CalendarDays,
  X,
} from "lucide-react";
import {
  isToday,
  isYesterday,
  isThisWeek,
  parseISO,
} from "date-fns";

interface BriefDate {
  date: string;
  createdAt: string;
}

interface DateGroup {
  label: string;
  briefs: BriefDate[];
}

const CATEGORY_ICONS: Record<string, string> = {
  "ai-models-breakthroughs": "MB",
  "ai-tools-products": "TP",
  "ai-business-strategy": "BS",
  "ai-automation-workflows": "AW",
  "ai-content-creators": "CC",
  "ai-ethics-safety": "ES",
};

function groupByDate(dates: BriefDate[]): DateGroup[] {
  const today: BriefDate[] = [];
  const yesterday: BriefDate[] = [];
  const thisWeek: BriefDate[] = [];
  const older: BriefDate[] = [];

  for (const brief of dates) {
    const d = parseISO(brief.date);
    if (isToday(d)) today.push(brief);
    else if (isYesterday(d)) yesterday.push(brief);
    else if (isThisWeek(d, { weekStartsOn: 1 })) thisWeek.push(brief);
    else older.push(brief);
  }

  const groups: DateGroup[] = [];
  if (today.length > 0) groups.push({ label: "Today", briefs: today });
  if (yesterday.length > 0) groups.push({ label: "Yesterday", briefs: yesterday });
  if (thisWeek.length > 0) groups.push({ label: "This Week", briefs: thisWeek });
  if (older.length > 0) groups.push({ label: "Older", briefs: older });
  return groups;
}

export function Sidebar() {
  const [dates, setDates] = useState<BriefDate[]>([]);
  const [generating, setGenerating] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [bookmarksOpen, setBookmarksOpen] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [calendarOpen, setCalendarOpen] = useState(false);
  const pathname = usePathname();
  const router = useRouter();
  const { bookmarks } = useBookmarkContext();
  const sidebarRef = useRef<HTMLDivElement>(null);

  const currentDate = pathname.startsWith("/brief/")
    ? pathname.split("/brief/")[1]
    : null;

  useEffect(() => {
    fetch("/api/briefs")
      .then((r) => r.json())
      .then(setDates)
      .catch(() => {});
  }, [pathname]);

  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        setSearchOpen((prev) => !prev);
      }
    }
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, []);

  // Close mobile sidebar on outside click
  const handleBackdropClick = useCallback(() => {
    setMobileOpen(false);
  }, []);

  // Close mobile sidebar on route change
  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  async function handleGenerate() {
    setGenerating(true);
    try {
      const res = await fetch("/api/generate", { method: "POST" });
      const data = await res.json();
      if (data.date) {
        router.push(`/brief/${data.date}`);
        router.refresh();
      }
    } catch {
      // minimal error handling for personal tool
    } finally {
      setGenerating(false);
    }
  }

  function formatDate(dateStr: string) {
    const d = new Date(dateStr + "T00:00:00");
    return d.toLocaleDateString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
    });
  }

  function handleCalendarSelect(date: Date | undefined) {
    if (!date) return;
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, "0");
    const d = String(date.getDate()).padStart(2, "0");
    const dateStr = `${y}-${m}-${d}`;
    router.push(`/brief/${dateStr}`);
    setCalendarOpen(false);
  }

  const dateGroups = groupByDate(dates);
  const availableDates = dates.map((b) => parseISO(b.date));

  const sidebarContent = (
    <aside
      ref={sidebarRef}
      className="w-[280px] border-r border-white/[0.06] bg-[#0a0f1a] flex flex-col h-screen shrink-0"
    >
      {/* Header */}
      <div className="p-5 space-y-4">
        <div className="animate-fade-in">
          <div className="flex items-center gap-2.5 mb-1">
            <div className="w-8 h-8 rounded-lg bg-amber-500/15 flex items-center justify-center">
              <span className="text-amber-500 text-sm font-bold">AI</span>
            </div>
            <h1 className="text-xl font-bold tracking-tight text-white">
              Intel Brief
            </h1>
          </div>
          <div className="flex items-center justify-between ml-[42px]">
            <p className="text-[13px] text-zinc-500">
              AI/Tech intelligence
            </p>
            <ThemeToggle />
          </div>
        </div>

        {/* Generate button */}
        <Button
          className="w-full h-11 text-[15px] font-medium bg-amber-500 hover:bg-amber-400 text-[#0a0f1a] transition-all duration-200 hover:shadow-[0_0_24px_rgba(245,158,11,0.25)] cursor-pointer"
          onClick={handleGenerate}
          disabled={generating}
        >
          {generating ? (
            <span className="flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin" />
              Generating...
            </span>
          ) : (
            <span className="flex items-center gap-2">
              <Sparkles className="w-4 h-4" />
              Generate Brief
            </span>
          )}
        </Button>

        {/* Action buttons */}
        <div className="space-y-1">
          <button
            onClick={() => setSearchOpen(true)}
            className="w-full flex items-center gap-2.5 text-[13px] text-zinc-500 hover:text-zinc-300 px-3 py-2 rounded-lg border border-white/[0.06] hover:border-white/[0.12] hover:bg-white/[0.03] transition-all duration-200"
          >
            <Search className="w-3.5 h-3.5 shrink-0" />
            <span className="flex-1 text-left">Search articles...</span>
            <kbd className="text-[10px] px-1.5 py-0.5 rounded bg-white/[0.06] text-zinc-600">
              Ctrl+K
            </kbd>
          </button>

          <button
            onClick={() => setBookmarksOpen(true)}
            className="w-full flex items-center gap-2.5 text-[13px] text-zinc-500 hover:text-zinc-300 px-3 py-2 rounded-lg border border-white/[0.06] hover:border-white/[0.12] hover:bg-white/[0.03] transition-all duration-200"
          >
            <Bookmark className="w-3.5 h-3.5 shrink-0" />
            <span className="flex-1 text-left">Saved articles</span>
            {bookmarks.length > 0 && (
              <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-amber-500/15 text-amber-500 font-medium">
                {bookmarks.length}
              </span>
            )}
          </button>

          <button
            onClick={() => router.push("/compare")}
            className="w-full flex items-center gap-2.5 text-[13px] text-zinc-500 hover:text-zinc-300 px-3 py-2 rounded-lg border border-white/[0.06] hover:border-white/[0.12] hover:bg-white/[0.03] transition-all duration-200"
          >
            <ArrowLeftRight className="w-3.5 h-3.5 shrink-0" />
            <span className="flex-1 text-left">Compare briefs</span>
          </button>
        </div>
      </div>

      <div className="h-px bg-white/[0.06] mx-4" />

      {/* Quick links when viewing a brief */}
      {currentDate && (
        <>
          <div className="px-5 py-4">
            <p className="text-[11px] font-semibold text-zinc-600 uppercase tracking-[0.1em] mb-3">
              Intelligence
            </p>
            <nav className="space-y-0.5 mb-4">
              {[
                { slug: "trending", label: "Trending Now", icon: "#" },
                { slug: "content-ideas", label: "Content Ideas", icon: "!" },
                { slug: "sentiment", label: "Sentiment", icon: "~" },
                { slug: "most-discussed", label: "Most Discussed", icon: "\u2191" },
              ].map((item) => (
                <a
                  key={item.slug}
                  href={`#${item.slug}`}
                  className="flex items-center gap-2.5 text-[14px] py-2 px-2.5 rounded-lg text-zinc-500 hover:text-zinc-200 hover:bg-white/[0.04] transition-all duration-200"
                >
                  <span className="w-7 h-7 rounded-md bg-teal-500/10 flex items-center justify-center text-[11px] font-bold text-teal-500/70 shrink-0">
                    {item.icon}
                  </span>
                  {item.label}
                </a>
              ))}
            </nav>

            <p className="text-[11px] font-semibold text-zinc-600 uppercase tracking-[0.1em] mb-3">
              Categories
            </p>
            <nav className="space-y-0.5">
              {CATEGORIES.map((cat) => (
                <a
                  key={cat.slug}
                  href={`#${cat.slug}`}
                  className="flex items-center gap-2.5 text-[14px] py-2 px-2.5 rounded-lg text-zinc-500 hover:text-zinc-200 hover:bg-white/[0.04] transition-all duration-200"
                >
                  <span className="w-7 h-7 rounded-md bg-amber-500/10 flex items-center justify-center text-[10px] font-bold text-amber-500/70 shrink-0">
                    {CATEGORY_ICONS[cat.slug] || "??"}
                  </span>
                  {cat.name}
                </a>
              ))}
            </nav>
          </div>
          <div className="h-px bg-white/[0.06] mx-4" />
        </>
      )}

      {/* Calendar date picker */}
      <div className="px-5 pt-4 pb-2">
        <div className="flex items-center justify-between mb-3">
          <p className="text-[11px] font-semibold text-zinc-600 uppercase tracking-[0.1em]">
            Past Briefs
          </p>
          <Popover open={calendarOpen} onOpenChange={setCalendarOpen}>
            <PopoverTrigger
              className="w-7 h-7 rounded-md flex items-center justify-center text-zinc-600 hover:text-zinc-300 hover:bg-white/[0.06] transition-all duration-200"
            >
              <CalendarDays className="w-3.5 h-3.5" />
            </PopoverTrigger>
            <PopoverContent side="right" sideOffset={8} className="w-auto p-0">
              <Calendar
                mode="single"
                selected={currentDate ? parseISO(currentDate) : undefined}
                onSelect={handleCalendarSelect}
                modifiers={{ hasBrief: availableDates }}
                modifiersClassNames={{
                  hasBrief: "font-bold text-amber-500",
                }}
              />
            </PopoverContent>
          </Popover>
        </div>
      </div>

      {/* Past briefs grouped by date */}
      <div className="px-5 pb-4 flex-1 min-h-0">
        <ScrollArea className="h-full">
          <div className="pr-3 space-y-4">
            {dates.length === 0 && (
              <p className="text-sm text-zinc-600 py-3">
                No briefs generated yet
              </p>
            )}
            {dateGroups.map((group) => (
              <div key={group.label}>
                <p className="text-[10px] font-semibold text-zinc-700 uppercase tracking-[0.1em] mb-1.5 px-1">
                  {group.label}
                </p>
                <div className="space-y-0.5">
                  {group.briefs.map((brief) => (
                    <button
                      key={brief.date}
                      onClick={() => router.push(`/brief/${brief.date}`)}
                      className={`w-full text-left text-[14px] py-2 px-2.5 rounded-lg transition-all duration-200 ${
                        currentDate === brief.date
                          ? "bg-amber-500/10 text-amber-500 font-semibold shadow-[inset_0_0_0_1px_rgba(245,158,11,0.2)]"
                          : "text-zinc-500 hover:bg-white/[0.04] hover:text-zinc-300"
                      }`}
                    >
                      {formatDate(brief.date)}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
      </div>

      {/* Generation status */}
      {generating && (
        <div className="px-5 py-3 border-t border-white/[0.06]">
          <div className="flex items-center gap-2 text-[12px] text-amber-500">
            <Loader2 className="w-3 h-3 animate-spin" />
            <span>Generating brief...</span>
          </div>
        </div>
      )}

      <SearchDialog open={searchOpen} onClose={() => setSearchOpen(false)} />
      <BookmarksPanel open={bookmarksOpen} onClose={() => setBookmarksOpen(false)} />
    </aside>
  );

  return (
    <>
      {/* Desktop sidebar */}
      <div className="hidden lg:block">{sidebarContent}</div>

      {/* Mobile toggle */}
      <button
        onClick={() => setMobileOpen(true)}
        className="lg:hidden fixed top-4 left-4 z-40 w-10 h-10 rounded-lg bg-[#0a0f1a] border border-white/[0.08] flex items-center justify-center text-zinc-400 hover:text-white transition-colors"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="3" y1="6" x2="21" y2="6" />
          <line x1="3" y1="12" x2="21" y2="12" />
          <line x1="3" y1="18" x2="21" y2="18" />
        </svg>
      </button>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div className="lg:hidden fixed inset-0 z-50">
          <div
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            onClick={handleBackdropClick}
          />
          <div className="relative animate-slide-in-left">
            <button
              onClick={() => setMobileOpen(false)}
              className="absolute top-4 right-[-44px] w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-white/70 hover:text-white"
            >
              <X className="w-4 h-4" />
            </button>
            {sidebarContent}
          </div>
        </div>
      )}
    </>
  );
}
