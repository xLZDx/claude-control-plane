export function Dialog({ open, onClose, children }) {
  if (!open) return null;
  return (
    <div className="overlay" onClick={onClose}>
      <div className="dialog">
        {children}
        <span onClick={onClose}>x</span>
      </div>
    </div>
  );
}
