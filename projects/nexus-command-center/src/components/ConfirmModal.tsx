interface Props {
  title: string;
  description: string;
  note: string;
  onCancel: () => void;
  onConfirm: () => void;
}

/** Shared confirm gate for deck presets and skill actions (design-system.md §6). */
export default function ConfirmModal({ title, description, note, onCancel, onConfirm }: Props) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ background: "rgba(0,0,0,0.55)", backdropFilter: "blur(8px)" }}
      onClick={onCancel}
    >
      <div
        className="np-panel w-[440px] p-6"
        style={{ transform: "scale(1)", transition: "transform 240ms var(--np-ease)" }}
        onClick={(e) => e.stopPropagation()}
      >
        <h3 className="np-display mb-1 text-xl">{title}</h3>
        <p className="mb-4 text-sm" style={{ color: "var(--np-fog)" }}>
          {description}
        </p>
        <div
          className="np-mono mb-5 rounded-md p-3"
          style={{ background: "rgba(11,11,11,0.7)", border: "1px solid var(--np-hairline)" }}
        >
          {note}
        </div>
        <div className="flex justify-end gap-3">
          <button className="np-btn-ghost" onClick={onCancel}>
            Cancel
          </button>
          <button className="np-btn-primary" onClick={onConfirm}>
            Run
          </button>
        </div>
      </div>
    </div>
  );
}
