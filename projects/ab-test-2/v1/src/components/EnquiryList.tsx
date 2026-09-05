import type { EnquirySummary } from '../types.ts';

type Props = {
  enquiries: EnquirySummary[];
  selectedId: number | null;
  loading: boolean;
  onSelect: (id: number) => void;
};

export function EnquiryList({ enquiries, selectedId, loading, onSelect }: Props) {
  if (loading) {
    return (
      <div aria-busy="true" aria-label="Loading enquiries">
        <div className="skeleton" />
        <div className="skeleton short" />
        <div className="skeleton" />
      </div>
    );
  }

  if (enquiries.length === 0) {
    return (
      <p style={{ fontSize: 13, color: 'var(--ink-3)', lineHeight: 1.6, margin: 0 }}>
        Nothing here yet. Paste an enquiry above, subject and body, and it will show up in this
        list ready to draft against.
      </p>
    );
  }

  return (
    <ul className="enquiry-list">
      {enquiries.map((enquiry) => (
        <li key={enquiry.id}>
          <button
            type="button"
            className="enquiry-item"
            aria-current={enquiry.id === selectedId}
            onClick={() => onSelect(enquiry.id)}
          >
            <span className="subject">{enquiry.subject}</span>
            <span className="preview">{enquiry.bodyPreview}</span>
            <span className="meta">
              <span
                className={`dot ${enquiry.latestRating ?? 'none'}`}
                aria-hidden="true"
              />
              <span>
                {enquiry.draftCount} draft{enquiry.draftCount === 1 ? '' : 's'}
              </span>
              {enquiry.latestRating ? <span>· rated {enquiry.latestRating}</span> : null}
            </span>
          </button>
        </li>
      ))}
    </ul>
  );
}
