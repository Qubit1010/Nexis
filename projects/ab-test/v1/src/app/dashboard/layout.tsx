import { cookies } from 'next/headers';
import Link from 'next/link';
import { redirect } from 'next/navigation';
import type { ReactNode } from 'react';
import { SESSION_COOKIE, verifySessionToken } from '@/lib/auth';
import { SignOutButton } from './sign-out-button';
import styles from './triage.module.css';

/**
 * Page-level gate. The API handlers check the session independently, because a layout
 * gate protects pages and nothing else.
 */
export default async function DashboardLayout({ children }: { children: ReactNode }) {
  const token = (await cookies()).get(SESSION_COOKIE)?.value;
  if (!(await verifySessionToken(token))) redirect('/login');

  return (
    <div className={styles.app}>
      <header className={styles.topbar}>
        <div className={'shell ' + styles.topbarInner}>
          <div className={styles.brand}>
            <span className="eyebrow">LeadQ</span>
            <nav className={styles.nav} aria-label="Dashboard">
              <Link href="/dashboard">Leads</Link>
              <Link href="/dashboard/rules">Scoring rules</Link>
              <Link href="/" target="_blank" rel="noreferrer">
                Public form
              </Link>
            </nav>
          </div>
          <SignOutButton />
        </div>
      </header>
      <main id="main">{children}</main>
    </div>
  );
}
