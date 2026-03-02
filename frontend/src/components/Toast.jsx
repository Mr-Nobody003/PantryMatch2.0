import React, { useEffect } from 'react';

function Toast({ toast, onClose }) {
  useEffect(() => {
    if (!toast) return undefined;
    const t = setTimeout(() => {
      onClose?.();
    }, toast.durationMs ?? 2800);
    return () => clearTimeout(t);
  }, [toast, onClose]);

  if (!toast) return null;

  return (
    <div className="toast-host" role="status" aria-live="polite">
      <div className={`toast toast-${toast.type || 'info'}`}>
        <div className="toast-title">{toast.title}</div>
        {toast.message ? <div className="toast-message">{toast.message}</div> : null}
        <button type="button" className="toast-close" onClick={onClose} aria-label="Close">
          ×
        </button>
      </div>
    </div>
  );
}

export default Toast;

