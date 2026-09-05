import type { LeadStatus } from '@/types';
import styles from './status-pill.module.css';

const LABELS: Record<LeadStatus, string> = {
  new: 'New',
  contacted: 'Contacted',
  qualified: 'Qualified',
  dead: 'Dead',
};

export function StatusPill({ status }: { status: LeadStatus }) {
  return <span className={styles.pill + ' ' + styles[status]}>{LABELS[status]}</span>;
}

export const STATUS_LABELS = LABELS;
