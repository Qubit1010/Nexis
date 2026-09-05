import type { ReactNode } from 'react';
import styles from './field.module.css';

interface Props {
  id: string;
  label: string;
  hint?: string;
  error?: string;
  children: ReactNode;
}

/**
 * Keeps the label/hint/error wiring in one place so no control can ship unlabelled or
 * with an error the screen reader never announces.
 */
export function Field({ id, label, hint, error, children }: Props) {
  const describedBy = [hint ? id + '-hint' : '', error ? id + '-error' : '']
    .filter(Boolean)
    .join(' ');

  return (
    <div className={styles.field}>
      <label className={styles.label} htmlFor={id}>
        {label}
      </label>
      {hint ? (
        <span className={styles.hint} id={id + '-hint'}>
          {hint}
        </span>
      ) : null}
      <div data-describedby={describedBy || undefined}>{children}</div>
      {error ? (
        <span className={styles.error} id={id + '-error'} role="alert">
          {error}
        </span>
      ) : null}
    </div>
  );
}
