import { StrictMode, useCallback, useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';

import './styles.css';
import { api, ApiError } from './api.ts';
import { loadLabels } from './labels.ts';
import { Link, navigate, usePath } from './router.tsx';
import Intake from './pages/Intake.tsx';
import Dashboard from './pages/Dashboard.tsx';
import Rules from './pages/Rules.tsx';

function Login({ onIn }: { onIn: () => void }) {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError('');
    try {
      await api.login(password);
      onIn();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not sign in');
      setPassword('');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="login-wrap">
      <form className="login-card" onSubmit={submit}>
        <p className="eyebrow">Internal</p>
        <h1>Lead desk</h1>
        <p className="sub">Sign in to triage the pipeline.</p>

        {error && <div className="banner" role="alert">{error}</div>}

        <div className="field">
          <label htmlFor="pw">Password</label>
          <input
            id="pw" type="password" value={password} autoFocus autoComplete="current-password"
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        <button className="btn btn-primary btn-lg" style={{ width: '100%' }} disabled={busy || !password}>
          {busy ? 'Checking' : 'Sign in'}
        </button>

        <p className="small muted" style={{ marginTop: 18, marginBottom: 0 }}>
          <Link to="/">Back to the public form</Link>
        </p>
      </form>
    </div>
  );
}

function Admin() {
  const path = usePath();
  const [authed, setAuthed] = useState<boolean | null>(null);
  const [ready, setReady] = useState(false);

  const check = useCallback(async () => {
    try {
      const { authed: ok } = await api.me();
      setAuthed(ok);
      if (ok) await loadLabels();
    } catch {
      setAuthed(false);
    } finally {
      setReady(true);
    }
  }, []);

  useEffect(() => { void check(); }, [check]);

  const signedOut = useCallback(() => {
    setAuthed(false);
    setReady(true);
  }, []);

  if (!ready) return <div className="loading"><span className="spinner" /> Loading</div>;
  if (!authed) return <Login onIn={() => { setReady(false); void check(); }} />;

  async function signOut() {
    await api.logout().catch(() => {});
    setAuthed(false);
  }

  return (
    <>
      <header className="masthead">
        <div className="masthead-inner">
          <span className="wordmark">Lead<span>desk</span></span>
          <nav className="nav">
            <Link to="/admin" className={path === '/admin' ? 'on' : ''}>Triage</Link>
            <Link to="/admin/rules" className={path === '/admin/rules' ? 'on' : ''}>Rules</Link>
            <Link to="/">Public form</Link>
            <button className="btn btn-sm btn-ghost" onClick={signOut} style={{ marginLeft: 8 }}>Sign out</button>
          </nav>
        </div>
      </header>
      <main className="shell">
        {path === '/admin/rules'
          ? <Rules onSignedOut={signedOut} />
          : <Dashboard onSignedOut={signedOut} />}
      </main>
    </>
  );
}

function App() {
  const path = usePath();

  useEffect(() => {
    document.title = path.startsWith('/admin') ? 'Lead desk' : 'Start a project';
  }, [path]);

  if (path.startsWith('/admin')) return <Admin />;
  if (path !== '/') {
    return (
      <main className="thanks">
        <h1>Page not found</h1>
        <p className="muted">That address does not exist.</p>
        <button className="btn" onClick={() => navigate('/')}>Go to the form</button>
      </main>
    );
  }
  return <Intake />;
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
