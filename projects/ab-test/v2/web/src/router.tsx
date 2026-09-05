import { useCallback, useEffect, useState } from 'react';

/**
 * Four views do not justify a routing library. This is the whole router: read the path,
 * re-render on popstate, and expose a navigate() that pushes without a reload.
 */

const listeners = new Set<() => void>();

export function navigate(path: string): void {
  if (path === window.location.pathname) return;
  window.history.pushState({}, '', path);
  for (const fn of listeners) fn();
}

export function usePath(): string {
  const [path, setPath] = useState(() => window.location.pathname);

  useEffect(() => {
    const update = () => setPath(window.location.pathname);
    listeners.add(update);
    window.addEventListener('popstate', update);
    return () => {
      listeners.delete(update);
      window.removeEventListener('popstate', update);
    };
  }, []);

  return path;
}

/** An anchor that stays a real link (middle-click, open in new tab) but navigates in-page. */
export function Link(props: { to: string; className?: string; children: React.ReactNode }) {
  const { to, className, children } = props;
  const onClick = useCallback(
    (e: React.MouseEvent<HTMLAnchorElement>) => {
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return;
      e.preventDefault();
      navigate(to);
    },
    [to],
  );
  return (
    <a href={to} className={className} onClick={onClick}>
      {children}
    </a>
  );
}
