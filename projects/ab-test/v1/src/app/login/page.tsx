import { LoginForm } from './login-form';
import styles from './login.module.css';

export const metadata = { title: 'Sign in | LeadQ' };

export default function LoginPage() {
  return (
    <main className={styles.page} id="main">
      <div className={styles.panel}>
        <div>
          <p className="eyebrow">LeadQ</p>
          <h1 className={styles.title}>Sign in</h1>
        </div>
        <LoginForm />
      </div>
    </main>
  );
}
