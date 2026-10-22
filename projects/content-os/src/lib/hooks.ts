import { useCallback, useEffect, useRef, useState, useSyncExternalStore } from "react";
import { api } from "./api";

// ---- Live activity: one EventSource for the app; pages refetch when the server says something changed.

export interface LiveEvent {
  id?: number;
  ts: string;
  actor: string;
  entity: string;
  entityId: string | null;
  type: string;
  data?: any;
}

type Listener = (e: LiveEvent) => void;
const listeners = new Set<Listener>();
let version = 0;
const versionListeners = new Set<() => void>();
let source: EventSource | null = null;
let connected = false;

function ensureSource() {
  if (source) return;
  source = new EventSource("/api/events/stream");
  source.onopen = () => {
    connected = true;
    bump();
  };
  source.onerror = () => {
    connected = false;
    bumpVersionOnly();
  };
  source.onmessage = (m) => {
    try {
      const e = JSON.parse(m.data) as LiveEvent;
      for (const fn of listeners) fn(e);
      if (e.type !== "publish.log") bump();
    } catch {
      /* ignore */
    }
  };
}

let bumpTimer: ReturnType<typeof setTimeout> | null = null;
function bump() {
  if (bumpTimer) return;
  bumpTimer = setTimeout(() => {
    bumpTimer = null;
    bumpVersionOnly();
  }, 300);
}
function bumpVersionOnly() {
  version++;
  for (const fn of versionListeners) fn();
}

/** A counter that increments whenever the server reports a change (debounced). */
export function useLiveVersion(): number {
  ensureSource();
  return useSyncExternalStore(
    (cb) => {
      versionListeners.add(cb);
      return () => versionListeners.delete(cb);
    },
    () => version,
  );
}

export function useConnected(): boolean {
  useLiveVersion();
  return connected;
}

export function useLiveEvents(fn: Listener) {
  const ref = useRef(fn);
  ref.current = fn;
  useEffect(() => {
    ensureSource();
    const l: Listener = (e) => ref.current(e);
    listeners.add(l);
    return () => {
      listeners.delete(l);
    };
  }, []);
}

/** GET with live refresh. `path` null skips the fetch. */
export function useApi<T>(path: string | null, opts: { live?: boolean } = { live: true }) {
  const live = useLiveVersion();
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [nonce, setNonce] = useState(0);
  const reload = useCallback(() => setNonce((n) => n + 1), []);
  const liveKey = opts.live === false ? 0 : live;
  useEffect(() => {
    if (!path) return;
    let cancelled = false;
    api
      .get<T>(path)
      .then((d) => {
        if (!cancelled) {
          setData(d);
          setError(null);
        }
      })
      .catch((e) => !cancelled && setError(e.message))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [path, liveKey, nonce]);
  return { data, error, loading, reload, setData };
}

// ---- Hash router (no dependency needed for seven pages)

export function useRoute(): string[] {
  const get = () => (location.hash.replace(/^#\/?/, "") || "").split("/").filter(Boolean);
  const [route, setRoute] = useState(get);
  useEffect(() => {
    const on = () => setRoute(get());
    addEventListener("hashchange", on);
    return () => removeEventListener("hashchange", on);
  }, []);
  return route;
}

export const go = (path: string) => {
  location.hash = path.startsWith("#") ? path : `#/${path.replace(/^\//, "")}`;
};

// ---- Toasts

export interface Toast {
  id: number;
  kind: "ok" | "err" | "info";
  text: string;
  href?: string;
}
let toasts: Toast[] = [];
const toastListeners = new Set<() => void>();
let toastId = 0;
export function toast(text: string, kind: Toast["kind"] = "info", href?: string) {
  const t = { id: ++toastId, kind, text, href };
  toasts = [...toasts, t].slice(-4);
  toastListeners.forEach((f) => f());
  setTimeout(() => {
    toasts = toasts.filter((x) => x.id !== t.id);
    toastListeners.forEach((f) => f());
  }, kind === "err" ? 9000 : 5000);
}
export function useToasts(): Toast[] {
  return useSyncExternalStore(
    (cb) => {
      toastListeners.add(cb);
      return () => toastListeners.delete(cb);
    },
    () => toasts,
  );
}

/** Wrap an async action: toast its error, report busy. */
export function useAction() {
  const [busy, setBusy] = useState<string | null>(null);
  const run = useCallback(async <T,>(key: string, fn: () => Promise<T>, okText?: string): Promise<T | undefined> => {
    setBusy(key);
    try {
      const out = await fn();
      if (okText) toast(okText, "ok");
      return out;
    } catch (e) {
      toast((e as Error).message, "err");
      return undefined;
    } finally {
      setBusy(null);
    }
  }, []);
  return { busy, run };
}
