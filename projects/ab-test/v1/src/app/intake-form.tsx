'use client';

import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { Field } from '@/components/field';
import { BUDGETS, SERVICES, TIMELINES } from '@/lib/options';
import styles from './form.module.css';

type FieldErrors = Record<string, string[] | undefined>;

const INITIAL = {
  name: '',
  email: '',
  company: '',
  budget: '',
  timeline: '',
  needs: '',
  source: '',
  website: '',
};

export function IntakeForm() {
  const router = useRouter();
  const [values, setValues] = useState(INITIAL);
  const [services, setServices] = useState<string[]>([]);
  const [errors, setErrors] = useState<FieldErrors>({});
  const [formError, setFormError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  function set(key: keyof typeof INITIAL, value: string) {
    setValues((current) => ({ ...current, [key]: value }));
  }

  function toggleService(value: string) {
    setServices((current) =>
      current.includes(value)
        ? current.filter((entry) => entry !== value)
        : [...current, value],
    );
  }

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setErrors({});
    setFormError('');

    try {
      const response = await fetch('/api/leads', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          ...values,
          budget: values.budget === '' ? undefined : Number(values.budget),
          services,
        }),
      });

      const payload: unknown = await response.json().catch(() => ({}));

      if (!response.ok) {
        const body = payload as { error?: string; details?: FieldErrors };
        setErrors(body.details ?? {});
        setFormError(body.error ?? 'Something went wrong. Try again.');
        return;
      }

      router.push('/thanks');
    } catch {
      setFormError('We could not reach the server. Check your connection and try again.');
    } finally {
      setSubmitting(false);
    }
  }

  const first = (key: string) => errors[key]?.[0];

  return (
    <form className={styles.form} onSubmit={onSubmit} noValidate>
      <div className={styles.question}>
        <span className={styles.index} aria-hidden="true">
          01
        </span>
        <div className={styles.body}>
          <div className={styles.pair}>
            <Field id="name" label="Your name" error={first('name')}>
              <input
                className="control"
                id="name"
                name="name"
                autoComplete="name"
                value={values.name}
                onChange={(event) => set('name', event.target.value)}
                aria-invalid={first('name') ? true : undefined}
                aria-describedby={first('name') ? 'name-error' : undefined}
              />
            </Field>
            <Field id="email" label="Email" error={first('email')}>
              <input
                className="control"
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                value={values.email}
                onChange={(event) => set('email', event.target.value)}
                aria-invalid={first('email') ? true : undefined}
                aria-describedby={first('email') ? 'email-error' : undefined}
              />
            </Field>
          </div>
        </div>
      </div>

      <div className={styles.question}>
        <span className={styles.index} aria-hidden="true">
          02
        </span>
        <div className={styles.body}>
          <Field
            id="company"
            label="Company"
            hint="Optional, but it helps us understand the context."
            error={first('company')}
          >
            <input
              className="control"
              id="company"
              name="company"
              autoComplete="organization"
              value={values.company}
              onChange={(event) => set('company', event.target.value)}
            />
          </Field>
        </div>
      </div>

      <div className={styles.question}>
        <span className={styles.index} aria-hidden="true">
          03
        </span>
        <div className={styles.body}>
          <fieldset className={styles.choices}>
            <legend className={styles.legend}>What do you need?</legend>
            {SERVICES.map((service) => (
              <label className={styles.choice} key={service.value}>
                <input
                  type="checkbox"
                  name="services"
                  value={service.value}
                  checked={services.includes(service.value)}
                  onChange={() => toggleService(service.value)}
                />
                {service.label}
              </label>
            ))}
          </fieldset>
          {first('services') ? (
            <span role="alert" style={{ color: 'var(--danger)', fontSize: 13 }}>
              {first('services')}
            </span>
          ) : null}
        </div>
      </div>

      <div className={styles.question}>
        <span className={styles.index} aria-hidden="true">
          04
        </span>
        <div className={styles.body}>
          <div className={styles.pair}>
            <Field id="budget" label="Budget" error={first('budget')}>
              <select
                className="control"
                id="budget"
                name="budget"
                value={values.budget}
                onChange={(event) => set('budget', event.target.value)}
                aria-invalid={first('budget') ? true : undefined}
              >
                <option value="">Choose a range</option>
                {BUDGETS.map((budget) => (
                  <option key={budget.value} value={budget.value}>
                    {budget.label}
                  </option>
                ))}
              </select>
            </Field>
            <Field id="timeline" label="Timeline" error={first('timeline')}>
              <select
                className="control"
                id="timeline"
                name="timeline"
                value={values.timeline}
                onChange={(event) => set('timeline', event.target.value)}
                aria-invalid={first('timeline') ? true : undefined}
              >
                <option value="">Choose a timeline</option>
                {TIMELINES.map((timeline) => (
                  <option key={timeline.value} value={timeline.value}>
                    {timeline.label}
                  </option>
                ))}
              </select>
            </Field>
          </div>
        </div>
      </div>

      <div className={styles.question}>
        <span className={styles.index} aria-hidden="true">
          05
        </span>
        <div className={styles.body}>
          <Field
            id="needs"
            label="What are you trying to achieve?"
            hint="The outcome, not the feature list. What changes for the business if this works?"
            error={first('needs')}
          >
            <textarea
              className="control"
              id="needs"
              name="needs"
              value={values.needs}
              onChange={(event) => set('needs', event.target.value)}
              aria-invalid={first('needs') ? true : undefined}
              aria-describedby={
                first('needs') ? 'needs-error needs-hint' : 'needs-hint'
              }
            />
          </Field>
          <Field
            id="source"
            label="How did you find us?"
            hint="Optional."
            error={first('source')}
          >
            <input
              className="control"
              id="source"
              name="source"
              value={values.source}
              onChange={(event) => set('source', event.target.value)}
            />
          </Field>
        </div>
      </div>

      {/* Honeypot. Positioned off-screen and hidden from assistive tech, never from bots. */}
      <div className={styles.trap} aria-hidden="true">
        <label htmlFor="website">Website</label>
        <input
          id="website"
          name="website"
          tabIndex={-1}
          autoComplete="off"
          value={values.website}
          onChange={(event) => set('website', event.target.value)}
        />
      </div>

      {formError ? <p className={styles.summary}>{formError}</p> : null}

      <div className={styles.actions}>
        <button className="btn btn-primary" type="submit" disabled={submitting}>
          {submitting ? 'Sending...' : 'Send enquiry'}
        </button>
        <span className="muted" style={{ fontSize: 14 }}>
          We reply to everything.
        </span>
      </div>
    </form>
  );
}
