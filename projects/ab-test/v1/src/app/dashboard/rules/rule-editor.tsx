'use client';

import { useState } from 'react';
import { SERVICES, TIMELINES } from '@/lib/options';
import { RULE_FIELDS, RULE_OPERATORS } from '@/types';
import type { Bands, Rule, RuleField, RuleOperator, RuleValue } from '@/types';
import styles from './rules.module.css';

interface Props {
  initialRules: Rule[];
  initialBands: Bands;
}

/** Draft shape: value is held as a string while editing, parsed on save. */
interface Draft {
  key: string;
  label: string;
  field: RuleField;
  operator: RuleOperator;
  value: string;
  points: number;
  enabled: boolean;
}

const FIELD_LABELS: Record<RuleField, string> = {
  budget: 'Budget',
  timeline: 'Timeline',
  services: 'Services',
  needs: 'What they need',
  company: 'Company',
  source: 'How they found us',
  email: 'Email',
};

const OPERATOR_LABELS: Record<RuleOperator, string> = {
  gte: 'is at least',
  lte: 'is at most',
  eq: 'is',
  neq: 'is not',
  contains: 'contains',
  in: 'is one of',
  present: 'is filled in',
  absent: 'is empty',
};

/** Which operators actually make sense per field. The engine tolerates the rest; the
    editor just does not offer them, so a rule that can never fire is hard to build. */
const FIELD_OPERATORS: Record<RuleField, RuleOperator[]> = {
  budget: ['gte', 'lte', 'eq', 'neq'],
  timeline: ['eq', 'neq', 'in'],
  services: ['contains', 'in', 'gte', 'present', 'absent'],
  needs: ['contains', 'present', 'absent'],
  company: ['present', 'absent', 'contains', 'eq'],
  source: ['contains', 'present', 'absent', 'eq'],
  email: ['contains', 'present', 'absent', 'eq'],
};

const VALUELESS: RuleOperator[] = ['present', 'absent'];

function valueToText(value: RuleValue): string {
  if (Array.isArray(value)) return value.join(', ');
  return String(value);
}

function textToValue(text: string, operator: RuleOperator, field: RuleField): RuleValue {
  if (VALUELESS.includes(operator)) return '';
  if (operator === 'in') {
    return text
      .split(',')
      .map((entry) => entry.trim())
      .filter(Boolean);
  }
  if (operator === 'gte' || operator === 'lte' || field === 'budget') {
    const numeric = Number(text);
    return Number.isFinite(numeric) ? numeric : text;
  }
  return text;
}

function toDraft(rule: Rule, index: number): Draft {
  return {
    key: rule.id || 'rule-' + index,
    label: rule.label,
    field: rule.field,
    operator: rule.operator,
    value: valueToText(rule.value),
    points: rule.points,
    enabled: rule.enabled,
  };
}

/** Suggestions so the operator does not have to remember the stored value strings. */
function suggestionsFor(field: RuleField): string[] {
  if (field === 'timeline') return TIMELINES.map((option) => option.value);
  if (field === 'services') return SERVICES.map((option) => option.value);
  return [];
}

