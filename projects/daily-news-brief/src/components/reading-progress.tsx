"use client";

import { useEffect, useState } from "react";

export function ReadingProgress() {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const main = document.querySelector("main");
    if (!main) return;

    function handleScroll() {
      if (!main) return;
      const scrollTop = main.scrollTop;
      const scrollHeight = main.scrollHeight - main.clientHeight;
      if (scrollHeight <= 0) {
        setProgress(0);
        return;
      }
      setProgress(Math.min(100, (scrollTop / scrollHeight) * 100));
    }

    main.addEventListener("scroll", handleScroll, { passive: true });
    return () => main.removeEventListener("scroll", handleScroll);
  }, []);

  if (progress === 0) return null;

  return (
    <div className="fixed top-0 left-0 right-0 z-50 h-[2px] pointer-events-none">
      <div
        className="h-full bg-primary/70 transition-[width] duration-150"
        style={{ width: `${progress}%` }}
      />
    </div>
  );
}
