import { useEffect, useState } from 'react';
import { api, ApiError } from '../api.ts';
import type { FormConfig } from '../api.ts';

const EMPTY = {
  name: '',
  email: '',
  company: '',
  budget: 0,
  timeline: 0,
  needs: [] as string[],
  message: '',
};

export default function Intake() {
  const [config, setConfig] = useState<FormConfig | null>(null);
  const [form, setForm] = useState({ ...EMPTY });
  const [honeypot, setHoneypot] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [banner, setBanner] = useState('');
  const [sending, setSending] = useState(false);
  const [done, setDone] = useState(false);

  useEffect(() => {
    api.formConfig().then(setConfig).catch(() => setBanner('Could not load the form. Please refresh.'));
  }, []);

  const set = <K extends keyof typeof EMPTY>(key: K, value: (typeof EMPTY)[K]) => {
    setForm((f) => ({ ...f, [key]: value }));
    setErrors((e) => {
      if (!(key in e)) return e;
      const next = { ...e };
      delete next[key as string];
      return next;
    });
  };

  const toggleNeed = (value: string) =>
    set('needs', form.needs.includes(value) ? form.needs.filter((n) => n !== value) : [...form.needs, value]);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setSending(true);
    setBanner('');
    setErrors({});
    try {
      await api.submitLead({ ...form, website: honeypot });
      setDone(true);
      window.scrollTo({ top: 0 });
    } catch (err) {
      if (err instanceof ApiError && Object.keys(err.fields).length) {
        setErrors(err.fields);
        setBanner('Please check the highlighted answers.');
        document.querySelector('.field.invalid')?.scrollIntoView({ block: 'center', behavior: 'smooth' });
      } else {
        setBanner(err instanceof ApiError ? err.message : 'Something went wrong. Please try again.');
      }
    } finally {
      setSending(false);
    }
  }

  if (done) {
    return (
      <main className="thanks">
        <div className="mark" aria-hidden="true">&#10003;</div>
        <h1>Thank you</h1>
        <p className="muted">
          Your enquiry is in. We read every one and reply to the ones we can genuinely help with,
          usually within two working days.
        </p>
      </main>
    );
  }

  if (!config) {
    return (
      <main className="loading">
        <span className="spinner" aria-hidden="true" /> Loading
      </main>
    );
  }

  const invalid = (key: string) => (errors[key] ? 'field invalid' : 'field');

  return (
    <main className="intake">
      <header className="intake-head">
        <p className="eyebrow">New project enquiry</p>
        <h1>Tell us about the work.</h1>
        <p className="lede">
          Five questions, about two minutes. The more concrete you are about budget and timing,
          the faster we can tell you whether we are the right fit.
        </p>
      </header>

      {banner && <div className="banner" role="alert">{banner}</div>}

      <form onSubmit={submit} noValidate>
        <section className="section" style={{ borderTop: 0, marginTop: 0, paddingTop: 0 }}>
          <div className="section-head">
            <span className="section-num">1</span>
            <div>
              <h2>Who you are</h2>
              <p className="section-sub">So we know who we are replying to.</p>
            </div>
          </div>

          <div className="row-2">
            <div className={invalid('name')}>
              <label htmlFor="name">Your name</label>
              <input
                id="name" type="text" value={form.name} autoComplete="name"
                onChange={(e) => set('name', e.target.value)}
                aria-invalid={!!errors.name}
              />
              {errors.name && <p className="error-text">{errors.name}</p>}
            </div>

            <div className={invalid('email')}>
              <label htmlFor="email">Email</label>
              <input
                id="email" type="email" value={form.email} autoComplete="email"
                onChange={(e) => set('email', e.target.value)}
                aria-invalid={!!errors.email}
              />
              {errors.email && <p className="error-text">{errors.email}</p>}
            </div>
          </div>

          <div className={invalid('company')}>
            <label htmlFor="company">Company <span className="muted" style={{ fontWeight: 400 }}>(optional)</span></label>
            <input
              id="company" type="text" value={form.company} autoComplete="organization"
              onChange={(e) => set('company', e.target.value)}
            />
            {errors.company && <p className="error-text">{errors.company}</p>}
          </div>
        </section>

        <section className="section">
          <div className="section-head">
            <span className="section-num">2</span>
            <div>
              <h2>What you need</h2>
              <p className="section-sub">Pick everything that applies.</p>
            </div>
          </div>
          <div className={errors.needs ? 'field invalid' : 'field'}>
            <div className="chips" role="group" aria-label="What you need">
              {config.needs.map((n) => (
                <button
                  type="button"
                  key={n.value}
                  className={form.needs.includes(n.value) ? 'chip on' : 'chip'}
                  aria-pressed={form.needs.includes(n.value)}
                  onClick={() => toggleNeed(n.value)}
                >
                  {n.label}
                </button>
              ))}
            </div>
            {errors.needs && <p className="error-text">{errors.needs}</p>}
          </div>
        </section>

        <section className="section">
          <div className="section-head">
            <span className="section-num">3</span>
            <div>
              <h2>Budget</h2>
              <p className="section-sub">A range is fine. It decides what is realistic to build.</p>
            </div>
          </div>
          <div className={errors.budget ? 'field invalid' : 'field'}>
            <div className="choices">
              {config.budget.map((o) => (
                <label key={o.value} className={form.budget === o.value ? 'choice on' : 'choice'}>
                  <input
                    type="radio" name="budget" value={o.value}
                    checked={form.budget === o.value}
                    onChange={() => set('budget', o.value)}
                  />
                  <span>
                    <span className="choice-label">{o.label}</span>
                    {o.hint && <span className="choice-hint" style={{ display: 'block' }}>{o.hint}</span>}
                  </span>
                </label>
              ))}
            </div>
            {errors.budget && <p className="error-text">{errors.budget}</p>}
          </div>
        </section>

        <section className="section">
          <div className="section-head">
            <span className="section-num">4</span>
            <div>
              <h2>Timing</h2>
              <p className="section-sub">When would you want to start?</p>
            </div>
          </div>
          <div className={errors.timeline ? 'field invalid' : 'field'}>
            <div className="choices">
              {config.timeline.map((o) => (
                <label key={o.value} className={form.timeline === o.value ? 'choice on' : 'choice'}>
                  <input
                    type="radio" name="timeline" value={o.value}
                    checked={form.timeline === o.value}
                    onChange={() => set('timeline', o.value)}
                  />
                  <span>
                    <span className="choice-label">{o.label}</span>
                    {o.hint && <span className="choice-hint" style={{ display: 'block' }}>{o.hint}</span>}
                  </span>
                </label>
              ))}
            </div>
            {errors.timeline && <p className="error-text">{errors.timeline}</p>}
          </div>
        </section>

        <section className="section">
          <div className="section-head">
            <span className="section-num">5</span>
            <div>
              <h2>The project</h2>
              <p className="section-sub">What are you trying to achieve, and what is in the way?</p>
            </div>
          </div>
          <div className={invalid('message')}>
            <label htmlFor="message" className="label">In your own words</label>
            <textarea
              id="message" value={form.message}
              onChange={(e) => set('message', e.target.value)}
              placeholder="We run a 12-person recruitment firm and our candidate intake is all manual..."
            />
            <p className="hint">{form.message.length} / 4000</p>
            {errors.message && <p className="error-text">{errors.message}</p>}
          </div>
        </section>

        {/* Honeypot. Hidden from sight and from screen readers; only a bot fills this in. */}
        <div className="hp" aria-hidden="true">
          <label htmlFor="website">Website</label>
          <input
            id="website" type="text" tabIndex={-1} autoComplete="off"
            value={honeypot} onChange={(e) => setHoneypot(e.target.value)}
          />
        </div>

        <div className="submit-row">
          <button type="submit" className="btn btn-primary btn-lg" disabled={sending}>
            {sending ? 'Sending' : 'Send enquiry'}
          </button>
          <span className="small muted">We reply to every serious enquiry.</span>
        </div>
      </form>
    </main>
  );
}
