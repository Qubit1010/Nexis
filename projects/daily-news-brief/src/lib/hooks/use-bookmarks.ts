"use client";

import { useState, useEffect, useCallback } from "react";

export interface BookmarkedArticle {
  id: number;
  title: string;
  url: string;
  source: string;
  tldr: string;
  date: string;
  savedAt: string;
}

const STORAGE_KEY = "intel-brief-bookmarks";

function loadBookmarks(): BookmarkedArticle[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveBookmarks(bookmarks: BookmarkedArticle[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(bookmarks));
}

export function useBookmarks() {
  const [bookmarks, setBookmarks] = useState<BookmarkedArticle[]>([]);

  useEffect(() => {
    setBookmarks(loadBookmarks());
  }, []);

  const isBookmarked = useCallback(
    (id: number) => bookmarks.some((b) => b.id === id),
    [bookmarks]
  );

  const toggleBookmark = useCallback(
    (article: Omit<BookmarkedArticle, "savedAt">) => {
      setBookmarks((prev) => {
        const exists = prev.some((b) => b.id === article.id);
        const next = exists
          ? prev.filter((b) => b.id !== article.id)
          : [...prev, { ...article, savedAt: new Date().toISOString() }];
        saveBookmarks(next);
        return next;
      });
    },
    []
  );

  const clearBookmarks = useCallback(() => {
    setBookmarks([]);
    saveBookmarks([]);
  }, []);

  return { bookmarks, isBookmarked, toggleBookmark, clearBookmarks };
}