export function RuleEditor({ initialRules, initialBands }: Props) {
  const [drafts, setDrafts] = useState<Draft[]>(initialRules.map(toDraft));
  const [bands, setBands] = useState<Bands>(initialBands);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [failed, setFailed] = useState(false);
  const [nextKey, setNextKey] = useState(0);

  function update(index: number, patch: Partial<Draft>) {
    setDrafts((current) =>
      current.map((draft, position) => (position === index ? { ...draft, ...patch } : draft)),
    );
    setMessage('');
  }

  function changeField(index: number, field: RuleField) {
    const allowed = FIELD_OPERATORS[field];
    setDrafts((current) =>
      current.map((draft, position) => {
        if (position !== index) return draft;
        const operator = allowed.includes(draft.operator) ? draft.operator : (allowed[0] as RuleOperator);
        return { ...draft, field, operator };
      }),
    );
    setMessage('');
  }

  function move(index: number, delta: number) {
    const target = index + delta;
    if (target < 0 || target >= drafts.length) return;
    setDrafts((current) => {
      const next = [...current];
      const moved = next[index];
      const other = next[target];
      if (!moved || !other) return current;
      next[index] = other;
      next[target] = moved;
      return next;
    });
    setMessage('');
  }

  function addRule() {
    setDrafts((current) => [
      ...current,
      {
        key: 'new-' + nextKey,
        label: '',
        field: 'budget',
        operator: 'gte',
        value: '5000',
        points: 10,
        enabled: true,
      },
    ]);
    setNextKey((value) => value + 1);
    setMessage('');
  }

  function removeRule(index: number) {
    setDrafts((current) => current.filter((_, position) => position !== index));
    setMessage('');
  }

  async function save() {
    setSaving(true);
    setMessage('');
    setFailed(false);

    const payload = {
      rules: drafts.map((draft) => ({
        label: draft.label.trim(),
        field: draft.field,
        operator: draft.operator,
        value: textToValue(draft.value, draft.operator, draft.field),
        points: Number(draft.points),
        enabled: draft.enabled,
      })),
      bands: { hot: Number(bands.hot), warm: Number(bands.warm) },
    };

    try {
      const response = await fetch('/api/rules', {
        method: 'PUT',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const body = (await response.json().catch(() => ({}))) as {
        error?: string;
        rescored?: number;
        rules?: Rule[];
      };

      if (!response.ok) {
        setFailed(true);
        setMessage(body.error ?? 'Could not save those rules.');
        return;
      }

      if (body.rules) setDrafts(body.rules.map(toDraft));
      setMessage('Saved. ' + (body.rescored ?? 0) + ' leads rescored.');
    } catch {
      setFailed(true);
      setMessage('We could not reach the server.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="shell">
      <div className={styles.header}>
        <h1>Scoring rules</h1>
        <p className="prose muted">
          Every rule that matches adds its points to the lead. Points can be negative.
          The total is capped at 100. Saving rescores every lead you already have.
        </p>
      </div>

      <div className={styles.bands}>
        <div className={styles.bandField}>
          <label className={styles.bandLabel + ' ' + styles.hotLabel} htmlFor="band-hot">
            Hot at
          </label>
          <input
            id="band-hot"
            className="control"
            type="number"
            min={1}
            max={100}
            value={bands.hot}
            onChange={(event) =>
              setBands((current) => ({ ...current, hot: Number(event.target.value) }))
            }
          />
        </div>
        <div className={styles.bandField}>
          <label className={styles.bandLabel + ' ' + styles.warmLabel} htmlFor="band-warm">
            Warm at
          </label>
          <input
            id="band-warm"
            className="control"
            type="number"
            min={0}
            max={99}
            value={bands.warm}
            onChange={(event) =>
              setBands((current) => ({ ...current, warm: Number(event.target.value) }))
            }
          />
        </div>
        <p className={styles.bandNote}>
          Anything below the warm threshold is cold. The hot threshold has to sit above the
          warm one.
        </p>
      </div>

      <div className={styles.columnHead} aria-hidden="true">
        <span>#</span>
        <span>Rule name</span>
        <span>Field</span>
        <span>Test</span>
        <span>Value</span>
        <span>Points</span>
        <span />
      </div>

      <div className={styles.list}>
        {drafts.map((draft, index) => {
          const operators = FIELD_OPERATORS[draft.field];
          const needsValue = !VALUELESS.includes(draft.operator);
          const listId = 'suggest-' + draft.key;
          const suggestions = suggestionsFor(draft.field);

          return (
            <div
              key={draft.key}
              className={styles.rule + (draft.enabled ? '' : ' ' + styles.ruleDisabled)}
            >
              <span className={styles.position}>
                {String(index + 1).padStart(2, '0')}
              </span>

              <div className={styles.cell}>
                <label className="sr-only" htmlFor={'label-' + draft.key}>
                  Rule name
                </label>
                <input
                  id={'label-' + draft.key}
                  className={'control ' + styles.small}
                  value={draft.label}
                  placeholder="Name this rule"
                  onChange={(event) => update(index, { label: event.target.value })}
                />
              </div>

              <div className={styles.cell}>
                <label className="sr-only" htmlFor={'field-' + draft.key}>
                  Field
                </label>
                <select
                  id={'field-' + draft.key}
                  className={'control ' + styles.small}
                  value={draft.field}
                  onChange={(event) => changeField(index, event.target.value as RuleField)}
                >
                  {RULE_FIELDS.map((field) => (
                    <option key={field} value={field}>
                      {FIELD_LABELS[field]}
                    </option>
                  ))}
                </select>
              </div>

              <div className={styles.cell}>
                <label className="sr-only" htmlFor={'op-' + draft.key}>
                  Test
                </label>
                <select
                  id={'op-' + draft.key}
                  className={'control ' + styles.small}
                  value={draft.operator}
                  onChange={(event) =>
                    update(index, { operator: event.target.value as RuleOperator })
                  }
                >
                  {(operators ?? RULE_OPERATORS).map((operator) => (
                    <option key={operator} value={operator}>
                      {OPERATOR_LABELS[operator]}
                    </option>
                  ))}
                </select>
              </div>

              <div className={styles.cell}>
                <label className="sr-only" htmlFor={'value-' + draft.key}>
                  Value
                </label>
                <input
                  id={'value-' + draft.key}
                  className={'control ' + styles.small}
                  value={needsValue ? draft.value : ''}
                  disabled={!needsValue}
                  list={suggestions.length > 0 ? listId : undefined}
                  placeholder={draft.operator === 'in' ? 'comma, separated' : ''}
                  onChange={(event) => update(index, { value: event.target.value })}
                />
                {suggestions.length > 0 ? (
                  <datalist id={listId}>
                    {suggestions.map((suggestion) => (
                      <option key={suggestion} value={suggestion} />
                    ))}
                  </datalist>
                ) : null}
              </div>

              <div className={styles.cell}>
                <label className="sr-only" htmlFor={'points-' + draft.key}>
                  Points
                </label>
                <input
                  id={'points-' + draft.key}
                  className={'control ' + styles.small + ' ' + styles.points}
                  type="number"
                  min={-100}
                  max={100}
                  value={draft.points}
                  onChange={(event) => update(index, { points: Number(event.target.value) })}
                />
              </div>

              <div className={styles.ruleActions}>
                <label className={styles.toggle}>
                  <span className="sr-only">Enable {draft.label || 'rule ' + (index + 1)}</span>
                  <input
                    type="checkbox"
                    checked={draft.enabled}
                    onChange={(event) => update(index, { enabled: event.target.checked })}
                  />
                </label>
                <button
                  type="button"
                  className={styles.iconBtn}
                  onClick={() => move(index, -1)}
                  disabled={index === 0}
                  aria-label={'Move ' + (draft.label || 'rule') + ' up'}
                >
                  ^
                </button>
                <button
                  type="button"
                  className={styles.iconBtn}
                  onClick={() => move(index, 1)}
                  disabled={index === drafts.length - 1}
                  aria-label={'Move ' + (draft.label || 'rule') + ' down'}
                >
                  v
                </button>
                <button
                  type="button"
                  className={styles.iconBtn}
                  onClick={() => removeRule(index)}
                  aria-label={'Delete ' + (draft.label || 'rule')}
                >
                  x
                </button>
              </div>
            </div>
          );
        })}
      </div>

      <p className={styles.hint}>
        Tiers stack on purpose. A $10k lead matches both &quot;at least 10000&quot; and
        &quot;at least 5000&quot;, and the receipt on each lead shows exactly which rules
        fired, so the total is always explainable.
      </p>

      <div className={styles.footer}>
        <button className="btn btn-primary" onClick={save} disabled={saving} type="button">
          {saving ? 'Saving...' : 'Save and rescore'}
        </button>
        <button className="btn btn-secondary" onClick={addRule} disabled={saving} type="button">
          Add rule
        </button>
        {message ? (
          <span
            className={styles.status + ' ' + (failed ? styles.bad : styles.ok)}
            role="status"
          >
            {message}
          </span>
        ) : null}
      </div>
    </div>
  );
}
