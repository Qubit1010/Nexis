import { useState } from 'react';

type Props = {
  onCreate: (subject: string, body: string) => Promise<void>;
};

export function NewEnquiry({ onCreate }: Props) {
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canSubmit = subject.trim().length > 0 && body.trim().length > 0 && !busy;

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!canSubmit) return;
    setBusy(true);
    setError(null);
    try {
      await onCreate(subject.trim(), body.trim());
      setSubject('');
      setBody('');
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Could not save that enquiry');
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <h2 className="section-label">Paste an enquiry</h2>

      <div className="field-group">
        <label htmlFor="new-subject">Subject</label>
        <input
          id="new-subject"
          type="text"
          value={subject}
          maxLength={300}
          placeholder="Website redesign + booking automation"
          onChange={(event) => setSubject(event.target.value)}
        />
      </div>

      <div className="field-group">
        <label htmlFor="new-body">Message</label>
        <textarea
          id="new-body"
          className="field"
          value={body}
          maxLength={20000}
          placeholder="Paste what they actually sent you."
          onChange={(event) => setBody(event.target.value)}
        />
      </div>

      {error ? <p className="error">{error}</p> : null}

      <button type="submit" className="primary" disabled={!canSubmit}>
        {busy ? 'Saving...' : 'Add enquiry'}
      </button>
    </form>
  );
}
