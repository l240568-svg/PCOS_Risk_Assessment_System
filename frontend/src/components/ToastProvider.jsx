import { CheckCircle2, CircleAlert, Info, X, XCircle } from "lucide-react";
import { createContext, useCallback, useContext, useMemo, useRef, useState } from "react";

const ToastContext = createContext(null);

const icons = {
  success: CheckCircle2,
  error: XCircle,
  warning: CircleAlert,
  info: Info,
};

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const nextId = useRef(1);

  const removeToast = useCallback((id) => {
    setToasts((current) => current.filter((toast) => toast.id !== id));
  }, []);

  const showToast = useCallback(
    (message, type = "success") => {
      const id = nextId.current++;
      setToasts((current) => [...current, { id, message, type }]);
      window.setTimeout(() => removeToast(id), 4500);
      return id;
    },
    [removeToast],
  );

  const value = useMemo(() => ({ showToast, removeToast }), [showToast, removeToast]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="toast-region" aria-live="polite" aria-atomic="true">
        {toasts.map((toast) => {
          const Icon = icons[toast.type] || Info;
          return (
            <div className={`toast toast-${toast.type}`} key={toast.id}>
              <Icon size={19} aria-hidden="true" />
              <p>{toast.message}</p>
              <button
                type="button"
                className="icon-button icon-button-small"
                onClick={() => removeToast(toast.id)}
                aria-label="Dismiss notification"
              >
                <X size={16} />
              </button>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) throw new Error("useToast must be used inside ToastProvider");
  return context;
}
