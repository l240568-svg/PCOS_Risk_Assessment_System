import { AlertTriangle, Inbox, RefreshCw, X } from "lucide-react";
import { useEffect, useId } from "react";
import { createPortal } from "react-dom";

export function Spinner({ label = "Loading" }) {
  return (
    <span className="inline-loader" role="status">
      <span className="spinner" aria-hidden="true" />
      <span>{label}</span>
    </span>
  );
}

export function PageLoader({ label = "Loading information" }) {
  return (
    <div className="page-state" role="status">
      <span className="spinner spinner-large" aria-hidden="true" />
      <p>{label}</p>
    </div>
  );
}

export function ErrorState({ message, onRetry }) {
  return (
    <div className="page-state page-state-error" role="alert">
      <AlertTriangle size={30} aria-hidden="true" />
      <h2>We could not load this view</h2>
      <p>{message}</p>
      {onRetry && (
        <button className="button button-secondary" type="button" onClick={onRetry}>
          <RefreshCw size={17} /> Retry
        </button>
      )}
    </div>
  );
}

export function EmptyState({ title, message, action }) {
  return (
    <div className="empty-state">
      <span className="empty-state-icon" aria-hidden="true">
        <Inbox size={25} />
      </span>
      <h3>{title}</h3>
      <p>{message}</p>
      {action}
    </div>
  );
}

export function RiskBadge({ value }) {
  const className =
    value === "High Risk" ? "risk-high" : value === "Low Risk" ? "risk-low" : "risk-none";
  return <span className={`risk-badge ${className}`}>{value || "Not assessed"}</span>;
}

export function Field({ label, hint, error, id: providedId, children, required = false }) {
  const generatedId = useId();
  const id = providedId || generatedId;
  const hintId = hint ? `${id}-hint` : undefined;
  const errorId = error ? `${id}-error` : undefined;

  return (
    <div className={`field ${error ? "field-error" : ""}`}>
      <label htmlFor={id}>
        {label} {required && <span aria-hidden="true">*</span>}
      </label>
      {typeof children === "function"
        ? children({ id, "aria-describedby": errorId || hintId, "aria-invalid": Boolean(error) })
        : children}
      {hint && !error && <small id={hintId}>{hint}</small>}
      {error && <small id={errorId}>{error}</small>}
    </div>
  );
}

export function SwitchField({ label, checked, onChange, hint }) {
  const id = useId();
  return (
    <label className="switch-row" htmlFor={id}>
      <span>
        <strong>{label}</strong>
        {hint && <small>{hint}</small>}
      </span>
      <span className="switch-control">
        <input
          id={id}
          type="checkbox"
          checked={checked}
          onChange={(event) => onChange(event.target.checked)}
        />
        <span aria-hidden="true" />
      </span>
    </label>
  );
}

export function Drawer({ open, title, description, onClose, children, wide = false }) {
  useEffect(() => {
    if (!open) return undefined;
    const previousOverflow = document.body.style.overflow;
    const handleKey = (event) => {
      if (event.key === "Escape") onClose();
    };
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", handleKey);
    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", handleKey);
    };
  }, [open, onClose]);

  if (!open) return null;

  return createPortal(
    <div className="overlay" role="presentation" onMouseDown={onClose}>
      <section
        className={`drawer ${wide ? "drawer-wide" : ""}`}
        role="dialog"
        aria-modal="true"
        aria-labelledby="drawer-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <header className="drawer-header">
          <div>
            <h2 id="drawer-title">{title}</h2>
            {description && <p>{description}</p>}
          </div>
          <button className="icon-button" type="button" onClick={onClose} aria-label="Close panel">
            <X size={20} />
          </button>
        </header>
        <div className="drawer-body">{children}</div>
      </section>
    </div>,
    document.body,
  );
}

export function ConfirmDialog({ open, title, message, confirmLabel = "Delete", loading, onCancel, onConfirm }) {
  useEffect(() => {
    if (!open) return undefined;
    const handleKey = (event) => {
      if (event.key === "Escape" && !loading) onCancel();
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [open, loading, onCancel]);

  if (!open) return null;

  return createPortal(
    <div className="overlay overlay-centered" role="presentation" onMouseDown={onCancel}>
      <section
        className="confirm-dialog"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="confirm-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <span className="danger-icon" aria-hidden="true">
          <AlertTriangle size={24} />
        </span>
        <h2 id="confirm-title">{title}</h2>
        <p>{message}</p>
        <div className="dialog-actions">
          <button className="button button-secondary" type="button" onClick={onCancel} disabled={loading}>
            Cancel
          </button>
          <button className="button button-danger" type="button" onClick={onConfirm} disabled={loading}>
            {loading ? <Spinner label="Deleting" /> : confirmLabel}
          </button>
        </div>
      </section>
    </div>,
    document.body,
  );
}
