'use client';

import { useRouter } from 'next/navigation';
import { useState } from 'react';

export function SignOutButton() {
  const router = useRouter();
  const [busy, setBusy] = useState(false);

  async function signOut() {
    setBusy(true);
    await fetch('/api/session', { method: 'DELETE' }).catch(() => null);
    router.push('/login');
    router.refresh();
  }

  return (
    <button className="btn btn-ghost" onClick={signOut} disabled={busy} type="button">
      Sign out
    </button>
  );
}
