"use client";

import { createContext, useContext, ReactNode } from "react";
import { useBookmarks, BookmarkedArticle } from "./use-bookmarks";

interface BookmarkContextValue {
  bookmarks: BookmarkedArticle[];
  isBookmarked: (id: number) => boolean;
  toggleBookmark: (article: Omit<BookmarkedArticle, "savedAt">) => void;
  clearBookmarks: () => void;
}

const BookmarkContext = createContext<BookmarkContextValue | null>(null);

export function BookmarkProvider({ children }: { children: ReactNode }) {
  const value = useBookmarks();
  return (
    <BookmarkContext.Provider value={value}>
      {children}
    </BookmarkContext.Provider>
  );
}

export function useBookmarkContext() {
  const ctx = useContext(BookmarkContext);
  if (!ctx)
    throw new Error("useBookmarkContext must be used within BookmarkProvider");
  return ctx;
}
