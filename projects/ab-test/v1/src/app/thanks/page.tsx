import Link from 'next/link';
import styles from '../form.module.css';

export const metadata = { title: 'Thanks | LeadQ' };

export default function ThanksPage() {
  return (
    <main className={styles.page} id="main">
      <div className={styles.column}>
        <p className="eyebrow">Received</p>
        <h1 className={styles.title}>Got it. Thank you.</h1>
        <p className={styles.standfirst}>
          Your enquiry is in front of us. If it is a fit you will hear back directly, usually
          within a working day. If it is not, we will still tell you, and say why.
        </p>
        <hr className="rule-line" style={{ margin: 'var(--s-6) 0' }} />
        <p>
          <Link href="/">Send another enquiry</Link>
        </p>
      </div>
    </main>
  );
}
