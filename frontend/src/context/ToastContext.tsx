import {
  createContext,
  useContext,
  useMemo,
  useState,
  type PropsWithChildren
} from "react";
import { AnimatePresence, motion } from "framer-motion";
import { X } from "lucide-react";
import { clsx } from "clsx";

export interface ToastOptions {
  title: string;
  description?: string;
  variant?: "default" | "success" | "warning" | "error";
}

interface ToastContextValue {
  addToast: (toast: ToastOptions) => void;
}

const ToastContext = createContext<ToastContextValue | undefined>(undefined);

interface ToastState extends ToastOptions {
  id: string;
}

export const ToastProvider = ({ children }: PropsWithChildren) => {
  const [toasts, setToasts] = useState<ToastState[]>([]);

  const addToast = (toast: ToastOptions) => {
    const id = crypto.randomUUID();
    setToasts((current) => [...current, { id, ...toast }]);
    window.setTimeout(() => {
      setToasts((current) => current.filter((item) => item.id !== id));
    }, 4_000);
  };

  const removeToast = (id: string) => {
    setToasts((current) => current.filter((item) => item.id !== id));
  };

  const value = useMemo<ToastContextValue>(() => ({ addToast }), []);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="fixed bottom-4 right-4 z-50 flex w-80 flex-col gap-3">
        <AnimatePresence>
          {toasts.map((toast) => (
            <motion.div
              key={toast.id}
              layout
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 16 }}
              className={clsx(
                "rounded-xl border border-white/10 bg-white/5 backdrop-blur p-4 shadow-lg",
                toast.variant === "success" && "border-emerald-400/40 text-emerald-100",
                toast.variant === "warning" && "border-amber-400/40 text-amber-100",
                toast.variant === "error" && "border-rose-400/40 text-rose-100"
              )}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="space-y-1">
                  <p className="font-semibold tracking-tight">{toast.title}</p>
                  {toast.description ? (
                    <p className="text-sm text-white/70">{toast.description}</p>
                  ) : null}
                </div>
                <button
                  aria-label="Dismiss toast"
                  className="rounded-md border border-white/10 bg-white/10 p-1 text-xs text-white/70 transition hover:border-white/20 hover:text-white"
                  onClick={() => removeToast(toast.id)}
                  type="button"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
};

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return context;
};
